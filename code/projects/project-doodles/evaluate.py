"""Measure a trained doodle model: test accuracy, per-class accuracy, confusion matrix, worst mistakes.

    python evaluate.py                                      # checkpoints/doodles.pt
    python evaluate.py --ckpt checkpoints/doodles-aug-bn.pt
    python evaluate.py --ckpt checkpoints/doodles-smoke.pt --smoke
    python evaluate.py --samples                            # also save a grid of training doodles

Plots go to outputs/: confusion-<name>.png, mistakes-<name>.png (the wrong answers the model was
most sure about) and, with --samples, samples.png.
"""
import argparse
from pathlib import Path

import torch

from data import OUT_DIR, load_split
from models import load_checkpoint

HERE = Path(__file__).parent


@torch.no_grad()
def predict_all(model, x, batch=1000):
    """Probabilities for every image, in batches (model must be in eval mode)."""
    return torch.cat([torch.softmax(model(x[i:i + batch]), dim=1) for i in range(0, len(x), batch)])


def confusion_matrix(y_true, y_pred, k):
    """cm[i, j] = number of doodles of true class i that the model called class j."""
    cm = torch.zeros(k, k, dtype=torch.long)
    cm.index_put_((y_true, y_pred), torch.ones_like(y_true), accumulate=True)
    return cm


def top_confusions(cm, classes, n=6):
    off = cm.clone()
    off.fill_diagonal_(0)                            # only the mistakes
    values, flat = off.flatten().topk(min(n, off.numel()))
    k = len(classes)
    return [(classes[i // k], classes[i % k], v) for v, i in zip(values.tolist(), flat.tolist()) if v > 0]


def print_matrix(cm, classes):
    short = [c[:5] for c in classes]
    print("rows = true class, columns = predicted class")
    print(" " * 9 + "".join(f"{c:>6}" for c in short))
    for name, row in zip(classes, cm.tolist()):
        print(f"{name:>8} " + "".join(f"{v:>6}" for v in row))


def plot_confusion(cm, classes, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rates = cm.float() / cm.sum(1, keepdim=True).clamp(min=1)    # each row as fractions of that class
    fig, ax = plt.subplots(figsize=(6.4, 5.6))
    ax.imshow(rates.sqrt(), cmap="Blues", vmin=0, vmax=1)          # sqrt: small error rates stay visible
    ax.set_xticks(range(len(classes)), classes, rotation=45, ha="right")
    ax.set_yticks(range(len(classes)), classes)
    ax.set_xlabel("predicted class")
    ax.set_ylabel("true class")
    for i in range(len(classes)):
        for j in range(len(classes)):
            ax.text(j, i, cm[i, j].item(), ha="center", va="center", fontsize=7,
                    color="white" if rates[i, j] > 0.5 else "black")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    print(f"saved {path}")


def plot_grid(images, titles, path, cols=8):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = (len(images) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 1.25, rows * 1.5), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for ax, img, title in zip(axes.flat, images, titles):
        ax.imshow(img[0], cmap="gray", vmin=0, vmax=1)
        ax.set_title(title, fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    print(f"saved {path}")


def main():
    p = argparse.ArgumentParser(description="Evaluate a trained doodle model")
    p.add_argument("--ckpt", default=str(HERE / "checkpoints" / "doodles.pt"))
    p.add_argument("--smoke", action="store_true", help="use the smoke download")
    p.add_argument("--no-plots", action="store_true")
    p.add_argument("--samples", action="store_true", help="save outputs/samples.png (4 training doodles per class)")
    a = p.parse_args()

    if not Path(a.ckpt).exists():
        raise SystemExit(f"{a.ckpt} not found: train a model first (python train.py, or python train.py --smoke)")
    model, ckpt = load_checkpoint(a.ckpt)
    splits, classes = load_split(a.smoke or ckpt.get("smoke", False), only=ckpt["classes"])
    if classes != ckpt["classes"]:
        raise SystemExit(f"the checkpoint knows {ckpt['classes']} but data/ holds {classes}")
    x, y = splits["test"]
    probs = predict_all(model, x)
    pred = probs.argmax(1)
    print(f"{Path(a.ckpt).name}: {(pred == y).float().mean():.2%} test accuracy "
          f"({(pred != y).sum().item():,} mistakes out of {len(y):,})")

    cm = confusion_matrix(y, pred, len(classes))
    per_class = cm.diag().float() / cm.sum(1).float()
    print("per-class accuracy, worst first:")
    for i in per_class.argsort().tolist():
        print(f"  {classes[i]:<10} {per_class[i]:.1%}")
    print()
    print_matrix(cm, classes)
    print("\nmost frequent confusions (true -> predicted: count):")
    print("  " + ",  ".join(f"{t} -> {q}: {v}" for t, q, v in top_confusions(cm, classes)))

    # Confidence is not correctness: how sure is the model when it is right, and when it is wrong?
    conf = probs.max(1).values
    right = pred == y
    print(f"\nmean confidence: {conf[right].mean():.1%} when right, {conf[~right].mean():.1%} when wrong; "
          f"{(conf[~right] > 0.9).sum().item()} wrong answers were given with more than 90% confidence")

    if a.no_plots:
        return
    OUT_DIR.mkdir(exist_ok=True)
    stem = Path(a.ckpt).stem
    plot_confusion(cm, classes, OUT_DIR / f"confusion-{stem}.png")
    wrong = (~right).nonzero().flatten()
    worst = wrong[conf[wrong].argsort(descending=True)][:24]
    plot_grid(x[worst], [f"true {classes[y[i]]}\nsaid {classes[pred[i]]} {conf[i]:.0%}" for i in worst.tolist()],
              OUT_DIR / f"mistakes-{stem}.png")
    if a.samples:
        xt, yt = splits["train"]
        idx = torch.cat([(yt == c).nonzero().flatten()[:4] for c in range(len(classes))])
        plot_grid(xt[idx], [classes[yt[i]] for i in idx.tolist()], OUT_DIR / "samples.png")


if __name__ == "__main__":
    main()
