---
term: Validation set
short: >-
  Data held out from training and used to compare models, pick hyperparameters and decide when to stop. The separate test set is used only once, for the final score.
level: intermediate
aliases: [validation data, dev set, held-out set, test set]
related: [overfitting, early-stopping]
sources:
  - id: wiki-sets
    title: Training, validation, and test data sets
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Training,_validation,_and_test_data_sets
    accessed: 2026-11-25
    type: wikipedia
  - id: goodfellow-guidelines
    title: "Deep Learning, chapter 11: Practical Methodology"
    author: Ian Goodfellow, Yoshua Bengio, Aaron Courville
    publisher: MIT Press
    year: 2016
    url: https://www.deeplearningbook.org/contents/guidelines.html
    accessed: 2026-11-25
    type: book
---
Every decision made by looking at a data set slowly fits the model to it. That is why the test set stays untouched until the end: once it has influenced a choice, its score is no longer an honest estimate of performance on new data.
