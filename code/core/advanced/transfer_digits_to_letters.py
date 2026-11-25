"""Transfer learning in miniature: reuse the digits CNN to learn letters from few examples.

    python transfer_digits_to_letters.py                  # 2,000 training letters, 10 epochs
    python transfer_digits_to_letters.py --train-size 500   # even fewer examples

Needs the trained digits checkpoint (project-digits-letters/checkpoints/mnist-cnn.pt)
and the EMNIST letters data that the digits project downloads.

Three runs on the same small letter set, same epochs, same test set:
  scratch   - random weights everywhere
  frozen    - digit-trained conv layers frozen (feature extraction), new head trained
  finetune  - digit-trained conv layers trained too, with a 10x smaller learning rate
"""
import argparse
import sys
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[2]
DIGITS = ROOT / "projects" / "project-digits-letters"
sys.path.insert(0, str(DIGITS))
from data import load_datasets, small_subset  # noqa: E402
from models import CNN, load_checkpoint  # noqa: E402


def as_tensors(ds):
    """Decode a dataset once into two tensors, so training is fast."""
    x, y = next(iter(DataLoader(ds, batch_size=len(ds))))
    return x, y


def build(mode, checkpoint):
    model = CNN(26)
    if mode == "scratch":
        return model, [{"params": model.parameters(), "lr": 1e-3}]
    digits, _ = load_checkpoint(checkpoint)
    state = {k: v for k, v in digits.state_dict().items() if not k.startswith("classifier.4")}
    model.load_state_dict(state, strict=False)       # everything except the 10-class output layer
    body, head = model.features, model.classifier
    if mode == "frozen":
        for p in body.parameters():
            p.requires_grad = False                    # feature extraction: the conv layers stay fixed
        return model, [{"params": head.parameters(), "lr": 1e-3}]
    return model, [{"params": body.parameters(), "lr": 1e-4},   # gentle changes to pretrained layers
                   {"params": head.parameters(), "lr": 1e-3}]


def run(mode, data, args):
    torch.manual_seed(args.seed)
    model, groups = build(mode, args.checkpoint)
    opt = torch.optim.Adam(groups)
    (xtr, ytr), (xte, yte) = data
    loss_fn = nn.CrossEntropyLoss()
    for _ in range(args.epochs):
        model.train()
        perm = torch.randperm(len(xtr))
        for i in range(0, len(xtr), 64):
            idx = perm[i:i + 64]
            opt.zero_grad()
            loss_fn(model(xtr[idx]), ytr[idx]).backward()
            opt.step()
    model.eval()
    with torch.no_grad():
        acc = (model(xte).argmax(1) == yte).float().mean().item()
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  {mode:<9} trainable {trainable:>8,}   test accuracy {acc:.2%}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=str(DIGITS / "checkpoints" / "mnist-cnn.pt"))
    ap.add_argument("--train-size", type=int, default=2000)
    ap.add_argument("--test-size", type=int, default=5000)
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    if not Path(args.checkpoint).exists():
        raise SystemExit("Train the digits CNN first: cd code/projects/project-digits-letters && python train.py")

    train, test = load_datasets("letters")
    data = (as_tensors(small_subset(train, args.train_size, seed=0)),
            as_tensors(small_subset(test, args.test_size, seed=1)))
    print(f"{args.train_size:,} training letters, {args.epochs} epochs, {args.test_size:,} test letters")
    for mode in ("scratch", "frozen", "finetune"):
        run(mode, data, args)


if __name__ == "__main__":
    main()
