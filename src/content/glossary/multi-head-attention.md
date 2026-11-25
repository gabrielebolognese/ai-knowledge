---
term: "Multi-head attention"
short: >-
  Several attention operations run in parallel on separate learned projections of size d/h; their outputs are concatenated and mixed by one more matrix. Heads can specialise in different patterns.
level: advanced
aliases: ["attention heads"]
related: [self-attention, query-key-value, transformer]
sources:
  - id: vaswani2017
    title: "Attention Is All You Need"
    author: Ashish Vaswani et al.
    publisher: arXiv
    url: https://arxiv.org/abs/1706.03762
    accessed: 2026-11-25
    type: paper
  - id: pt-mha
    title: "torch.nn.MultiheadAttention"
    publisher: PyTorch documentation
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html
    accessed: 2026-11-25
    type: docs
---
The base Transformer of 2017 used 8 heads of size 64 on 512-number vectors.
