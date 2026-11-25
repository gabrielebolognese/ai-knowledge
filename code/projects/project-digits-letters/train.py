"""Train an MLP or a CNN on MNIST digits or EMNIST letters, on a CPU.

    python train.py --smoke                      # 1,000 images, 1 epoch: checks your setup in well under 2 minutes
    python train.py --model mlp                  # MLP baseline on MNIST: about 97-98% test accuracy
    python train.py                              # CNN on MNIST, 3 epochs: about 99%
    python train.py --dataset letters --epochs 5 # CNN on EMNIST letters: about 92-94%
    python train.py --kernel-size 5              # an experiment from the lessons

The trained model is saved to checkpoints/<dataset>-<model>[-smoke].pt for evaluate.py and draw_app.py.
"""
import argparse
import time
from pathlib import Path

import torch
from torch import nn

from data import CLASSES, make_loaders
from models import build_model, count_parameters, save_checkpoint

HERE = Path(__file__).parent


def get_args():
    p = argparse.ArgumentParser(description="Train a handwriting classifier")
    p.add_argument("--dataset", choices=["mnist", "letters"], default="mnist")
    p.add_argument("--model", choices=["mlp", "cnn"], default="cnn")
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--lr", type=float, default=1e-3, help="Adam learning rate")
    p.add_argument("--kernel-size", type=int, default=3, help="CNN kernel size (odd: 3, 5, 7)")
    p.add_argument("--smoke", action="store_true", help="~1,000 training images, 1 epoch")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--threads", type=int, default=None, help="torch.set_num_threads (default: PyTorch's choice)")
    p.add_argument("--out", default=None, help="checkpoint path (default checkpoints/<dataset>-<model>[-smoke].pt)")
    a = p.parse_args()
    if a.smoke:
        a.epochs = 1
    a.out = Path(a.out or HERE / "checkpoints" / f"{a.dataset}-{a.model}{'-smoke' if a.smoke else ''}.pt")
    return a


def train_one_epoch(model, loader, loss_fn, optimizer, epoch, log_every=100):
    model.train()                                   # Dropout on
    losses = []
    for step, (x, y) in enumerate(loader, start=1):
        logits = model(x)                           # 1. forward: (N, 1, 28, 28) -> (N, classes)
        loss = loss_fn(logits, y)                   # 2. how wrong, on average, for this batch
        optimizer.zero_grad()                       # 3. clear the previous step's gradients
        loss.backward()                             # 4. backpropagation: d(loss)/d(every weight)
        optimizer.step()                            # 5. nudge every weight downhill
        losses.append(loss.item())
        if step % log_every == 0 or step == len(loader):
            recent = sum(losses[-log_every:]) / len(losses[-log_every:])
            print(f"  epoch {epoch} step {step:>4}/{len(loader)}  loss {recent:.4f}")
    return losses


@torch.no_grad()                                    # no gradients needed to measure accuracy
def accuracy(model, loader):
    model.eval()                                    # Dropout off
    correct = total = 0
    for x, y in loader:
        pred = model(x).argmax(dim=1)               # the class with the highest score
        correct += (pred == y).sum().item()
        total += y.numel()
    return correct / total


def main():
    a = get_args()
    torch.manual_seed(a.seed)
    if a.threads:
        torch.set_num_threads(a.threads)

    train_loader, test_loader = make_loaders(a.dataset, a.batch_size, smoke=a.smoke)
    classes = CLASSES[a.dataset]
    model = build_model(a.model, len(classes), a.kernel_size)
    print(f"{a.model.upper()} on {a.dataset}: {count_parameters(model):,} parameters, "
          f"{len(train_loader.dataset):,} training images, {a.epochs} epoch(s)")

    loss_fn = nn.CrossEntropyLoss()                 # softmax + negative log-likelihood, on raw logits
    optimizer = torch.optim.Adam(model.parameters(), lr=a.lr)

    start = time.time()
    first_losses, last_losses = None, None
    for epoch in range(1, a.epochs + 1):
        losses = train_one_epoch(model, train_loader, loss_fn, optimizer, epoch,
                                 log_every=5 if a.smoke else 100)
        first_losses = first_losses or losses[:5]
        last_losses = losses[-5:]
        acc = accuracy(model, test_loader)
        print(f"epoch {epoch}: test accuracy {acc:.2%}  ({time.time() - start:.0f} s so far)")

    save_checkpoint(a.out, model, arch=a.model, dataset=a.dataset, classes=classes,
                    kernel_size=a.kernel_size, extra={"test_accuracy": acc, "epochs": a.epochs})
    print(f"saved {a.out}")

    if a.smoke:
        before = sum(first_losses) / len(first_losses)
        after = sum(last_losses) / len(last_losses)
        assert after < before, f"loss did not go down ({before:.3f} -> {after:.3f})"
        print(f"smoke test OK: loss {before:.2f} -> {after:.2f} in {time.time() - start:.0f} s "
              f"(chance level is {1 / len(classes):.0%}; a full run reaches far higher accuracy)")


if __name__ == "__main__":
    main()
