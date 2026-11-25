---
term: "Recurrent neural network"
short: >-
  A network that reads a sequence one element at a time and carries a hidden state, a vector of numbers that acts as its running memory, from each step to the next.
level: intermediate
aliases: [RNN, recurrent network, char-rnn]
related: [long-short-term-memory, gated-recurrent-unit, language-model]
sources:
  - id: d2l-rnn
    title: "Dive into Deep Learning, 9.4 Recurrent Neural Networks"
    author: Aston Zhang, Zachary Lipton, Mu Li, Alexander Smola
    publisher: d2l.ai
    url: https://d2l.ai/chapter_recurrent-neural-networks/rnn.html
    accessed: 2026-11-25
    type: book
  - id: karpathy2015
    title: "The Unreasonable Effectiveness of Recurrent Neural Networks"
    author: Andrej Karpathy
    year: 2015
    url: https://karpathy.github.io/2015/05/21/rnn-effectiveness/
    accessed: 2026-11-25
    type: article
---
The same weights are used at every step. Training unrolls the network over the sequence and backpropagates through the steps (backpropagation through time). In plain RNNs the gradients tend to vanish or explode over long spans, which gated cells such as the LSTM and GRU reduce.
