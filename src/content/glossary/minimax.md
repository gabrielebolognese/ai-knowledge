---
term: "Minimax"
short: >-
  A game-tree search rule: the side to move picks the move with the highest score, assuming the opponent always answers with the move that is worst for it.
level: intermediate
aliases: [negamax]
related: [alpha-beta-pruning]
sources:
  - id: cpw
    title: "Minimax"
    publisher: Chessprogramming Wiki
    url: https://www.chessprogramming.org/Minimax
    accessed: 2026-11-24
    type: docs
  - id: cpw-negamax
    title: "Negamax"
    publisher: Chessprogramming Wiki
    url: https://www.chessprogramming.org/Negamax
    accessed: 2026-11-24
    type: docs
---
Negamax is the same rule written once for both players, using the identity max(a, b) = −min(−a, −b). It needs scores given from the side to move's point of view.
