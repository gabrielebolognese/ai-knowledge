---
term: Overfitting
short: >-
  When a model fits its training data, noise included, so closely that it does worse on new data. The sign is a low training loss with a validation loss that stalls or rises.
level: intermediate
aliases: [overfit, underfitting]
related: [dropout, weight-decay, early-stopping, validation-set, data-augmentation]
sources:
  - id: wiki-overfitting
    title: Overfitting
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Overfitting
    accessed: 2026-11-25
    type: wikipedia
  - id: d2l-generalization
    title: "Dive into Deep Learning, 3.6 Generalization"
    author: Aston Zhang, Zachary Lipton, Mu Li, Alexander Smola
    publisher: d2l.ai
    url: https://d2l.ai/chapter_linear-regression/generalization.html
    accessed: 2026-11-25
    type: book
---
The opposite problem, **underfitting**, means the model is too simple or too briefly trained to fit even the training data: both losses stay high. The usual remedies for overfitting are more data, data augmentation, weight decay, dropout, early stopping and a smaller model.
