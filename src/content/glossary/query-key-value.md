---
term: "Query, key and value"
short: >-
  The three learned projections of each token in attention. A query is matched against every key with a dot product; the resulting weights mix the values into the output.
level: advanced
aliases: ["QKV", "queries, keys and values"]
related: [self-attention, multi-head-attention, dot-product]
sources:
  - id: vaswani2017
    title: "Attention Is All You Need"
    author: Ashish Vaswani et al.
    publisher: arXiv
    url: https://arxiv.org/abs/1706.03762
    accessed: 2026-11-25
    type: paper
  - id: d2l
    title: "Dive into Deep Learning, 11 Attention Mechanisms and Transformers"
    publisher: d2l.ai
    url: https://d2l.ai/chapter_attention-mechanisms-and-transformers/index.html
    accessed: 2026-11-25
    type: book
---
Each is computed by multiplying the token vector by its own learned matrix: $q = xW_Q$, $k = xW_K$, $v = xW_V$.
