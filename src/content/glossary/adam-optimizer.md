---
term: Adam
short: >-
  An adaptive optimizer that combines momentum (a running average of gradients) with per-parameter step sizes (a running average of squared gradients), plus a bias correction for the first steps. A common default for training neural networks.
level: intermediate
aliases: [Adam optimizer, AdamW]
related: [momentum, learning-rate, gradient-descent]
sources:
  - id: kingma2014
    title: "Adam: A Method for Stochastic Optimization"
    author: Diederik P. Kingma, Jimmy Ba
    publisher: arXiv
    year: 2014
    url: https://arxiv.org/abs/1412.6980
    accessed: 2026-11-25
    type: paper
  - id: pt-adam
    title: torch.optim.Adam
    publisher: PyTorch
    url: https://docs.pytorch.org/docs/stable/generated/torch.optim.Adam.html
    accessed: 2026-11-25
    type: docs
---
The default settings are $\beta_1 = 0.9$, $\beta_2 = 0.999$ and $\epsilon = 10^{-8}$. AdamW is a variant that applies weight decay directly to the weights instead of adding it to the gradient.
