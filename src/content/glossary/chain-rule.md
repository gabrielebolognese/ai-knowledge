---
term: Chain rule
short: >-
  The rule for the slope of a function built from other functions: multiply the slopes of the pieces. If y depends on u and u depends on x, then dy/dx = (dy/du)·(du/dx).
level: beginner
related: [derivative, partial-derivative, gradient]
sources:
  - id: wikipedia
    title: Chain rule
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Chain_rule
    accessed: 2026-11-25
    type: wikipedia
  - id: d2l-calculus
    title: "Dive into Deep Learning, 2.4 Calculus"
    author: Aston Zhang, Zachary Lipton, Mu Li, Alexander Smola
    publisher: d2l.ai
    url: https://d2l.ai/chapter_preliminaries/calculus.html
    accessed: 2026-11-25
    type: book
---
Example: for $y = (3x + 1)^2$ at $x = 2$, the inner value is $u = 7$, $dy/du = 2u = 14$ and $du/dx = 3$, so $dy/dx = 42$. Backpropagation is the chain rule applied through every layer of a network.
