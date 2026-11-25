"""Train a small MLP on MNIST with the standard PyTorch training loop.

Companion code for the lesson "The PyTorch training loop" (intermediate track).
Run:  python code/core/intermediate/train_loop_mnist.py            (3 epochs, about 1 minute on a laptop CPU)
      python code/core/intermediate/train_loop_mnist.py --epochs 5
Needs torch and torchvision. MNIST (about 12 MB) is downloaded into data/ next to this file the first time.
Expected: validation accuracy about 96% after epoch 1 and about 97% after epoch 3; test accuracy about 97%.
"""
import argparse
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

HERE = Path(__file__).parent


def evaluate(model, loader, loss_fn):
    """Average loss and accuracy over a whole loader, without tracking gradients."""
    model.eval()                                   # evaluation mode (matters for dropout/BatchNorm)
    total_loss, correct, n = 0.0, 0, 0
    with torch.no_grad():                          # no graph is built: faster, less memory
        for X, y in loader:
            logits = model(X)
            total_loss += loss_fn(logits, y).item() * len(y)
            correct += (logits.argmax(dim=1) == y).sum().item()
            n += len(y)
    return total_loss / n, correct / n


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args()

    torch.manual_seed(0)                           # same initial weights and shuffles every run

    # 1. Data: 60,000 training images split 55,000 / 5,000, plus the official 10,000 test images.
    tf = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    full_train = datasets.MNIST(HERE / "data", train=True, download=True, transform=tf)
    test_ds = datasets.MNIST(HERE / "data", train=False, download=True, transform=tf)
    train_ds, val_ds = random_split(full_train, [55_000, 5_000], generator=torch.Generator().manual_seed(0))
    train_dl = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)    # num_workers=0 (default)
    val_dl = DataLoader(val_ds, batch_size=1000)
    test_dl = DataLoader(test_ds, batch_size=1000)

    # 2. Model, loss and optimizer.
    model = nn.Sequential(nn.Flatten(), nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 10))
    loss_fn = nn.CrossEntropyLoss()                # takes raw logits and integer class labels
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    val_loss, val_acc = evaluate(model, val_dl, loss_fn)
    print(f"before training: val loss {val_loss:.3f} (ln 10 = 2.303), val acc {val_acc:.3f}")

    # 3. The training loop.
    best_acc = 0.0
    ckpt_path = HERE / "checkpoints" / "mlp_mnist_best.pt"
    ckpt_path.parent.mkdir(exist_ok=True)
    for epoch in range(1, args.epochs + 1):
        model.train()                              # training mode
        running, seen = 0.0, 0
        for X, y in train_dl:                      # X: (64, 1, 28, 28), y: (64,)
            logits = model(X)                      # 1. forward pass
            loss = loss_fn(logits, y)              # 2. loss
            optimizer.zero_grad()                  # 3. clear old gradients
            loss.backward()                        # 4. backpropagation fills .grad
            optimizer.step()                       # 5. update the weights
            running += loss.item() * len(y)        # .item() turns a 1-element tensor into a float
            seen += len(y)
        val_loss, val_acc = evaluate(model, val_dl, loss_fn)
        print(f"epoch {epoch}: train loss {running / seen:.3f} | val loss {val_loss:.3f} | val acc {val_acc:.3f}")
        if val_acc > best_acc:                     # keep the best model according to VALIDATION data
            best_acc = val_acc
            torch.save(model.state_dict(), ckpt_path)

    # 4. Touch the test set once, with the best checkpoint.
    model.load_state_dict(torch.load(ckpt_path, weights_only=True))
    test_loss, test_acc = evaluate(model, test_dl, loss_fn)
    print(f"best val acc {best_acc:.3f}; test acc {test_acc:.3f} (saved to {ckpt_path.name})")


if __name__ == "__main__":                         # needed on Windows if you raise num_workers above 0
    main()
