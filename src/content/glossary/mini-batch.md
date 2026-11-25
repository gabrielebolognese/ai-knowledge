---
term: Mini-batch
short: >-
  A small random group of training examples (often 32 to 512) processed together in one training step. The gradient computed on a mini-batch is a cheap, slightly noisy estimate of the gradient over the whole data set.
level: intermediate
aliases: [batch, batch size]
related: [gradient-descent, epoch, learning-rate]
sources:
  - id: cs231n-opt
    title: "Optimization: Stochastic Gradient Descent"
    publisher: Stanford CS231n course notes
    url: https://cs231n.github.io/optimization-1/
    accessed: 2026-11-25
    type: course
  - id: pt-data
    title: torch.utils.data
    publisher: PyTorch documentation
    url: https://docs.pytorch.org/docs/stable/data.html
    accessed: 2026-11-25
    type: docs
---
The number of examples in a mini-batch is the batch size. One full pass over the training data, made of many mini-batch steps, is an epoch. In PyTorch a `DataLoader` deals out shuffled mini-batches.
