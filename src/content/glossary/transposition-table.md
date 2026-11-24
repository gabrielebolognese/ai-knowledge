---
term: "Transposition table"
short: >-
  A hash table in which a chess engine stores results for positions it has already searched (depth, score, bound type, best move), so positions reached by another move order are not searched again.
level: advanced
related: [zobrist-hashing]
sources:
  - id: cpw
    title: "Transposition Table"
    publisher: Chessprogramming Wiki
    url: https://www.chessprogramming.org/Transposition_Table
    accessed: 2026-11-24
    type: docs
---
Each entry records whether its score is exact, a lower bound (after a beta cutoff) or an upper bound (when every move failed low).
