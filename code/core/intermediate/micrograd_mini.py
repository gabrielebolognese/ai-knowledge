"""A tiny automatic-differentiation engine in about 60 lines (in the spirit of micrograd).

Companion code for the lesson "Backpropagation, step by step".
Run:  python code/core/intermediate/micrograd_mini.py
Pure Python, no libraries. Based on the idea of Andrej Karpathy's micrograd (MIT licence).
"""


class Value:
    """One number in a computation, plus the gradient of the final output with respect to it."""

    def __init__(self, data, parents=(), op=""):
        self.data = data
        self.grad = 0.0                        # d(output)/d(this value), filled by backward()
        self._parents = parents                # the Values this one was computed from
        self._backward = lambda: None          # pushes self.grad to the parents
        self.op = op

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), "+")

        def _backward():                       # add: pass the gradient through unchanged
            self.grad += out.grad
            other.grad += out.grad
        out._backward = _backward
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")

        def _backward():                       # multiply: each input gets the OTHER input
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        out._backward = _backward
        return out

    def relu(self):
        out = Value(max(0.0, self.data), (self,), "relu")

        def _backward():                       # relu: pass the gradient only if the input was > 0
            self.grad += (1.0 if self.data > 0 else 0.0) * out.grad
        out._backward = _backward
        return out

    def __neg__(self): return self * -1
    def __sub__(self, other): return self + (-other)
    __radd__ = __add__
    __rmul__ = __mul__

    def backward(self):
        order, seen = [], set()                # topological order: parents before children

        def visit(v):
            if v not in seen:
                seen.add(v)
                for p in v._parents:
                    visit(p)
                order.append(v)
        visit(self)
        self.grad = 1.0                        # d(output)/d(output) = 1
        for v in reversed(order):              # walk from the output back to the inputs
            v._backward()

    def __repr__(self):
        return f"Value(data={self.data:g}, grad={self.grad:g})"


def network(p, x=(1.0, 2.0), y=2.0):
    """The lesson's 2-2-1 network: two ReLU hidden units, one linear output, L = 1/2 (y_hat - y)^2."""
    w11, w12, b1, w21, w22, b2, v1, v2, c = p
    h1 = (w11 * x[0] + w12 * x[1] + b1).relu()
    h2 = (w21 * x[0] + w22 * x[1] + b2).relu()
    y_hat = v1 * h1 + v2 * h2 + c
    return 0.5 * (y_hat - y) * (y_hat - y)


if __name__ == "__main__":
    # Example 1: L = a*b + c
    a, b, c = Value(2.0), Value(-3.0), Value(10.0)
    L = a * b + c
    L.backward()
    print("L = a*b + c =", L.data, "| dL/da =", a.grad, "dL/db =", b.grad, "dL/dc =", c.grad)

    # Example 2: a value used twice (a fork) collects gradient from both uses
    a = Value(3.0)
    d = a + a
    d.backward()
    print("d = a + a: dd/da =", a.grad)

    # Example 3: the 2-layer network from the lesson
    names = ["w11", "w12", "b1", "w21", "w22", "b2", "v1", "v2", "c"]
    start = [0.5, 0.5, 0.0, 1.0, -1.0, 0.5, 2.0, 1.0, 0.0]
    params = [Value(v) for v in start]
    loss = network(params)
    loss.backward()
    print(f"loss = {loss.data:g}")
    print("gradients:", {n: p.grad for n, p in zip(names, params)})

    # Numerical gradient check: (L(w + h) - L(w - h)) / 2h for every parameter
    h = 1e-6
    for i, n in enumerate(names):
        up, down = start.copy(), start.copy()
        up[i] += h
        down[i] -= h
        numeric = (network([Value(v) for v in up]).data - network([Value(v) for v in down]).data) / (2 * h)
        assert abs(numeric - params[i].grad) < 1e-6, (n, numeric, params[i].grad)
    print("numerical gradient check: all 9 gradients match")

    # One gradient-descent step with learning rate 0.05, then the new loss
    lr = 0.05
    new = [p.data - lr * p.grad for p in params]
    print("after one step:", {n: round(v, 4) for n, v in zip(names, new)})
    print(f"new loss = {network([Value(v) for v in new]).data:.4f}")
