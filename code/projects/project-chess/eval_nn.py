"""The trained network as an evaluator for search, in plain NumPy.

    python eval_nn.py                              # evaluates a few positions with checkpoints/evaluator.npz
    python eval_nn.py --weights checkpoints/smoke.npz

Why NumPy and not PyTorch? A search calls evaluate() thousands of times per
second, one position at a time. Each PyTorch call carries tens of microseconds
of overhead, which is more than the arithmetic of this tiny network. NumPy on
the exported weights (model.export_numpy) is faster for single positions and
does not need PyTorch installed at all.

Three speed tricks, each optional:
  1. Cache: qsearch evaluates the same positions again and again, so results are
     kept in a dict keyed by the Zobrist hash the search already computed.
  2. Accumulator (accumulator=True): the first layer is updated move by move
     instead of recomputed (the NNUE idea, explained in model.py). search.py calls
     push()/pop() around every move when `incremental` is True.
  3. Batching (evaluate_batch): many positions in one matrix product. Alpha-beta
     needs one leaf at a time, so this helps offline jobs (labelling, testing,
     bench.py), not the search itself.
"""
import argparse
from pathlib import Path

import chess
import numpy as np

from data import PAD, feature_index, features

HERE = Path(__file__).parent
DEFAULT_WEIGHTS = HERE / "checkpoints" / "evaluator.npz"
CP_LIMIT = 10_000  # keep network scores far away from mate scores (search.MATE = 100,000)


def find_weights(path=None) -> Path | None:
    """The weights to use: an explicit path, else evaluator.npz, else None."""
    if path:
        return Path(path)
    return DEFAULT_WEIGHTS if DEFAULT_WEIGHTS.exists() else None


class NNEvaluator:
    uses_key = True     # search.py passes Zobrist keys so the cache works in qsearch too

    def __init__(self, weights=DEFAULT_WEIGHTS, accumulator: bool = False, cache_size: int = 500_000):
        w = np.load(weights)
        self.W1 = np.vstack([w["W1"], np.zeros((1, w["W1"].shape[1]), np.float32)])  # extra zero row = PAD
        self.b1, self.W2, self.b2 = w["b1"], w["W2"], w["b2"]
        self.W3, self.b3 = w["W3"][:, 0], float(w["b3"][0])
        self.scale = float(w["scale"])
        self.name = f"nn ({Path(weights).name}{', accumulator' if accumulator else ''})"
        self.incremental = accumulator
        self.cache: dict[int, int] = {}
        self.cache_size = cache_size
        self.stack: list = []
        self.acc = None

    # ----------------------------------------------------------- the network
    def _head(self, a: np.ndarray) -> int:
        """Everything after the first layer: ClippedReLU, 256 -> 32, ClippedReLU, 32 -> 1."""
        h1 = np.clip(a, 0.0, 1.0)
        h2 = np.clip(h1 @ self.W2 + self.b2, 0.0, 1.0)
        cp = (h2 @ self.W3 + self.b3) * self.scale
        return int(max(-CP_LIMIT, min(CP_LIMIT, cp)))

    def accumulator_for(self, board: chess.Board, perspective: bool) -> np.ndarray:
        """Full refresh: bias + the sum of the ~25 active columns of W1."""
        idx = [feature_index(perspective, pc.color, pc.piece_type, sq) for sq, pc in board.piece_map().items()]
        return self.b1 + self.W1[idx].sum(axis=0)

    def evaluate(self, board: chess.Board, key=None) -> int:
        """Centipawns for the side to move (same contract as eval_material.evaluate)."""
        if key is not None:
            hit = self.cache.get(key)
            if hit is not None:
                return hit
        if self.incremental and self.acc is not None:
            a = self.acc[board.turn]                         # pick the side to move's perspective
        else:
            a = self.b1 + self.W1[features(board)].sum(axis=0)
        cp = self._head(a)
        if key is not None:
            if len(self.cache) >= self.cache_size:
                self.cache.clear()
            self.cache[key] = cp
        return cp

    def evaluate_batch(self, boards) -> np.ndarray:
        """Evaluate many positions at once (side-to-move centipawns)."""
        idx = np.full((len(boards), 32), PAD, dtype=np.int64)
        for i, b in enumerate(boards):
            f = features(b)
            idx[i, : len(f)] = f
        h1 = np.clip(self.W1[idx].sum(axis=1) + self.b1, 0.0, 1.0)
        h2 = np.clip(h1 @ self.W2 + self.b2, 0.0, 1.0)
        return np.clip((h2 @ self.W3 + self.b3) * self.scale, -CP_LIMIT, CP_LIMIT)

    # ------------------------------------------------ incremental accumulator
    def reset(self, board: chess.Board):
        """Rebuild both accumulators from scratch (start of every search)."""
        self.stack.clear()
        self.acc = {chess.WHITE: self.accumulator_for(board, chess.WHITE),
                    chess.BLACK: self.accumulator_for(board, chess.BLACK)}

    @staticmethod
    def changed_features(board: chess.Board, move: chess.Move):
        """(removed, added) pieces as (color, piece_type, square) for `move`, BEFORE it is pushed.

        quiet move: 1 off + 1 on   capture: 2 off + 1 on   castling: 2 off + 2 on
        """
        piece = board.piece_at(move.from_square)
        us, them = piece.color, not piece.color
        removed = [(us, piece.piece_type, move.from_square)]
        added = [(us, move.promotion or piece.piece_type, move.to_square)]
        if board.is_en_passant(move):
            victim_sq = move.to_square - 8 if us == chess.WHITE else move.to_square + 8
            removed.append((them, chess.PAWN, victim_sq))
        elif board.is_castling(move):
            rank = chess.square_rank(move.from_square)
            king_side = chess.square_file(move.to_square) > chess.square_file(move.from_square)
            rook_from = chess.square(7 if king_side else 0, rank)
            rook_to = chess.square(5 if king_side else 3, rank)
            added[0] = (us, chess.KING, chess.square(6 if king_side else 2, rank))
            removed.append((us, chess.ROOK, rook_from))
            added.append((us, chess.ROOK, rook_to))
        else:
            victim = board.piece_at(move.to_square)
            if victim is not None:
                removed.append((them, victim.piece_type, move.to_square))
        return removed, added

    def push(self, board: chess.Board, move: chess.Move):
        """Update both accumulators for `move` (called just before board.push(move))."""
        self.stack.append(self.acc)
        removed, added = self.changed_features(board, move)
        new = {}
        for p in (chess.WHITE, chess.BLACK):
            a = self.acc[p].copy()
            for c, t, sq in removed:
                a -= self.W1[feature_index(p, c, t, sq)]
            for c, t, sq in added:
                a += self.W1[feature_index(p, c, t, sq)]
            new[p] = a
        self.acc = new

    def pop(self):
        """Undo: restore the accumulators saved before the last push."""
        self.acc = self.stack.pop()


def main():
    p = argparse.ArgumentParser(description="Evaluate positions with the trained network")
    p.add_argument("--weights", default=None, help="NumPy weights (default checkpoints/evaluator.npz)")
    p.add_argument("--fen", action="append", help="position(s) to evaluate")
    a = p.parse_args()
    weights = find_weights(a.weights)
    if weights is None or not weights.exists():
        raise SystemExit("no weights found: run `python train.py --smoke` (or the full data.py + train.py)")
    ev = NNEvaluator(weights)
    fens = a.fen or [chess.STARTING_FEN,
                     "rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                     "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNB1KBNR w KQkq - 0 1",
                     "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"]
    boards = [chess.Board(f) for f in fens]
    batch = ev.evaluate_batch(boards)
    for b, cp in zip(boards, batch):
        assert abs(ev.evaluate(b) - cp) <= 1          # single and batched paths agree
        print(f"{ev.evaluate(b):+6d} cp  ({'White' if b.turn else 'Black'} to move)  {b.fen()}")


if __name__ == "__main__":
    main()
