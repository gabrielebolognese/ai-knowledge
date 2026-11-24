---
term: "Causal mask"
short: >-
  A mask that stops each position in a sequence from attending to later positions, so a language model can only use the past when predicting the next token.
level: advanced
aliases: [attention mask, look-ahead mask]
related: [self-attention, language-model]
sources:
  - id: vaswani2017
    title: "Attention Is All You Need"
    author: Ashish Vaswani et al.
    publisher: arXiv
    year: 2017
    url: https://arxiv.org/abs/1706.03762
    accessed: 2026-11-24
    type: paper
  - id: pt-sdpa
    title: "torch.nn.functional.scaled_dot_product_attention"
    publisher: PyTorch documentation
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html
    accessed: 2026-11-24
    type: docs
---
In practice the attention scores above the diagonal of the T×T score matrix are set to minus infinity before the softmax, which makes their weights exactly zero. In PyTorch the same effect comes from `is_causal=True`.
