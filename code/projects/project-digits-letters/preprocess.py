"""Turn a drawing (any size, dark ink on a light background) into a 28x28 image framed like the dataset.

MNIST digits were scaled to fit a 20x20 box and placed so their centre of mass sits at the centre of
a 28x28 image. EMNIST letters were cropped, centred in a square frame with a small border and scaled
to 28x28 (they fill more of the frame). A model only works well on inputs prepared the same way.

    python preprocess.py --check --ckpt checkpoints/mnist-cnn.pt    # measure how much each step matters
"""
import argparse
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from data import OUT_DIR, drawing_transform, load_datasets, small_subset

HERE = Path(__file__).parent
INK_THRESHOLD = 30          # pixel values (0..255, after inverting) above this count as ink


def to_white_on_black(img):
    """Grayscale, with the dataset's polarity: white ink (high values) on a black (0) background."""
    a = np.asarray(img.convert("L"), dtype=np.float32)
    if a.mean() > 127:      # mostly light: dark ink on paper, like a canvas -> invert
        a = 255.0 - a
    return a


def crop_to_ink(a):
    """Cut away the empty border. Returns None for an empty drawing."""
    rows, cols = np.nonzero(a > INK_THRESHOLD)
    if len(rows) == 0:
        return None
    return a[rows.min():rows.max() + 1, cols.min():cols.max() + 1]


def mnist_frame(ink):
    """Fit in 20x20 (keeping the aspect ratio), then move the centre of mass to the centre of 28x28."""
    h, w = ink.shape
    scale = 20.0 / max(h, w)
    new_w, new_h = max(1, round(w * scale)), max(1, round(h * scale))
    small = Image.fromarray(ink.astype(np.uint8)).resize((new_w, new_h), Image.LANCZOS)  # anti-aliased
    canvas = np.zeros((28, 28), dtype=np.float32)
    top, left = (28 - new_h) // 2, (28 - new_w) // 2
    canvas[top:top + new_h, left:left + new_w] = np.asarray(small, dtype=np.float32)
    # centre of mass = the ink-weighted average row and column
    ys, xs = np.mgrid[0:28, 0:28]
    total = canvas.sum()
    cy, cx = (canvas * ys).sum() / total, (canvas * xs).sum() / total
    dy, dx = int(round(14 - cy)), int(round(14 - cx))       # MNIST's centres of mass average (14.0, 14.0)
    return shift(canvas, dy, dx)


def emnist_frame(ink):
    """Centre in a square frame (keeping the aspect ratio), add an empty border, scale to 28x28 (bicubic)."""
    h, w = ink.shape
    side = max(h, w)
    square = np.zeros((side, side), dtype=np.float32)
    top, left = (side - h) // 2, (side - w) // 2
    square[top:top + h, left:left + w] = ink
    # Border of 3/24 of the letter's size on each side: the letter's longest side then comes out at
    # about 23.7 px, the average measured on the EMNIST training letters (MNIST digits: 20 px).
    square = np.pad(square, round(side * 3 / 24))
    img = Image.fromarray(square.astype(np.uint8))
    return np.asarray(img.resize((28, 28), Image.BICUBIC), dtype=np.float32)


def shift(a, dy, dx):
    out = np.zeros_like(a)
    h, w = a.shape
    src = a[max(0, -dy):h - max(0, dy), max(0, -dx):w - max(0, dx)]
    out[max(0, dy):max(0, dy) + src.shape[0], max(0, dx):max(0, dx) + src.shape[1]] = src
    return out


def preprocess(img, dataset):
    """PIL image of any size -> 28x28 PIL image (white ink on black), framed like `dataset`."""
    ink = crop_to_ink(to_white_on_black(img))
    if ink is None:
        return Image.new("L", (28, 28), 0)
    a = mnist_frame(ink) if dataset == "mnist" else emnist_frame(ink)
    a = a * (255.0 / max(a.max(), 1.0))                       # strongest ink = 255, as in the datasets
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


@torch.no_grad()
def predict(model, dataset, classes, img28, k=3):
    """28x28 PIL image -> [(class, probability), ...] for the k most likely classes."""
    x = drawing_transform(dataset)(img28).unsqueeze(0)       # same ToTensor + Normalize as training; (1, 1, 28, 28)
    probs = torch.softmax(model(x), dim=1)[0]
    top = probs.topk(k)
    return [(classes[i], p) for p, i in zip(top.values.tolist(), top.indices.tolist())]


# ---------------------------------------------------------------------------------------------
# --check: simulate drawings from test images and measure what each preprocessing step is worth


def fake_drawing(upright28, rng, size=280):
    """A test image redrawn like a canvas drawing: random size and position, solid black ink on white."""
    ink = crop_to_ink(upright28.astype(np.float32))
    h, w = ink.shape
    target = rng.uniform(0.35, 0.8) * size                    # people draw big or small
    scale = target / max(h, w)
    big = Image.fromarray(ink.astype(np.uint8)).resize((max(1, round(w * scale)), max(1, round(h * scale))),
                                                       Image.BILINEAR)
    pen = np.where(np.asarray(big) > 100, 0, 255).astype(np.uint8)   # a pen has no grey levels
    page = np.full((size, size), 255, dtype=np.uint8)
    top = rng.integers(0, size - pen.shape[0] + 1)
    left = rng.integers(0, size - pen.shape[1] + 1)
    page[top:top + pen.shape[0], left:left + pen.shape[1]] = pen
    return Image.fromarray(page)


def naive(img, invert):
    """What happens without proper preprocessing: shrink the whole canvas to 28x28."""
    a = np.asarray(img.convert("L").resize((28, 28), Image.LANCZOS), dtype=np.float32)
    if invert:
        a = 255.0 - a
    return Image.fromarray(a.astype(np.uint8))


def check(ckpt_path, n):
    from models import load_checkpoint

    model, ckpt = load_checkpoint(ckpt_path)
    dataset, classes = ckpt["dataset"], ckpt["classes"]
    _, raw_test = load_datasets(dataset, transform=None)      # PIL images, labels already 0-based
    subset = small_subset(raw_test, n, seed=2)
    rng = np.random.default_rng(0)
    variants = {
        "dataset image as is": [],
        "drawing + full preprocessing": [],
        "drawing, shrink only (black ink on white)": [],
        "drawing, shrink + invert (no crop, no centring)": [],
    }
    examples = []
    for img, y in subset:
        a = np.asarray(img)
        if dataset == "letters":
            a = a.T                                           # stored transposed: make it upright first
        drawing = fake_drawing(a, rng)
        inputs = [Image.fromarray(a), preprocess(drawing, dataset), naive(drawing, False), naive(drawing, True)]
        for name, inp in zip(variants, inputs):
            variants[name].append(predict(model, dataset, classes, inp, k=1)[0][0] == classes[y])
        if len(examples) < 6:
            examples.append([drawing.resize((84, 84))] + inputs)
    print(f"{ckpt['arch'].upper()} trained on {dataset}, {n} test images redrawn as canvas drawings:")
    for name, hits in variants.items():
        print(f"  {name:<50} {np.mean(hits):6.1%}")
    save_examples(examples)


def save_examples(examples):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    titles = ["drawing", "dataset", "preprocessed", "shrink only", "shrink+invert"]
    fig, axes = plt.subplots(len(examples), 5, figsize=(6.5, 1.4 * len(examples)), squeeze=False)
    for r, row in enumerate(examples):
        for c, im in enumerate(row):
            axes[r, c].imshow(np.asarray(im), cmap="gray", vmin=0, vmax=255)
            axes[r, c].axis("off")
            if r == 0:
                axes[r, c].set_title(titles[c], fontsize=8)
    fig.tight_layout()
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / "preprocess-check.png"
    fig.savefig(path, dpi=110)
    plt.close(fig)
    print(f"saved {path}")


def main():
    p = argparse.ArgumentParser(description="Preprocessing for your own drawings")
    p.add_argument("--check", action="store_true", help="measure accuracy with and without preprocessing")
    p.add_argument("--ckpt", default=str(HERE / "checkpoints" / "mnist-cnn.pt"))
    p.add_argument("--n", type=int, default=1000, help="test images for --check")
    p.add_argument("--image", help="preprocess one image file and save the 28x28 result in outputs/")
    p.add_argument("--dataset", choices=["mnist", "letters"], default="mnist", help="framing for --image")
    a = p.parse_args()
    if a.check:
        check(a.ckpt, a.n)
    elif a.image:
        OUT_DIR.mkdir(exist_ok=True)
        out = OUT_DIR / f"{Path(a.image).stem}-28x28.png"
        preprocess(Image.open(a.image), a.dataset).save(out)
        print(f"saved {out}")
    else:
        p.print_help()


if __name__ == "__main__":
    main()
