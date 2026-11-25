---
term: Convolution
short: >-
  The operation inside a convolutional layer: a small grid of weights (the kernel) slides over the input, and at each position the overlapping values are multiplied pairwise and summed, plus a bias. Deep learning libraries actually compute cross-correlation (no kernel flip).
level: advanced
aliases: [kernel, filter, cross-correlation, Conv2d]
related: [convolutional-neural-network, feature-map, receptive-field]
sources:
  - id: d2l
    title: "Dive into Deep Learning, 7.2 Convolutions for Images"
    publisher: d2l.ai
    url: https://d2l.ai/chapter_convolutional-neural-networks/conv-layer.html
    accessed: 2026-11-25
    type: book
  - id: pt-conv2d
    title: torch.nn.Conv2d
    publisher: PyTorch documentation
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.Conv2d.html
    accessed: 2026-11-25
    type: docs
---
For an input of width $W$, kernel size $K$, padding $P$ and stride $S$, the output width is $\lfloor (W - K + 2P)/S \rfloor + 1$. A layer with $C_{in}$ input and $C_{out}$ output channels has $(K^2 C_{in} + 1) C_{out}$ parameters, independent of the image size.
