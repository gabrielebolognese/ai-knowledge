---
term: "Elo rating"
short: >-
  A rating system in which the difference between two players' ratings predicts their expected score; a 400-point gap means the stronger side is expected to score about 91%.
level: advanced
aliases: [Elo]
related: [uci]
sources:
  - id: wikipedia
    title: "Elo rating system"
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Elo_rating_system
    accessed: 2026-11-24
    type: wikipedia
  - id: cpw
    title: "Match Statistics"
    publisher: Chessprogramming Wiki
    url: https://www.chessprogramming.org/Match_Statistics
    accessed: 2026-11-24
    type: docs
---
The expected score for a rating difference Δ is 1 / (1 + 10^(−Δ/400)). Ratings from different pools (FIDE, Lichess, engine rating lists) are not directly comparable.
