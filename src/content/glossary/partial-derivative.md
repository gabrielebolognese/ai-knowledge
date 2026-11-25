---
term: Partial derivative
short: >-
  The slope of a function of several inputs with respect to one of them, while all the other inputs are held fixed at their current values. Written with a curly ∂, as in ∂f/∂x.
level: beginner
aliases: [partial]
related: [derivative, gradient, chain-rule]
sources:
  - id: wikipedia
    title: Partial derivative
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Partial_derivative
    accessed: 2026-11-25
    type: wikipedia
  - id: khan-multivar
    title: Multivariable calculus
    publisher: Khan Academy
    url: https://www.khanacademy.org/math/multivariable-calculus
    accessed: 2026-11-25
    type: course
---
Example: for $f(x, y) = x^2 y + y$ at $(2, 3)$, freezing $y$ gives $\partial f/\partial x = 2xy = 12$, and freezing $x$ gives $\partial f/\partial y = x^2 + 1 = 5$. Stacking all the partial derivatives of a function gives its gradient.
