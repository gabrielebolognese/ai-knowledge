---
term: Softmax
short: >-
  A function that turns a list of raw scores (logits) into probabilities: it exponentiates each score and divides by the sum, so every output is between 0 and 1 and they add up to 1.
level: intermediate
related: [cross-entropy, activation-function]
sources:
  - id: wikipedia
    title: Softmax function
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Softmax_function
    accessed: 2026-11-25
    type: wikipedia
  - id: pt-softmax
    title: torch.nn.functional.softmax
    publisher: PyTorch
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.softmax.html
    accessed: 2026-11-25
    type: docs
---
