---
term: Natural logarithm
short: >-
  The function ln x, the inverse of e^x: ln x answers "e to what power gives x?". It turns products into sums and is used in cross-entropy and log-probabilities.
level: beginner
aliases: [ln]
related: [exponential-function, cross-entropy]
sources:
  - id: wikipedia
    title: Natural logarithm
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Natural_logarithm
    accessed: 2026-11-25
    type: wikipedia
  - id: goodfellow-ch3
    title: "Deep Learning, chapter 3: Probability and Information Theory"
    author: Ian Goodfellow, Yoshua Bengio, Aaron Courville
    publisher: MIT Press
    year: 2016
    url: https://www.deeplearningbook.org/contents/prob.html
    accessed: 2026-11-25
    type: book
---
Values: $\ln 1 = 0$, $\ln e = 1$, $\ln 0.5 \approx -0.693$, $\ln 10 \approx 2.303$. Its derivative is $1/x$. In NumPy it is `np.log`, which is base $e$, not base 10.
