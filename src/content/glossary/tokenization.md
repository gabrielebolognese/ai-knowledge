---
term: "Tokenization"
short: >-
  Splitting text into a sequence of tokens (characters, words or sub-word pieces) from a fixed vocabulary, each mapped to an integer id that a model can embed.
level: intermediate
aliases: [tokenizer, token]
related: [byte-pair-encoding, language-model]
sources:
  - id: hf-course
    title: "Hugging Face LLM course: Tokenizers"
    publisher: Hugging Face
    url: https://huggingface.co/learn/llm-course/chapter2/4
    accessed: 2026-11-24
    type: course
  - id: wiki
    title: "Lexical analysis: Tokenization"
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Lexical_analysis#Tokenization
    accessed: 2026-11-24
    type: wikipedia
---
Character-level tokenizers have tiny vocabularies but long sequences; word-level ones have short sequences but cannot handle unseen words. Sub-word methods such as byte-pair encoding sit between the two.
