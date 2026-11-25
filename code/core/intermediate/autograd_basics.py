"""PyTorch tensors and autograd: the backprop lesson's numbers, computed automatically.

Companion code for the lesson "PyTorch tensors and autograd".
Run:  python code/core/intermediate/autograd_basics.py
Needs PyTorch and NumPy (CPU is fine).
"""
import numpy as np
import torch

torch.manual_seed(0)

# 1. Tensors look like NumPy arrays and carry a shape, a dtype and a device.
t = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
print(t.shape, t.dtype, t.device)                   # torch.Size([2, 3]) torch.float32 cpu
print((t @ t.T).shape, t.sum(dim=0))                # matrix product and a column sum

a = np.arange(3.0)                                  # NumPy float64
s = torch.from_numpy(a)                             # shares memory with a, keeps float64
a[0] = 100.0
print(s, "| back to NumPy:", s.numpy().dtype)       # the change shows up in s

# 2. requires_grad + backward(): the 2-2-1 network from the backprop lesson.
x = torch.tensor([1.0, 2.0])
W1 = torch.tensor([[0.5, 0.5], [1.0, -1.0]], requires_grad=True)   # one row per hidden unit
b1 = torch.tensor([0.0, 0.5], requires_grad=True)
v = torch.tensor([2.0, 1.0], requires_grad=True)
c = torch.tensor(0.0, requires_grad=True)

h = torch.relu(W1 @ x + b1)                         # forward pass, recorded by autograd
y_hat = v @ h + c
loss = 0.5 * (y_hat - 2.0) ** 2
loss.backward()                                     # backward pass: fills .grad
print("loss", loss.item())
print("dL/dW1", W1.grad.tolist())
print("dL/db1", b1.grad.tolist(), "dL/dv", v.grad.tolist(), "dL/dc", c.grad.item())

# 3. Gradients ACCUMULATE: a second backward adds to .grad instead of replacing it.
w = torch.tensor(3.0, requires_grad=True)
for i in range(2):
    (w * w).backward()                              # d(w^2)/dw = 2w = 6
    print(f"after backward #{i + 1}: w.grad = {w.grad.item()}")
w.grad.zero_()                                      # what optimizer.zero_grad() does for you
print("after zero_(): w.grad =", w.grad.item())

# 4. No tracking when you only need numbers (evaluation, plotting, updates).
with torch.no_grad():
    pred = v @ torch.relu(W1 @ x + b1) + c
print("inside no_grad: requires_grad =", pred.requires_grad)
print("detach():       requires_grad =", y_hat.detach().requires_grad)
