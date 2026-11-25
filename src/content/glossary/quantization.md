---
term: Quantization
short: >-
  Storing a model's weights (and often activations) with fewer bits, typically 8-bit integers instead of 32-bit floats, using a scale and zero-point so that real = scale × (integer − zero-point). It makes models about 4 times smaller and can speed up inference.
level: advanced
aliases: [int8, quantisation, quantization-aware training]
related: [nnue, weight]
sources:
  - id: jacob2017
    title: Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference
    publisher: arXiv
    url: https://arxiv.org/abs/1712.05877
    accessed: 2026-11-25
    type: paper
  - id: pt-quantization
    title: Quantization
    publisher: PyTorch documentation
    url: https://docs.pytorch.org/docs/stable/quantization.html
    accessed: 2026-11-25
    type: docs
---
