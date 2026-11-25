"""Turn pen strokes into a 28x28 bitmap exactly the way the Quick, Draw! bitmaps were made.

The pipeline follows the dataset's README and the generation snippet the README links to
(https://github.com/googlecreativelab/quickdraw-dataset/issues/19#issuecomment-402247262):

  1. align the drawing to the top-left corner (minimum x and y become 0)
  2. scale it uniformly so the larger side spans 0..255
  3. simplify each stroke with Ramer-Douglas-Peucker, epsilon 2.0
  4. centre the drawing's bounding box in a 256x256 square (NOT the centre of mass, unlike MNIST)
  5. draw 16-unit-wide round lines, add 16 units of padding, shrink to 28x28 with antialiasing

    python preprocess.py --check     # renders real Quick, Draw! strokes and compares them with the
                                     # official bitmaps and with the model's accuracy
"""
import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
SIDE, LINE, PAD = 256.0, 16.0, 16.0      # the snippet's units: 256x256 drawing, line_diameter 16, padding 16
SUPERSAMPLE = 10                          # draw at 280x280, then shrink: smooth (antialiased) edges


def rdp(points, epsilon=2.0):
    """Ramer-Douglas-Peucker: drop points that lie within epsilon of the line between their neighbours."""
    if len(points) < 3:
        return points
    start, end = points[0], points[-1]
    d = end - start
    norm = np.hypot(*d)
    if norm == 0:
        dist = np.hypot(*(points - start).T)
    else:
        dist = np.abs(d[0] * (points[:, 1] - start[1]) - d[1] * (points[:, 0] - start[0])) / norm
    i = int(np.argmax(dist))
    if dist[i] <= epsilon:
        return np.stack([start, end])
    return np.concatenate([rdp(points[:i + 1], epsilon)[:-1], rdp(points[i:], epsilon)])


def normalize_strokes(strokes, simplify=True):
    """Steps 1-3. strokes = [[xs, ys], ...] in any coordinates -> list of (n, 2) arrays in 0..255."""
    arrays = [np.asarray(s, dtype=np.float64).T for s in strokes if len(s[0]) > 0]
    if not arrays:
        return []
    allp = np.concatenate(arrays)
    low = allp.min(0)
    extent = (allp.max(0) - low).max()
    scale = 255.0 / extent if extent > 0 else 1.0
    arrays = [(a - low) * scale for a in arrays]
    return [rdp(a) for a in arrays] if simplify else arrays


def render(strokes, size=28):
    """Steps 4-5. Normalised strokes (0..255) -> float array (size, size) in [0, 1], white on black."""
    big = size * SUPERSAMPLE
    img = Image.new("L", (big, big), 0)
    if strokes:
        pen = ImageDraw.Draw(img)
        k = big / (SIDE + 2 * PAD + LINE)                    # 256 units + padding -> big pixels
        offset = (SIDE - np.concatenate(strokes).max(0)) / 2  # centre the bounding box in 256x256
        width = LINE * k
        for s in strokes:
            pts = [tuple(((p + offset) + PAD + LINE / 2) * k) for p in s]
            if len(pts) > 1:
                pen.line(pts, fill=255, width=max(1, round(width)), joint="curve")
            for x, y in pts:
                r = width / 2                                # round caps and joints, like cairo's
                pen.ellipse([x - r, y - r, x + r, y + r], fill=255)
    small = img.resize((size, size), Image.BOX)              # average each 10x10 block = antialiasing
    return np.asarray(small, dtype=np.float32) / 255.0


def strokes_to_input(strokes):
    """Raw strokes (e.g. from a canvas, y pointing down) -> tensor (1, 1, 28, 28) ready for the model."""
    import torch

    return torch.from_numpy(render(normalize_strokes(strokes))).view(1, 1, 28, 28)


def naive_render(strokes, canvas=280, width=14):
    """What you get WITHOUT the pipeline: draw on the canvas as it is, then shrink the whole canvas."""
    img = Image.new("L", (canvas, canvas), 0)
    pen = ImageDraw.Draw(img)
    for xs, ys in strokes:
        pen.line(list(zip(xs, ys)), fill=255, width=width, joint="curve")
    return np.asarray(img.resize((28, 28), Image.BOX), dtype=np.float32) / 255.0


# ---------------------------------------------------------------- --check: compare with the real bitmaps
def fetch_strokes(name, n=200):
    """The first n drawings of a class from the official simplified .ndjson file (Range request, ~70 KB)."""
    url = ("https://storage.googleapis.com/quickdraw_dataset/full/simplified/"
           + urllib.parse.quote(name) + ".ndjson")
    req = urllib.request.Request(url, headers={"Range": f"bytes=0-{n * 1500}", "User-Agent": "ai-knowledge-course/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        lines = resp.read().decode("utf-8").split("\n")[:-1]   # drop the last, cut-off line
    return [json.loads(line)["drawing"] for line in lines[:n]]


def check(ckpt_path):
    import torch

    from data import available_classes, data_dir
    from models import load_checkpoint

    classes = available_classes()
    model, ckpt = load_checkpoint(ckpt_path) if Path(ckpt_path).exists() else (None, None)
    diffs, results = [], {"official bitmaps": [0, 0], "pipeline": [0, 0], "naive canvas shrink": [0, 0]}
    print(f"Rendering the first 200 simplified drawings of each class with this file's pipeline")
    for label, name in enumerate(classes):
        drawings = fetch_strokes(name)
        official = np.load(data_dir() / f"{name}.npy", mmap_mode="r")[:len(drawings)].astype(np.float32) / 255
        ours = np.stack([render(normalize_strokes(d, simplify=False)) for d in drawings])  # already simplified
        diffs.append(np.abs(ours - official.reshape(-1, 28, 28)).mean(axis=(1, 2)))
        if model is not None:
            # Simulate a canvas: the 0..255 strokes drawn at 280x280 in the top-left corner, as a user would
            naive = np.stack([naive_render([[np.array(xs) * 0.8 + 10, np.array(ys) * 0.8 + 10] for xs, ys in d])
                              for d in drawings])
            batches = [("official bitmaps", official.reshape(-1, 28, 28)), ("pipeline", ours),
                       ("naive canvas shrink", naive)]
            for key, batch in batches:
                with torch.no_grad():
                    pred = model(torch.from_numpy(batch).unsqueeze(1)).argmax(1)
                results[key][0] += (pred == label).sum().item()
                results[key][1] += len(pred)
    d = np.concatenate(diffs)
    print(f"mean absolute pixel difference from the official bitmaps: {d.mean():.4f} "
          f"(0 = identical, 1 = opposite); {np.mean(d < 0.02):.0%} of drawings differ by less than 0.02")
    if model is not None:
        for key, (right, total) in results.items():
            print(f"model accuracy on the same {total:,} drawings, {key:<20}: {right / total:.1%}")
        print("(these drawings are a mix of training, validation and test rows: compare the three lines "
              "with each other, not with the test accuracy)")
    else:
        print(f"({ckpt_path} not found: train a model to also measure accuracy)")
    return d


def main():
    p = argparse.ArgumentParser(description="Quick, Draw!-style preprocessing")
    p.add_argument("--check", action="store_true", help="compare with the official bitmaps (needs the full download)")
    p.add_argument("--ckpt", default=str(HERE / "checkpoints" / "doodles.pt"))
    a = p.parse_args()
    if a.check:
        check(a.ckpt)
    else:
        demo = [[[0, 100, 100, 0, 0], [0, 0, 100, 100, 0]]]          # a square
        print((render(normalize_strokes(demo)) > 0.5).astype(int))


if __name__ == "__main__":
    main()
