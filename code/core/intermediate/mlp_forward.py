"""The forward pass of a multilayer perceptron, written as matrix operations.

Companion code for the lesson "Multilayer perceptrons and the forward pass".
Run:  python code/core/intermediate/mlp_forward.py
Needs only NumPy.
"""
import numpy as np

rng = np.random.default_rng(0)                   # fixed seed: same numbers every run


def relu(z):
    return np.maximum(0.0, z)


# 1. A 784 -> 128 -> 10 network for 28x28 images (MNIST-sized), batch of 64 images.
X = rng.random((64, 784))                        # 64 fake "images", one row each
W1 = rng.normal(0, np.sqrt(2 / 784), (784, 128)) # layer 1: 784 inputs -> 128 units
b1 = np.zeros(128)
W2 = rng.normal(0, np.sqrt(2 / 128), (128, 10))  # layer 2: 128 units -> 10 scores
b2 = np.zeros(10)

H = relu(X @ W1 + b1)                            # hidden layer: matmul + bias + activation
logits = H @ W2 + b2                             # output layer: no activation (logits)
print("X", X.shape, "-> H", H.shape, "-> logits", logits.shape)

n_params = W1.size + b1.size + W2.size + b2.size
print(f"parameters: {W1.size + b1.size:,} + {W2.size + b2.size:,} = {n_params:,}")

# 2. XOR with two ReLU hidden units (hand-set weights from Goodfellow et al., section 6.1).
W = np.array([[1.0, 1.0],
              [1.0, 1.0]])                       # both hidden units add the two inputs
c = np.array([0.0, -1.0])                        # ...but the second one is shifted down by 1
w = np.array([1.0, -2.0])                        # output = h1 - 2*h2
b = 0.0
for x in [(0, 0), (0, 1), (1, 0), (1, 1)]:
    h = relu(np.array(x, dtype=float) @ W + c)
    print(f"XOR{x}: hidden {h} -> output {h @ w + b:.0f}")

# 3. Without the activation, two layers collapse into one: W2(W1 x) = (W2 W1) x.
A, B, v = rng.normal(size=(3, 4)), rng.normal(size=(4, 3)), rng.normal(size=3)
print("two linear layers == one linear layer:", np.allclose(A @ (B @ v), (A @ B) @ v))
