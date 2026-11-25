"""Softmax regression trained from scratch with NumPy (the beginner capstone).

Companion code for the lesson "Capstone: train a classifier from scratch with NumPy".
Run:  python code/core/beginner/softmax_regression.py
Needs NumPy; matplotlib is optional (it only draws the two plots).
"""
import numpy as np

rng = np.random.default_rng(0)                  # fixed seed: same numbers every run

# 1. Data: 3 clouds of 2-D points, 100 per class, centred at three corners.
centres = np.array([[0.0, 2.0], [-2.0, -1.0], [2.0, -1.0]])
X = np.concatenate([c + rng.normal(0.0, 0.9, size=(100, 2)) for c in centres])
y = np.repeat([0, 1, 2], 100)                   # labels 0, 1, 2

order = rng.permutation(len(X))                 # shuffle, then hold out 20% for testing
X, y = X[order], y[order]
X_train, y_train, X_test, y_test = X[:240], y[:240], X[240:], y[240:]

# 2. Model: one weight per (feature, class) and one bias per class.
W = np.zeros((2, 3))
b = np.zeros(3)


def softmax(z):
    z = z - z.max(axis=1, keepdims=True)        # subtract the row max: same result, no overflow
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def accuracy(X, y):
    return np.mean(np.argmax(X @ W + b, axis=1) == y)


# 3. Training loop: forward, loss, gradient, update.
lr, epochs = 0.1, 200
Y = np.eye(3)[y_train]                          # one-hot targets, shape (240, 3)
losses = []
for epoch in range(epochs + 1):
    P = softmax(X_train @ W + b)                # forward pass: probabilities, shape (240, 3)
    loss = -np.mean(np.log(P[np.arange(len(y_train)), y_train]))   # cross-entropy
    losses.append(loss)
    dZ = (P - Y) / len(X_train)                 # gradient of the loss w.r.t. the scores
    dW = X_train.T @ dZ                         # chain rule: scores = X @ W + b
    db = dZ.sum(axis=0)
    W -= lr * dW                                # gradient-descent update
    b -= lr * db
    if epoch % 50 == 0:
        print(f"epoch {epoch:3d}  loss {loss:.4f}")

# 4. Evaluate on data the model never trained on.
print(f"train accuracy {accuracy(X_train, y_train):.3f}")
print(f"test accuracy  {accuracy(X_test, y_test):.3f}")

# 5. Optional plots: the loss curve and the decision boundary.
try:
    import matplotlib
    matplotlib.use("Agg")                       # draw to files; no window needed
    import matplotlib.pyplot as plt
except ImportError:
    print("matplotlib not installed: skipping the plots")
else:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.plot(losses)
    ax1.set(xlabel="epoch", ylabel="training loss", title="Loss curve")
    gx, gy = np.meshgrid(np.linspace(-5, 5, 300), np.linspace(-5, 5, 300))
    grid = np.c_[gx.ravel(), gy.ravel()]
    ax2.contourf(gx, gy, np.argmax(grid @ W + b, axis=1).reshape(gx.shape), alpha=0.25)
    ax2.scatter(X[:, 0], X[:, 1], c=y, s=10)
    ax2.set(title="Decision boundary")
    fig.savefig("softmax_regression.png", dpi=120, bbox_inches="tight")
    print("saved softmax_regression.png")
