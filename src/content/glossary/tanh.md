---
term: Tanh
short: >-
  The hyperbolic tangent, an S-shaped activation function that squeezes any number into the range −1 to 1. It is zero-centred, and its slope is at most 1 (at zero).
level: beginner
aliases: [hyperbolic tangent]
related: [activation-function, sigmoid, relu]
sources:
  - id: wikipedia
    title: Hyperbolic functions
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Hyperbolic_functions
    accessed: 2026-11-25
  - id: cs231n
    title: "Neural Networks Part 1: Setting up the Architecture"
    publisher: Stanford CS231n course notes
    url: https://cs231n.github.io/neural-networks-1/
    accessed: 2026-11-25
---
Its derivative is $1 - \tanh^2(z)$. Like the sigmoid it saturates for large positive or negative inputs, where the slope is close to 0.
