"""Save, load and resume a PyTorch model: state_dict, full checkpoints and safe loading.

Companion code for the lesson "Saving, loading and reusing models" (intermediate track).
Run:  python code/core/intermediate/checkpoint.py      (a few seconds; no dataset needed)
Needs torch. Files are written to checkpoints/ next to this script (git-ignored).
"""
from pathlib import Path

import torch
from torch import nn

HERE = Path(__file__).parent
CKPT_DIR = HERE / "checkpoints"
CKPT_DIR.mkdir(exist_ok=True)

torch.manual_seed(0)
X = torch.randn(256, 4)                          # toy regression data: y = x @ w_true + noise
y = X @ torch.tensor([1.0, -2.0, 0.5, 3.0]) + 0.1 * torch.randn(256)


def make_model():
    return nn.Sequential(nn.Linear(4, 16), nn.ReLU(), nn.Linear(16, 1))


def train(model, opt, epochs, start=0):
    for epoch in range(start, start + epochs):
        model.train()
        loss = nn.functional.mse_loss(model(X).squeeze(1), y)
        opt.zero_grad()
        loss.backward()
        opt.step()
    return loss.item()


# 1. Train for 50 epochs, then save a full checkpoint (everything needed to resume).
model = make_model()
opt = torch.optim.Adam(model.parameters(), lr=1e-2)
loss = train(model, opt, 50)
print(f"after 50 epochs: loss {loss:.4f}")
print("state_dict keys:", list(model.state_dict().keys()))
torch.save({
    "epoch": 50,
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": opt.state_dict(),   # Adam's running averages live here
    "loss": loss,
}, CKPT_DIR / "toy_checkpoint.pt")
torch.save(model.state_dict(), CKPT_DIR / "toy_weights.pt")        # weights only, for inference

# 2. Resume in a "new session": rebuild the objects, then load their state into them.
model2 = make_model()
opt2 = torch.optim.Adam(model2.parameters(), lr=1e-2)
ckpt = torch.load(CKPT_DIR / "toy_checkpoint.pt", map_location="cpu", weights_only=True)
model2.load_state_dict(ckpt["model_state_dict"])
opt2.load_state_dict(ckpt["optimizer_state_dict"])
start = ckpt["epoch"]
loss_resumed = train(model2, opt2, 50, start=start)

# Reference: the same 100 epochs without stopping. Same seed, same data, so the numbers match.
torch.manual_seed(0)
_ = torch.randn(256, 4), torch.randn(256)         # replay the data draws to reach the same RNG state
ref = make_model()
ref_opt = torch.optim.Adam(ref.parameters(), lr=1e-2)
loss_ref = train(ref, ref_opt, 100)
print(f"resumed to 100 epochs: loss {loss_resumed:.4f} | uninterrupted 100 epochs: loss {loss_ref:.4f}")

# 3. Inference: load only the weights, switch to eval mode, turn off gradient tracking.
infer = make_model()
infer.load_state_dict(torch.load(CKPT_DIR / "toy_weights.pt", map_location="cpu", weights_only=True))
infer.eval()
with torch.no_grad():
    same = torch.equal(infer(X), model(X).detach())
print(f"reloaded weights give identical predictions: {same}")
print(f"file sizes: weights {(CKPT_DIR / 'toy_weights.pt').stat().st_size} bytes, "
      f"full checkpoint {(CKPT_DIR / 'toy_checkpoint.pt').stat().st_size} bytes")
