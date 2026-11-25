---
term: Hyperparameter
short: >-
  A setting chosen before or around training rather than learned from the data, such as the learning rate, batch size, number of layers or dropout rate. Hyperparameters are tuned on the validation set.
level: intermediate
aliases: [hyperparameters, hyper-parameter]
related: [learning-rate, weight, epoch]
sources:
  - id: wiki-hp
    title: Hyperparameter (machine learning)
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Hyperparameter_(machine_learning)
    accessed: 2026-11-25
    type: wikipedia
  - id: tuning-playbook
    title: Deep Learning Tuning Playbook
    author: Varun Godbole, George E. Dahl, Justin Gilmer, Christopher J. Shallue, Zachary Nado
    publisher: Google Research (GitHub)
    year: 2023
    url: https://github.com/google-research/tuning_playbook
    accessed: 2026-11-25
    type: article
---
Weights and biases are *parameters*: the optimizer learns them. Hyperparameters are the knobs you set; the learning rate is usually the most important one.
