"""A learning-rate range test and a small random search, on synthetic data.

Companion code for the lesson "Hyperparameters and how to tune them".
Run:  python code/core/intermediate/lr_range_test.py
Needs PyTorch (CPU is fine). Takes well under a minute.
"""
import math
import random

import torch
from torch import nn

torch.manual_seed(0)
random.seed(0)

# Synthetic data: 3 interleaved spirals, 2-D points, 3 classes (not linearly separable).
def spirals(n_per_class=400, noise=0.5):
    xs, ys = [], []
    for c in range(3):
        t = torch.linspace(0.0, 1.0, n_per_class)
        angle = t * 6.0 + c * 2 * math.pi / 3 + noise * torch.randn(n_per_class)
        xs.append(torch.stack([t * torch.cos(angle), t * torch.sin(angle)], dim=1))
        ys.append(torch.full((n_per_class,), c))
    X, y = torch.cat(xs), torch.cat(ys)
    order = torch.randperm(len(X))
    return X[order], y[order]


X, y = spirals()
X_train, y_train, X_val, y_val = X[:960], y[:960], X[960:], y[960:]   # 80/20 split


def make_model():
    return nn.Sequential(nn.Linear(2, 64), nn.ReLU(), nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 3))


def batches(batch_size=32):
    while True:
        idx = torch.randperm(len(X_train))
        for i in range(0, len(idx) - batch_size + 1, batch_size):
            j = idx[i:i + batch_size]
            yield X_train[j], y_train[j]


# 1. LR range test (Smith 2015): raise the learning rate exponentially, one batch per value,
#    and watch the loss. Stop once it has blown up to 4x the best loss seen so far.
def lr_range_test(lr_min=1e-4, lr_max=10.0, steps=100):
    model, loss_fn = make_model(), nn.CrossEntropyLoss()
    opt = torch.optim.SGD(model.parameters(), lr=lr_min, momentum=0.9)
    factor = (lr_max / lr_min) ** (1 / (steps - 1))
    smooth, best, history, data = None, float("inf"), [], batches()
    for i in range(steps):
        lr = lr_min * factor ** i
        for g in opt.param_groups:
            g["lr"] = lr
        xb, yb = next(data)
        loss = loss_fn(model(xb), yb)
        opt.zero_grad()
        loss.backward()
        opt.step()
        smooth = loss.item() if smooth is None else 0.9 * smooth + 0.1 * loss.item()  # smoothed loss
        history.append((lr, smooth))
        best = min(best, smooth)
        if smooth > 4 * best:
            break
    return history


history = lr_range_test()
print("LR range test (smoothed training loss):")
for lr, loss in history[::10]:
    print(f"  lr = {lr:9.5f}   loss = {loss:.3f}")
lr_at_min = min(history, key=lambda h: h[1])[0]
print(f"lowest loss at lr = {lr_at_min:.3f}; stopped at lr = {history[-1][0]:.3f}")
print(f"suggested starting lr (about 10x below the minimum): {lr_at_min / 10:.4f}")


# 2. Random search: sample learning rate and weight decay on a log scale, train briefly,
#    and keep the trial with the best *validation* accuracy.
def train_and_validate(lr, weight_decay, steps=300):
    torch.manual_seed(1)                        # same init and batches for every trial: a fair comparison
    model, loss_fn = make_model(), nn.CrossEntropyLoss()
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    data = batches()
    for _ in range(steps):
        xb, yb = next(data)
        loss = loss_fn(model(xb), yb)
        opt.zero_grad()
        loss.backward()
        opt.step()
    model.eval()
    with torch.no_grad():
        return (model(X_val).argmax(dim=1) == y_val).float().mean().item()


print("\nRandom search (8 trials, log-uniform samples):")
trials = []
for _ in range(8):
    lr = 10 ** random.uniform(-4, -1)           # between 1e-4 and 1e-1
    wd = 10 ** random.uniform(-5, -1)           # between 1e-5 and 1e-1
    acc = train_and_validate(lr, wd)
    trials.append((acc, lr, wd))
    print(f"  lr = {lr:.5f}   weight_decay = {wd:.5f}   val accuracy = {acc:.3f}")
acc, lr, wd = max(trials)
print(f"best: lr = {lr:.5f}, weight_decay = {wd:.5f}, val accuracy = {acc:.3f}")
