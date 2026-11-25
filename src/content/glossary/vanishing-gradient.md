---
term: Vanishing gradient
short: >-
  A training problem in deep networks where the gradients reaching the early layers become tiny, because many small slopes are multiplied together on the way back, so those layers barely learn.
level: beginner
aliases: [vanishing gradient problem]
related: [sigmoid, relu, gradient]
sources:
  - id: wikipedia
    title: Vanishing gradient problem
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Vanishing_gradient_problem
    accessed: 2026-11-25
  - id: d2l
    title: "Dive into Deep Learning, 5.4 Numerical Stability and Initialization"
    author: Aston Zhang, Zachary Lipton, Mu Li, Alexander Smola
    publisher: d2l.ai
    url: https://d2l.ai/chapter_multilayer-perceptrons/numerical-stability-and-init.html
    accessed: 2026-11-25
---
The sigmoid's slope is at most 0.25, so ten sigmoid layers can shrink a gradient by up to $0.25^{10} \approx 10^{-6}$. ReLU, careful initialisation and normalisation layers reduce the problem.
