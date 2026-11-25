---
term: Finite difference
short: >-
  An estimate of a derivative made by nudging the input by a small step h and computing rise over run, (f(x + h) − f(x)) / h. Used to check hand-written gradients.
level: beginner
aliases: [numerical derivative, numerical gradient]
related: [derivative, gradient]
sources:
  - id: wikipedia
    title: Finite difference
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Finite_difference
    accessed: 2026-11-25
    type: wikipedia
  - id: cs231n-optim1
    title: "Optimization: Stochastic Gradient Descent"
    publisher: Stanford CS231n course notes
    url: https://cs231n.github.io/optimization-1/
    accessed: 2026-11-25
    type: course
---
For $f(x) = x^2$ at $x = 3$ with $h = 0.001$: $(9.006001 - 9)/0.001 = 6.001$, close to the exact slope 6. The centred version $(f(x+h) - f(x-h))/(2h)$ is usually more accurate.
