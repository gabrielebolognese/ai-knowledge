---
term: Weight initialization
short: >-
  The choice of random starting values for a network's weights. Good schemes such as Xavier/Glorot (for tanh) and He/Kaiming (for ReLU) scale the random values by the layer size so signals neither vanish nor explode.
level: intermediate
aliases: [initialisation, Xavier initialization, Glorot initialization, He initialization, Kaiming initialization]
related: [weight, relu, exploding-gradient]
sources:
  - id: glorot2010
    title: Understanding the difficulty of training deep feedforward neural networks
    author: Xavier Glorot, Yoshua Bengio
    publisher: Proceedings of AISTATS 2010 (PMLR 9)
    year: 2010
    url: https://proceedings.mlr.press/v9/glorot10a.html
    accessed: 2026-11-25
    type: paper
  - id: he2015
    title: "Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification"
    author: Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun
    publisher: arXiv
    year: 2015
    url: https://arxiv.org/abs/1502.01852
    accessed: 2026-11-25
    type: paper
  - id: pt-init
    title: torch.nn.init
    publisher: PyTorch
    url: https://docs.pytorch.org/docs/stable/nn.init.html
    accessed: 2026-11-25
    type: docs
---
He initialization draws weights with variance $2/n_\text{in}$; Xavier uses $2/(n_\text{in}+n_\text{out})$. Biases usually start at zero.
