---
term: F1 score
short: >-
  The harmonic mean of precision and recall, 2PR / (P + R). It is high only when both are high, so it summarises a classifier in one number when classes are imbalanced.
level: intermediate
aliases: [F1, F-score, F-measure]
related: [precision-and-recall, confusion-matrix]
sources:
  - id: wiki-f1
    title: F-score
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/F-score
    accessed: 2026-11-25
    type: wikipedia
  - id: sklearn-f1
    title: sklearn.metrics.f1_score
    publisher: scikit-learn
    url: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html
    accessed: 2026-11-25
    type: docs
---
With precision 0.8 and recall 0.667, F1 = 2 · 0.8 · 0.667 / 1.467 ≈ 0.727. For several classes, the **macro** F1 averages the per-class scores (every class counts equally) and the **micro** F1 pools all counts first (every example counts equally).
