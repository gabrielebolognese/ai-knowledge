---
term: "Hidden state"
short: >-
  The vector a recurrent network carries from one time step to the next: its running memory of the sequence so far. In PyTorch it is the h (and, for LSTMs, c) returned with the outputs.
level: advanced
aliases: ["memory state"]
related: [recurrent-neural-network, long-short-term-memory]
sources:
  - id: goodfellow2016-rnn
    title: "Deep Learning, chapter 10: Sequence Modeling"
    author: Ian Goodfellow, Yoshua Bengio, Aaron Courville
    publisher: MIT Press
    url: https://www.deeplearningbook.org/contents/rnn.html
    accessed: 2026-11-25
    type: book
---
A vanilla RNN computes it as $h_t = \tanh(W_{xh} x_t + W_{hh} h_{t-1} + b)$.
