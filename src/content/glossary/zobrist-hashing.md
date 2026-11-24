---
term: "Zobrist hashing"
short: >-
  A way to give every chess position a 64-bit fingerprint by XOR-ing random numbers for each piece on each square, plus side to move, castling and en passant.
level: advanced
related: [transposition-table]
sources:
  - id: cpw
    title: "Zobrist Hashing"
    publisher: Chessprogramming Wiki
    url: https://www.chessprogramming.org/Zobrist_Hashing
    accessed: 2026-11-24
    type: docs
---
Because XOR undoes itself, a move updates the hash with a few XORs instead of a full recomputation. Albert Zobrist described the method in 1970.
