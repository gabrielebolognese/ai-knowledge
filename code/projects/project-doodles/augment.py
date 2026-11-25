"""Label-preserving data augmentation for doodles: small random shifts, rotations and rescaling.

    python augment.py           # saves outputs/augment-examples.png: one doodle, 8 random versions

A doodle shifted by two pixels, tilted by 10 degrees or drawn 10% smaller is still the same object,
so the model should give the same answer. Large changes can break that: a cloud rotated by 90 degrees
no longer looks like a cloud, and a mirrored clock reads backwards (harmless here, but not for digits).
"""
from torchvision.transforms import v2

from data import OUT_DIR


def doodle_augment(degrees=10, shift=0.08, scale=(0.9, 1.1)):
    """Random affine transform on a (1, 28, 28) tensor. shift=0.08 means up to ~2 pixels each way."""
    return v2.RandomAffine(degrees=degrees, translate=(shift, shift), scale=scale)


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import torch

    from data import load_split

    try:
        splits, classes = load_split(smoke=False, per_class=60)
    except SystemExit:
        splits, classes = load_split(smoke=True, per_class=60)
    x, y = splits["train"]
    torch.manual_seed(0)
    aug = doodle_augment()
    img = x[0]
    fig, axes = plt.subplots(1, 9, figsize=(11, 1.6))
    axes[0].imshow(img[0], cmap="gray")
    axes[0].set_title(f"original ({classes[y[0]]})", fontsize=8)
    for ax in axes[1:]:
        ax.imshow(aug(img)[0], cmap="gray")
        ax.set_title("augmented", fontsize=8)
    for ax in axes:
        ax.axis("off")
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / "augment-examples.png"
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    print(f"saved {path}")


if __name__ == "__main__":
    main()
