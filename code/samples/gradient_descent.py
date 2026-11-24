"""Gradient descent on f(w) = (w - 3)^2, in plain Python.

Companion code for the lesson "Gradient descent".
Run:  python code/samples/gradient_descent.py
"""


def f(w):
    return (w - 3) ** 2


def grad_f(w):
    # Derivative of (w - 3)^2 is 2 * (w - 3)
    return 2 * (w - 3)


def gradient_descent(w0, lr, steps):
    w = w0
    history = [w]
    for _ in range(steps):
        w = w - lr * grad_f(w)  # step against the slope
        history.append(w)
    return history


if __name__ == "__main__":
    for lr in (0.1, 0.5, 1.1):
        path = gradient_descent(w0=0.0, lr=lr, steps=5)
        shown = ", ".join(f"{w:.3f}" for w in path)
        print(f"learning rate {lr}: w = {shown}  (loss at end {f(path[-1]):.4f})")
