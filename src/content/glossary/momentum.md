---
term: Momentum
short: >-
  An optimizer technique that keeps a running "velocity" of past gradients and steps along it, so updates speed up in consistent directions and zig-zag less. A coefficient of 0.9 is typical.
level: intermediate
aliases: [SGD with momentum, heavy-ball method]
related: [gradient-descent, learning-rate, adam-optimizer]
sources:
  - id: sutskever2013
    title: On the importance of initialization and momentum in deep learning
    author: Ilya Sutskever, James Martens, George Dahl, Geoffrey Hinton
    publisher: Proceedings of ICML 2013 (PMLR 28)
    year: 2013
    url: https://proceedings.mlr.press/v28/sutskever13.html
    accessed: 2026-11-25
    type: paper
  - id: d2l-momentum
    title: "Dive into Deep Learning, 12.6 Momentum"
    publisher: d2l.ai
    url: https://d2l.ai/chapter_optimization/momentum.html
    accessed: 2026-11-25
    type: book
---
In PyTorch, `torch.optim.SGD(params, lr=0.1, momentum=0.9)` updates a velocity $v \leftarrow \beta v + g$ and then the weights $w \leftarrow w - \eta v$.
