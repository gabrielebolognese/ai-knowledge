---
term: "NNUE"
short: >-
  Efficiently Updatable Neural Network: a small network with a wide, sparse first layer that is updated move by move, used as the evaluation function of Stockfish and other engines.
level: advanced
aliases: [efficiently updatable neural network]
related: [centipawn]
sources:
  - id: cpw
    title: "NNUE"
    publisher: Chessprogramming Wiki
    url: https://www.chessprogramming.org/NNUE
    accessed: 2026-11-24
    type: docs
  - id: nnue-doc
    title: "NNUE"
    publisher: Stockfish nnue-pytorch documentation
    url: https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue.html
    accessed: 2026-11-24
    type: docs
---
Yu Nasu introduced NNUE for computer shogi in 2018, and Stockfish adopted it in version 12 (2020). The first layer's output, the accumulator, changes in only a few columns per move, which makes evaluation cheap on a CPU.
