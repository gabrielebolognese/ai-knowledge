---
term: "Greedy decoding"
short: >-
  Generating text by always picking the single most probable next token. It is deterministic and simple, but tends to produce bland, repetitive text that can get stuck in loops.
level: advanced
aliases: [greedy search, argmax decoding]
related: [sampling-temperature, nucleus-sampling, language-model]
sources:
  - id: holtzman2019
    title: The Curious Case of Neural Text Degeneration
    author: Ari Holtzman, Jan Buys, Li Du, Maxwell Forbes, Yejin Choi
    publisher: arXiv
    year: 2019
    url: https://arxiv.org/abs/1904.09751
    accessed: 2026-11-25
  - id: hf-generate
    title: "How to generate text: using different decoding methods for language generation with Transformers"
    author: Patrick von Platen
    publisher: Hugging Face
    year: 2020
    url: https://huggingface.co/blog/how-to-generate
    accessed: 2026-11-25
---
Greedy decoding is the limit of temperature sampling as the temperature goes to 0. Holtzman et al. (2019) found that the probability of repeating a phrase rises with each repetition, which is why always taking the maximum loops.
