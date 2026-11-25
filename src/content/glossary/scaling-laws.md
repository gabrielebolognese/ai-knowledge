---
term: "Scaling laws"
short: >-
  Empirical power laws relating a language model's loss to its parameter count, data size and training compute. Kaplan et al. (2020) also popularised the estimate of about 6 x parameters x tokens training FLOPs.
level: advanced
aliases: ["neural scaling laws"]
related: [language-model, transformer]
sources:
  - id: kaplan2020
    title: "Scaling Laws for Neural Language Models"
    author: Jared Kaplan et al.
    publisher: arXiv
    url: https://arxiv.org/abs/2001.08361
    accessed: 2026-11-25
    type: paper
  - id: wiki
    title: "Neural scaling law"
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Neural_scaling_law
    accessed: 2026-11-25
    type: wikipedia
---
Later work, such as the 2022 Chinchilla study by Hoffmann et al., revised how best to split a compute budget between parameters and data.
