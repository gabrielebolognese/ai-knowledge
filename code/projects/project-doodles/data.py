"""Load the downloaded Quick, Draw! bitmaps and split them into train, validation and test sets.

    python data.py            # sizes, class balance and pixel statistics of the full download
    python data.py --smoke    # the same for the 2-class smoke download

Every class is split the same way (balanced): 3/4 train, 1/12 validation, 1/6 test.
With 12,000 doodles per class that is 9,000 / 1,000 / 2,000.

Data: Quick, Draw! dataset by Google, CC BY 4.0 (https://github.com/googlecreativelab/quickdraw-dataset).
"""
import argparse
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset, TensorDataset

from download import CLASSES, data_dir

HERE = Path(__file__).parent
OUT_DIR = HERE / "outputs"


def available_classes(smoke=False, only=None):
    """Class names, sorted so the label numbers never change.

    Default: the 10 course classes (or every smoke file). `only` picks other downloaded classes.
    """
    folder = data_dir(smoke)
    found = sorted(p.stem for p in folder.glob("*.npy"))
    if not found:
        flag = " --smoke" if smoke else ""
        raise SystemExit(f"No data in {folder}. Download it first: python download.py{flag}")
    wanted = sorted(only) if only else (found if smoke else [c for c in CLASSES if c in found])
    missing = [c for c in wanted if c not in found]
    if missing or not wanted:
        raise SystemExit(f"Not downloaded: {missing or CLASSES}. Run: python download.py --classes {' '.join(missing or CLASSES)}")
    return wanted


def load_split(smoke=False, per_class=None, seed=0, only=None):
    """Returns {'train': (X, y), 'val': (X, y), 'test': (X, y)} and the class names.

    X is a float tensor (N, 1, 28, 28) in [0, 1] (white strokes on black, like MNIST); y holds class indices.
    """
    classes = available_classes(smoke, only)
    rng = np.random.default_rng(seed)
    parts = {"train": ([], []), "val": ([], []), "test": ([], [])}
    for label, name in enumerate(classes):
        arr = np.load(data_dir(smoke) / f"{name}.npy", mmap_mode="r")   # reads lazily from disk
        n = min(per_class or len(arr), len(arr))
        idx = rng.permutation(n)                     # shuffle inside the class before splitting
        n_test, n_val = n // 6, n // 12
        cuts = {"test": idx[:n_test], "val": idx[n_test:n_test + n_val], "train": idx[n_test + n_val:]}
        for split, rows in cuts.items():
            parts[split][0].append(np.asarray(arr[np.sort(rows)]).reshape(-1, 28, 28))
            parts[split][1].append(np.full(len(rows), label))
    out = {}
    for split, (xs, ys) in parts.items():
        x = torch.from_numpy(np.concatenate(xs)).float().div(255).unsqueeze(1)   # (N, 1, 28, 28)
        out[split] = (x, torch.from_numpy(np.concatenate(ys)).long())
    return out, classes


class AugmentedDataset(Dataset):
    """Applies a random transform to each training image every time it is read (a fresh one per epoch)."""

    def __init__(self, x, y, transform):
        self.x, self.y, self.transform = x, y, transform

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        return self.transform(self.x[i]), self.y[i]


def make_loaders(smoke=False, batch_size=128, augment=None, per_class=None, seed=0, only=None):
    """DataLoaders for train (shuffled, optionally augmented), validation and test."""
    splits, classes = load_split(smoke, per_class, seed, only)
    x, y = splits["train"]
    train_ds = AugmentedDataset(x, y, augment) if augment else TensorDataset(x, y)
    loaders = {
        "train": DataLoader(train_ds, batch_size=batch_size, shuffle=True),
        "val": DataLoader(TensorDataset(*splits["val"]), batch_size=1000),
        "test": DataLoader(TensorDataset(*splits["test"]), batch_size=1000),
    }
    return loaders, classes


def ink_box_side(x, threshold=0.1):
    """Longest side (in pixels) of the box around the ink, for each image in a (N, 1, 28, 28) batch."""
    ink = x[:, 0] > threshold
    rows, cols = ink.any(dim=2), ink.any(dim=1)

    def extent(mask):
        first = mask.float().argmax(dim=1)
        last = mask.shape[1] - 1 - mask.flip(1).float().argmax(dim=1)
        return last - first + 1

    return torch.maximum(extent(rows), extent(cols)).float()


def main():
    p = argparse.ArgumentParser(description="Inspect the Quick, Draw! split")
    p.add_argument("--smoke", action="store_true")
    a = p.parse_args()
    splits, classes = load_split(a.smoke)
    print(f"{len(classes)} classes: {', '.join(classes)}")
    for name, (x, y) in splits.items():
        counts = torch.bincount(y, minlength=len(classes)).tolist()
        print(f"  {name:<5} {tuple(x.shape)}  per class: {counts[0]:,}" + ("" if len(set(counts)) == 1 else " (unequal!)"))
    x = splits["train"][0]
    side = ink_box_side(x)
    print(f"pixel mean {x.mean():.3f}, share of pixels with ink {(x > 0.1).float().mean():.1%}")
    print(f"longest side of the ink box: mean {side.mean():.1f} px, median {side.median():.0f} px "
          f"(the doodle is centred on its bounding box and fills most of the 28x28 frame)")


if __name__ == "__main__":
    main()
