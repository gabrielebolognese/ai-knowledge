---
term: Learning-rate schedule
short: >-
  A rule that changes the learning rate during training, for example a short warmup from a small value, then a gradual decay (step, cosine or linear) towards zero.
level: intermediate
aliases: [LR schedule, learning-rate scheduler, warmup, cosine decay]
related: [learning-rate, gradient-descent]
sources:
  - id: pt-optim
    title: "torch.optim: How to adjust learning rate"
    publisher: PyTorch
    url: https://docs.pytorch.org/docs/stable/optim.html
    accessed: 2026-11-25
    type: docs
  - id: smith2015
    title: Cyclical Learning Rates for Training Neural Networks
    author: Leslie N. Smith
    publisher: arXiv
    year: 2015
    url: https://arxiv.org/abs/1506.01186
    accessed: 2026-11-25
    type: paper
---
In PyTorch a scheduler such as `torch.optim.lr_scheduler.CosineAnnealingLR` wraps the optimizer, and `scheduler.step()` is called after `optimizer.step()`, usually once per epoch or once per batch.
