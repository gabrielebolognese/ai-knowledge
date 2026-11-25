---
term: One-hot encoding
short: >-
  A way to write a category as a list of zeros with a single 1 in the position of the category. With three classes, class 1 becomes [0, 1, 0].
level: beginner
aliases: [one-hot, one-hot vector]
related: [cross-entropy, softmax]
sources:
  - id: wikipedia
    title: One-hot
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/One-hot
    accessed: 2026-11-25
---
Classifiers compare their predicted probabilities with the one-hot target; for softmax with cross-entropy, the gradient with respect to the scores is simply "probabilities minus one-hot".
