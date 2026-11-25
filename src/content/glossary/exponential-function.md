---
term: Exponential function
short: >-
  The function e^x, where e ≈ 2.718 is Euler's number. It is always positive, grows faster and faster, and is its own derivative. Softmax and sigmoid are built from it.
level: beginner
aliases: [exp, e^x]
related: [natural-logarithm, softmax, sigmoid]
sources:
  - id: wikipedia
    title: Exponential function
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Exponential_function
    accessed: 2026-11-25
    type: wikipedia
  - id: d2l-calculus
    title: "Dive into Deep Learning, 2.4 Calculus"
    author: Aston Zhang, Zachary Lipton, Mu Li, Alexander Smola
    publisher: d2l.ai
    url: https://d2l.ai/chapter_preliminaries/calculus.html
    accessed: 2026-11-25
    type: book
---
Values: $e^0 = 1$, $e^1 \approx 2.718$, $e^2 \approx 7.389$, $e^{-1} \approx 0.368$. In NumPy it is `np.exp`. Very large inputs overflow (`np.exp(1000)` gives `inf`), which is why softmax implementations subtract the largest score first.
