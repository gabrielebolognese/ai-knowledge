---
term: "Sampling temperature"
short: >-
  A number T that divides a model's scores before the softmax when generating. T below 1 makes likely tokens even likelier (safer, more repetitive); T above 1 flattens the choice (more varied, more mistakes).
level: intermediate
aliases: [temperature, top-k sampling, top-k]
related: [softmax, language-model]
sources:
  - id: hf-generate
    title: "How to generate text: using different decoding methods for language generation with Transformers"
    author: Patrick von Platen
    publisher: Hugging Face
    year: 2020
    url: https://huggingface.co/blog/how-to-generate
    accessed: 2026-11-25
    type: article
  - id: fan2018
    title: "Hierarchical Neural Story Generation"
    author: Angela Fan, Mike Lewis, Yann Dauphin
    publisher: arXiv
    year: 2018
    url: https://arxiv.org/abs/1805.04833
    accessed: 2026-11-25
    type: paper
---
Temperature is often combined with top-k sampling, which keeps only the k most likely tokens before sampling (Fan et al. 2018). T = 0 is treated as greedy decoding: always pick the most likely token.
