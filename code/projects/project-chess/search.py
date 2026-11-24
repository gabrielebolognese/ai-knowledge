"""Alpha-beta search: the half of the engine that imagines the future.

    python search.py                    # searches a few test positions and prints the result
    python search.py --fen "<FEN>" --depth 5
    python search.py --movetime 2000    # iterative deepening for 2 seconds

What is inside (each part has a lesson in the chess track):
  * negamax with alpha-beta pruning ............ Searcher.negamax
  * mate / stalemate / repetition / 50-move draws
  * move ordering: hash move, MVV-LVA captures, two killer moves per ply,
    history heuristic ........................... Searcher.order_moves
  * quiescence search (captures only, check evasions, losing captures
    skipped) ................................... Searcher.qsearch
  * iterative deepening with a time limit, node limit and a stop flag
  * a transposition table keyed by python-chess's Zobrist hash
    (chess.polyglot.zobrist_hash), with EXACT / LOWER / UPPER bounds and
    mate scores stored relative to the node

The evaluator is pluggable: anything with evaluate(board, key) -> centipawns
for the side to move. MaterialEvaluator (eval_material.py) and NNEvaluator
(eval_nn.py) both qualify. If the evaluator also has push(board, move), pop()
and reset(board), the search calls them around every move so an NNUE-style
accumulator can be updated incrementally.

Sources: https://www.chessprogramming.org/Alpha-Beta, .../Negamax,
.../Quiescence_Search, .../MVV-LVA, .../Killer_Heuristic, .../History_Heuristic,
.../Iterative_Deepening, .../Transposition_Table, .../Zobrist_Hashing
"""
import argparse
import threading
import time
from dataclasses import dataclass, field

import chess
import chess.polyglot

from eval_material import PIECE_VALUES, MaterialEvaluator

INF = 1_000_000
MATE = 100_000            # score of "checkmate right now"; a mate in n plies scores MATE - n
MATE_BOUND = MATE - 1_000  # anything above this is a mate score
MAX_PLY = 128

# Transposition-table bound types.
EXACT, LOWER, UPPER = 0, 1, 2

# Move-ordering priorities (bigger = searched earlier).
HASH_MOVE = 10_000_000
CAPTURE_BASE = 1_000_000
KILLER_1, KILLER_2 = 900_000, 800_000


class SearchStopped(Exception):
    """Raised inside the tree when time, nodes or the stop flag run out."""


@dataclass
class SearchResult:
    move: chess.Move | None
    score: int
    depth: int
    nodes: int
    seconds: float
    pv: list = field(default_factory=list)


def mvv_lva(board: chess.Board, move: chess.Move) -> int:
    """Most Valuable Victim - Least Valuable Aggressor: 10 * victim - attacker.

    PxQ = 10*900 - 100 = 8,900 (try first);  QxP = 10*100 - 900 = 100 (try last).
    """
    if board.is_en_passant(move):
        victim = PIECE_VALUES[chess.PAWN]
    else:
        victim = PIECE_VALUES[board.piece_type_at(move.to_square)]
    attacker = PIECE_VALUES[board.piece_type_at(move.from_square)] or 1_000  # king = "most valuable" attacker
    return 10 * victim - attacker


def score_to_uci(score: int) -> str:
    """'cp 34' or 'mate 3' (moves, not plies), as the UCI protocol expects."""
    if score > MATE_BOUND:
        return f"mate {(MATE - score + 1) // 2}"
    if score < -MATE_BOUND:
        return f"mate -{(MATE + score) // 2}"
    return f"cp {score}"


class Searcher:
    def __init__(self, evaluator=None, tt_size: int = 1_000_000,
                 use_ordering: bool = True, use_qsearch: bool = True, use_tt: bool = True):
        self.ev = evaluator or MaterialEvaluator()
        self.tt_size = tt_size
        self.use_ordering = use_ordering
        self.use_qsearch = use_qsearch
        self.use_tt = use_tt
        self.stop_event = threading.Event()
        self.tt: dict[int, tuple] = {}
        self.clear()

    # ------------------------------------------------------------------ setup
    def clear(self):
        """Forget everything (call on 'ucinewgame')."""
        self.tt.clear()
        self.history = [[0] * 64 for _ in range(64)]
        self.killers = [[None, None] for _ in range(MAX_PLY)]

    def stop(self):
        self.stop_event.set()

    def _has_hooks(self):
        return getattr(self.ev, "incremental", False)

    def _push(self, board, move):
        if self.hooks:
            self.ev.push(board, move)
        board.push(move)

    def _pop(self, board):
        board.pop()
        if self.hooks:
            self.ev.pop()

    def _check_limits(self):
        # Called every 1,024 nodes: cheap enough not to slow the search down.
        if self.stop_event.is_set():
            raise SearchStopped
        if self.deadline is not None and time.perf_counter() >= self.deadline:
            raise SearchStopped
        if self.node_limit is not None and self.nodes >= self.node_limit:
            raise SearchStopped

    # ----------------------------------------------------------- move ordering
    def order_moves(self, board: chess.Board, moves, ply: int, tt_move=None):
        """Sort moves so the likely best one comes first: alpha-beta prunes most when it does."""
        if not self.use_ordering:
            return moves
        killers = self.killers[ply] if ply < MAX_PLY else (None, None)

        def priority(m):
            if m == tt_move:
                return HASH_MOVE
            if board.is_capture(m):
                return CAPTURE_BASE + mvv_lva(board, m)
            if m.promotion:
                return CAPTURE_BASE + PIECE_VALUES[m.promotion]
            if m == killers[0]:
                return KILLER_1
            if m == killers[1]:
                return KILLER_2
            return self.history[m.from_square][m.to_square]

        return sorted(moves, key=priority, reverse=True)

    def _store_killer(self, move, ply, depth):
        """A quiet move that caused a beta cutoff: remember it for siblings at the same ply."""
        if ply < MAX_PLY and move != self.killers[ply][0]:
            self.killers[ply][1] = self.killers[ply][0]
            self.killers[ply][0] = move
        self.history[move.from_square][move.to_square] = min(self.history[move.from_square][move.to_square] + depth * depth, KILLER_2 - 1)

    # ------------------------------------------------------ transposition table
    def _tt_store(self, key, depth, flag, score, move, ply):
        if not self.use_tt:
            return
        if len(self.tt) >= self.tt_size:
            self.tt.clear()                      # simplest replacement scheme: start over
        # Mate scores are stored relative to THIS node, so they stay right at another ply.
        if score > MATE_BOUND:
            score += ply
        elif score < -MATE_BOUND:
            score -= ply
        self.tt[key] = (depth, flag, score, move)

    def _tt_probe(self, key, ply):
        entry = self.tt.get(key) if self.use_tt else None
        if entry is None:
            return None
        depth, flag, score, move = entry
        if score > MATE_BOUND:
            score -= ply
        elif score < -MATE_BOUND:
            score += ply
        return depth, flag, score, move

    # ------------------------------------------------------------------ search
    def evaluate(self, board, key):
        self.evals += 1
        return self.ev.evaluate(board, key)

    @staticmethod
    def _losing_capture(board: chess.Board, move: chess.Move) -> bool:
        """A cheap stand-in for static exchange evaluation (SEE): a bigger piece taking a
        smaller one on a defended square probably loses material, so qsearch skips it.
        This keeps quiescence from exploding when the evaluator is still weak."""
        if board.is_en_passant(move):
            return False
        victim = PIECE_VALUES[board.piece_type_at(move.to_square)]
        attacker = PIECE_VALUES[board.piece_type_at(move.from_square)] or 1_000
        return attacker > victim and board.is_attacked_by(not board.turn, move.to_square)

    def qsearch(self, board: chess.Board, alpha: int, beta: int, ply: int) -> int:
        """Quiescence search: keep resolving captures until the position is quiet.

        Without it the search stops in the middle of an exchange ("I take your queen")
        and never sees the recapture: the horizon effect.
        """
        self.nodes += 1
        if self.nodes & 1023 == 0:
            self._check_limits()
        if ply >= MAX_PLY - 1:
            return self.evaluate(board, None)
        in_check = board.is_check()
        if in_check:
            # In check you may not "stand pat": every evasion must be tried.
            moves = list(board.legal_moves)
            if not moves:
                return -MATE + ply
            best = -INF
        else:
            key = chess.polyglot.zobrist_hash(board) if self.wants_key else None
            stand_pat = self.evaluate(board, key)    # the side to move may decline every capture
            if stand_pat >= beta:
                return stand_pat
            alpha = max(alpha, stand_pat)
            best = stand_pat
            moves = [m for m in board.generate_legal_captures() if not self._losing_capture(board, m)]
            moves += [m for m in board.generate_legal_moves() if m.promotion == chess.QUEEN and not board.is_capture(m)]
        moves.sort(key=lambda m: mvv_lva(board, m) if board.is_capture(m) else 0, reverse=True)
        for move in moves:
            self._push(board, move)
            score = -self.qsearch(board, -beta, -alpha, ply + 1)
            self._pop(board)
            if score > best:
                best = score
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break
        return best

    def negamax(self, board: chess.Board, depth: int, alpha: int, beta: int, ply: int) -> int:
        """Value of `board` for the side to move, searched `depth` plies deep."""
        self.nodes += 1
        if self.nodes & 1023 == 0:
            self._check_limits()

        key = chess.polyglot.zobrist_hash(board)
        if ply > 0:
            # Draws: 50-move rule and repetition (of a position in the game or on this path).
            if board.halfmove_clock >= 100 or key in self.seen:
                return 0
            # Mate-distance pruning: no line from here can beat "mate at this ply".
            alpha = max(alpha, -MATE + ply)
            beta = min(beta, MATE - ply - 1)
            if alpha >= beta:
                return alpha

        in_check = board.is_check()
        if in_check and ply < MAX_PLY // 2:
            depth += 1                   # check extension: never stop the search in the middle of a check

        if depth <= 0:
            if self.use_qsearch:
                return self.qsearch(board, alpha, beta, ply)
            return self.evaluate(board, key)

        alpha_orig = alpha
        tt_move = None
        entry = self._tt_probe(key, ply)
        if entry is not None:
            tt_depth, flag, tt_score, tt_move = entry
            if ply > 0 and tt_depth >= depth:
                if flag == EXACT:
                    return tt_score
                if flag == LOWER and tt_score >= beta:
                    return tt_score
                if flag == UPPER and tt_score <= alpha:
                    return tt_score

        moves = list(board.legal_moves)
        if not moves:
            return -MATE + ply if in_check else 0   # checkmated (prefer slow losses) or stalemate

        moves = self.order_moves(board, moves, ply, tt_move)
        best, best_move = -INF, None
        self.seen.add(key)
        try:
            for move in moves:
                quiet = not board.is_capture(move) and not move.promotion
                self._push(board, move)
                score = -self.negamax(board, depth - 1, -beta, -alpha, ply + 1)
                self._pop(board)
                if score > best:
                    best, best_move = score, move
                    if ply == 0:
                        self.root_best = (move, score)   # usable even if the iteration is cut short
                if score > alpha:
                    alpha = score
                if alpha >= beta:                       # beta cutoff: the opponent will avoid this line
                    if quiet:
                        self._store_killer(move, ply, depth)
                    break
        finally:
            self.seen.discard(key)

        flag = UPPER if best <= alpha_orig else LOWER if best >= beta else EXACT
        self._tt_store(key, depth, flag, best, best_move, ply)
        return best

    def principal_variation(self, board: chess.Board, max_len: int = 12):
        """Follow best moves stored in the transposition table."""
        pv, b = [], board.copy(stack=False)
        for _ in range(max_len):
            entry = self.tt.get(chess.polyglot.zobrist_hash(b))
            if not entry or entry[3] is None or entry[3] not in b.legal_moves:
                break
            pv.append(entry[3])
            b.push(entry[3])
        return pv

    def search(self, board: chess.Board, max_depth: int = 64, time_limit: float | None = None,
               node_limit: int | None = None, info=None) -> SearchResult:
        """Iterative deepening: depth 1, 2, 3 ... until a limit hits; returns the best move found.

        time_limit is in seconds (None = no limit). info(dict) is called after every
        completed depth, which is how uci.py prints its 'info depth ...' lines.
        """
        board = board.copy()                 # never touch the caller's board
        self.stop_event.clear()
        self.nodes = self.evals = 0
        self.node_limit = node_limit
        start = time.perf_counter()
        self.deadline = start + time_limit if time_limit is not None else None
        self.killers = [[None, None] for _ in range(MAX_PLY)]
        self.hooks = self._has_hooks()
        self.wants_key = getattr(self.ev, "uses_key", False)   # only the NN cache needs hashes in qsearch
        if self.hooks:
            self.ev.reset(board)

        # Positions already played in the game count for repetition draws.
        self.seen = set()
        replay = board.root()
        for mv in board.move_stack:
            self.seen.add(chess.polyglot.zobrist_hash(replay))
            replay.push(mv)
        self.seen.discard(chess.polyglot.zobrist_hash(board))

        legal = list(board.legal_moves)
        if not legal:
            return SearchResult(None, -MATE if board.is_check() else 0, 0, 0, 0.0)
        best = SearchResult(legal[0], 0, 0, 0, 0.0)

        for depth in range(1, max_depth + 1):
            self.root_best = None
            try:
                score = self.negamax(board, depth, -INF, INF, 0)
            except SearchStopped:
                # Unfinished iteration: keep its best move only if it is a fully searched improvement.
                if self.root_best is not None and (best.depth == 0 or self.root_best[1] > best.score):
                    best.move, best.score = self.root_best
                break
            elapsed = time.perf_counter() - start
            entry = self.tt.get(chess.polyglot.zobrist_hash(board))
            move = entry[3] if entry and entry[3] is not None else (self.root_best or (legal[0],))[0]
            pv = self.principal_variation(board) or [move]
            best = SearchResult(move, score, depth, self.nodes, elapsed, pv)
            if info:
                info({"depth": depth, "score": score, "nodes": self.nodes, "seconds": elapsed,
                      "nps": int(self.nodes / elapsed) if elapsed > 0 else 0, "pv": pv})
            if abs(score) > MATE_BOUND and depth >= MATE - abs(score):
                break                         # a forced mate was found and fully proved
            # Soft limit: the next depth costs several times this one, so don't start it late.
            if time_limit is not None and elapsed > 0.45 * time_limit:
                break
        best.nodes = self.nodes
        best.seconds = time.perf_counter() - start
        return best


def minimax(board: chess.Board, depth: int, evaluate, counter=None) -> int:
    """Plain negamax without pruning, for comparison: same answer, many more nodes."""
    if counter is not None:
        counter[0] += 1
    moves = list(board.legal_moves)
    if not moves:
        return -MATE if board.is_check() else 0
    if depth == 0:
        return evaluate(board)
    best = -INF
    for m in moves:
        board.push(m)
        best = max(best, -minimax(board, depth - 1, evaluate, counter))
        board.pop()
    return best


TEST_POSITIONS = {
    "start position": chess.STARTING_FEN,
    "back-rank mate in 1 (a1a8)": "6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1",
    "mate in 2 (Kb6 or Kc7, then a rook mate)": "k7/8/2K5/8/8/8/8/7R w - - 0 1",
    "free queen: take it (e4xd5)": "rnb1kbnr/ppp1pppp/8/3q4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1",
    "Kiwipete (busy middlegame)": "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
}


def main():
    p = argparse.ArgumentParser(description="Run the alpha-beta search on a position")
    p.add_argument("--fen", help="position to search (default: a few test positions)")
    p.add_argument("--depth", type=int, default=4)
    p.add_argument("--movetime", type=int, help="milliseconds; overrides --depth")
    p.add_argument("--nn", metavar="WEIGHTS", help="use the neural evaluator (e.g. checkpoints/evaluator.npz)")
    a = p.parse_args()

    evaluator = None
    if a.nn:
        from eval_nn import NNEvaluator
        evaluator = NNEvaluator(a.nn)
    searcher = Searcher(evaluator)
    positions = {"your position": a.fen} if a.fen else TEST_POSITIONS
    for name, fen in positions.items():
        board = chess.Board(fen)
        searcher.clear()
        if a.movetime:
            r = searcher.search(board, time_limit=a.movetime / 1000)
        else:
            r = searcher.search(board, max_depth=a.depth)
        nps = int(r.nodes / r.seconds) if r.seconds else 0
        pv = board.variation_san(r.pv) if r.pv else ""
        print(f"{name}\n  best {board.san(r.move)}  score {score_to_uci(r.score)}  depth {r.depth}  "
              f"nodes {r.nodes:,}  {r.seconds:.2f}s  {nps:,} nodes/s\n  pv {pv}")


if __name__ == "__main__":
    main()
