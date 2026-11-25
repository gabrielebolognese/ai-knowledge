---
term: "Positional encoding"
short: >-
  Information about each token's position added to its embedding, because attention by itself ignores order. The original Transformer used fixed sinusoids; GPT models learn one position vector per slot.
level: advanced
aliases: ["position embedding", "positional embedding"]
related: [transformer, embedding, self-attention]
sources:
  - id: vaswani2017
    title: "Attention Is All You Need"
    author: Ashish Vaswani et al.
    publisher: arXiv
    url: https://arxiv.org/abs/1706.03762
    accessed: 2026-11-25
    type: paper
---
Learned position embeddings limit the context to the number of slots the model was trained with.
