---
term: Layer normalization
short: >-
  A layer that rescales each example's features to mean 0 and standard deviation 1, then applies a learned scale and shift. Unlike batch normalization it does not depend on the other examples in the batch, which is why Transformers use it.
level: intermediate
aliases: [LayerNorm]
related: [batch-normalization, transformer]
sources:
  - id: ba2016
    title: Layer Normalization
    author: Jimmy Lei Ba, Jamie Ryan Kiros, Geoffrey E. Hinton
    publisher: arXiv
    year: 2016
    url: https://arxiv.org/abs/1607.06450
    accessed: 2026-11-25
    type: paper
  - id: pt-layernorm
    title: torch.nn.LayerNorm
    publisher: PyTorch
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html
    accessed: 2026-11-25
    type: docs
---
Because it uses no batch statistics, layer normalization computes the same thing in training and in evaluation mode.
