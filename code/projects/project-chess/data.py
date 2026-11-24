"""Training data for the neural evaluator: positions + Stockfish scores from Lichess.

    python data.py --smoke                    # bundled CC0 sample (4,000 records, ~2,200 kept) -> data/smoke.npz (seconds, offline)
    python data.py --positions 1000000        # stream the Lichess evaluation database -> data/train.npz
    python data.py --make-sample              # (re)build the bundled sample from the live database

Source: the Lichess evaluation export, lichess_db_eval.jsonl.zst, released under
CC0 (public domain): https://database.lichess.org/  The file is about 22 GB
compressed, so we never download it. We stream it over HTTPS, decompress on
the fly with python-zstandard and stop after the positions we need.

Each line of the export is one JSON object:
    {"fen": "<pieces> <side> <castling> <ep>",
     "evals": [{"pvs": [{"cp": 31, "line": "e2e4 ..."}], "knodes": 1234, "depth": 36}, ...]}
`cp` is from WHITE's point of view; `mate` replaces `cp` when a mate is found.
Lichess's advice: take the evaluation with the highest depth and its first PV.

What we keep (see the "dataset" lesson for why):
  * no mate scores, no illegal positions, no positions where the side to move is in check,
  * no positions whose best move is a capture or a promotion (not "quiet"),
  * the score converted to the SIDE TO MOVE's point of view and clipped to +-2000.

Each position becomes at most 32 active features out of 768 (2 colours x 6
piece types x 64 squares), seen from the side to move's chair. We store the
indices as int16 (padded with 768 = "no feature") plus an int16 score: about
66 bytes per position, so 1 million positions is about 66 MB.
"""
import argparse
import csv
import io
import json
import sys
import time
import urllib.request
from pathlib import Path

import chess
import numpy as np

HERE = Path(__file__).parent
URL = "https://database.lichess.org/lichess_db_eval.jsonl.zst"
SAMPLE = HERE / "sample" / "lichess_eval_sample.csv"   # committed, CC0, 4,000 raw records
DATA = HERE / "data"                                     # git-ignored output folder
N_FEATURES = 768
PAD = N_FEATURES      # index used to pad rows to 32 entries; the network ignores it
MAX_ACTIVE = 32
CP_CLIP = 2000


# --------------------------------------------------------------------- features
def feature_index(perspective: bool, color: bool, piece_type: int, square: int) -> int:
    """Index of 'piece of `color` and `piece_type` on `square`' seen by `perspective`.

    0-383 are the perspective's OWN pieces, 384-767 the opponent's. Black sees the
    board flipped vertically (square_mirror), so "my pawn one step from promoting"
    is the same input for both colours.
    """
    if perspective == chess.BLACK:
        square = chess.square_mirror(square)
    own = color == perspective
    return (0 if own else 384) + (piece_type - 1) * 64 + square


def features(board: chess.Board) -> list[int]:
    """The 768-dim one-hot input as a list of active indices, from the side to move's view."""
    stm = board.turn
    return [feature_index(stm, pc.color, pc.piece_type, sq) for sq, pc in board.piece_map().items()]


def encode(board: chess.Board) -> np.ndarray:
    """Fixed-size int16 row: the active indices, then PAD up to 32 entries."""
    row = np.full(MAX_ACTIVE, PAD, dtype=np.int16)
    idx = features(board)
    row[: len(idx)] = idx
    return row


# ------------------------------------------------------------------ the records
def best_eval(rec: dict):
    """(cp_white, mate, best_move_uci, depth) from one export line: deepest eval, first PV."""
    best = max(rec["evals"], key=lambda e: e["depth"])
    pv = best["pvs"][0]
    first = pv.get("line", "").split()[:1]
    return pv.get("cp"), pv.get("mate"), (first[0] if first else ""), best["depth"]


def to_example(fen: str, cp_white, mate, best_uci: str):
    """Apply the filters; return (encoded features, cp for the side to move) or None."""
    if mate is not None or cp_white is None:
        return None                                   # mates are search's job, not the net's
    try:
        board = chess.Board(fen)                      # the export's FENs have no move counters; that's fine
    except ValueError:
        return None
    if not board.is_valid() or board.is_check():      # a few user-made positions are illegal (e.g. 35 pieces)
        return None
    if best_uci:
        try:
            move = chess.Move.from_uci(best_uci)
        except ValueError:
            return None
        if move.promotion or board.is_capture(move):
            return None                               # not quiet: the score depends on a tactic
    cp = int(cp_white) if board.turn == chess.WHITE else -int(cp_white)
    return encode(board), max(-CP_CLIP, min(CP_CLIP, cp))


def stream_lichess(limit: int):
    """Yield (fen, cp_white, mate, best_uci, depth) records straight from the live export."""
    import zstandard  # pip install zstandard

    req = urllib.request.Request(URL, headers={"User-Agent": "ai-knowledge-course-chess/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        reader = zstandard.ZstdDecompressor().stream_reader(resp)
        for i, line in enumerate(io.TextIOWrapper(reader, encoding="utf-8")):
            if i >= limit:
                break
            rec = json.loads(line)
            cp, mate, best, depth = best_eval(rec)
            yield rec["fen"], cp, mate, best, depth


def read_sample():
    """Yield the same records from the bundled CSV sample (works offline)."""
    with open(SAMPLE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cp = int(row["cp"]) if row["cp"] else None
            mate = int(row["mate"]) if row["mate"] else None
            yield row["fen"], cp, mate, row["best"], int(row["depth"])


def build(records, max_examples: int | None = None):
    """Filter + encode a stream of records into arrays (idx: N x 32 int16, cp: N int16)."""
    rows, cps = [], []
    seen = kept = 0
    t0 = time.time()
    for fen, cp, mate, best, _depth in records:
        seen += 1
        ex = to_example(fen, cp, mate, best)
        if ex is not None:
            rows.append(ex[0])
            cps.append(ex[1])
            kept += 1
            if max_examples and kept >= max_examples:
                break
        if seen % 100_000 == 0:
            print(f"  {seen:,} read, {kept:,} kept ({time.time() - t0:.0f}s)", flush=True)
    if not rows:
        raise SystemExit("no positions survived the filters")
    print(f"read {seen:,} positions, kept {kept:,} quiet ones ({kept / seen:.0%})")
    return np.stack(rows), np.array(cps, dtype=np.int16)


def save(path: Path, idx: np.ndarray, cp: np.ndarray):
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, idx=idx, cp=cp)
    print(f"saved {len(cp):,} positions to {path} ({path.stat().st_size / 1e6:.1f} MB)")


def load(path: Path):
    d = np.load(path)
    return d["idx"], d["cp"]


def smoke_arrays():
    """The bundled sample as arrays, built in memory (used by train.py --smoke)."""
    return build(read_sample())


def make_sample(n: int = 4000):
    """Write the first n raw records of the live export to sample/ (kept small on purpose)."""
    SAMPLE.parent.mkdir(exist_ok=True)
    with open(SAMPLE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["fen", "cp", "mate", "best", "depth"])
        for fen, cp, mate, best, depth in stream_lichess(n):
            w.writerow([fen, "" if cp is None else cp, "" if mate is None else mate, best, depth])
    print(f"wrote {n} records to {SAMPLE}")


def self_check():
    """Catch the classic sign bug before it reaches training."""
    start = chess.Board()
    after = chess.Board()
    after.push_san("e4")
    mirrored = after.mirror()                    # same position with colours swapped
    assert sorted(features(after)) == sorted(features(mirrored)), "mirrored positions must look identical to the net"
    assert len(features(start)) == 32 and max(features(start)) < N_FEATURES
    # Lichess cp is White-relative: +40 for White becomes -40 when Black is to move.
    _, cp = to_example(after.fen(), 40, None, "e7e5")
    assert cp == -40, "side-to-move conversion is broken"


def main():
    p = argparse.ArgumentParser(description="Build the training set for the chess evaluator")
    p.add_argument("--smoke", action="store_true", help="use the bundled 4,000-record sample (offline, seconds)")
    p.add_argument("--positions", type=int, default=1_000_000, help="how many quiet positions to keep")
    p.add_argument("--read-limit", type=int, default=None, help="stop after reading this many records (default 3x --positions)")
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--make-sample", action="store_true", help="refresh sample/lichess_eval_sample.csv from the live export")
    a = p.parse_args()

    self_check()
    if a.make_sample:
        make_sample()
        return
    if a.smoke:
        idx, cp = smoke_arrays()
        out = a.out or DATA / "smoke.npz"
    else:
        print(f"streaming {URL}\n(only the first part of the 22 GB file is downloaded; Ctrl+C is safe)")
        limit = a.read_limit or 3 * a.positions
        try:
            idx, cp = build(stream_lichess(limit), a.positions)
        except OSError as e:
            sys.exit(f"download failed ({e}). Check your connection, or use --smoke to work offline.")
        out = a.out or DATA / "train.npz"
    save(out, idx, cp)
    print(f"score range {cp.min()} .. {cp.max()} cp, mean |cp| {np.abs(cp).mean():.0f}, "
          f"active features per position {np.mean((idx != PAD).sum(1)):.1f}")


if __name__ == "__main__":
    main()
