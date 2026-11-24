---
term: "Transformer"
short: >-
  A neural-network architecture built from self-attention and small feed-forward layers instead of recurrence. Introduced in 2017, it underlies GPT and most modern language models.
level: advanced
aliases: [transformer model]
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
  - id: wiki
    title: "Transformer (deep learning architecture)"
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Transformer_(deep_learning_architecture)
    accessed: 2026-11-24
    type: wikipedia
---
A Transformer block mixes information between positions with multi-head self-attention, then processes each position separately with a two-layer MLP. Residual connections and layer normalisation wrap both parts. GPT-style models keep only the decoder half and add a causal mask.
