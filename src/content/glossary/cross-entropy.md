---
term: Cross-entropy loss
short: >-
  The standard loss for classification: minus the logarithm of the probability the model gave to the correct class. It is 0 for a perfectly confident right answer and grows without limit for a confident wrong one.
level: intermediate
aliases: [log loss, CrossEntropyLoss]
related: [softmax, loss-function]
sources:
  - id: pt-ce
    title: torch.nn.CrossEntropyLoss
    publisher: PyTorch
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html
    accessed: 2026-11-25
    type: docs
  - id: wikipedia
    title: Cross-entropy
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Cross-entropy
    accessed: 2026-11-25
    type: wikipedia
---
PyTorch's `nn.CrossEntropyLoss` expects raw logits and applies the softmax itself, so a model trained with it should not end with a softmax layer.
