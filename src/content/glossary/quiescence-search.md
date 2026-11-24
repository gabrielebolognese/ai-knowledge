---
term: "Quiescence search"
short: >-
  An extra search at the end of a chess-engine line that keeps playing captures until the position is quiet, so it is never evaluated in the middle of an exchange.
level: advanced
related: [alpha-beta-pruning]
sources:
  - id: cpw
    title: "Quiescence Search"
    publisher: Chessprogramming Wiki
    url: https://www.chessprogramming.org/Quiescence_Search
    accessed: 2026-11-24
    type: docs
---
It fixes the horizon effect. The side to move may also "stand pat", accepting the static evaluation instead of capturing, except when in check.
