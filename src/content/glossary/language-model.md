---
term: "Language model"
short: >-
  A model that assigns probabilities to sequences of tokens, usually by predicting the next token from the ones before it. Sampling from it one token at a time generates text or code.
level: intermediate
aliases: [LM, autoregressive model]
related: [transformer, tokenization]
sources:
  - id: wiki
    title: "Language model"
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Language_model
    accessed: 2026-11-24
    type: wikipedia
  - id: radford2019
    title: "Language Models are Unsupervised Multitask Learners"
    author: Alec Radford et al.
    publisher: OpenAI
    year: 2019
    url: https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
    accessed: 2026-11-24
    type: paper
---
A language model is trained with cross-entropy on the next token, so its loss can be read as the average surprise per token in nats (or bits). GPT models are language models built from Transformer blocks.
