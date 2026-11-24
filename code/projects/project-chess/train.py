"""Train the 768 -> 256 -> 32 -> 1 evaluator on a CPU.

    python train.py --smoke                    # bundled 2,255-position sample, ~15 s: checks the whole pipeline
    python train.py                            # data/train.npz from `python data.py` (20-60 min for 1-2 M positions)
    python train.py --epochs 30 --power 2.6    # the NNUE docs' loss exponent, as an experiment

Writes checkpoints/evaluator.pt (PyTorch) and checkpoints/evaluator.npz (NumPy
weights that eval_nn.py, uci.py and play.py load). With --smoke the files are
called smoke.pt / smoke.npz so a smoke run never overwrites a real network.

What to expect: the validation loss should fall for the first epochs and then
flatten (or rise again: overfitting). The weights from the epoch with the lowest
validation loss are the ones saved. The smoke net learns from only ~2,000 positions, so it is weak and
noisy: it only proves that everything runs. A useful net needs at least a few
hundred thousand positions (see the "Training the evaluator" lesson).
"""
import argparse
import time
from pathlib import Path

import chess
import numpy as np
import torch

import data
from model import SCALE, Evaluator, count_parameters, export_numpy, wdl_loss

HERE = Path(__file__).parent
CKPT = HERE / "checkpoints"

# Positions the trained net is asked about after training (FEN, what a sensible net says).
SANITY = [
    (chess.STARTING_FEN, "about 0 to +50 cp (White moves first)"),
    ("rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "clearly positive, several hundred cp (White is a queen up)"),
    ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNB1KBNR w KQkq - 0 1", "clearly negative, several hundred cp (White is a queen down)"),
]


def get_args():
    p = argparse.ArgumentParser(description="Train the chess evaluator")
    p.add_argument("--smoke", action="store_true", help="tiny bundled sample, a few epochs: checks the pipeline")
    p.add_argument("--data", type=Path, default=data.DATA / "train.npz")
    p.add_argument("--epochs", type=int, default=20)
    p.add_argument("--batch-size", type=int, default=1024)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--power", type=float, default=2.0, help="loss exponent: 2 = MSE in win-probability space")
    p.add_argument("--val-fraction", type=float, default=0.05)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--threads", type=int, default=None, help="CPU threads for PyTorch (default: all)")
    return p.parse_args()


def evaluate_loss(model, idx, cp, power, batch_size=8192):
    model.eval()
    total = 0.0
    with torch.no_grad():
        for i in range(0, len(cp), batch_size):
            pred = model(idx[i:i + batch_size])
            total += wdl_loss(pred, cp[i:i + batch_size], power).item() * len(pred)
    model.train()
    return total / len(cp)


def predict_cp(model, board: chess.Board) -> float:
    model.eval()
    with torch.no_grad():
        x = torch.from_numpy(data.encode(board).astype(np.int64)).unsqueeze(0)
        return model(x).item() * SCALE


def main():
    a = get_args()
    torch.manual_seed(a.seed)
    if a.threads:
        torch.set_num_threads(a.threads)
    if a.smoke:
        a.epochs = min(a.epochs, 15)
        a.batch_size = 128
        idx_np, cp_np = data.smoke_arrays()
        name = "smoke"
    else:
        if not a.data.exists():
            raise SystemExit(f"{a.data} not found: run `python data.py` first (or use --smoke)")
        idx_np, cp_np = data.load(a.data)
        name = "evaluator"

    # Shuffle once, then hold out a validation slice the model never trains on.
    rng = np.random.default_rng(a.seed)
    order = rng.permutation(len(cp_np))
    idx = torch.from_numpy(idx_np[order].astype(np.int64))
    cp = torch.from_numpy(cp_np[order].astype(np.float32))
    n_val = max(1, int(len(cp) * a.val_fraction))
    idx_val, cp_val, idx_tr, cp_tr = idx[:n_val], cp[:n_val], idx[n_val:], cp[n_val:]

    model = Evaluator()
    opt = torch.optim.Adam(model.parameters(), lr=a.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=a.epochs)
    print(f"{len(cp_tr):,} training / {n_val:,} validation positions, "
          f"{count_parameters(model):,} parameters, {a.epochs} epochs")
    baseline = wdl_loss(torch.zeros(n_val), cp_val, a.power).item()
    print(f"baseline (always predict 'equal'): val loss {baseline:.5f}")

    t0 = time.time()
    best_val, best_state, best_epoch = float("inf"), None, 0
    for epoch in range(1, a.epochs + 1):
        perm = torch.randperm(len(cp_tr))
        running = 0.0
        for i in range(0, len(cp_tr), a.batch_size):
            b = perm[i:i + a.batch_size]
            loss = wdl_loss(model(idx_tr[b]), cp_tr[b], a.power)
            opt.zero_grad()
            loss.backward()
            opt.step()
            running += loss.item() * len(b)
        sched.step()
        val = evaluate_loss(model, idx_val, cp_val, a.power)
        mark = ""
        if val < best_val:   # keep the weights with the best validation loss (early stopping by hand)
            best_val, best_epoch, mark = val, epoch, "  *"
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        print(f"epoch {epoch:3d}  train {running / len(cp_tr):.5f}  val {val:.5f}  ({time.time() - t0:.0f}s){mark}", flush=True)

    model.load_state_dict(best_state)
    print(f"keeping the epoch-{best_epoch} weights (best validation loss {best_val:.5f}, baseline {baseline:.5f})")

    CKPT.mkdir(exist_ok=True)
    torch.save(model.state_dict(), CKPT / f"{name}.pt")
    export_numpy(model, CKPT / f"{name}.npz")
    print(f"saved {CKPT / (name + '.pt')} and {CKPT / (name + '.npz')}")

    print("\nsanity checks (centipawns for the side to move):")
    for fen, expect in SANITY:
        print(f"  {predict_cp(model, chess.Board(fen)):+8.0f}   expected {expect}")
    # By construction the net sees mirrored positions identically, so their scores match exactly.
    b = chess.Board()
    b.push_san("e4")
    assert abs(predict_cp(model, b) - predict_cp(model, b.mirror())) < 1e-3, "mirror symmetry broken"
    print("  mirror check passed: a position and its colour-flipped copy get the same score")
    if a.smoke:
        print("\n(smoke net: trained on ~2,000 positions, so expect rough numbers. Run data.py + train.py for a real net.)")


if __name__ == "__main__":
    main()
