---
term: "Perplexity"
short: >-
  The exponential of a language model's average cross-entropy loss. A perplexity of 8 means the model is, on average, as unsure as if it were choosing uniformly among 8 symbols; lower is better.
level: intermediate
aliases: [PPL]
related: [cross-entropy, language-model]
sources:
  - id: wiki
    title: "Perplexity"
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Perplexity
    accessed: 2026-11-25
    type: wikipedia
  - id: jm-ch3
    title: "Speech and Language Processing, Chapter 3: N-gram Language Models"
    author: Daniel Jurafsky, James H. Martin
    publisher: Stanford University
    url: https://web.stanford.edu/~jurafsky/slp3/3.pdf
    accessed: 2026-11-25
    type: book
---
With the loss $L$ measured in nats (natural logarithm), perplexity is $e^{L}$. A model that guesses uniformly among $V$ symbols has loss $\ln V$ and perplexity exactly $V$, which makes perplexity easy to compare with the vocabulary size.
