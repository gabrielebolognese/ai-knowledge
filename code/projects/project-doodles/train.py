"""Train the doodle CNN on CPU and track training and validation accuracy per epoch.

    python download.py --smoke && python train.py --smoke   # 2 classes x 500 doodles: well under 2 minutes
    python train.py                                        # 10 classes, 5 epochs: see the lesson for timings
    python train.py --augment --batch-norm --epochs 15 --tag aug-bn-e15   # the app's preferred model (~27 min)
    python train.py --dropout 0 --tag no-dropout           # one-variable-at-a-time experiments

Saves checkpoints/doodles[-tag][-smoke].pt and outputs/history-<same name>.json (+ a curves .png).
"""
import argparse
import json
import time
from pathlib import Path

import torch
from torch import nn

from augment import doodle_augment
from data import OUT_DIR, make_loaders
from models import DoodleCNN, count_parameters, save_checkpoint

HERE = Path(__file__).parent


def get_args():
    p = argparse.ArgumentParser(description="Train a doodle classifier")
    p.add_argument("--epochs", type=int, default=5)
    p.add_argument("--batch-size", type=int, default=128)
    p.add_argument("--lr", type=float, default=1e-3, help="Adam learning rate")
    p.add_argument("--augment", action="store_true", help="random shifts, rotations and scaling (augment.py)")
    p.add_argument("--batch-norm", action="store_true", help="BatchNorm2d after each convolution")
    p.add_argument("--dropout", type=float, default=0.5)
    p.add_argument("--classes", nargs="+", default=None,
                   help="train on these downloaded classes instead of the default 10 (e.g. add pear)")
    p.add_argument("--per-class", type=int, default=None, help="use only the first N downloaded doodles per class")
    p.add_argument("--smoke", action="store_true", help="smoke data (2 classes x 500), 2 epochs")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--threads", type=int, default=None, help="torch.set_num_threads (default: PyTorch's choice)")
    p.add_argument("--tag", default="", help="added to the output names, e.g. --tag aug-bn")
    a = p.parse_args()
    if a.smoke:
        a.epochs = min(a.epochs, 2)
    a.name = "doodles" + (f"-{a.tag}" if a.tag else "") + ("-smoke" if a.smoke else "")
    return a


def train_one_epoch(model, loader, loss_fn, optimizer):
    model.train()                                   # Dropout on, batch norm uses batch statistics
    total_loss = correct = seen = 0
    for x, y in loader:
        logits = model(x)                           # 1. forward
        loss = loss_fn(logits, y)                   # 2. loss
        optimizer.zero_grad()                       # 3. clear old gradients
        loss.backward()                             # 4. backpropagation
        optimizer.step()                            # 5. update the weights
        total_loss += loss.item() * len(y)
        correct += (logits.argmax(1) == y).sum().item()
        seen += len(y)
    return total_loss / seen, correct / seen        # averaged over the epoch (on augmented images, if any)


@torch.no_grad()
def accuracy(model, loader):
    model.eval()                                    # Dropout off, batch norm uses running averages
    correct = total = 0
    for x, y in loader:
        correct += (model(x).argmax(1) == y).sum().item()
        total += len(y)
    return correct / total


def plot_curves(history, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    epochs = [h["epoch"] for h in history]
    fig, ax = plt.subplots(figsize=(5, 3.2))
    ax.plot(epochs, [h["train_acc"] for h in history], "o-", label="train (during the epoch)")
    ax.plot(epochs, [h["val_acc"] for h in history], "s-", label="validation")
    ax.set_xlabel("epoch")
    ax.set_ylabel("accuracy")
    ax.set_xticks(epochs)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def main():
    a = get_args()
    torch.manual_seed(a.seed)
    if a.threads:
        torch.set_num_threads(a.threads)

    augment = doodle_augment() if a.augment else None
    loaders, classes = make_loaders(a.smoke, a.batch_size, augment, a.per_class, a.seed, a.classes)
    config = {"dropout": a.dropout, "batch_norm": a.batch_norm}
    model = DoodleCNN(len(classes), **config)
    print(f"DoodleCNN {config}, augment={a.augment}: {count_parameters(model):,} parameters, "
          f"{len(classes)} classes, {len(loaders['train'].dataset):,} training doodles, {a.epochs} epoch(s)")

    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=a.lr)
    history, start = [], time.time()
    for epoch in range(1, a.epochs + 1):
        train_loss, train_acc = train_one_epoch(model, loaders["train"], loss_fn, optimizer)
        val_acc = accuracy(model, loaders["val"])
        history.append({"epoch": epoch, "train_loss": round(train_loss, 4), "train_acc": round(train_acc, 4),
                        "val_acc": round(val_acc, 4), "seconds": round(time.time() - start)})
        print(f"epoch {epoch}: train loss {train_loss:.3f}  train acc {train_acc:.2%}  "
              f"val acc {val_acc:.2%}  gap {train_acc - val_acc:+.2%}  ({time.time() - start:.0f} s)")

    test_acc = accuracy(model, loaders["test"])     # measured once, at the very end
    print(f"test accuracy {test_acc:.2%} on {len(loaders['test'].dataset):,} unseen doodles")

    ckpt = HERE / "checkpoints" / f"{a.name}.pt"
    save_checkpoint(ckpt, model, classes=classes, config=config,
                    extra={"test_accuracy": test_acc, "augment": a.augment, "epochs": a.epochs, "smoke": a.smoke})
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / f"history-{a.name}.json").write_text(json.dumps(
        {"args": {k: v for k, v in vars(a).items()}, "history": history, "test_acc": test_acc}, indent=1))
    plot_curves(history, OUT_DIR / f"curves-{a.name}.png")
    print(f"saved {ckpt} and outputs/history-{a.name}.json")

    if a.smoke:
        assert history[-1]["train_loss"] < 0.69, "loss did not drop below chance level (ln 2 = 0.69)"
        print(f"smoke test OK in {time.time() - start:.0f} s (2 classes: chance is 50%; "
              f"the full 10-class run reaches about 95-96% after 5 epochs)")


if __name__ == "__main__":
    main()
