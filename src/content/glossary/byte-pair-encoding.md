---
term: "Byte-pair encoding"
short: >-
  A sub-word tokenization method that starts from single characters (or bytes) and repeatedly merges the most frequent adjacent pair into a new token, until the vocabulary reaches a chosen size.
level: advanced
aliases: [BPE]
related: [tokenization]
sources:
  - id: sennrich2016
    title: "Neural Machine Translation of Rare Words with Subword Units"
    author: Rico Sennrich, Barry Haddow, Alexandra Birch
    publisher: arXiv
    year: 2016
    url: https://arxiv.org/abs/1508.07909
    accessed: 2026-11-24
    type: paper
  - id: wiki
    title: "Byte pair encoding"
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Byte_pair_encoding
    accessed: 2026-11-24
    type: wikipedia
---
BPE began as a 1994 data-compression algorithm by Philip Gage. Sennrich and colleagues adapted it to neural translation in 2016, and GPT-2 applied it to raw bytes so that any text can be encoded without unknown tokens.
