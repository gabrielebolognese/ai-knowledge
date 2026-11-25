---
term: "Nucleus sampling"
short: >-
  A text-generation rule, also called top-p sampling: keep the smallest set of most likely tokens whose probabilities add up to at least p, renormalise them, and sample from that set.
level: advanced
aliases: [top-p sampling, top-p]
related: [sampling-temperature, greedy-decoding, language-model]
sources:
  - id: holtzman2019
    title: The Curious Case of Neural Text Degeneration
    author: Ari Holtzman, Jan Buys, Li Du, Maxwell Forbes, Yejin Choi
    publisher: arXiv
    year: 2019
    url: https://arxiv.org/abs/1904.09751
    accessed: 2026-11-25
---
Unlike top-k, the candidate set adapts: it shrinks to one or two tokens when the model is confident and grows when it is unsure. It was introduced by Holtzman et al. (2019) to cut off the unreliable tail of the distribution.
