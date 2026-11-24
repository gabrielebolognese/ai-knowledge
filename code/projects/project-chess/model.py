"""The neural evaluator: a 768 -> 256 -> 32 -> 1 multilayer perceptron.

    python model.py          # prints the layer sizes and the parameter count (205,121)

Input: the 768 one-hot piece-square features of data.py (at most 32 are 1).
Output: one number in "cp / 400" units. sigmoid(output) is the predicted
expected score (0 = loss, 0.5 = equal, 1 = win) for the side to move, and
output * 400 is the evaluation in centipawns that search.py uses.

This is the simple "A" feature set from Stockfish's NNUE documentation
(https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue.html),
with Stockfish-style ClippedReLU activations (clamp to 0..1).

Parameters: 768*256 + 256 (first layer) + 256*32 + 32 (second) + 32*1 + 1 (output) = 205,121.

------------------------------------------------------------------------------
Why the first layer is cheap, and the NNUE accumulator idea
------------------------------------------------------------------------------
The input x is 0/1 with at most 32 ones, so the first layer's product W1 @ x is
just the SUM OF THE COLUMNS of W1 for the active features. nn.EmbeddingBag with
mode="sum" computes exactly that, without ever building a 768-wide vector.

A move changes only 2-4 features: a quiet move turns one off and one on, a
capture also removes the victim, castling moves two pieces. So instead of
re-adding ~25 columns at every node you can keep the first-layer result
("the accumulator") and update it:

    a_after = a_before - W1[:, (my knight, g1)] + W1[:, (my knight, f3)]

Undoing the move restores the saved vector. This incrementally updated first
layer is the "Efficiently Updatable" in NNUE (Nasu, 2018), and it is how
Stockfish evaluates millions of positions per second on a CPU.

One subtlety. Our net sees the board from the side to move's chair, and after
every move the side to move changes, so every feature index changes. The fix is
to keep TWO accumulators, one built from White's point of view and one from
Black's, update both on every move, and feed the network the one that belongs
to the side to move. That is exactly why real NNUE networks keep two
"perspectives". eval_nn.py implements this (NNEvaluator(..., accumulator=True))
and bench.py checks that it gives the same numbers as a full recomputation.
------------------------------------------------------------------------------
"""
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from data import N_FEATURES, PAD

SCALE = 400.0  # centipawns <-> win-probability space; the NNUE docs use values around 400


class Evaluator(nn.Module):
    def __init__(self, n_features: int = N_FEATURES, h1: int = 256, h2: int = 32):
        super().__init__()
        # Sparse first layer: row i of this table is column i of W1. Index PAD (768)
        # is the "no feature" filler that data.py uses; padding_idx keeps it at zero.
        self.ft = nn.EmbeddingBag(n_features + 1, h1, mode="sum", padding_idx=PAD)
        self.ft_bias = nn.Parameter(torch.zeros(h1))
        self.l2 = nn.Linear(h1, h2)
        self.out = nn.Linear(h2, 1)
        with torch.no_grad():                       # small first-layer weights: ~25 of them get summed
            self.ft.weight.normal_(0.0, 0.05)
            self.ft.weight[PAD].zero_()

    def forward(self, idx: torch.Tensor) -> torch.Tensor:
        """idx: (batch, 32) int64 feature indices padded with PAD. Returns (batch,) in cp/SCALE units."""
        a = self.ft(idx) + self.ft_bias            # the accumulator: sum of active columns + bias
        h1 = torch.clamp(a, 0.0, 1.0)              # ClippedReLU
        h2 = torch.clamp(self.l2(h1), 0.0, 1.0)    # ClippedReLU
        return self.out(h2).squeeze(-1)


def wdl_loss(pred: torch.Tensor, cp: torch.Tensor, power: float = 2.0) -> torch.Tensor:
    """Compare prediction and target in win-probability space: |sigmoid(pred) - sigmoid(cp/400)|^power.

    sigmoid squashes +1500 and +3000 cp to almost the same 0.98, so the net does not
    waste effort on the exact size of an already-won advantage. power=2 is mean
    squared error; the NNUE docs report good results with 2.6.
    """
    target = torch.sigmoid(cp / SCALE)
    return (torch.sigmoid(pred) - target).abs().pow(power).mean()


def count_parameters(model: nn.Module) -> int:
    # The PAD row is a constant zero, not a real parameter, so leave it out.
    return sum(p.numel() for p in model.parameters()) - model.ft.weight.shape[1]


def export_numpy(model: Evaluator, path: Path):
    """Save plain NumPy weights for fast inference inside search (eval_nn.py)."""
    sd = {k: v.detach().cpu().numpy().astype(np.float32) for k, v in model.state_dict().items()}
    np.savez(
        path,
        W1=sd["ft.weight"][:N_FEATURES],   # (768, 256): row i = contribution of feature i
        b1=sd["ft_bias"],                  # (256,)
        W2=sd["l2.weight"].T.copy(),       # (256, 32)
        b2=sd["l2.bias"],                  # (32,)
        W3=sd["out.weight"].T.copy(),      # (32, 1)
        b3=sd["out.bias"],                 # (1,)
        scale=np.float32(SCALE),
    )


if __name__ == "__main__":
    m = Evaluator()
    print(m)
    print(f"trainable parameters: {count_parameters(m):,} (expected 205,121)")
