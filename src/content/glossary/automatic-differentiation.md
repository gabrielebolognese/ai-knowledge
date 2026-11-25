---
term: Automatic differentiation
short: >-
  A technique by which software computes exact derivatives of a program by recording its elementary operations and applying the chain rule to them. Reverse mode, which works backwards from one output, is what deep-learning libraries call autograd.
level: intermediate
aliases: [autodiff, autograd, AD]
related: [backpropagation, computational-graph, gradient, pytorch]
sources:
  - id: baydin2018
    title: "Automatic differentiation in machine learning: a survey"
    author: Atilim Gunes Baydin, Barak Pearlmutter, Alexey Radul, Jeffrey Siskind
    publisher: Journal of Machine Learning Research 18
    year: 2018
    url: https://arxiv.org/abs/1502.05767
    accessed: 2026-11-25
    type: paper
  - id: pt-autograd
    title: Automatic Differentiation with torch.autograd
    publisher: PyTorch tutorials
    url: https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html
    accessed: 2026-11-25
    type: docs
---
It is neither symbolic differentiation (manipulating formulas) nor numerical differentiation (finite differences): it gives exact values at the current inputs, at a cost of a small constant times the cost of the original computation.
