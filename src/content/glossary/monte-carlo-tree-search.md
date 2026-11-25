---
term: "Monte Carlo tree search"
short: >-
  A search method that grows a game tree selectively, repeatedly choosing promising but under-explored moves, evaluating where it lands and backing the results up the tree. AlphaZero and Leela Chess Zero use it with a neural network.
level: advanced
aliases: [MCTS, PUCT]
related: [minimax, self-play, reinforcement-learning]
sources:
  - id: wiki-mcts
    title: Monte Carlo tree search
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Monte_Carlo_tree_search
    accessed: 2026-11-25
  - id: silver2017
    title: Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm
    author: David Silver et al.
    publisher: arXiv
    year: 2017
    url: https://arxiv.org/abs/1712.01815
    accessed: 2026-11-25
---
AlphaZero's variant, PUCT, picks the move maximising Q(s,a) + U(s,a): the average value found so far plus an exploration bonus that is large for moves with a high network prior and few visits.
