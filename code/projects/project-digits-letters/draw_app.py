"""Draw a digit or a letter with the mouse and let your trained model read it.

    python draw_app.py                                     # uses checkpoints/mnist-cnn.pt
    python draw_app.py --ckpt checkpoints/letters-cnn.pt   # letters (merged case: 'a' means A or a)
    python draw_app.py --selftest                          # no window: draws a test stroke and predicts

Left mouse button draws, right button (or the Clear button) wipes the canvas. The model predicts every
time you lift the pen. The small image on the right is exactly what the model sees.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from models import load_checkpoint
from preprocess import predict, preprocess

HERE = Path(__file__).parent
SIZE = 280          # canvas size in screen pixels (10x the 28x28 input)
PEN = 22            # brush width; after scaling to 20x20 this gives MNIST-like 2-3 pixel strokes


def find_checkpoint(path):
    if path:
        return Path(path)
    for name in ["mnist-cnn.pt", "mnist-cnn-smoke.pt"]:
        if (HERE / "checkpoints" / name).exists():
            return HERE / "checkpoints" / name
    raise SystemExit("No checkpoint found. Train one first: python train.py   (or python train.py --smoke)")


class DrawApp:
    def __init__(self, root, model, ckpt):
        import tkinter as tk

        self.tk = tk
        self.model, self.dataset, self.classes = model, ckpt["dataset"], ckpt["classes"]
        root.title(f"Handwriting reader: {ckpt['arch'].upper()} trained on {self.dataset}")
        # Two copies of the drawing: the tkinter canvas you see, and a PIL image the model reads.
        self.canvas = tk.Canvas(root, width=SIZE, height=SIZE, bg="white", cursor="pencil")
        self.canvas.grid(row=0, column=0, rowspan=4, padx=10, pady=10)
        self.image = Image.new("L", (SIZE, SIZE), 255)            # white paper
        self.pen = ImageDraw.Draw(self.image)
        self.last = None

        tk.Label(root, text="What the model sees (28x28)").grid(row=0, column=1, sticky="s")
        self.preview = tk.Label(root, bg="black", width=140, height=140)
        self.preview.grid(row=1, column=1, padx=10)
        self.result = tk.Label(root, text="Draw something", font=("Segoe UI", 14), justify="left", width=22)
        self.result.grid(row=2, column=1, padx=10)
        tk.Button(root, text="Clear", command=self.clear).grid(row=3, column=1, pady=10)

        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.lift)
        self.canvas.bind("<Button-3>", lambda e: self.clear())

    def draw(self, event):
        x, y = event.x, event.y
        if self.last:
            self.canvas.create_line(*self.last, x, y, width=PEN, capstyle="round", smooth=True)
            self.pen.line([self.last, (x, y)], fill=0, width=PEN)
        r = PEN // 2
        self.pen.ellipse([x - r, y - r, x + r, y + r], fill=0)     # round joints, like the canvas line
        self.last = (x, y)

    def lift(self, _event):
        self.last = None
        self.classify()

    def classify(self):
        from PIL import ImageTk

        img28 = preprocess(self.image, self.dataset)              # crop, scale, centre, invert
        top3 = predict(self.model, self.dataset, self.classes, img28, k=3)
        self.photo = ImageTk.PhotoImage(img28.resize((140, 140), Image.NEAREST))
        self.preview.configure(image=self.photo, width=140, height=140)
        lines = [f"{label!s:>3}   {p:6.1%}" for label, p in top3]
        self.result.configure(text="\n".join(lines))

    def clear(self):
        self.canvas.delete("all")
        self.pen.rectangle([0, 0, SIZE, SIZE], fill=255)
        self.result.configure(text="Draw something")
        self.preview.configure(image="")
        self.last = None


def selftest(model, ckpt):
    """Draw a '1' (or an 'l' for letters) and a '7' with code, without opening a window."""
    shapes = {"vertical bar": [(140, 50), (140, 230)], "seven": [(80, 60), (200, 60), (120, 230)]}
    for name, points in shapes.items():
        img = Image.new("L", (SIZE, SIZE), 255)
        ImageDraw.Draw(img).line(points, fill=0, width=PEN, joint="curve")
        top3 = predict(model, ckpt["dataset"], ckpt["classes"], preprocess(img, ckpt["dataset"]))
        print(f"{name:<13} -> " + ", ".join(f"{c} {p:.1%}" for c, p in top3))


def check():
    """No window and no checkpoint: is tkinter installed, and does a drawing become a valid model input?"""
    import tkinter                                            # fails here if Python was installed without Tk
    from PIL import ImageTk  # noqa: F401  (the preview image needs it)

    import numpy as np
    from models import build_model

    print(f"tkinter {tkinter.TkVersion} available")
    img = Image.new("L", (SIZE, SIZE), 255)
    ImageDraw.Draw(img).line([(80, 60), (200, 60), (120, 230)], fill=0, width=PEN, joint="curve")
    for dataset, n in [("mnist", 10), ("letters", 26)]:
        img28 = preprocess(img, dataset)
        a = np.asarray(img28)
        ink = (a > 0).mean()
        assert img28.size == (28, 28) and a.max() == 255 and 0.05 < ink < 0.5, (img28.size, a.max(), ink)
        top3 = predict(build_model("cnn", n).eval(), dataset, list(range(n)), img28)   # untrained net
        assert len(top3) == 3 and all(0 <= p <= 1 for _, p in top3)
        print(f"{dataset:<8} drawing -> 28x28, {ink:.0%} ink pixels -> input accepted by a {n}-class CNN")
    print("check passed")


def main():
    p = argparse.ArgumentParser(description="Draw and classify handwriting")
    p.add_argument("--ckpt", default=None, help="default: checkpoints/mnist-cnn.pt")
    p.add_argument("--selftest", action="store_true", help="no window: predict two shapes drawn by code")
    p.add_argument("--check", action="store_true", help="no window, no checkpoint: test tkinter and preprocessing")
    a = p.parse_args()
    if a.check:
        check()
        return
    path = find_checkpoint(a.ckpt)
    model, ckpt = load_checkpoint(path)
    print(f"loaded {path.name}: {ckpt['arch'].upper()} trained on {ckpt['dataset']}")
    if a.selftest:
        selftest(model, ckpt)
        return
    import tkinter as tk

    root = tk.Tk()
    DrawApp(root, model, ckpt)
    root.mainloop()


if __name__ == "__main__":
    main()
