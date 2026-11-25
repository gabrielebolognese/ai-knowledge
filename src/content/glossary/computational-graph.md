---
term: Computational graph
short: >-
  A diagram of a calculation in which each node is a simple operation (add, multiply, ReLU) and each edge carries a value from one operation to the next. Backpropagation walks this graph backwards to compute gradients.
level: intermediate
aliases: [compute graph]
related: [backpropagation, automatic-differentiation]
sources:
  - id: cs231n-backprop
    title: "Backpropagation, Intuitions"
    publisher: Stanford CS231n course notes
    url: https://cs231n.github.io/optimization-2/
    accessed: 2026-11-25
    type: course
  - id: d2l-backprop
    title: "Forward Propagation, Backward Propagation, and Computational Graphs"
    publisher: d2l.ai
    url: https://d2l.ai/chapter_multilayer-perceptrons/backprop.html
    accessed: 2026-11-25
    type: book
---
PyTorch builds the graph on the fly while your code runs (a "define-by-run" graph) and frees it after `backward()`, which is why the same Python code can build a different graph on every call.
