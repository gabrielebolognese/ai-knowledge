---
term: Backpropagation
short: >-
  The algorithm that computes the gradient of the loss with respect to every weight in a network, by applying the chain rule backwards from the loss through each layer. An optimizer then uses those gradients to update the weights.
level: intermediate
aliases: [backprop, backward pass]
related: [gradient, computational-graph, automatic-differentiation, gradient-descent]
sources:
  - id: rumelhart1986
    title: Learning representations by back-propagating errors
    author: David Rumelhart, Geoffrey Hinton, Ronald Williams
    publisher: Nature 323
    year: 1986
    url: https://doi.org/10.1038/323533a0
    accessed: 2026-11-25
    type: paper
  - id: wikipedia
    title: Backpropagation
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Backpropagation
    accessed: 2026-11-25
    type: wikipedia
---
Backpropagation only *computes* gradients; it does not change any weights by itself. It reuses the intermediate results of the forward pass, so the backward pass costs about as much as the forward pass instead of one pass per parameter. It is a special case of reverse-mode automatic differentiation.
