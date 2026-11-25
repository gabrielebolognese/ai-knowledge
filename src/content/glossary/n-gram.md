---
term: "N-gram model"
short: >-
  A language model that predicts the next symbol from the previous n−1 symbols using counts from a corpus. A bigram model (n = 2) looks only at the one previous symbol.
level: intermediate
aliases: [bigram model, trigram model, n-gram language model]
related: [language-model, perplexity]
sources:
  - id: jm-ch3
    title: "Speech and Language Processing, Chapter 3: N-gram Language Models"
    author: Daniel Jurafsky, James H. Martin
    publisher: Stanford University
    url: https://web.stanford.edu/~jurafsky/slp3/3.pdf
    accessed: 2026-11-25
    type: book
  - id: wiki
    title: "Word n-gram language model"
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Word_n-gram_language_model
    accessed: 2026-11-25
    type: wikipedia
---
N-gram tables grow as $V^n$ and give zero probability to any sequence never seen in training, which is why they need smoothing and why neural language models, which share information between similar contexts, replaced them.
