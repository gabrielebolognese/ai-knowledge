"""Draw a doodle with the mouse and watch the model guess while you draw.

    python draw_app.py                                    # uses checkpoints/doodles-aug-bn-e15.pt or doodles.pt
    python draw_app.py --ckpt checkpoints/doodles.pt
    python draw_app.py --selftest                         # no window: draws shapes in code and predicts

Left mouse button draws, right button (or Clear) wipes the canvas. The app keeps your strokes as lists
of points, exactly like the Quick, Draw! game recorded them, and turns them into a 28x28 bitmap with
the dataset's own recipe (preprocess.py). The small image on the right is what the model sees.

Model trained on the Quick, Draw! dataset by Google, CC BY 4.0
(https://github.com/googlecreativelab/quickdraw-dataset).
"""
import argparse
import math
import time
from pathlib import Path

import numpy as np
import torch

from models import load_checkpoint
from preprocess import strokes_to_input

HERE = Path(__file__).parent
SIZE = 360            # canvas size in screen pixels
CREDIT = "Model trained on the Quick, Draw! dataset by Google (CC BY 4.0)"


def find_checkpoint(path):
    if path:
        return Path(path)
    for name in ["doodles-aug-bn-e15.pt", "doodles.pt", "doodles-smoke.pt"]:
        if (HERE / "checkpoints" / name).exists():
            return HERE / "checkpoints" / name
    raise SystemExit("No checkpoint found. Train one first: python train.py   (or python train.py --smoke)")


@torch.no_grad()
def top_k(model, classes, strokes, k=3):
    x = strokes_to_input(strokes)
    probs = torch.softmax(model(x), dim=1)[0]
    values, idx = probs.topk(min(k, len(classes)))
    return x, [(classes[i], p) for i, p in zip(idx.tolist(), values.tolist())]


class DrawApp:
    def __init__(self, root, model, ckpt):
        import tkinter as tk

        self.model, self.classes = model, ckpt["classes"]
        root.title("Doodle guesser")
        self.canvas = tk.Canvas(root, width=SIZE, height=SIZE, bg="white", cursor="pencil",
                                highlightthickness=1, highlightbackground="#bbb")
        self.canvas.grid(row=0, column=0, rowspan=4, padx=12, pady=12)
        tk.Label(root, text="What the model sees (28x28)").grid(row=0, column=1, sticky="s")
        self.preview = tk.Label(root, bg="black", width=140, height=140)
        self.preview.grid(row=1, column=1, padx=12)
        self.result = tk.Label(root, text="Draw: " + ", ".join(self.classes), wraplength=220,
                               font=("Consolas", 12), justify="left", width=24)
        self.result.grid(row=2, column=1, padx=12)
        tk.Button(root, text="Clear", command=self.clear).grid(row=3, column=1, pady=8)
        tk.Label(root, text=CREDIT, fg="#666", font=("Segoe UI", 8)).grid(row=4, column=0, columnspan=2, pady=(0, 6))

        self.strokes, self.current, self.last_guess = [], None, 0.0
        self.canvas.bind("<ButtonPress-1>", self.start)
        self.canvas.bind("<B1-Motion>", self.move)
        self.canvas.bind("<ButtonRelease-1>", self.lift)
        self.canvas.bind("<Button-3>", lambda e: self.clear())

    def start(self, e):
        self.current = [[e.x], [e.y]]               # a stroke = [[x0, x1, ...], [y0, y1, ...]]
        self.strokes.append(self.current)

    def move(self, e):
        if self.current is None:
            return
        xs, ys = self.current
        self.canvas.create_line(xs[-1], ys[-1], e.x, e.y, width=5, capstyle="round", smooth=True)
        xs.append(e.x)
        ys.append(e.y)
        if time.time() - self.last_guess > 0.15:    # guess while drawing, at most ~7 times a second
            self.guess()

    def lift(self, _e):
        self.current = None
        self.guess()

    def guess(self):
        from PIL import Image, ImageTk

        self.last_guess = time.time()
        if not any(len(xs) > 1 for xs, _ in self.strokes):
            return
        x, top3 = top_k(self.model, self.classes, self.strokes)
        img = Image.fromarray((x[0, 0].numpy() * 255).astype(np.uint8)).resize((140, 140), Image.NEAREST)
        self.photo = ImageTk.PhotoImage(img)
        self.preview.configure(image=self.photo, width=140, height=140)
        self.result.configure(text="\n".join(f"{name:<10} {p:6.1%}" for name, p in top3))

    def clear(self):
        self.canvas.delete("all")
        self.strokes, self.current = [], None
        self.preview.configure(image="")
        self.result.configure(text="Draw: " + ", ".join(self.classes))


def demo_shapes():
    """A few doodles drawn with code, in canvas coordinates (y points down)."""
    circle = [[180 + 120 * math.cos(t / 20 * 2 * math.pi) for t in range(21)],
              [180 + 120 * math.sin(t / 20 * 2 * math.pi) for t in range(21)]]
    star_pts = [(180 + (130 if i % 2 == 0 else 50) * math.sin(i * math.pi / 5),
                 190 - (130 if i % 2 == 0 else 50) * math.cos(i * math.pi / 5)) for i in range(11)]
    star = [[p[0] for p in star_pts], [p[1] for p in star_pts]]
    return {
        "clock (circle + hands)": [circle, [[180, 180, 250], [100, 180, 180]]],
        "star (5 points)": [star],
        "house (square + roof)": [[[80, 80, 280, 280, 80], [160, 320, 320, 160, 160]],
                                  [[60, 180, 300], [170, 50, 170]]],
        "tree (trunk + crown)": [[[160, 160], [330, 230]], [[200, 200], [330, 230]],
                                 [[180 + 90 * math.cos(t / 16 * 2 * math.pi) for t in range(17)],
                                  [140 + 90 * math.sin(t / 16 * 2 * math.pi) for t in range(17)]]],
    }


def selftest(model, ckpt):
    for name, strokes in demo_shapes().items():
        _, top3 = top_k(model, ckpt["classes"], strokes)
        print(f"{name:<24} -> " + ", ".join(f"{c} {p:.1%}" for c, p in top3))


def check():
    """No window and no checkpoint: is tkinter installed, and do canvas strokes become a valid model input?"""
    import tkinter                                            # fails here if Python was installed without Tk
    from PIL import ImageTk  # noqa: F401  (the preview image needs it)

    from models import DoodleCNN

    print(f"tkinter {tkinter.TkVersion} available")
    model = DoodleCNN(num_classes=10).eval()                  # untrained: only the shapes are tested
    for name, strokes in demo_shapes().items():
        x, top3 = top_k(model, [str(i) for i in range(10)], strokes)
        ink = (x > 0).float().mean().item()
        assert x.shape == (1, 1, 28, 28) and x.dtype == torch.float32, (x.shape, x.dtype)
        assert 0.0 <= x.min() and x.max() <= 1.0 and 0.02 < ink < 0.6, (x.min(), x.max(), ink)
        assert len(top3) == 3
        print(f"{name:<24} -> 28x28, {ink:.0%} ink pixels -> input accepted by the CNN")
    print("check passed")


def main():
    p = argparse.ArgumentParser(description="Draw doodles and let the CNN guess")
    p.add_argument("--ckpt", default=None)
    p.add_argument("--selftest", action="store_true", help="no window: predict shapes drawn by code")
    p.add_argument("--check", action="store_true", help="no window, no checkpoint: test tkinter and preprocessing")
    a = p.parse_args()
    if a.check:
        check()
        return
    path = find_checkpoint(a.ckpt)
    model, ckpt = load_checkpoint(path)
    print(f"loaded {path.name} ({len(ckpt['classes'])} classes). {CREDIT}")
    if a.selftest:
        selftest(model, ckpt)
        return
    import tkinter as tk

    root = tk.Tk()
    DrawApp(root, model, ckpt)
    root.mainloop()


if __name__ == "__main__":
    main()
