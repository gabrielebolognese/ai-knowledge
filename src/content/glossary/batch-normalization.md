---
term: Batch normalization
short: >-
  A layer that re-centres and re-scales each channel using the mean and variance of the current mini-batch, then applies a learned scale and shift. It usually makes training faster and more stable; at evaluation time it uses running averages instead.
level: intermediate
aliases: [batch norm, BatchNorm]
related: [dropout]
sources:
  - id: ioffe2015
    title: "Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift"
    author: Sergey Ioffe, Christian Szegedy
    publisher: arXiv
    year: 2015
    url: https://arxiv.org/abs/1502.03167
    accessed: 2026-11-25
    type: paper
  - id: pt-bn2d
    title: torch.nn.BatchNorm2d
    publisher: PyTorch
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.BatchNorm2d.html
    accessed: 2026-11-25
    type: docs
---
Like dropout, batch normalization behaves differently in `model.train()` and `model.eval()` mode, so always switch to evaluation mode before measuring accuracy or predicting.
