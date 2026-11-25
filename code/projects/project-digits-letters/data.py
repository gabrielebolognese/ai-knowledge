"""MNIST digits and EMNIST letters, loaded with torchvision and prepared for training.

    python data.py                      # MNIST: shapes, labels, pixel range, and samples-mnist.png
    python data.py --dataset letters    # EMNIST letters (downloads ~560 MB the first time)
    python data.py --stats              # recompute the mean and standard deviation used below

Datasets are downloaded into ./data/ at run time and are never committed.
"""
import argparse
import gzip
import shutil
import sys
import zipfile
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms

HERE = Path(__file__).parent
DATA_DIR = HERE / "data"
OUT_DIR = HERE / "outputs"      # plots go here (git-ignored)

# Mean and standard deviation of the training pixels after ToTensor() (values in 0..1).
# MNIST's numbers are the ones the PyTorch MNIST example uses; the letters numbers were
# computed with `python data.py --dataset letters --stats` (124,800 training images).
STATS = {
    "mnist": (0.1307, 0.3081),
    "letters": (0.1722, 0.3309),
}

CLASSES = {
    "mnist": [str(d) for d in range(10)],
    # EMNIST letters merges upper and lower case: class 0 is "A or a", ..., class 25 is "Z or z".
    "letters": [chr(ord("a") + i) for i in range(26)],
}

EMNIST_HELP = """
Could not download EMNIST automatically. The NIST server has failed before.
Manual fallback (about 560 MB):
  1. Open https://www.nist.gov/itl/products-and-services/emnist-dataset
  2. Download "Binary format as the original MNIST dataset" (gzip.zip).
  3. Put gzip.zip, without unzipping it, into this folder:
       {raw}
  4. Run the same command again: the code unpacks the four letters files and skips the download.
"""


def unpack_manual_emnist(root):
    """If gzip.zip was downloaded by hand, extract only the letters files, where torchvision looks."""
    raw = Path(root) / "EMNIST" / "raw"
    archive = raw / "gzip.zip"
    wanted = [f"emnist-letters-{part}-{kind}" for part in ("train", "test")
              for kind in ("images-idx3-ubyte", "labels-idx1-ubyte")]
    if not archive.exists() or all((raw / name).exists() for name in wanted):
        return
    with zipfile.ZipFile(archive) as z:
        for name in wanted:
            with z.open(f"gzip/{name}.gz") as packed, gzip.open(packed) as src, open(raw / name, "wb") as dst:
                shutil.copyfileobj(src, dst)
    print(f"unpacked the EMNIST letters files from {archive}")


def fix_emnist_orientation(img):
    """EMNIST images are stored transposed (mirrored and turned 90 degrees). Swap height and width back.

    img is a (1, 28, 28) tensor: (channels, height, width) -> (channels, width, height).
    A named function instead of a lambda, so DataLoader workers can pickle it on Windows.
    """
    return img.transpose(1, 2)


def shift_letter_label(y):
    """EMNIST letters are labelled 1..26 (there is no class 0). CrossEntropyLoss needs 0..25."""
    return y - 1


def dataset_transform(name):
    """The exact pipeline every training and test image goes through."""
    mean, std = STATS[name]
    steps = [transforms.ToTensor()]          # PIL image (0..255) -> float tensor (1, 28, 28) in 0..1
    if name == "letters":
        steps.append(fix_emnist_orientation)  # upright letters, like the ones you draw
    steps.append(transforms.Normalize((mean,), (std,)))  # centre on 0 with spread 1
    return transforms.Compose(steps)


def drawing_transform(name):
    """For an upright 28x28 drawing (preprocess.py): the same ToTensor and Normalize, no transpose."""
    mean, std = STATS[name]
    return transforms.Compose([transforms.ToTensor(), transforms.Normalize((mean,), (std,))])


def load_datasets(name, root=DATA_DIR, transform="default"):
    """Return (train, test) torchvision datasets. transform=None gives raw PIL images."""
    if transform == "default":
        transform = dataset_transform(name)
    if name == "mnist":
        train = datasets.MNIST(root, train=True, download=True, transform=transform)
        test = datasets.MNIST(root, train=False, download=True, transform=transform)
        return train, test
    if name == "letters":
        kwargs = dict(split="letters", transform=transform, target_transform=shift_letter_label)
        unpack_manual_emnist(root)    # no-op unless you placed gzip.zip there by hand
        try:
            train = datasets.EMNIST(root, train=True, download=True, **kwargs)
            test = datasets.EMNIST(root, train=False, download=True, **kwargs)
        except Exception as err:  # network errors, a moved URL, a bad zip...
            print(EMNIST_HELP.format(raw=Path(root) / "EMNIST" / "raw"), file=sys.stderr)
            raise SystemExit(f"EMNIST download failed: {err}")
        return train, test
    raise ValueError(f"unknown dataset {name!r}: use 'mnist' or 'letters'")


def small_subset(ds, n, seed=0):
    """A fixed random sample of n items (used by --smoke)."""
    g = torch.Generator().manual_seed(seed)
    idx = torch.randperm(len(ds), generator=g)[:n].tolist()
    return Subset(ds, idx)


def make_loaders(name, batch_size=64, smoke=False, smoke_size=1000):
    train, test = load_datasets(name)
    if smoke:
        train, test = small_subset(train, smoke_size, seed=0), small_subset(test, smoke_size, seed=1)
    # num_workers=0 keeps things simple and works everywhere (no Windows pickling issues).
    train_loader = DataLoader(train, batch_size=batch_size, shuffle=True, num_workers=0)
    test_loader = DataLoader(test, batch_size=1000, shuffle=False, num_workers=0)
    return train_loader, test_loader


def compute_stats(name):
    """Mean and std of all training pixels, in 0..1 (the orientation does not change them)."""
    train, _ = load_datasets(name, transform=transforms.ToTensor())
    x = train.data.float() / 255.0          # (N, 28, 28) uint8 -> float, without the slow per-item loop
    return x.mean().item(), x.std().item()


def save_grid(name, path, n=32):
    """Plot the first n training images with their labels (needs matplotlib)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    train, _ = load_datasets(name)
    mean, std = STATS[name]
    fig, axes = plt.subplots(4, n // 4, figsize=(n // 4, 4.4))
    for i, ax in enumerate(axes.flat):
        x, y = train[i]
        ax.imshow((x[0] * std + mean).numpy(), cmap="gray")   # undo Normalize for display
        ax.set_title(CLASSES[name][y], fontsize=10)
        ax.axis("off")
    fig.tight_layout()
    Path(path).parent.mkdir(exist_ok=True)
    fig.savefig(path, dpi=100)
    print(f"saved {path}")


def main():
    p = argparse.ArgumentParser(description="Download and inspect MNIST or EMNIST letters")
    p.add_argument("--dataset", choices=["mnist", "letters"], default="mnist")
    p.add_argument("--stats", action="store_true", help="recompute the training mean and std")
    p.add_argument("--no-plot", action="store_true", help="skip the sample grid")
    a = p.parse_args()

    train, test = load_datasets(a.dataset)
    x, y = train[0]
    raw, _ = load_datasets(a.dataset, transform=transforms.ToTensor())
    r, _ = raw[0]
    print(f"dataset      {a.dataset}: {len(train):,} train / {len(test):,} test images")
    print(f"one image    {tuple(x.shape)} (channels, height, width), dtype {x.dtype}")
    print(f"raw pixels   {r.min():.2f} .. {r.max():.2f} after ToTensor (0 = black background, 1 = ink)")
    print(f"normalized   {x.min():.2f} .. {x.max():.2f}, using mean {STATS[a.dataset][0]} and std {STATS[a.dataset][1]}")
    labels = torch.as_tensor(train.targets)
    lo, hi = labels.min().item(), labels.max().item()
    print(f"stored labels {lo} .. {hi}" + ("  (shifted to 0..25 by shift_letter_label)" if a.dataset == "letters" else ""))
    counts = torch.bincount(labels - lo)
    print(f"per class    min {counts.min().item():,}, max {counts.max().item():,} training images")
    print(f"first label  {y} = {CLASSES[a.dataset][y]!r}")
    if a.stats:
        mean, std = compute_stats(a.dataset)
        print(f"computed     mean {mean:.4f}, std {std:.4f}")
    if not a.no_plot:
        save_grid(a.dataset, OUT_DIR / f"samples-{a.dataset}.png")


if __name__ == "__main__":
    main()
