---
term: Gradient clipping
short: >-
  Shrinking the gradient before an optimizer step whenever its overall size (norm) exceeds a chosen maximum, so that one bad batch cannot produce a huge update. Common in RNNs and Transformers.
level: intermediate
aliases: [clip_grad_norm_, gradient norm clipping]
related: [exploding-gradient, gradient, recurrent-neural-network]
sources:
  - id: pt-clip
    title: torch.nn.utils.clip_grad_norm_
    publisher: PyTorch
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html
    accessed: 2026-11-25
    type: docs
  - id: pascanu2013
    title: On the difficulty of training recurrent neural networks
    author: Razvan Pascanu, Tomas Mikolov, Yoshua Bengio
    publisher: Proceedings of ICML 2013 (PMLR 28)
    year: 2013
    url: https://proceedings.mlr.press/v28/pascanu13.html
    accessed: 2026-11-25
    type: paper
---
In PyTorch, call `torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)` between `loss.backward()` and `optimizer.step()`.
