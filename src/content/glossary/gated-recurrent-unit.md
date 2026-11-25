---
term: "Gated recurrent unit (GRU)"
short: >-
  A lighter recurrent cell than the LSTM, with two gates (reset and update) and no separate cell state. Its new hidden state is a gated blend of the old state and a candidate.
level: advanced
aliases: [GRU]
related: [recurrent-neural-network, long-short-term-memory]
sources:
  - id: cho2014
    title: "Learning Phrase Representations using RNN Encoder-Decoder for Statistical Machine Translation"
    author: Kyunghyun Cho et al.
    publisher: arXiv
    year: 2014
    url: https://arxiv.org/abs/1406.1078
    accessed: 2026-11-25
    type: paper
  - id: chung2014
    title: "Empirical Evaluation of Gated Recurrent Neural Networks on Sequence Modeling"
    author: Junyoung Chung, Caglar Gulcehre, KyungHyun Cho, Yoshua Bengio
    publisher: arXiv
    year: 2014
    url: https://arxiv.org/abs/1412.3555
    accessed: 2026-11-25
    type: paper
---
Chung et al. (2014) found GRUs and LSTMs broadly comparable on their sequence tasks, so the choice is often made on speed and size.
