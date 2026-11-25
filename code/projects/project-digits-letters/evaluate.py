"""Measure a trained model: accuracy, per-class accuracy, confusion matrix and its worst mistakes.

    python evaluate.py                                   # checkpoints/mnist-cnn.pt
    python evaluate.py --ckpt checkpoints/letters-cnn.pt
    python evaluate.py --ckpt checkpoints/mnist-cnn-smoke.pt --smoke --no-plots

Plots (confusion matrix, most confidently wrong images) are saved in outputs/.
"""
import argparse
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from data import OUT_DIR, STATS, load_datasets, small_subset
from models import load_checkpoint

HERE = Path(__file__).parent


@torch.no_grad()                                     # no gradients: faster, less memory
def predict_all(model, loader):
    """Run the whole test set once. Returns true labels, predicted labels, probabilities, images."""
    model.eval()                                     # Dropout off (load_checkpoint already did this)
    ys, preds, probs, images = [], [], [], []
    for x, y in loader:
        p = torch.softmax(model(x), dim=1)           # logits -> probabilities that sum to 1
        ys.append(y)
        preds.append(p.argmax(dim=1))
        probs.append(p)
        images.append(x)
    return torch.cat(ys), torch.cat(preds), torch.cat(probs), torch.cat(images)


def confusion_matrix(y_true, y_pred, num_classes):
    """cm[i, j] = how many images of true class i were predicted as class j."""
    cm = torch.zeros(num_classes, num_classes, dtype=torch.long)
    for t, p in zip(y_true.tolist(), y_pred.tolist()):
        cm[t, p] += 1
    return cm


def print_matrix(cm, classes):
    width = max(4, len(str(cm.max().item())) + 1)
    print("rows = true class, columns = predicted class")
    print("    " + "".join(f"{c:>{width}}" for c in classes))
    for i, row in enumerate(cm.tolist()):
        print(f"{classes[i]:>3} " + "".join(f"{v:>{width}}" for v in row))


def top_confusions(cm, classes, k=8):
    off = cm.clone()
    off.fill_diagonal_(0)                            # ignore correct answers
    values, flat = off.flatten().topk(k)
    n = len(classes)
    return [(classes[i // n], classes[i % n], v) for v, i in zip(values.tolist(), flat.tolist()) if v > 0]


def plot_confusion(cm, classes, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    size = 0.3 * len(classes) + 3
    fig, ax = plt.subplots(figsize=(size, size))
    ax.imshow(cm.float().log1p(), cmap="Blues")     # log scale, so the small error counts are visible
    ax.set_xticks(range(len(classes)), classes)
    ax.set_yticks(range(len(classes)), classes)
    ax.set_xlabel("predicted class")
    ax.set_ylabel("true class")
    if len(classes) <= 10:
        for i in range(len(classes)):
            for j in range(len(classes)):
                v = cm[i, j].item()
                ax.text(j, i, v, ha="center", va="center", fontsize=8,
                        color="white" if i == j else "black")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    print(f"saved {path}")


def plot_mistakes(images, y_true, y_pred, probs, classes, dataset, path, n=24):
    """The n wrong predictions the model was most sure about."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    wrong = (y_pred != y_true).nonzero().flatten()
    confidence = probs[wrong, y_pred[wrong]]
    worst = wrong[confidence.argsort(descending=True)][:n]
    if len(worst) == 0:
        return
    mean, std = STATS[dataset]
    cols = 8
    rows = (len(worst) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 1.3, rows * 1.6), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for ax, i in zip(axes.flat, worst.tolist()):
        ax.imshow((images[i, 0] * std + mean).numpy(), cmap="gray")
        ax.set_title(f"true {classes[y_true[i]]}\npred {classes[y_pred[i]]} {probs[i, y_pred[i]]:.0%}", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    print(f"saved {path}")


def main():
    p = argparse.ArgumentParser(description="Evaluate a trained handwriting model")
    p.add_argument("--ckpt", default=str(HERE / "checkpoints" / "mnist-cnn.pt"))
    p.add_argument("--smoke", action="store_true", help="evaluate on 1,000 test images only")
    p.add_argument("--no-plots", action="store_true")
    a = p.parse_args()

    if not Path(a.ckpt).exists():
        raise SystemExit(f"{a.ckpt} not found: train a model first, for example `python train.py`")
    model, ckpt = load_checkpoint(a.ckpt)
    dataset, classes = ckpt["dataset"], ckpt["classes"]
    _, test = load_datasets(dataset)
    if a.smoke:
        test = small_subset(test, 1000, seed=1)
    y, pred, probs, images = predict_all(model, DataLoader(test, batch_size=1000))

    acc = (pred == y).float().mean().item()
    print(f"{ckpt['arch'].upper()} on {dataset}: {acc:.2%} test accuracy "
          f"({(pred != y).sum().item():,} mistakes out of {len(y):,})\n")

    cm = confusion_matrix(y, pred, len(classes))
    per_class = cm.diag().float() / cm.sum(dim=1).clamp(min=1).float()
    print("per-class accuracy (worst first):")
    order = per_class.argsort()
    print("  " + "  ".join(f"{classes[i]} {per_class[i]:.1%}" for i in order.tolist()[:10]))
    print()
    print_matrix(cm, classes)
    print("\nmost frequent confusions (true -> predicted: count):")
    print("  " + ",  ".join(f"{t} -> {p_}: {v}" for t, p_, v in top_confusions(cm, classes)))

    if not a.no_plots:
        stem = Path(a.ckpt).stem
        OUT_DIR.mkdir(exist_ok=True)
        plot_confusion(cm, classes, OUT_DIR / f"confusion-{stem}.png")
        plot_mistakes(images, y, pred, probs, classes, dataset, OUT_DIR / f"mistakes-{stem}.png")


if __name__ == "__main__":
    main()
