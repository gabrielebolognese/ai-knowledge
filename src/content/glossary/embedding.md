---
term: "Embedding"
short: >-
  A learned vector of numbers that represents a discrete item such as a character, word or token. An embedding layer is a lookup table with one trainable row per item.
level: intermediate
aliases: [embeddings, word embedding, embedding layer, word vector]
related: [language-model, tokenization]
sources:
  - id: pt-embedding
    title: "torch.nn.Embedding"
    publisher: PyTorch
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.Embedding.html
    accessed: 2026-11-25
    type: docs
  - id: bengio2003
    title: "A Neural Probabilistic Language Model"
    author: Yoshua Bengio, Réjean Ducharme, Pascal Vincent, Christian Jauvin
    publisher: Journal of Machine Learning Research 3
    year: 2003
    url: https://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf
    accessed: 2026-11-25
    type: paper
---
Embeddings start random and are trained with the rest of the network, so items used in similar ways end up with similar vectors. Bengio et al. (2003) introduced learned word vectors for neural language modelling.
