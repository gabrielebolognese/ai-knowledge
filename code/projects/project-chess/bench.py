"""Measure the engine: perft, speed, the accumulator, UCI compliance and matches with an Elo estimate.

    python bench.py --smoke                  # everything quick (about a minute)
    python bench.py --perft                  # move-generation check against known perft counts
    python bench.py --speed --depth 4        # nodes, nodes/second, and what move ordering saves
    python bench.py --uci-check              # starts uci.py as a real UCI engine and talks to it
    python bench.py --match pst --games 100 --movetime 200      # network vs piece-square engine
    python bench.py --match stockfish --sf-skill 0 --games 20   # needs a stockfish binary
    python bench.py --match stockfish --sf-elo 1320 --games 50  # calibrated anchor (UCI_Elo >= 1320)

Elo from a match score s (wins + draws/2, divided by games):
    elo_difference = 400 * log10(s / (1 - s))
with a 95 % interval from the standard error of s. 100 games give roughly
+-70 Elo near a 50 % score, so small differences need many more games
(https://www.chessprogramming.org/Match_Statistics).

Honest expectations: this is a Python engine searching thousands of nodes per
second; Stockfish searches tens of millions. Expect to lose to full-strength
Stockfish every game. Stockfish's weakened settings (Skill Level 0, or
UCI_LimitStrength with UCI_Elo 1320, its minimum) are the useful yardsticks.
"""
import argparse
import math
import random
import shutil
import sys
import time
from pathlib import Path

import chess
import chess.engine

from eval_material import MaterialEvaluator
from search import Searcher

HERE = Path(__file__).parent

# ---------------------------------------------------------------------- perft
PERFT_SUITE = [
    # (name, FEN, [counts for depth 1, 2, 3, ...]) from https://www.chessprogramming.org/Perft_Results
    ("start position", chess.STARTING_FEN, [20, 400, 8_902, 197_281]),
    ("Kiwipete", "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1", [48, 2_039, 97_862]),
    ("position 3", "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1", [14, 191, 2_812, 43_238]),
]


def perft(board: chess.Board, depth: int) -> int:
    """Count the leaf nodes of the legal-move tree `depth` plies deep."""
    if depth == 1:
        return board.legal_moves.count()
    nodes = 0
    for move in board.legal_moves:
        board.push(move)
        nodes += perft(board, depth - 1)
        board.pop()
    return nodes


def run_perft(max_depth: int) -> bool:
    print("perft (counts every legal move sequence; a mismatch means a move-generation bug)")
    ok = True
    for name, fen, expected in PERFT_SUITE:
        board = chess.Board(fen)
        for depth, want in enumerate(expected[:max_depth], start=1):
            t = time.perf_counter()
            got = perft(board, depth)
            dt = time.perf_counter() - t
            flag = "ok" if got == want else "MISMATCH"
            ok &= got == want
            print(f"  {name:15s} depth {depth}: {got:>9,} (expected {want:>9,}) {flag}  {dt:.2f}s")
    return ok


# ---------------------------------------------------------------------- speed
SPEED_FENS = [
    chess.STARTING_FEN,
    "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",       # Italian game
    "r2q1rk1/pp2bppp/2n1pn2/3p4/3P4/2NBPN2/PP3PPP/R2Q1RK1 w - - 0 10",        # quiet middlegame
]


def load_nn(weights=None, accumulator=False):
    from eval_nn import NNEvaluator, find_weights
    path = find_weights(weights)
    if path is None or not path.exists():
        return None
    return NNEvaluator(path, accumulator=accumulator)


def run_speed(depth: int, weights=None):
    print(f"\nsearch speed, fixed depth {depth} (nodes include quiescence)")
    configs = [("material+pst, no move ordering", Searcher(MaterialEvaluator(), use_ordering=False)),
               ("material+pst", Searcher(MaterialEvaluator()))]
    nn = load_nn(weights)
    if nn is not None:
        configs.append((nn.name, Searcher(nn)))
        configs.append((load_nn(weights, accumulator=True).name, Searcher(load_nn(weights, accumulator=True))))
    else:
        print("  (no trained network found: run train.py to add it to the comparison)")
    for label, searcher in configs:
        nodes = secs = 0
        for fen in SPEED_FENS:
            searcher.clear()
            r = searcher.search(chess.Board(fen), max_depth=depth)
            nodes += r.nodes
            secs += r.seconds
        print(f"  {label:42s} {nodes:>9,} nodes  {secs:6.2f}s  {int(nodes / secs):>7,} nodes/s")


def run_accumulator_check(weights=None, plies: int = 80) -> bool:
    """Play random moves and compare the incremental accumulator with a full refresh at every step."""
    nn = load_nn(weights, accumulator=True)
    if nn is None:
        print("\naccumulator check skipped (no trained network)")
        return True
    full = load_nn(weights)
    rng = random.Random(1)
    board = chess.Board()
    nn.reset(board)
    worst = 0
    ops = []
    for _ in range(plies):
        moves = list(board.legal_moves)
        if not moves:
            break
        # Prefer captures/castling now and then so every update type gets tested.
        special = [m for m in moves if board.is_capture(m) or board.is_castling(m) or m.promotion]
        move = rng.choice(special if special and rng.random() < 0.5 else moves)
        removed, added = nn.changed_features(board, move)
        ops.append(len(removed) + len(added))
        nn.push(board, move)
        board.push(move)
        worst = max(worst, abs(nn.evaluate(board) - full.evaluate(board)))
    # Unwind everything and check we are back at the start.
    while board.move_stack:
        board.pop()
        nn.pop()
    worst = max(worst, abs(nn.evaluate(board) - full.evaluate(board)))
    ok = worst <= 1
    print(f"\naccumulator check: {len(ops)} moves, {sum(ops) / len(ops):.2f} column updates per move per perspective "
          f"(a full refresh adds ~{len(board.piece_map())}), max difference {worst} cp -> {'ok' if ok else 'BROKEN'}")
    return ok


# ------------------------------------------------------------------ UCI check
def run_uci_check() -> bool:
    """Start uci.py exactly as a GUI would and exercise the protocol through python-chess."""
    print("\nUCI check: launching `python uci.py` as a subprocess")
    cmd = [sys.executable, str(HERE / "uci.py")]
    ok = True
    with chess.engine.SimpleEngine.popen_uci(cmd, cwd=str(HERE)) as eng:
        print(f"  id name: {eng.id.get('name')}   options: {', '.join(sorted(eng.options))}")
        board = chess.Board()
        for _ in range(6):
            result = eng.play(board, chess.engine.Limit(time=0.2))
            ok &= result.move in board.legal_moves
            board.push(result.move)
        print(f"  played 6 plies at 0.2 s/move: {chess.Board().variation_san(board.move_stack)}")
        info = eng.analyse(chess.Board("6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1"), chess.engine.Limit(depth=3))
        ok &= info["pv"][0] == chess.Move.from_uci("a1a8")
        print(f"  mate-in-1 test: pv {info['pv'][0].uci()}, score {info['score'].white()}")
        with eng.analysis(chess.Board()) as analysis:      # 'go infinite', then 'stop' on exit
            for i, _ in enumerate(analysis):
                if i >= 2:
                    break
        print("  go infinite + stop: ok")
        result = eng.play(chess.Board(), chess.engine.Limit(white_clock=5, black_clock=5, white_inc=0.1, black_inc=0.1))
        ok &= result.move is not None
        print(f"  clock-based move (5 s + 0.1 s): {result.move.uci()}")
    print(f"  -> {'ok' if ok else 'FAILED'}")
    return ok


# --------------------------------------------------------------------- matches
OPENINGS = [  # short, balanced openings; each is played once with each colour
    "e2e4 e7e5 g1f3 b8c6", "d2d4 d7d5 c2c4 e7e6", "e2e4 c7c5 g1f3 d7d6", "d2d4 g8f6 c2c4 g7g6",
    "c2c4 e7e5 b1c3 g8f6", "e2e4 e7e6 d2d4 d7d5", "e2e4 c7c6 d2d4 d7d5", "g1f3 d7d5 g2g3 g8f6",
]


class InProcessPlayer:
    def __init__(self, name, searcher, movetime):
        self.name, self.searcher, self.movetime = name, searcher, movetime

    def new_game(self):
        self.searcher.clear()
        if hasattr(self.searcher.ev, "cache"):
            self.searcher.ev.cache.clear()

    def move(self, board):
        return self.searcher.search(board, time_limit=self.movetime).move

    def close(self):
        pass


class StockfishPlayer:
    def __init__(self, path, movetime, skill=None, elo=None):
        self.eng = chess.engine.SimpleEngine.popen_uci(path)
        if elo is not None:
            self.eng.configure({"UCI_LimitStrength": True, "UCI_Elo": elo})
            self.name = f"Stockfish UCI_Elo {elo}"
        else:
            self.eng.configure({"Skill Level": skill})
            self.name = f"Stockfish Skill Level {skill}"
        self.movetime = movetime

    def new_game(self):
        pass

    def move(self, board):
        return self.eng.play(board, chess.engine.Limit(time=self.movetime)).move

    def close(self):
        self.eng.quit()


def play_game(white, black, opening: str, max_plies: int = 300):
    board = chess.Board()
    for mv in opening.split():
        board.push_uci(mv)
    white.new_game()
    black.new_game()
    while not board.is_game_over(claim_draw=True) and len(board.move_stack) < max_plies:
        player = white if board.turn == chess.WHITE else black
        board.push(player.move(board))
    if len(board.move_stack) >= max_plies and not board.is_game_over(claim_draw=True):
        return "1/2-1/2", board
    return board.outcome(claim_draw=True).result(), board


def elo_report(wins, draws, losses):
    n = wins + draws + losses
    s = (wins + draws / 2) / n
    # Standard error of the mean score, using the actual spread of results (draws reduce it).
    var = (wins * (1 - s) ** 2 + draws * (0.5 - s) ** 2 + losses * (0 - s) ** 2) / n
    se = math.sqrt(var / n)

    def elo(x):
        x = min(max(x, 1e-3), 1 - 1e-3)
        return 400 * math.log10(x / (1 - x))

    los = 0.5 * (1 + math.erf((wins - losses) / math.sqrt(2 * (wins + losses)))) if wins + losses else 0.5
    return s, elo(s), elo(s - 1.96 * se), elo(s + 1.96 * se), los


def run_match(kind, games, movetime, weights=None, stockfish=None, sf_skill=0, sf_elo=None, ours_eval="auto"):
    nn = load_nn(weights, accumulator=True) if ours_eval in ("auto", "nn") else None
    ours = InProcessPlayer(nn.name if nn else "material+pst", Searcher(nn or MaterialEvaluator()), movetime)
    if kind == "pst":
        if nn is None:
            print("match vs pst needs a trained network (run train.py)")
            return
        opp = InProcessPlayer("material+pst", Searcher(MaterialEvaluator()), movetime)
    else:
        path = stockfish or shutil.which("stockfish")
        if not path:
            print("Stockfish not found. Download it from https://stockfishchess.org/download/ and pass "
                  "--stockfish <path to the binary>, or put it on your PATH as 'stockfish'.")
            return
        opp = StockfishPlayer(path, movetime, skill=sf_skill, elo=sf_elo)
    print(f"\nmatch: {ours.name}  vs  {opp.name}, {games} games, {movetime:.2f} s/move")
    w = d = l = 0
    try:
        for g in range(games):
            opening = OPENINGS[(g // 2) % len(OPENINGS)]
            ours_white = g % 2 == 0
            white, black = (ours, opp) if ours_white else (opp, ours)
            result, board = play_game(white, black, opening)
            score = {"1-0": 1.0, "0-1": 0.0}.get(result, 0.5)
            score = score if ours_white else 1 - score
            w, d, l = w + (score == 1), d + (score == 0.5), l + (score == 0)
            print(f"  game {g + 1:3d}: {white.name} - {black.name}  {result}  ({len(board.move_stack)} plies)"
                  f"   running +{w} ={d} -{l}", flush=True)
    finally:
        opp.close()
    s, e, lo, hi, los = elo_report(w, d, l)
    print(f"\nresult for {ours.name}: +{w} ={d} -{l}, score {s:.1%}")
    if s in (0.0, 1.0):
        print("a 0 % or 100 % score has no finite Elo estimate: play more games, or pick a closer opponent")
        return
    # An interval end at a 0 % or 100 % score is unbounded (elo() clamps it to +-1200).
    lo_txt = f"{lo:+.0f}" if lo > -1199 else "no lower bound"
    hi_txt = f"{hi:+.0f}" if hi < 1199 else "no upper bound"
    print(f"Elo difference {e:+.0f} (95% interval {lo_txt} to {hi_txt}), likelihood of superiority {los:.0%}")
    if kind == "stockfish" and sf_elo is not None:
        lo_r = f"{sf_elo + lo:.0f}" if lo > -1199 else "?"
        hi_r = f"{sf_elo + hi:.0f}" if hi < 1199 else "?"
        print(f"rough rating on Stockfish's CCRL-anchored scale: {sf_elo + e:.0f} ({lo_r} to {hi_r}); "
              "not a FIDE or Lichess rating")
    elif kind == "stockfish":
        print("Skill Level is not calibrated in Elo, so this is a difference to that opponent only; "
              "use --sf-elo 1320 for an anchored estimate")


def main():
    p = argparse.ArgumentParser(description="Benchmarks and matches for the chess engine")
    p.add_argument("--smoke", action="store_true", help="quick version of every check")
    p.add_argument("--perft", action="store_true")
    p.add_argument("--perft-depth", type=int, default=3)
    p.add_argument("--speed", action="store_true")
    p.add_argument("--depth", type=int, default=4)
    p.add_argument("--accumulator", action="store_true", help="check the incremental accumulator")
    p.add_argument("--uci-check", action="store_true")
    p.add_argument("--match", choices=["pst", "stockfish"])
    p.add_argument("--games", type=int, default=20)
    p.add_argument("--movetime", type=int, default=200, help="ms per move in matches")
    p.add_argument("--weights", default=None, help="NumPy weights (default checkpoints/evaluator.npz)")
    p.add_argument("--eval", choices=["auto", "nn", "material"], default="auto", help="our side in a Stockfish match")
    p.add_argument("--stockfish", default=None, help="path to the stockfish binary")
    p.add_argument("--sf-skill", type=int, default=0, help="Stockfish Skill Level 0-20")
    p.add_argument("--sf-elo", type=int, default=None, help="Stockfish UCI_Elo (1320-3190); overrides --sf-skill")
    a = p.parse_args()

    if not any([a.smoke, a.perft, a.speed, a.accumulator, a.uci_check, a.match]):
        a.perft = a.speed = True
    ok = True
    if a.smoke:
        weights = a.weights
        if weights is None and load_nn() is None and (HERE / "checkpoints" / "smoke.npz").exists():
            weights = str(HERE / "checkpoints" / "smoke.npz")
        ok &= run_perft(3)
        run_speed(3, weights)
        ok &= run_accumulator_check(weights)
        ok &= run_uci_check()
        if shutil.which("stockfish") or a.stockfish:
            run_match("stockfish", 2, 0.1, weights, a.stockfish, a.sf_skill, a.sf_elo, a.eval)
        print(f"\nsmoke {'passed' if ok else 'FAILED'}")
        sys.exit(0 if ok else 1)
    if a.perft:
        ok &= run_perft(a.perft_depth)
    if a.speed:
        run_speed(a.depth, a.weights)
    if a.accumulator:
        ok &= run_accumulator_check(a.weights)
    if a.uci_check:
        ok &= run_uci_check()
    if a.match:
        run_match(a.match, a.games, a.movetime / 1000, a.weights, a.stockfish, a.sf_skill, a.sf_elo, a.eval)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
