---
term: Weight decay
short: >-
  A regulariser that shrinks every weight a little at each update, equivalent for plain SGD to adding an L2 penalty (λ/2)·‖w‖² to the loss. It discourages large weights the data does not need.
level: intermediate
aliases: [L2 regularization, L2 penalty, ridge]
related: [overfitting, dropout, weight]
sources:
  - id: d2l-weight-decay
    title: "Dive into Deep Learning, 3.7 Weight Decay"
    author: Aston Zhang, Zachary Lipton, Mu Li, Alexander Smola
    publisher: d2l.ai
    url: https://d2l.ai/chapter_linear-regression/weight-decay.html
    accessed: 2026-11-25
    type: book
  - id: loshchilov2017
    title: Decoupled Weight Decay Regularization
    author: Ilya Loshchilov, Frank Hutter
    publisher: arXiv (ICLR 2019)
    year: 2017
    url: https://arxiv.org/abs/1711.05101
    accessed: 2026-11-25
    type: paper
---
For adaptive optimizers such as Adam the two are not the same: Loshchilov and Hutter showed that applying the decay directly to the weights ("decoupled", as in `torch.optim.AdamW`) works better than adding an L2 term to the loss.
