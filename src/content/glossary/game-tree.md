---
term: "Game tree"
short: >-
  A tree whose root is the current position of a game, whose branches are legal moves and whose nodes are the positions they lead to. Its size grows roughly as the branching factor to the power of the depth.
level: advanced
aliases: [search tree, branching factor, ply]
related: [minimax, alpha-beta-pruning, move-ordering]
sources:
  - id: wiki-game-tree
    title: Game tree
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Game_tree
    accessed: 2026-11-25
  - id: cpw-search-tree
    title: Search Tree
    publisher: Chessprogramming Wiki
    url: https://www.chessprogramming.org/Search_Tree
    accessed: 2026-11-25
---
One move by one player is a ply. With about 35 legal moves per chess position, a full tree six plies deep already has about 1.8 billion leaves.
