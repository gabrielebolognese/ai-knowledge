---
term: Early stopping
short: >-
  Stopping training when the validation loss has not improved for a set number of epochs (the patience), and keeping the weights from the best epoch.
level: intermediate
related: [overfitting, validation-set, epoch]
sources:
  - id: wiki-early-stopping
    title: Early stopping
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Early_stopping
    accessed: 2026-11-25
    type: wikipedia
  - id: goodfellow-reg
    title: "Deep Learning, chapter 7: Regularization for Deep Learning (7.8 Early Stopping)"
    author: Ian Goodfellow, Yoshua Bengio, Aaron Courville
    publisher: MIT Press
    year: 2016
    url: https://www.deeplearningbook.org/contents/regularization.html
    accessed: 2026-11-25
    type: book
---
It is one of the simplest and most widely used regularisers: training is cut short before the model starts memorising noise. In code it means saving a checkpoint whenever the validation score improves.
