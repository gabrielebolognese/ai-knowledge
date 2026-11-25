"""Five sanity checks that catch most neural-network training bugs.

Companion code for the lesson "Debugging neural network training".
Run:  python code/core/intermediate/debug_checks.py
Needs PyTorch (CPU is fine). Uses random data, so it runs in a few seconds.
"""
import math

import torch
from torch import nn

torch.manual_seed(0)
C = 10                                          # number of classes
X = torch.randn(512, 20)                        # 512 examples with 20 features
y = torch.randint(0, C, (512,))                 # integer class labels (dtype long)


def make_model():
    return nn.Sequential(nn.Linear(20, 64), nn.ReLU(), nn.Linear(64, C))


loss_fn = nn.CrossEntropyLoss()                 # expects raw logits and long labels

# Check 1: the loss before any training should be close to ln(C).
model = make_model()
with torch.no_grad():
    first = loss_fn(model(X), y).item()
print(f"1. initial loss {first:.3f}  (expected about ln({C}) = {math.log(C):.3f})")

# Check 2: a correct model and loop can drive the loss on ONE small batch to almost zero.
xb, yb = X[:16], y[:16]
opt = torch.optim.Adam(model.parameters(), lr=1e-2)
for step in range(200):
    loss = loss_fn(model(xb), yb)
    opt.zero_grad()                             # forget last step's gradients
    loss.backward()
    opt.step()
print(f"2. loss on one batch of 16 after 200 steps: {loss.item():.4f}")

# Check 3: the classic bug, softmax before CrossEntropyLoss (which applies log-softmax itself).
buggy = nn.Sequential(make_model(), nn.Softmax(dim=1))
opt = torch.optim.Adam(buggy.parameters(), lr=1e-2)
for step in range(200):
    loss = loss_fn(buggy(xb), yb)
    opt.zero_grad()
    loss.backward()
    opt.step()
print(f"3. same batch WITH an extra softmax layer: {loss.item():.4f}  (stuck far above 0)")

# Check 4: compare autograd with finite differences. gradcheck needs float64 inputs.
lin = nn.Linear(5, 3).double()
inp = torch.randn(4, 5, dtype=torch.float64, requires_grad=True)
ok = torch.autograd.gradcheck(lambda t: torch.tanh(lin(t)), (inp,), eps=1e-6, atol=1e-4)
print(f"4. gradcheck passed: {ok}")
w = torch.tensor(2.0, dtype=torch.float64)
h = 1e-3
numeric = ((w + h) ** 3 - (w - h) ** 3) / (2 * h)
print(f"   d(w^3)/dw at w=2: analytic 12, centred difference {numeric.item():.7f}")

# Check 5: gradient clipping rescales a huge gradient to a chosen maximum norm.
model = make_model()
loss = loss_fn(model(X) * 1000, y)              # absurdly large logits -> huge gradients
loss.backward()
before = nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)   # returns the norm BEFORE clipping
after = torch.sqrt(sum(p.grad.pow(2).sum() for p in model.parameters()))
print(f"5. gradient norm before clipping {before.item():.1f}, after {after.item():.3f}")

# Bonus: the broadcasting trap. (N,) minus (N, 1) silently becomes an (N, N) matrix.
pred, target = torch.randn(4), torch.randn(4, 1)
print(f"   shape of pred - target: {tuple((pred - target).shape)}  (wanted (4,))")
