"""A small CNN for 28x28 doodles: the digits project's CNN, with optional batch normalization.

    python models.py          # parameter counts and the shape after every layer
"""
from pathlib import Path

import torch
from torch import nn


class DoodleCNN(nn.Module):
    """Two conv blocks (conv -> [batch norm] -> ReLU -> 2x2 max-pool), then two fully connected layers.

    With 10 classes and no batch norm this has 421,642 parameters, exactly like the MNIST CNN:
    only the data changes. batch_norm=True adds 2 learned numbers per channel (192 in total).
    """

    def __init__(self, num_classes=10, channels=(32, 64), hidden=128, dropout=0.5, batch_norm=False):
        super().__init__()
        c1, c2 = channels

        def block(c_in, c_out):
            layers = [nn.Conv2d(c_in, c_out, 3, padding=1)]
            if batch_norm:
                layers.append(nn.BatchNorm2d(c_out))     # re-centres and re-scales each channel per batch
            return layers + [nn.ReLU(), nn.MaxPool2d(2)]

        self.features = nn.Sequential(*block(1, c1),     # (N, 1, 28, 28) -> (N, 32, 14, 14)
                                      *block(c1, c2))    # -> (N, 64, 7, 7)
        self.classifier = nn.Sequential(
            nn.Flatten(),                                # -> (N, 3136)
            nn.Linear(c2 * 7 * 7, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),                         # dropout=0 switches it off
            nn.Linear(hidden, num_classes),              # logits; CrossEntropyLoss applies softmax
        )

    def forward(self, x):
        return self.classifier(self.features(x))


def count_parameters(model):
    return sum(p.numel() for p in model.parameters())


def save_checkpoint(path, model, *, classes, config, extra=None):
    """Weights plus everything needed to rebuild the model (classes, dropout, batch norm)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": model.state_dict(), "classes": classes, "config": config, **(extra or {})}, path)


def load_checkpoint(path):
    ckpt = torch.load(path, map_location="cpu", weights_only=True)
    model = DoodleCNN(len(ckpt["classes"]), **ckpt["config"])
    model.load_state_dict(ckpt["state_dict"])
    model.eval()                                         # Dropout off, batch norm uses its running averages
    return model, ckpt


def main():
    for bn in (False, True):
        model = DoodleCNN(10, batch_norm=bn)
        print(f"DoodleCNN(10 classes, batch_norm={bn}): {count_parameters(model):,} parameters")
    model = DoodleCNN(10, batch_norm=True)
    print("\nShape after every layer (batch norm on), for a batch of 8 doodles:")
    x = torch.zeros(8, 1, 28, 28)
    print(f"  {'input':<12} {tuple(x.shape)}")
    model.eval()
    for layer in list(model.features) + list(model.classifier):
        x = layer(x)
        print(f"  {type(layer).__name__:<12} {tuple(x.shape)}")


if __name__ == "__main__":
    main()
