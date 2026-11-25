---
term: "Self-play"
short: >-
  Training a game-playing program by having it play against copies of itself, so its own games become the training data. Used by Samuel's checkers program, AlphaGo, AlphaZero and Leela Chess Zero.
level: advanced
related: [reinforcement-learning, monte-carlo-tree-search]
sources:
  - id: silver2018
    title: A general reinforcement learning algorithm that masters chess, shogi, and Go through self-play
    author: David Silver et al.
    publisher: Science
    year: 2018
    url: https://www.science.org/doi/10.1126/science.aar6404
    accessed: 2026-11-25
  - id: samuel1959
    title: Some Studies in Machine Learning Using the Game of Checkers
    author: Arthur L. Samuel
    publisher: IBM Journal of Research and Development
    year: 1959
    url: https://doi.org/10.1147/rd.33.0210
    accessed: 2026-11-25
---
Self-play needs no human examples, but it must generate millions of games, each requiring many network evaluations, which makes it expensive in compute.
