---
term: "Move ordering"
short: >-
  The order in which a game-tree search tries moves. Alpha-beta returns the same value in any order, but searching the best moves first lets it prune far more of the tree.
level: advanced
aliases: [MVV-LVA, killer moves]
related: [alpha-beta-pruning, game-tree, minimax]
sources:
  - id: cpw-move-ordering
    title: Move Ordering
    publisher: Chessprogramming Wiki
    url: https://www.chessprogramming.org/Move_Ordering
    accessed: 2026-11-25
  - id: knuth1975
    title: An Analysis of Alpha-Beta Pruning
    author: Donald E. Knuth, Ronald W. Moore
    publisher: Artificial Intelligence
    year: 1975
    url: https://doi.org/10.1016/0004-3702%2875%2990019-3
    accessed: 2026-11-25
---
With perfect ordering alpha-beta visits about b^⌈d/2⌉ + b^⌊d/2⌋ − 1 leaves instead of b^d (Knuth and Moore 1975). Chess engines approximate it by trying the transposition-table move, good captures and killer moves first.
