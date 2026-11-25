---
term: "Backpropagation through time"
short: >-
  Backpropagation applied to a recurrent network unrolled over its time steps. Truncated BPTT cuts long sequences into chunks and stops gradients at the chunk borders.
level: advanced
aliases: ["BPTT", "truncated BPTT"]
related: [backpropagation, recurrent-neural-network, vanishing-gradient]
sources:
  - id: goodfellow2016-rnn
    title: "Deep Learning, chapter 10: Sequence Modeling"
    author: Ian Goodfellow, Yoshua Bengio, Aaron Courville
    publisher: MIT Press
    url: https://www.deeplearningbook.org/contents/rnn.html
    accessed: 2026-11-25
    type: book
  - id: wiki
    title: "Backpropagation through time"
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Backpropagation_through_time
    accessed: 2026-11-25
    type: wikipedia
---
The gradient reaching early steps is a product of one factor per step, which is why it tends to vanish or explode.
