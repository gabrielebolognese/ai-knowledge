---
term: "Sentiment analysis"
short: >-
  Classifying the opinion expressed in a text, most simply as positive or negative. A standard benchmark for short texts is SST-2, built from movie-review sentences.
level: intermediate
aliases: [sentiment classification, opinion mining]
related: [embedding, recurrent-neural-network]
sources:
  - id: wiki
    title: "Sentiment analysis"
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Sentiment_analysis
    accessed: 2026-11-25
    type: wikipedia
  - id: socher2013
    title: "Recursive Deep Models for Semantic Compositionality Over a Sentiment Treebank"
    author: Richard Socher et al.
    publisher: EMNLP 2013 (ACL Anthology)
    year: 2013
    url: https://aclanthology.org/D13-1170/
    accessed: 2026-11-25
    type: paper
---
Negation and contrast ("not bad", "slow at first, but moving") are the classic hard cases: they flip or mix the polarity of individual words, so models that ignore word order often get them wrong.
