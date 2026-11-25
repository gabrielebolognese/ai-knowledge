"""Shrink the digits CNN with 8-bit quantization and measure what changes.

    python quantize_cnn.py            # uses the trained digits checkpoint if it exists
    python quantize_cnn.py --random   # random weights: size and speed only, no accuracy

Part 1 quantizes one weight matrix by hand with the lesson's formulas
(scale S and zero-point Z, so that real = S * (q - Z)).
Part 2 uses PyTorch's dynamic quantization on the Linear layers and compares
file size, speed and test accuracy with the original float32 model.
"""
import argparse
import io
import sys
import time
import warnings
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
DIGITS = ROOT / "projects" / "project-digits-letters"
sys.path.insert(0, str(DIGITS))
from models import CNN, count_parameters, load_checkpoint  # noqa: E402


def quantize_affine(x, qmin=-128, qmax=127):
    """Map floats to integers in [qmin, qmax]: q = round(x / S) + Z."""
    lo, hi = min(x.min().item(), 0.0), max(x.max().item(), 0.0)  # the range must contain 0
    scale = (hi - lo) / (qmax - qmin)
    zero_point = qmin - round(lo / scale)
    q = torch.clamp(torch.round(x / scale) + zero_point, qmin, qmax).to(torch.int8)
    return q, scale, zero_point


def dequantize(q, scale, zero_point):
    return scale * (q.float() - zero_point)


def file_size(model):
    buf = io.BytesIO()
    torch.save(model.state_dict(), buf)
    return buf.getbuffer().nbytes


@torch.no_grad()
def accuracy_and_time(model, loader):
    correct = total = 0
    start = time.perf_counter()
    for x, y in loader:
        correct += (model(x).argmax(1) == y).sum().item()
        total += len(y)
    return correct / total, time.perf_counter() - start


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=str(DIGITS / "checkpoints" / "mnist-cnn.pt"))
    ap.add_argument("--random", action="store_true", help="skip the checkpoint and the test set")
    args = ap.parse_args()
    torch.manual_seed(0)

    if not args.random and Path(args.checkpoint).exists():
        model, _ = load_checkpoint(args.checkpoint)
        from data import make_loaders
        _, test_loader = make_loaders("mnist")
        loader = list(test_loader)  # decode the images once, so the timing below measures only the model
    else:
        print("No checkpoint used: random weights, so accuracy is skipped.")
        model, loader = CNN(10).eval(), None
    has_labels = loader is not None
    print(f"CNN: {count_parameters(model):,} parameters")

    # Part 1: one matrix by hand (fc1 holds 401,408 of the weights).
    w = model.classifier[1].weight.data
    q, s, z = quantize_affine(w)
    err = (dequantize(q, s, z) - w).abs().max().item()
    print(f"\nfc1 weights {tuple(w.shape)}: S = {s:.6f}, Z = {z}")
    print(f"  float32 {w.numel() * 4:,} bytes -> int8 {q.numel():,} bytes")
    print(f"  largest rounding error {err:.6f} (never more than S/2 = {s / 2:.6f})")

    # Part 2: PyTorch dynamic quantization (int8 weights for every nn.Linear).
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # torch.ao.quantization prints a deprecation notice (see the lesson)
        try:
            qmodel = torch.ao.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
        except (AttributeError, RuntimeError) as e:
            raise SystemExit(f"Dynamic quantization is not available in this PyTorch build: {e}")

        print(f"\nsaved size: float32 {file_size(model):,} bytes, int8-Linear {file_size(qmodel):,} bytes")
        if loader is None:
            x = torch.randn(1000, 1, 28, 28)
            loader = [(x, torch.zeros(1000, dtype=torch.long))] * 10
        for name, m in [("float32", model), ("int8-Linear", qmodel)]:
            accuracy_and_time(m, loader[:2])  # warm-up
            acc, sec = accuracy_and_time(m, loader)
            shown = f"{acc:.2%}" if has_labels else "n/a"
            print(f"  {name:<12} accuracy {shown:>7}   time for 10,000 images {sec:.2f} s")


if __name__ == "__main__":
    main()
