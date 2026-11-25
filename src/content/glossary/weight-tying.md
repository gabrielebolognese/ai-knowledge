---
term: "Weight tying"
short: >-
  Sharing one matrix between the input token embeddings and the output layer of a language model. It saves vocabulary-size times width parameters and usually improves results.
level: advanced
aliases: ["tied embeddings"]
related: [embedding, transformer, language-model]
sources:
  - id: press2016
    title: "Using the Output Embedding to Improve Language Models"
    author: Ofir Press, Lior Wolf
    publisher: arXiv
    url: https://arxiv.org/abs/1608.05859
    accessed: 2026-11-25
    type: paper
---
In PyTorch it is one line: `lm_head.weight = wte.weight`.
