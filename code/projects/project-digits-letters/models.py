"""Two models for 28x28 handwriting: an MLP baseline and a small CNN.

    python models.py          # parameter counts per layer, and the shape after every CNN layer
"""
from pathlib import Path

import torch
from torch import nn


class MLP(nn.Module):
    """784 -> 128 -> num_classes. Treats the image as a flat list of 784 unrelated numbers."""

    def __init__(self, num_classes=10, hidden=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Flatten(),                    # (N, 1, 28, 28) -> (N, 784)
            nn.Linear(28 * 28, hidden),
            nn.ReLU(),
            nn.Linear(hidden, num_classes),  # raw scores (logits); CrossEntropyLoss applies softmax
        )

    def forward(self, x):
        return self.net(x)


class CNN(nn.Module):
    """Two conv blocks (conv -> ReLU -> 2x2 max-pool), then two fully connected layers.

    With kernel_size=3 and 10 classes this has 421,642 parameters.
    padding = kernel_size // 2 keeps 28x28 after each conv (for odd kernel sizes),
    so the pools give 28 -> 14 -> 7 and the flattened size stays 64 * 7 * 7 = 3136.
    """

    def __init__(self, num_classes=10, kernel_size=3, channels=(32, 64), hidden=128, dropout=0.5):
        super().__init__()
        c1, c2 = channels
        pad = kernel_size // 2
        self.features = nn.Sequential(
            nn.Conv2d(1, c1, kernel_size, padding=pad),   # (N, 1, 28, 28) -> (N, 32, 28, 28)
            nn.ReLU(),
            nn.MaxPool2d(2),                              # -> (N, 32, 14, 14)
            nn.Conv2d(c1, c2, kernel_size, padding=pad),  # -> (N, 64, 14, 14)
            nn.ReLU(),
            nn.MaxPool2d(2),                              # -> (N, 64, 7, 7)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),                                 # -> (N, 3136)
            nn.Linear(c2 * 7 * 7, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),                          # only active in model.train() mode
            nn.Linear(hidden, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


def build_model(arch, num_classes, kernel_size=3):
    if arch == "mlp":
        return MLP(num_classes)
    if arch == "cnn":
        return CNN(num_classes, kernel_size=kernel_size)
    raise ValueError(f"unknown model {arch!r}: use 'mlp' or 'cnn'")


def count_parameters(model):
    return sum(p.numel() for p in model.parameters())


def save_checkpoint(path, model, *, arch, dataset, classes, kernel_size, extra=None):
    """Save the weights plus everything needed to rebuild and use the model later."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "state_dict": model.state_dict(),
        "arch": arch,
        "dataset": dataset,          # tells preprocess.py which normalization and framing to use
        "classes": classes,
        "kernel_size": kernel_size,
        **(extra or {}),
    }, path)


def load_checkpoint(path):
    """Rebuild the model from a checkpoint and switch it to evaluation mode."""
    ckpt = torch.load(path, map_location="cpu", weights_only=True)
    model = build_model(ckpt["arch"], len(ckpt["classes"]), ckpt.get("kernel_size", 3))
    model.load_state_dict(ckpt["state_dict"])
    model.eval()                     # turns Dropout off: predictions become deterministic
    return model, ckpt


def layer_table(model):
    for name, p in model.named_parameters():
        print(f"  {name:<22} {str(tuple(p.shape)):<18} {p.numel():>9,}")
    print(f"  {'total':<41}{count_parameters(model):>9,}")


def main():
    print("MLP (10 classes)")
    layer_table(MLP(10))
    print("\nCNN (10 classes, 3x3 kernels)")
    cnn = CNN(10)
    layer_table(cnn)
    print(f"\nCNN with 26 outputs (letters): {count_parameters(CNN(26)):,} parameters")
    print(f"CNN with 5x5 kernels:          {count_parameters(CNN(10, kernel_size=5)):,} parameters")

    print("\nShape after every CNN layer, for a batch of 8 images:")
    x = torch.zeros(8, 1, 28, 28)
    print(f"  {'input':<12} {tuple(x.shape)}")
    for layer in list(cnn.features) + list(cnn.classifier):
        x = layer(x)
        print(f"  {type(layer).__name__:<12} {tuple(x.shape)}")

    print("\nThe classic mistake: a batch without the channel dimension, shape (8, 28, 28)")
    bad = torch.zeros(8, 28, 28)
    try:
        cnn(bad)
    except RuntimeError as err:
        print(f"  RuntimeError: {str(err).splitlines()[0]}")
    print(f"  fix: bad.unsqueeze(1) has shape {tuple(bad.unsqueeze(1).shape)} -> output {tuple(cnn(bad.unsqueeze(1)).shape)}")


if __name__ == "__main__":
    main()
