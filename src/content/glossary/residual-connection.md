---
term: Residual connection
short: >-
  A shortcut that adds a block's input to its output, y = F(x) + x, so the block only has to learn a correction. It keeps gradients flowing through very deep networks and is used in ResNets and every Transformer block.
level: advanced
aliases: [skip connection, shortcut connection, residual block, ResNet]
related: [vanishing-gradient, batch-normalization, transformer]
sources:
  - id: he2015
    title: Deep Residual Learning for Image Recognition
    publisher: arXiv
    url: https://arxiv.org/abs/1512.03385
    accessed: 2026-11-25
    type: paper
  - id: wikipedia
    title: Residual neural network
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Residual_neural_network
    accessed: 2026-11-25
    type: wikipedia
---
The derivative of $y = F(x) + x$ with respect to $x$ is $\partial F/\partial x + 1$: the $+1$ gives the gradient a path that skips the block entirely.
