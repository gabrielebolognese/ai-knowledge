---
term: Exploding gradient
short: >-
  A training failure in which gradients grow very large as they are multiplied back through many layers or time steps, causing huge weight updates and often a loss of NaN.
level: intermediate
aliases: [exploding gradients]
related: [gradient, gradient-clipping, weight-initialization]
sources:
  - id: wiki-vanishing
    title: Vanishing gradient problem (exploding gradients)
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Vanishing_gradient_problem
    accessed: 2026-11-25
    type: wikipedia
  - id: pascanu2013
    title: On the difficulty of training recurrent neural networks
    author: Razvan Pascanu, Tomas Mikolov, Yoshua Bengio
    publisher: Proceedings of ICML 2013 (PMLR 28)
    year: 2013
    url: https://proceedings.mlr.press/v28/pascanu13.html
    accessed: 2026-11-25
    type: paper
---
Fixes include a lower learning rate, careful weight initialization, normalization layers and gradient clipping.
