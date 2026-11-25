---
term: "Long short-term memory (LSTM)"
short: >-
  A recurrent cell with a separate cell state and three gates (forget, input, output) that decide what to erase, what to write and what to reveal, so information and gradients survive over longer sequences.
level: advanced
aliases: [LSTM]
related: [recurrent-neural-network, gated-recurrent-unit]
sources:
  - id: hochreiter1997
    title: "Long Short-Term Memory"
    author: Sepp Hochreiter, Jürgen Schmidhuber
    publisher: Neural Computation 9(8)
    year: 1997
    url: https://doi.org/10.1162/neco.1997.9.8.1735
    accessed: 2026-11-25
    type: paper
  - id: olah2015
    title: "Understanding LSTM Networks"
    author: Christopher Olah
    year: 2015
    url: https://colah.github.io/posts/2015-08-Understanding-LSTMs/
    accessed: 2026-11-25
    type: article
---
The forget gate was added by Gers, Schmidhuber and Cummins in 2000; "LSTM" today means the version with it. PyTorch implements it as `torch.nn.LSTM`.
