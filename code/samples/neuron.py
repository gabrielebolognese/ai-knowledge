"""One artificial neuron, computed by hand in plain Python.

Companion code for the lesson "The artificial neuron".
Run:  python code/samples/neuron.py
"""
import math


def weighted_sum(inputs, weights, bias):
    """z = w1*x1 + w2*x2 + ... + b  (a dot product plus a bias)."""
    return sum(w * x for w, x in zip(weights, inputs)) + bias


def relu(z):
    """ReLU: keep positive values, replace negative ones with 0."""
    return max(0.0, z)


def sigmoid(z):
    """Sigmoid: squash any number into the range (0, 1)."""
    return 1.0 / (1.0 + math.exp(-z))


def step(z):
    """Perceptron step: 1 if z > 0, else 0."""
    return 1 if z > 0 else 0


if __name__ == "__main__":
    x = [1.0, 2.0]   # inputs
    w = [0.5, -1.0]  # weights
    b = 0.5          # bias

    z = weighted_sum(x, w, b)
    print(f"weighted sum z = {z}")                # -1.0
    print(f"ReLU(z)        = {relu(z)}")          # 0.0
    print(f"sigmoid(z)     = {sigmoid(z):.3f}")   # 0.269

    # A perceptron that computes logical AND: w = [1, 1], b = -1.5
    for a in (0, 1):
        for c in (0, 1):
            print(f"AND({a}, {c}) = {step(weighted_sum([a, c], [1, 1], -1.5))}")
