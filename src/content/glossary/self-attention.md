---
term: "Self-attention"
short: >-
  An operation in which every position of a sequence builds its output as a weighted average of all positions' value vectors, with weights from how well its query matches their keys.
level: advanced
aliases: [scaled dot-product attention, attention]
related: [transformer, causal-mask, dot-product]
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
    title: "Attention (machine learning)"
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Attention_(machine_learning)
    accessed: 2026-11-24
    type: wikipedia
---
The scores are dot products of queries and keys, divided by the square root of the key size and turned into weights with softmax: softmax(QKᵀ/√d)V. Several attention "heads" run in parallel on slices of the vectors.
