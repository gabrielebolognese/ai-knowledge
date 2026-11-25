"""Gradient descent, momentum and Adam by hand, checked against torch.optim.

Companion code for the lesson "Optimizers: SGD, momentum, RMSProp and Adam".
Run:  python code/core/intermediate/optimizers_compare.py
Needs PyTorch (CPU is fine). Every optimizer minimises f(w) = (w - 3)^2 from w = 0.
"""
import math

import torch


def grad(w):
    return 2.0 * (w - 3.0)                      # f'(w) for f(w) = (w - 3)^2


def plain_gd(lr=0.1, steps=3):
    w, path = 0.0, []
    for _ in range(steps):
        w = w - lr * grad(w)                    # w <- w - lr * g
        path.append(w)
    return path


def momentum(lr=0.1, beta=0.9, steps=3):
    w, v, path = 0.0, 0.0, []
    for _ in range(steps):
        v = beta * v + grad(w)                  # velocity: running sum of gradients
        w = w - lr * v                          # step along the velocity
        path.append(w)
    return path


def adam(lr=0.1, b1=0.9, b2=0.999, eps=1e-8, steps=3):
    w, m, v, path = 0.0, 0.0, 0.0, []
    for t in range(1, steps + 1):
        g = grad(w)
        m = b1 * m + (1 - b1) * g               # first moment: average gradient
        v = b2 * v + (1 - b2) * g * g           # second moment: average squared gradient
        m_hat = m / (1 - b1 ** t)               # bias correction (m and v start at 0)
        v_hat = v / (1 - b2 ** t)
        w = w - lr * m_hat / (math.sqrt(v_hat) + eps)
        path.append(w)
    return path


def with_torch(make_opt, steps=3):
    w = torch.zeros(1, requires_grad=True)
    opt = make_opt([w])
    path = []
    for _ in range(steps):
        loss = ((w - 3.0) ** 2).sum()
        opt.zero_grad()
        loss.backward()
        opt.step()
        path.append(w.item())
    return path


def show(name, mine, theirs):
    fmt = lambda p: ", ".join(f"{x:.4f}" for x in p)
    same = all(abs(a - b) < 1e-5 for a, b in zip(mine, theirs))
    print(f"{name:<9} by hand: {fmt(mine)}   torch.optim: {fmt(theirs)}   match: {same}")


show("SGD", plain_gd(), with_torch(lambda p: torch.optim.SGD(p, lr=0.1)))
show("momentum", momentum(), with_torch(lambda p: torch.optim.SGD(p, lr=0.1, momentum=0.9)))
show("Adam", adam(), with_torch(lambda p: torch.optim.Adam(p, lr=0.1)))

# Distance to the minimum after 50 steps: how far each one still has to go.
for name, path in [("SGD", plain_gd(steps=50)), ("momentum", momentum(steps=50)), ("Adam", adam(steps=50))]:
    print(f"{name:<9} after 50 steps: w = {path[-1]:.4f}")
