"""How initialization keeps signals alive, and what BatchNorm and LayerNorm compute.

Companion code for the lesson "Initialization and normalization".
Run:  python code/core/intermediate/init_norm.py
Needs PyTorch (CPU is fine). Takes a few seconds.
"""
import math

import torch
from torch import nn

torch.manual_seed(0)
x = torch.randn(1000, 256)                      # 1000 inputs with 256 features, std 1


def activation_std(init, act, layers=10, width=256):
    """Push x through `layers` linear layers + activation; return the std after each."""
    h, stds = x, []
    for _ in range(layers):
        layer = nn.Linear(width, width, bias=False)
        init(layer.weight)                      # nn.init functions work in place
        h = act(layer(h))
        stds.append(h.std().item())
    return stds


inits = {
    "too small (std 0.01)": lambda w: nn.init.normal_(w, std=0.01),
    "too large (std 1.0)": lambda w: nn.init.normal_(w, std=1.0),
    "Xavier/Glorot": lambda w: nn.init.xavier_normal_(w),
    "He/Kaiming": lambda w: nn.init.kaiming_normal_(w, nonlinearity="relu"),
}
for act_name, act in [("tanh", torch.tanh), ("ReLU", torch.relu)]:
    print(f"\nActivation std after layers 1, 5 and 10 ({act_name}):")
    for name, init in inits.items():
        s = activation_std(init, act)
        print(f"  {name:<22} {s[0]:10.4g} {s[4]:10.4g} {s[9]:10.4g}")

# The numbers behind the two recipes, for a layer with 256 inputs and 128 outputs.
print(f"\nHe std for n_in=256:          {math.sqrt(2 / 256):.4f}")
print(f"Xavier uniform limit 256->128: {math.sqrt(6 / (256 + 128)):.4f}")

# BatchNorm on one feature with batch values [1, 2, 3, 6].
bn = nn.BatchNorm1d(1, eps=1e-8)                # tiny eps so the output matches the hand calculation
with torch.no_grad():
    bn.weight.fill_(2.0)                        # gamma (learned scale)
    bn.bias.fill_(1.0)                          # beta (learned shift)
batch = torch.tensor([[1.0], [2.0], [3.0], [6.0]])
bn.train()
print("\nBatchNorm, train mode:", [round(v, 3) for v in bn(batch).flatten().tolist()])
print("running mean / var after one batch:", round(bn.running_mean.item(), 3), round(bn.running_var.item(), 3))
bn.eval()                                       # eval mode uses the running statistics instead
print("BatchNorm, eval mode: ", [round(v, 3) for v in bn(batch).flatten().tolist()])

# LayerNorm normalizes each example over its own features: no batch statistics at all.
ln = nn.LayerNorm(4, elementwise_affine=False, eps=1e-8)
print("LayerNorm of [1, 2, 3, 6]:", [round(v, 3) for v in ln(torch.tensor([[1.0, 2.0, 3.0, 6.0]])).flatten().tolist()])
