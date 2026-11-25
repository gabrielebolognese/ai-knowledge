---
term: Logits
short: >-
  The raw, unnormalised scores a classifier outputs, one per class, before softmax turns them into probabilities. PyTorch's CrossEntropyLoss expects logits, not probabilities.
level: intermediate
aliases: [logit, raw scores]
related: [softmax, cross-entropy]
sources:
  - id: pt-ce
    title: torch.nn.CrossEntropyLoss
    publisher: PyTorch
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html
    accessed: 2026-11-25
    type: docs
  - id: wiki-logit
    title: Logit
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Logit
    accessed: 2026-11-25
    type: wikipedia
---
The name comes from statistics, where the logit is the log-odds $\ln(p/(1-p))$. In deep learning it is used loosely for any pre-softmax output. Larger logits mean higher probability, but only differences between logits matter: adding the same number to all of them leaves the softmax unchanged.
