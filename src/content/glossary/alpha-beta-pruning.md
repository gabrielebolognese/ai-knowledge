---
term: "Alpha-beta pruning"
short: >-
  An improvement of minimax that skips branches which cannot change the final decision, giving the same result while searching far fewer positions.
level: advanced
aliases: [alpha-beta]
related: [minimax]
sources:
  - id: cpw
    title: "Alpha-Beta"
    publisher: Chessprogramming Wiki
    url: https://www.chessprogramming.org/Alpha-Beta
    accessed: 2026-11-24
    type: docs
  - id: wikipedia
    title: "Alpha–beta pruning"
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning
    accessed: 2026-11-24
    type: wikipedia
---
The search keeps a window [α, β]: α is the score already guaranteed elsewhere, β the most the opponent will allow. A move that reaches β ends the search of its node (a beta cutoff). With perfect move ordering the number of leaves drops from about b^d to about 2·b^(d/2).
