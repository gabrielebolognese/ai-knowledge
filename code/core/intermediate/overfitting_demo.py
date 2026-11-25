"""Underfitting, overfitting, and what weight decay and dropout do about it.

Companion code for the lesson "Overfitting and regularization" (intermediate track).
Run:  python code/core/intermediate/overfitting_demo.py      (about 15-30 seconds on a laptop CPU)
Needs NumPy, torch and torchvision (MNIST is downloaded into data/ next to this file the first time).
"""
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torchvision import datasets

HERE = Path(__file__).parent
rng = np.random.default_rng(0)

# 1. Polynomials of growing degree on 15 noisy points of a sine curve.
x_tr, x_va = rng.uniform(0, 1, 15), rng.uniform(0, 1, 200)
y_tr = np.sin(2 * np.pi * x_tr) + rng.normal(0, 0.2, 15)
y_va = np.sin(2 * np.pi * x_va) + rng.normal(0, 0.2, 200)
print("polynomial fit   train MSE   val MSE")
for degree in [1, 3, 12]:
    c = np.polyfit(x_tr, y_tr, degree)
    tr, va = np.mean((np.polyval(c, x_tr) - y_tr) ** 2), np.mean((np.polyval(c, x_va) - y_va) ** 2)
    print(f"  degree {degree:2d}       {tr:7.3f}   {va:7.3f}")

# 2. A big MLP on only 1,000 MNIST training images: it can memorize them.
mnist = datasets.MNIST(HERE / "data", train=True, download=True)
X = ((mnist.data.float() / 255 - 0.1307) / 0.3081).flatten(1)       # (60000, 784), standardized
Y = mnist.targets
idx = torch.randperm(60_000, generator=torch.Generator().manual_seed(0))
X_tr, Y_tr = X[idx[:1000]], Y[idx[:1000]]                           # small training set
X_va, Y_va = X[idx[50_000:55_000]], Y[idx[50_000:55_000]]           # 5,000 held-out images


def scores(model):
    model.eval()                                 # dropout off
    with torch.no_grad():
        out_tr, out_va = model(X_tr), model(X_va)
        return ((out_tr.argmax(1) == Y_tr).float().mean().item(),
                (out_va.argmax(1) == Y_va).float().mean().item(),
                nn.functional.cross_entropy(out_va, Y_va).item())


def train(weight_decay=0.0, p=0.0, epochs=40, report=()):
    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(784, 512), nn.ReLU(), nn.Dropout(p),
                          nn.Linear(512, 512), nn.ReLU(), nn.Dropout(p),
                          nn.Linear(512, 10))
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=weight_decay)
    for epoch in range(1, epochs + 1):
        model.train()                            # dropout on
        perm = torch.randperm(1000)
        for i in range(0, 1000, 100):            # mini-batches of 100
            b = perm[i:i + 100]
            loss = nn.functional.cross_entropy(model(X_tr[b]), Y_tr[b])
            opt.zero_grad()
            loss.backward()
            opt.step()
        if epoch in report:
            tr_acc, va_acc, va_loss = scores(model)
            print(f"  epoch {epoch:2d}: train acc {tr_acc:.3f} | val acc {va_acc:.3f} | val loss {va_loss:.3f}")
    return scores(model)


print("\nno regularization, watching the validation loss:")
train(epochs=40, report=(2, 5, 10, 20, 40))

print("\nafter 40 epochs        train acc   val acc   val loss")
for name, kw in [("no regularization", {}),
                 ("dropout p = 0.5", {"p": 0.5}),
                 ("weight decay 1.0", {"weight_decay": 1.0})]:
    tr_acc, va_acc, va_loss = train(**kw)
    print(f"  {name:20s} {tr_acc:7.3f}   {va_acc:7.3f}   {va_loss:7.3f}")
