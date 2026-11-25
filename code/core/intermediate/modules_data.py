"""nn.Module, Dataset and DataLoader: a model class and shuffled mini-batches.

Companion code for the lesson "nn.Module, Dataset and DataLoader".
Run:  python code/core/intermediate/modules_data.py
Needs PyTorch (CPU is fine). No download: the data set is generated in memory.
"""
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset, TensorDataset


class MLP(nn.Module):
    """784 -> 128 -> 10, the network from the multilayer-perceptron lesson."""

    def __init__(self, n_in=784, n_hidden=128, n_out=10):
        super().__init__()                          # always call this first
        self.flatten = nn.Flatten()                 # (N, 1, 28, 28) -> (N, 784)
        self.hidden = nn.Linear(n_in, n_hidden)     # weight (128, 784) and bias (128,)
        self.out = nn.Linear(n_hidden, n_out)

    def forward(self, x):                           # runs when you call model(x)
        x = self.flatten(x)
        x = torch.relu(self.hidden(x))
        return self.out(x)                          # logits, no softmax


class TwoMoons(Dataset):
    """A custom Dataset: 1,000 noisy 2-D points in two interleaved half-circles."""

    def __init__(self, n=1000, seed=0):
        g = torch.Generator().manual_seed(seed)
        t = torch.rand(n, generator=g) * torch.pi
        label = torch.randint(0, 2, (n,), generator=g)
        x = torch.stack([torch.cos(t), torch.sin(t)], dim=1)
        x[label == 1] = torch.tensor([1.0, 0.5]) - x[label == 1]   # second moon, flipped and shifted
        self.x = x + 0.1 * torch.randn(n, 2, generator=g)
        self.y = label

    def __len__(self):                              # how many examples
        return len(self.y)

    def __getitem__(self, i):                       # one example as (features, label)
        return self.x[i], self.y[i]


def main():
    torch.manual_seed(0)
    model = MLP()
    print(model)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"parameters: {n_params:,}")
    for name, p in model.named_parameters():
        print(f"  {name:15s} {tuple(p.shape)}")

    images = torch.rand(64, 1, 28, 28)              # a fake batch of 64 MNIST-sized images
    print("logits shape:", tuple(model(images).shape))

    same = nn.Sequential(nn.Flatten(), nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 10))
    print("nn.Sequential version:", sum(p.numel() for p in same.parameters()), "parameters")

    ds = TwoMoons()
    loader = DataLoader(ds, batch_size=64, shuffle=True, num_workers=0)
    sizes = [len(yb) for _, yb in loader]
    xb, yb = next(iter(loader))
    print(f"{len(ds)} examples -> {len(loader)} batches per epoch, sizes {sizes[0]} ... {sizes[-1]}")
    print("one batch:", tuple(xb.shape), yb.dtype)

    tensors = TensorDataset(ds.x, ds.y)             # the shortcut when the data is already tensors
    print("TensorDataset item 0:", [tuple(t.shape) for t in tensors[0]])


if __name__ == "__main__":                          # required for num_workers > 0 on Windows and macOS
    main()
