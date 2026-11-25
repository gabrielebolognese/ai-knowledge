---
term: Dropout
short: >-
  A regularisation layer that, during training only, sets a random fraction of its inputs to zero (and scales up the rest), so the network cannot rely on any single unit. It does nothing in evaluation mode.
level: intermediate
related: [weight]
sources:
  - id: srivastava2014
    title: "Dropout: A Simple Way to Prevent Neural Networks from Overfitting"
    author: Nitish Srivastava, Geoffrey Hinton, Alex Krizhevsky, Ilya Sutskever, Ruslan Salakhutdinov
    publisher: Journal of Machine Learning Research
    year: 2014
    url: https://jmlr.org/papers/v15/srivastava14a.html
    accessed: 2026-11-25
    type: paper
  - id: pt-dropout
    title: torch.nn.Dropout
    publisher: PyTorch
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.Dropout.html
    accessed: 2026-11-25
    type: docs
---
Because dropout behaves differently in training and evaluation, call `model.eval()` before measuring accuracy or making predictions, and `model.train()` before training again.
