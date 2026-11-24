---
term: "Centipawn"
short: >-
  One hundredth of a pawn, the usual unit of chess-engine evaluations. +100 cp means the side in question is about one pawn better.
level: intermediate
aliases: [cp]
related: [minimax]
sources:
  - id: cpw
    title: "Centipawns"
    publisher: Chessprogramming Wiki
    url: https://www.chessprogramming.org/Centipawns
    accessed: 2026-11-24
    type: docs
---
Engines measure advantage in centipawns so that material and positional factors share one scale. Large values such as +1500 and +3000 both mean "winning", which is why neural evaluators are trained in a squashed win-probability space instead of raw centipawns.
