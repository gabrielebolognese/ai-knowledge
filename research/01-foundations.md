# Research 01: Foundations of Math, Machine Learning and Neural Networks

> **Purpose.** This file is the sourced backbone of the **beginner** and **intermediate** tracks. Each topic has the same structure:
> **Distilled** (short original summary) · **Math, micro-step by micro-step** (with a tiny worked numeric example) · **Analogy** (for beginners, with its limits stated) · **Misconceptions** · **Sources**.
>
> Lesson writers: the wording here is original and paraphrases the sources. Do not copy text from the sources. Cite them with links in the lesson's footnotes. Math uses `$...$` (KaTeX) notation. Every worked example has been checked by hand. If you change the numbers, recompute them.
>
> Research date: 2026-11-24. All URLs were checked for reachability on that date.

---

## Table of contents

1. [AI, ML and DL: definitions and history timeline](#1-ai-ml-and-dl-definitions-and-history-timeline)
2. [Python and NumPy essentials for ML](#2-python-and-numpy-essentials-for-ml)
3. [Vectors, matrices, dot product, matrix multiplication](#3-vectors-matrices-dot-product-matrix-multiplication)
4. [Derivatives, partial derivatives, the chain rule, gradients](#4-derivatives-partial-derivatives-the-chain-rule-gradients)
5. [Probability basics, softmax, cross-entropy, MSE](#5-probability-basics-softmax-cross-entropy-mse)
6. [Neuron, perceptron, activations, MLP, forward pass](#6-neuron-perceptron-activations-mlp-forward-pass)
7. [Backpropagation derived step by step](#7-backpropagation-derived-step-by-step)
8. [Gradient descent variants and optimizers](#8-gradient-descent-variants-and-optimizers)
9. [Initialization, normalization, regularization, overfitting, splits, metrics](#9-initialization-normalization-regularization-overfitting-splits-metrics)
10. [The PyTorch training loop](#10-the-pytorch-training-loop)
11. [Debugging training](#11-debugging-training)
12. [Bibliography (deduplicated)](#12-bibliography-deduplicated)

---

## 1. AI, ML and DL: definitions and history timeline

### Distilled
- **Artificial intelligence (AI)** is the broad field of building systems that do tasks we would call "intelligent" if a person did them: perceiving, reasoning, planning, using language. The term comes from the 1955 proposal for the 1956 Dartmouth summer workshop (McCarthy, Minsky, Rochester, Shannon).
- **Machine learning (ML)** is the subset of AI where behaviour is *learned from data* instead of written as explicit rules. Arthur Samuel popularised the phrase in his 1959 checkers paper. Goodfellow et al. (ch. 5) use Mitchell's definition: a program learns from experience E on task T, measured by P, if P on T improves with E.
- **Deep learning (DL)** is the subset of ML that uses **neural networks with many layers**. Each layer learns a slightly more abstract representation (edges → shapes → objects) (Goodfellow et al., ch. 1).
- The nesting is **AI ⊃ ML ⊃ DL**. Not all AI is ML (e.g. a hand-written chess search). Not all ML is DL (e.g. decision trees, linear regression).
- Three main ML settings:
  - **supervised**: learn from input→label pairs, like digit images with their digits.
  - **unsupervised / self-supervised**: find structure without labels. This includes predicting the next character of text, which is how small language models learn.
  - **reinforcement learning**: learn from rewards.
- The field has gone through hype cycles and "AI winters". Deep learning's comeback after about 2006–2012 came from three things together: **big labelled datasets** (ImageNet), **GPUs** and **better training tricks** (ReLU, dropout, good initialization, BatchNorm, Adam).
- The algorithmic core is old. Backpropagation was popularised in 1986, and its reverse-mode differentiation roots go back to Linnainmaa (1970) and Werbos (1974).

### Timeline (for the lesson's interactive timeline)
| Year | Event | Source |
|---|---|---|
| 1943 | McCulloch & Pitts publish a mathematical model of a neuron as a logic unit | [McCulloch & Pitts 1943](https://doi.org/10.1007/BF02478259) |
| 1950 | Turing asks "Can machines think?" and proposes the imitation game | [Turing 1950](https://doi.org/10.1093/mind/LIX.236.433) |
| 1955–56 | Dartmouth proposal coins "artificial intelligence"; workshop held in 1956 | [Dartmouth proposal](http://jmc.stanford.edu/articles/dartmouth/dartmouth.pdf) |
| 1958 | Rosenblatt's perceptron: a trainable neuron | [Rosenblatt 1958](https://doi.org/10.1037/h0042519) |
| 1959 | Samuel's self-learning checkers program; "machine learning" | [Samuel 1959](https://doi.org/10.1147/rd.33.0210) |
| 1969 | Minsky & Papert, *Perceptrons*: limits of single-layer networks (e.g. XOR) | [Wikipedia: Perceptrons (book)](https://en.wikipedia.org/wiki/Perceptrons_%28book%29) |
| 1970s | First "AI winter" (funding collapse) | [Wikipedia: AI winter](https://en.wikipedia.org/wiki/AI_winter) |
| 1986 | Rumelhart, Hinton & Williams: learning representations by back-propagating errors | [Rumelhart et al. 1986](https://doi.org/10.1038/323533a0) |
| 1989–98 | LeCun's convolutional networks read handwritten digits; LeNet-5 and MNIST (1998) | [LeCun et al. 1998](https://doi.org/10.1109/5.726791) |
| 1997 | Hochreiter & Schmidhuber: LSTM | [LSTM 1997](https://doi.org/10.1162/neco.1997.9.8.1735) |
| 2006 | Hinton et al.: deep belief nets, layer-wise pre-training; "deep learning" revival | [Hinton et al. 2006](https://doi.org/10.1162/neco.2006.18.7.1527) |
| 2009 | ImageNet dataset | [Deng et al. 2009](https://doi.org/10.1109/CVPR.2009.5206848) |
| 2010 | Glorot & Bengio initialization; Nair & Hinton popularise ReLU | [Glorot & Bengio 2010](https://proceedings.mlr.press/v9/glorot10a.html), [Nair & Hinton 2010](https://www.cs.toronto.edu/~hinton/absps/reluICML.pdf) |
| 2012 | AlexNet wins ImageNet by a wide margin on GPUs | [Krizhevsky et al. 2012](https://papers.nips.cc/paper/2012/hash/c399862d3b9d6b76c8436e924a68c45b-Abstract.html) |
| 2014 | Adam optimizer; dropout journal paper | [Kingma & Ba 2014](https://arxiv.org/abs/1412.6980), [Srivastava et al. 2014](https://jmlr.org/papers/v15/srivastava14a.html) |
| 2015 | Batch normalization; He initialization; ResNet | [Ioffe & Szegedy](https://arxiv.org/abs/1502.03167), [He et al. init](https://arxiv.org/abs/1502.01852), [ResNet](https://arxiv.org/abs/1512.03385) |
| 2016 | AlphaGo defeats Lee Sedol (deep nets + tree search, relevant to our chess project) | [Silver et al. 2016](https://doi.org/10.1038/nature16961) |
| 2017 | Transformer: "Attention Is All You Need" | [Vaswani et al. 2017](https://arxiv.org/abs/1706.03762) |
| 2018 | Turing Award to Bengio, Hinton, LeCun | [ACM 2018 Turing Award](https://awards.acm.org/about/2018-turing) |
| 2024 | Nobel Prize in Physics to Hopfield & Hinton for foundational work on neural networks | [Nobel Prize 2024](https://www.nobelprize.org/prizes/physics/2024/summary/) |

### Math, micro-step by micro-step: "learning" as function fitting
1. Choose a **model**: a function with adjustable numbers (parameters), e.g. $\hat y = w x$.
2. Collect **data**: pairs $(x, y)$, e.g. $(1, 2), (2, 4), (3, 6)$.
3. Choose a **loss** that measures wrongness, e.g. the squared error $(\hat y - y)^2$.
4. Try $w = 1$: the predictions are $1, 2, 3$, the errors are $-1, -2, -3$, and the mean squared error is $(1+4+9)/3 = 4.67$.
5. Try $w = 2$: the predictions are $2, 4, 6$, so the loss is $0$. "Learning" means finding $w = 2$ *automatically* (sections 4, 7, 8).

### Analogy
- **ML vs classic programming:** Classic programming is writing a recipe. ML is giving the computer hundreds of finished dishes plus their ingredient lists and letting it work out the recipe. *Limit:* the learned "recipe" is a pile of numbers, not readable instructions.
- **Nesting dolls:** AI is the biggest doll, ML sits inside it, and DL sits inside ML.

### Misconceptions
- "AI = deep learning." No. Search-based chess engines (like classic Stockfish before NNUE) are AI without deep learning.
- "Neural networks work like the brain." They are *loosely inspired* by neurons. Artificial neurons are simple weighted sums followed by a nonlinearity (Goodfellow et al., ch. 1 make this point explicitly).
- "Deep learning was invented in 2012." The main ideas are decades old. What changed in 2012 was data and compute.

### Sources
- Goodfellow, Bengio, Courville, *Deep Learning*, ch. 1 Introduction — MIT Press — https://www.deeplearningbook.org/contents/intro.html
- Goodfellow et al., ch. 5 Machine Learning Basics — https://www.deeplearningbook.org/contents/ml.html
- Zhang, Lipton, Li, Smola, *Dive into Deep Learning*, Introduction — https://d2l.ai/chapter_introduction/index.html
- Wikipedia, "History of artificial intelligence" — https://en.wikipedia.org/wiki/History_of_artificial_intelligence
- Papers in the timeline table above.

---

## 2. Python and NumPy essentials for ML

### Distilled
- **Python** is the main language of ML because the libraries (NumPy, PyTorch, scikit-learn) are in Python and the syntax reads almost like pseudocode.
- Python basics a learner needs before ML:
  - variables, numbers and strings
  - **lists** and **dicts**
  - `for` loops and `if`
  - **functions** (`def`)
  - **classes**, because `nn.Module` is a class
  - `import`
  - list comprehensions
  - f-strings for printing
- **NumPy** gives you the `ndarray`, a grid of numbers of one type with a **shape** (e.g. `(28, 28)` for an MNIST image).
- **Vectorization:** operations on whole arrays (`a * b`, `a @ b`, `a.sum()`) run in optimised C and are far faster than Python loops over elements.
- **Shape** is the most important property to track. Most bugs are shape bugs. Use `x.shape` constantly.
- **Axes:** `a.sum(axis=0)` sums down the columns, giving one result per column. `axis=1` sums across each row.
- **Broadcasting** lets arrays of different shapes combine. NumPy compares shapes from the right, and two dimensions are compatible if they are equal or one of them is 1.
- **Indexing and slicing:**
  - `a[0]` is the first row.
  - `a[:, 0]` is the first column.
  - `a[a > 0]` is boolean masking.
- **Reshaping:**
  - `a.reshape(-1, 784)` flattens images into rows. `-1` means "work this dimension out".
- **Random numbers:**
  - `rng = np.random.default_rng(0)` is the modern, seedable generator.
- **dtype:** ML usually uses `float32`. Mixing integer and float arrays can silently cast.
- **PyTorch tensors** mirror NumPy arrays almost one-to-one and add GPU support and autograd (section 10).

### Math, micro-step by micro-step: broadcasting
1. `a` has shape `(3, 1)`: the values `[[0],[10],[20]]`.
2. `b` has shape `(1, 4)`: the values `[[0, 1, 2, 3]]`.
3. Compare the shapes from the right. The last dimensions are `1` vs `4`, which is compatible, so the result size is 4. The first dimensions are `3` vs `1`, which is compatible, so the result size is 3.
4. NumPy virtually "stretches" `a` across 4 columns and `b` down 3 rows. No copy is made.
5. `a + b` has shape `(3, 4)`: `[[0,1,2,3],[10,11,12,13],[20,21,22,23]]`.
6. Counter-example: shapes `(3,)` and `(4,)` are **not** compatible (3 ≠ 4 and neither is 1), so NumPy raises an error.

```python
import numpy as np
x = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)  # shape (2, 3)
print(x.shape, x.sum(axis=0), x.mean(axis=1))          # (2, 3) [5. 7. 9.] [2. 5.]
x_centered = x - x.mean(axis=0)                        # broadcasting (2,3) - (3,)
```

### Analogy
- **ndarray = spreadsheet with strict rules.** Every cell holds the same type of number, and the "shape" is the number of rows and columns. A 3-D array is a stack of spreadsheet sheets.
- **Broadcasting = a rubber stamp.** If one array has size 1 along an axis, NumPy "stamps" it repeatedly along that axis to match the other array.
- **Vectorization:** a loop is a cashier scanning items one by one. A vectorised op is a scanner that reads the whole cart at once.

### Misconceptions
- "`*` multiplies matrices." In NumPy and PyTorch, `*` is **element-wise**. Matrix multiplication is `@` (or `np.matmul`).
- "Shape `(3,)` is the same as `(3, 1)`." No. `(3,)` is a 1-D vector, while `(3, 1)` is a 2-D column. They broadcast differently.
- "Slices copy data." Basic NumPy slices are **views**: changing them changes the original. Use `.copy()` when you need an independent array.

### Sources
- Python Software Foundation, *The Python Tutorial* — https://docs.python.org/3/tutorial/index.html
- NumPy, "NumPy: the absolute basics for beginners" — https://numpy.org/doc/stable/user/absolute_beginners.html
- NumPy, "Broadcasting" — https://numpy.org/doc/stable/user/basics.broadcasting.html
- NumPy, "Copies and views" — https://numpy.org/doc/stable/user/basics.copies.html
- Stanford CS231n, "Python Numpy Tutorial" (Justin Johnson) — https://cs231n.github.io/python-numpy-tutorial/
- d2l.ai, 2.1 Data Manipulation — https://d2l.ai/chapter_preliminaries/ndarray.html

---

## 3. Vectors, matrices, dot product, matrix multiplication

### Distilled
- A **scalar** is one number. A **vector** is an ordered list of numbers, e.g. a pixel row or the features of a house. A **matrix** is a 2-D grid. A **tensor** is the general n-D version (Goodfellow et al., ch. 2).
- A vector can be seen as a **point** or an **arrow** in space. 3Blue1Brown's "Essence of linear algebra" builds the geometric intuition.
- The **dot product** $a \cdot b = \sum_i a_i b_i$ multiplies matching entries and adds them up. It is large when the vectors point the same way, zero when they are perpendicular, and negative when they point in opposite directions: $a\cdot b = \|a\|\|b\|\cos\theta$.
- **A single neuron is a dot product** (plus a bias). This is why linear algebra matters for neural networks.
- **Matrix–vector product** $W x$: each output entry is the dot product of one row of $W$ with $x$. One layer of neurons is one matrix–vector product.
- **Matrix multiplication** $C = AB$ requires the "inner" sizes to match: $(m \times n)(n \times p) \to (m \times p)$. Entry $C_{ij}$ is row $i$ of $A$ dotted with column $j$ of $B$.
- Matrix multiplication is **not commutative**: $AB \ne BA$ in general. It *is* associative: $(AB)C = A(BC)$.
- The **transpose** $A^\top$ flips rows and columns. It appears in backprop: gradients flow back through $W^\top$.
- **Batching:** stacking many inputs as the rows of $X$ lets one product $XW^\top$ process the whole batch. This is why GPUs speed up deep learning.
- **Norms:** $\|x\|_2 = \sqrt{\sum x_i^2}$ is the length, used in weight decay (section 9).

### Math, micro-step by micro-step
**Dot product** of $a = [1, 2, 3]$ and $b = [4, 5, 6]$:
1. Multiply pairwise: $1\cdot4 = 4$, $2\cdot5 = 10$, $3\cdot6 = 18$.
2. Add: $4 + 10 + 18 = 32$.

**Matrix multiplication** $A = \begin{bmatrix}1&2\\3&4\end{bmatrix}$, $B = \begin{bmatrix}5&6\\7&8\end{bmatrix}$:
1. Check the shapes: $(2\times2)(2\times2) \to (2\times2)$. ✓
2. $C_{11}$ = row 1 of $A$ · column 1 of $B$ = $1\cdot5 + 2\cdot7 = 19$.
3. $C_{12}$ = row 1 · column 2 = $1\cdot6 + 2\cdot8 = 22$.
4. $C_{21}$ = row 2 · column 1 = $3\cdot5 + 4\cdot7 = 43$.
5. $C_{22}$ = row 2 · column 2 = $3\cdot6 + 4\cdot8 = 50$.
6. $C = \begin{bmatrix}19&22\\43&50\end{bmatrix}$. Check in NumPy with `A @ B`.
7. Non-commutativity: $BA = \begin{bmatrix}23&34\\31&46\end{bmatrix} \ne AB$.

**Length (norm)** of $[3, 4]$: $\sqrt{9+16} = 5$.

### Analogy
- **Dot product = a shopping bill.** The quantities $[2, 1, 3]$ (apples, bread, milk) dotted with the prices $[0.5, 2, 1]$ give $1 + 2 + 3 = 6$, the total bill. A neuron does exactly this: inputs × "importance prices", summed.
- **Matrix–vector product = several cashiers at once.** Each row of $W$ is one cashier with their own price list, and each produces one total.
- **Dot product as agreement:** two arrows pointing the same way "agree" (large positive), perpendicular ones "don't care" (zero), and opposite ones "disagree" (negative).

### Misconceptions
- "Matrix multiplication multiplies entries in the same position." That is the element-wise (Hadamard) product $A \odot B$, a different operation.
- "Order doesn't matter." $AB \neq BA$ in general, and often only one of them is even defined.
- "Vectors are only arrows in 2-D or 3-D." In ML they often have 784 dimensions (an MNIST image) or more. The algebra is the same.

### Sources
- Goodfellow et al., ch. 2 Linear Algebra — https://www.deeplearningbook.org/contents/linear_algebra.html
- d2l.ai, 2.3 Linear Algebra — https://d2l.ai/chapter_preliminaries/linear-algebra.html
- 3Blue1Brown, "Essence of linear algebra" — https://www.3blue1brown.com/topics/linear-algebra
- Khan Academy, Linear algebra — https://www.khanacademy.org/math/linear-algebra
- NumPy, `numpy.matmul` reference — https://numpy.org/doc/stable/reference/generated/numpy.matmul.html

---

## 4. Derivatives, partial derivatives, the chain rule, gradients

### Distilled
- A **derivative** $f'(x)$ is the instantaneous rate of change: how much the output moves per tiny nudge of the input. Geometrically, it is the **slope of the tangent line**.
- The definition is $f'(x) = \lim_{h\to0} \frac{f(x+h) - f(x)}{h}$. For a small $h$, this ratio is a good **numerical approximation**, which is the basis of *gradient checking* (section 11).
- Rules a beginner needs:
  - power rule: $(x^n)' = n x^{n-1}$
  - constant rule
  - sum rule
  - $(e^x)' = e^x$
  - $(\ln x)' = 1/x$
- A **partial derivative** $\partial f/\partial x$ changes one input while holding the others fixed.
- The **gradient** $\nabla f$ is the vector of all partial derivatives. It points in the direction of **steepest ascent**, so $-\nabla f$ points steepest **downhill**.
- The **chain rule**: if $y = f(u)$ and $u = g(x)$, then $\frac{dy}{dx} = \frac{dy}{du}\cdot\frac{du}{dx}$. Rates of change **multiply along a chain**.
- A neural network is a long chain of simple functions, so the chain rule lets us get the derivative of the loss with respect to *every* weight. That is backpropagation (section 7).
- In a **computational graph**, each node holds a simple operation, and the chain rule is applied node by node from the output backwards (CS231n "Backprop, intuitions"; Karpathy's micrograd).
- When a variable feeds several paths, **its gradients add up** (the multivariable chain rule).
- Derivatives of common activations:
  - $\sigma'(z) = \sigma(z)(1-\sigma(z))$
  - $\tanh'(z) = 1 - \tanh^2 z$
  - $\text{ReLU}'(z) = 1$ if $z>0$, else $0$

### Math, micro-step by micro-step
**Derivative of $f(x) = x^2$ at $x = 3$:**
1. Power rule: $f'(x) = 2x$.
2. Plug in: $f'(3) = 6$.
3. Numerical check with $h = 0.001$: $(3.001^2 - 9)/0.001 = (9.006001 - 9)/0.001 = 6.001 \approx 6$. ✓

**Chain rule, $y = (3x+1)^2$ at $x = 2$:**
1. Name the inner part: $u = 3x + 1$, so $y = u^2$.
2. Forward: $u = 3\cdot2+1 = 7$ and $y = 49$.
3. Outer derivative: $dy/du = 2u = 14$.
4. Inner derivative: $du/dx = 3$.
5. Multiply: $dy/dx = 14 \cdot 3 = 42$.
6. Check by expanding: $y = 9x^2 + 6x + 1$, so $y' = 18x + 6 = 42$ at $x = 2$. ✓

**Partial derivatives and gradient of $f(x, y) = x^2 y + y$ at $(2, 3)$:**
1. $\partial f/\partial x$: treat $y$ as a constant, which gives $2xy = 2\cdot2\cdot3 = 12$.
2. $\partial f/\partial y$: treat $x$ as a constant, which gives $x^2 + 1 = 4 + 1 = 5$.
3. Gradient: $\nabla f(2,3) = [12, 5]$. A small step in $x$ changes $f$ about 2.4× more than the same step in $y$.

### Analogy
- **Derivative = speedometer.** Position is the function, and the derivative is the speed reading right now.
- **Gradient = the slope under your feet on a foggy mountain.** You can't see the valley, but you can feel which way the ground tilts. Stepping opposite the steepest upward tilt takes you downhill. *Limit:* real loss "mountains" have millions of dimensions, and the steepest local direction does not always lead to the lowest point.
- **Chain rule = gears.** If gear A turns gear B 3× as fast, and B turns C 14× as fast, then A turns C $3 \times 14 = 42$× as fast (3Blue1Brown's calculus series uses similar "nudge" intuitions).

### Misconceptions
- "The gradient points to the minimum." It points in the direction of steepest *local ascent*. Its negative is only the best *local* downhill direction.
- "Partial derivatives ignore the other variables." They hold them *fixed at their current values*, and the result usually depends on those values (the 12 above depends on $y = 3$).
- "ReLU has no derivative, so it can't be trained." It is not differentiable exactly at 0, but frameworks just use 0 (or 1) there, and it works fine in practice.

### Sources
- Goodfellow et al., ch. 4 Numerical Computation (gradient-based optimization) — https://www.deeplearningbook.org/contents/numerical.html
- d2l.ai, 2.4 Calculus — https://d2l.ai/chapter_preliminaries/calculus.html
- d2l.ai, 2.5 Automatic Differentiation — https://d2l.ai/chapter_preliminaries/autograd.html
- 3Blue1Brown, "Essence of calculus" — https://www.3blue1brown.com/topics/calculus
- Khan Academy, Calculus 1 — https://www.khanacademy.org/math/calculus-1
- Khan Academy, Multivariable calculus (partial derivatives, gradient) — https://www.khanacademy.org/math/multivariable-calculus
- Stanford CS231n, "Backpropagation, Intuitions" — https://cs231n.github.io/optimization-2/

---

## 5. Probability basics, softmax, cross-entropy, MSE

### Distilled
- A **probability** is a number in $[0, 1]$, and the probabilities of all outcomes of one event sum to 1. A **distribution** assigns probabilities to outcomes (Goodfellow et al., ch. 3).
- **Expected value** is the probability-weighted average outcome, e.g. a fair die has $E = 3.5$.
- A **conditional probability** $P(A\mid B)$ is the probability of A given that B happened. A classifier outputs $P(\text{class}\mid\text{image})$.
- **Logits** are the raw, unbounded scores a network outputs. **Softmax** turns them into a probability distribution: $\text{softmax}(z)_i = e^{z_i} / \sum_j e^{z_j}$. All outputs are positive, they sum to 1, and the order of the scores is kept.
- Softmax is unchanged if you add the same constant to all logits. Implementations subtract $\max(z)$ before exponentiating to avoid overflow (Goodfellow et al., ch. 4).
- **Sigmoid** $\sigma(z) = 1/(1+e^{-z})$ is the 2-class special case. It turns one score into $P(\text{yes})$.
- **Cross-entropy loss** for one example with true class $c$ is $L = -\ln p_c$. It is 0 when the model is certain and right, and grows without limit as $p_c \to 0$. It equals the **negative log-likelihood**, so minimising it is maximum-likelihood estimation.
- The gradient of softmax + cross-entropy with respect to the logits is simply $p - y$ (predicted probabilities minus the one-hot target). It is clean and stable.
- **Mean squared error (MSE)** $\frac{1}{n}\sum(\hat y_i - y_i)^2$ is the standard loss for **regression** (predicting numbers, e.g. a chess evaluation score). Squaring punishes big errors much more than small ones.
- For a 10-class classifier that guesses uniformly, the starting loss should be about $\ln 10 \approx 2.303$, which is a handy sanity check (Karpathy, "A Recipe for Training Neural Networks").
- In PyTorch, `nn.CrossEntropyLoss` expects **raw logits**, not softmax outputs, because it applies log-softmax internally.

### Math, micro-step by micro-step
**Softmax of logits $z = [2, 1, 0]$:**
1. Exponentiate: $e^2 = 7.389$, $e^1 = 2.718$, $e^0 = 1$.
2. Sum: $7.389 + 2.718 + 1 = 11.107$.
3. Divide: $p = [0.665, 0.245, 0.090]$, which sums to 1.000. ✓
4. Stability trick: subtracting 2 gives $[0, -1, -2]$ and the same $p$.

**Cross-entropy when the true class is 0:**
1. Pick the true class probability: $p_0 = 0.665$.
2. $L = -\ln(0.665) = 0.408$.
3. If the model had said $p_0 = 0.99$, the loss would be $0.010$. If it had said $p_0 = 0.01$, the loss would be $4.605$. Confident and wrong is punished hard.

**Gradient with respect to the logits:**
1. The one-hot target is $y = [1, 0, 0]$.
2. $\partial L/\partial z = p - y = [-0.335, 0.245, 0.090]$.
3. Reading it: raise logit 0 (its gradient is negative, so a descent step increases it) and lower logits 1 and 2.

**MSE with predictions $[2, 4]$ and targets $[3, 7]$:**
1. Errors: $2-3 = -1$ and $4-7 = -3$.
2. Squares: $1$ and $9$.
3. Mean: $(1+9)/2 = 5$.

### Analogy
- **Softmax = splitting a pizza by enthusiasm.** Each option shouts a score, and exponentiating makes louder voices count disproportionately more. The pizza (total probability 1) is then cut in proportion. *Limit:* softmax probabilities show the model's *confidence*, which can be badly calibrated. They are not guaranteed true frequencies.
- **Cross-entropy = a weather forecaster's penalty.** A forecaster who said "1% chance of rain" on a rainy day looks far worse than one who said "60%". Cross-entropy charges $-\ln(\text{probability you gave to what actually happened})$.
- **MSE = a dartboard where distance is squared.** Missing by 3 cm costs 9 points, not 3.

### Misconceptions
- "Softmax outputs are certainties." They are model scores scaled to sum to 1. Networks are often overconfident.
- "Apply softmax, then pass the result to `CrossEntropyLoss`." That double-applies softmax and hurts training. Pass logits.
- "MSE works fine for classification." It can be used, but cross-entropy gives better gradients for probabilities (Nielsen ch. 3 shows how a sigmoid with MSE learns slowly when it is saturated).

### Sources
- Goodfellow et al., ch. 3 Probability and Information Theory — https://www.deeplearningbook.org/contents/prob.html
- d2l.ai, 2.6 Probability and Statistics — https://d2l.ai/chapter_preliminaries/probability.html
- d2l.ai, 4.1 Softmax Regression — https://d2l.ai/chapter_linear-classification/softmax-regression.html
- Stanford CS231n, "Linear classification" (softmax, cross-entropy, numerical stability) — https://cs231n.github.io/linear-classify/
- Nielsen, *Neural Networks and Deep Learning*, ch. 3 (cross-entropy vs quadratic cost) — http://neuralnetworksanddeeplearning.com/chap3.html
- PyTorch docs, `torch.nn.CrossEntropyLoss` — https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html
- Khan Academy, Statistics and probability — https://www.khanacademy.org/math/statistics-probability

---

## 6. Neuron, perceptron, activations, MLP, forward pass

### Distilled
- An **artificial neuron** computes $z = w \cdot x + b$ (a weighted sum plus a **bias**) and then applies an **activation** $a = \phi(z)$.
- Rosenblatt's **perceptron** (1958) uses a step activation that outputs 1 if $z > 0$ and 0 otherwise. Its learning rule nudges the weights only when it is wrong: $w \leftarrow w + \eta (y - \hat y) x$. It converges if the data is linearly separable.
- A single perceptron draws a **straight line (hyperplane)** between classes. It **cannot learn XOR** (Minsky & Papert 1969). Stacking layers fixes this.
- **Activations add nonlinearity.** Without them, any stack of linear layers collapses into one linear layer, because $W_2(W_1x) = (W_2W_1)x$.
- **Sigmoid:** output in (0, 1) and smooth, but it *saturates*. Its gradient is at most 0.25, which causes **vanishing gradients** in deep stacks.
- **Tanh:** output in (−1, 1) and zero-centred. Its maximum gradient is 1, but it still saturates.
- **ReLU** $\max(0,z)$: cheap and does not saturate for $z>0$. It is the default for hidden layers since about 2010–2012. A risk is "dead ReLUs", units that are stuck at 0.
- **ReLU variants:** Leaky ReLU, and GELU (used in Transformers and GPT).
- A **multilayer perceptron (MLP)**, or fully connected network, is made of layers $h^{(l)} = \phi(W^{(l)} h^{(l-1)} + b^{(l)})$. The last layer outputs logits (classification) or a number (regression).
- **Forward pass:** compute the layers in order from input to output, then compute the loss.
- **Universal approximation:** an MLP with one hidden layer and enough units can approximate any continuous function on a bounded region. That says nothing about how *easy* it is to learn (Nielsen ch. 4; Goodfellow et al. §6.4.1).
- **Parameter count** of a dense layer: $n_\text{in}\times n_\text{out} + n_\text{out}$. Example: 784→128 has 100,480 parameters.

### Math, micro-step by micro-step
**One neuron:** $x = [1, 2]$, $w = [0.5, -1]$, $b = 0.5$.
1. Weighted sum: $0.5\cdot1 + (-1)\cdot2 = -1.5$.
2. Add the bias: $z = -1.5 + 0.5 = -1$.
3. ReLU: $\max(0, -1) = 0$. Sigmoid: $1/(1+e^{1}) = 0.269$.

**Perceptron computing AND:** $w = [1, 1]$, $b = -1.5$, step activation.
1. $(0,0)$: $z = -1.5$, so the output is 0.
2. $(0,1)$ and $(1,0)$: $z = -0.5$, so the output is 0.
3. $(1,1)$: $z = 0.5$, so the output is 1. ✓ AND learned.
4. XOR would need $(0,1)\to1$, $(1,0)\to1$, $(0,0)\to0$, $(1,1)\to0$. No single straight line separates those points.

**Two-layer forward pass solving XOR** (hand-set weights, step activations):
1. Hidden unit $h_1$ = OR: $w=[1,1], b=-0.5$.
2. Hidden unit $h_2$ = NAND: $w=[-1,-1], b=1.5$.
3. Output = AND of $h_1, h_2$: $w=[1,1], b=-1.5$.
4. Input $(1,1)$: $h_1 = 1$ ($z = 1.5$), $h_2 = 0$ ($z = -0.5$), output $z = 1 + 0 - 1.5 = -0.5$, so the output is 0. ✓
5. Input $(1,0)$: $h_1=1$, $h_2=1$ ($z = 0.5$), output $z = 0.5$, so the output is 1. ✓

**Vanishing gradient:** 10 sigmoid layers, each contributing at most $0.25$, give $0.25^{10} \approx 9.5\times10^{-7}$.

### Analogy
- **Neuron = a committee member voting.** Each input is a piece of evidence, each weight is how much this member trusts that evidence (negative means distrust), and the bias is their prior mood. The activation decides whether the total is enough to "speak up".
- **Layers = an assembly line.** Early stations detect simple things (strokes in a digit), and later stations combine them into loops and lines and finally into "this is a 9" (3Blue1Brown's "But what is a neural network?" uses this digit example).
- **Nonlinearity = folding paper.** Stacking straight cuts on flat paper still gives one straight cut, but folding between cuts makes complex shapes possible.

### Misconceptions
- "More neurons always means better." More capacity can overfit and costs compute (section 9).
- "Hidden layers learn human-readable features." Sometimes partly (edge detectors in CNNs), but often not.
- "The bias is optional decoration." Without a bias, every decision boundary must pass through the origin.

### Sources
- Rosenblatt, F. (1958), "The perceptron: a probabilistic model for information storage and organization in the brain", *Psychological Review* — https://doi.org/10.1037/h0042519
- Nielsen, ch. 1 "Using neural nets to recognize handwritten digits" — http://neuralnetworksanddeeplearning.com/chap1.html
- Nielsen, ch. 4 "A visual proof that neural nets can compute any function" — http://neuralnetworksanddeeplearning.com/chap4.html
- Goodfellow et al., ch. 6 Deep Feedforward Networks — https://www.deeplearningbook.org/contents/mlp.html
- d2l.ai, 5.1 Multilayer Perceptrons — https://d2l.ai/chapter_multilayer-perceptrons/mlp.html
- Stanford CS231n, "Neural Networks Part 1: Setting up the Architecture" — https://cs231n.github.io/neural-networks-1/
- 3Blue1Brown, Neural networks series — https://www.3blue1brown.com/topics/neural-networks
- Nair & Hinton (2010), "Rectified Linear Units Improve Restricted Boltzmann Machines" — https://www.cs.toronto.edu/~hinton/absps/reluICML.pdf
- Hendrycks & Gimpel (2016), "Gaussian Error Linear Units (GELUs)" — https://arxiv.org/abs/1606.08415

---

## 7. Backpropagation derived step by step

### Distilled
- **Goal:** compute $\partial L/\partial w$ for every parameter $w$, so that gradient descent knows which way to nudge each one.
- **Backpropagation** is the chain rule applied systematically from the loss backwards through the computational graph. It reuses intermediate results, so the backward pass costs roughly the same as the forward pass, not once per parameter (Rumelhart, Hinton & Williams 1986; Goodfellow et al. §6.5).
- It is a special case of **reverse-mode automatic differentiation**. PyTorch's autograd implements it for you (Baydin et al. 2018 survey).
- **Each node only needs its local derivative.** The incoming "upstream gradient" × the local derivative gives the downstream gradient (CS231n).
- **Patterns at nodes** (CS231n):
  - an **add** gate *distributes* the gradient unchanged to its inputs
  - a **multiply** gate *swaps* the inputs (the gradient for $a$ in $a\cdot b$ is $b$ × upstream)
  - a **max/ReLU** gate *routes* the gradient to the winner, or blocks it if $z \le 0$
- **Matrix form** for a dense layer $z = Wx + b$ with upstream gradient $\delta = \partial L/\partial z$:
  - $\partial L/\partial W = \delta x^\top$
  - $\partial L/\partial b = \delta$
  - $\partial L/\partial x = W^\top\delta$
- **Nielsen's four equations** give the same result in "error $\delta^l$ per layer" notation:
  - BP1: output error
  - BP2: error moved back a layer through $W^\top$ and $\phi'$
  - BP3: bias gradient
  - BP4: weight gradient
- **Sequence of one training step:** forward (store intermediates) → loss → backward (gradients) → update → **zero the gradients** (PyTorch accumulates them).
- Karpathy's **micrograd** (about 150 lines) implements a scalar autograd engine. It is the best "build it yourself" exercise for the intermediate track.

### Math, micro-step by micro-step
**Example A: one linear neuron, squared error.** $x = 2$, $w = 0.5$, $b = 0$, target $y = 3$, learning rate $\eta = 0.1$.
1. Forward: $\hat y = wx + b = 1.0$.
2. Loss: $L = (\hat y - y)^2 = (1 - 3)^2 = 4$.
3. $\partial L/\partial \hat y = 2(\hat y - y) = -4$.
4. $\partial \hat y/\partial w = x = 2$, so by the chain rule $\partial L/\partial w = -4 \cdot 2 = -8$.
5. $\partial \hat y/\partial b = 1$, so $\partial L/\partial b = -4$.
6. Update: $w \leftarrow 0.5 - 0.1(-8) = 1.3$ and $b \leftarrow 0 - 0.1(-4) = 0.4$.
7. New forward: $\hat y = 1.3\cdot2 + 0.4 = 3.0$, so $L = 0$. (It is a coincidence that it lands exactly. Usually it takes many steps.)

**Example B: two layers with ReLU.** $x = 1$, $w_1 = 2$, $w_2 = 3$, $y = 4$, $L = \tfrac12(\hat y - y)^2$, $\eta = 0.1$.
1. Forward: $z_1 = w_1 x = 2$, $h = \text{ReLU}(z_1) = 2$, $\hat y = w_2 h = 6$.
2. Loss: $L = \tfrac12(6-4)^2 = 2$.
3. Backward, output: $\partial L/\partial \hat y = \hat y - y = 2$.
4. $\partial L/\partial w_2 = 2 \cdot h = 4$.
5. $\partial L/\partial h = 2 \cdot w_2 = 6$.
6. Through ReLU: $z_1 = 2 > 0$, so the local derivative is 1 and $\partial L/\partial z_1 = 6$.
7. $\partial L/\partial w_1 = 6 \cdot x = 6$.
8. Update: $w_2 = 3 - 0.4 = 2.6$ and $w_1 = 2 - 0.6 = 1.4$.
9. New forward: $h = 1.4$, $\hat y = 3.64$, $L = \tfrac12(0.36)^2 = 0.0648$. The loss dropped from 2 to 0.065. ✓

**Example C: micrograd-style graph.** $L = a\cdot b + c$ with $a = 2$, $b = -3$, $c = 10$.
1. Forward: $d = ab = -6$ and $L = d + c = 4$.
2. $\partial L/\partial L = 1$.
3. Add node: $\partial L/\partial d = 1$ and $\partial L/\partial c = 1$ (distributes).
4. Multiply node: $\partial L/\partial a = b \cdot 1 = -3$ and $\partial L/\partial b = a\cdot1 = 2$ (swaps).
5. Interpretation: nudging $a$ up by 0.01 lowers $L$ by about 0.03.

```python
import torch
a = torch.tensor(2.0, requires_grad=True); b = torch.tensor(-3.0, requires_grad=True)
c = torch.tensor(10.0, requires_grad=True)
L = a * b + c; L.backward()
print(a.grad, b.grad, c.grad)  # tensor(-3.) tensor(2.) tensor(1.)
```

### Analogy
- **Backprop = blame assignment after a group project.** The final grade (the loss) is known. Going backwards, each member passes blame to the people who gave them input, in proportion to how much that input influenced their part. Everyone ends up knowing how much to change.
- **Upstream × local = a relay of exchange rates.** Converting euros→dollars→yen means multiplying the rates along the way. The gradient is the "exchange rate" between a weight and the loss.
- *Limit:* the blame is *local and linear*. It says what a **tiny** nudge does, not what a big change would do.

### Misconceptions
- "Backprop is the learning algorithm." Backprop only *computes gradients*. The optimizer (SGD, Adam) does the learning.
- "Backprop computes each weight's gradient separately." Its efficiency comes from *sharing* intermediate results.
- "Gradients reset automatically each step." In PyTorch, `.grad` **accumulates**. Call `optimizer.zero_grad()` every iteration.
- "Backprop is how the brain learns." That is an open research question. Don't claim it.

### Sources
- Rumelhart, Hinton & Williams (1986), "Learning representations by back-propagating errors", *Nature* 323 — https://doi.org/10.1038/323533a0
- Nielsen, ch. 2 "How the backpropagation algorithm works" — http://neuralnetworksanddeeplearning.com/chap2.html
- Stanford CS231n, "Backpropagation, Intuitions" — https://cs231n.github.io/optimization-2/
- Goodfellow et al., §6.5 Back-Propagation — https://www.deeplearningbook.org/contents/mlp.html
- d2l.ai, 5.3 Forward Propagation, Backward Propagation, and Computational Graphs — https://d2l.ai/chapter_multilayer-perceptrons/backprop.html
- Karpathy, micrograd (GitHub) — https://github.com/karpathy/micrograd
- Karpathy, *Neural Networks: Zero to Hero* — https://karpathy.ai/zero-to-hero.html
- Baydin et al. (2018), "Automatic differentiation in machine learning: a survey", JMLR — https://arxiv.org/abs/1502.05767
- Wikipedia, "Backpropagation" (history: Linnainmaa 1970, Werbos 1974) — https://en.wikipedia.org/wiki/Backpropagation

---

## 8. Gradient descent variants and optimizers

### Distilled
- **Gradient descent:** $w \leftarrow w - \eta \nabla_w L$. The **learning rate** $\eta$ is the step size and the single most important hyperparameter (Goodfellow et al. ch. 8; Karpathy's recipe).
- **Batch GD** uses the whole dataset per step: accurate but slow. **Stochastic GD (SGD)** uses one example: noisy but cheap. **Mini-batch SGD** uses 32–512 examples and is the standard compromise. Its noise even helps escape poor regions. Its roots are in Robbins & Monro (1951).
- An **epoch** is one full pass over the training data. An **iteration** (step) is one mini-batch update.
- **Learning rate too small** means slow progress. **Too big** means the loss bounces or explodes (NaN).
- **Momentum:** keep a running "velocity" $v \leftarrow \beta v + g$ and set $w \leftarrow w - \eta v$. It smooths out zig-zags and speeds up travel along consistent directions. $\beta = 0.9$ is typical (Sutskever et al. 2013).
- **RMSProp** (Hinton's Coursera lecture 6) divides each parameter's step by a running root-mean-square of its recent gradients, giving per-parameter adaptive step sizes.
- **Adam** (Kingma & Ba 2014) combines momentum (first moment $m$) and RMSProp (second moment $v$) with **bias correction**. The defaults are $\beta_1=0.9$, $\beta_2=0.999$, $\epsilon=10^{-8}$. A typical $\eta$ is $10^{-3}$ for small nets and about $3\times10^{-4}$ for Transformers.
- **AdamW** (Loshchilov & Hutter) *decouples* weight decay from the adaptive update. It is the standard for Transformers such as our tiny GPT.
- **Learning-rate schedules:**
  - step decay
  - cosine decay
  - **warmup** (start small, then ramp up)
  - one-cycle / cyclical (Smith 2015)
- **Rule of thumb:** Adam for fast, robust results. SGD with momentum often generalises slightly better on vision tasks when it is tuned.

### Math, micro-step by micro-step
**Plain GD on $f(w) = (w-3)^2$**, $w_0 = 0$, $\eta = 0.1$. The gradient is $2(w-3)$.
1. Step 1: gradient $= 2(0-3) = -6$, so $w_1 = 0 - 0.1(-6) = 0.6$.
2. Step 2: gradient $= 2(0.6-3) = -4.8$, so $w_2 = 0.6 + 0.48 = 1.08$.
3. Step 3: gradient $= -3.84$, so $w_3 = 1.464$.
4. Pattern: the distance to 3 shrinks by a factor of $(1 - 2\eta) = 0.8$ each step: $3 \to 2.4 \to 1.92 \to 1.536$.
5. With $\eta = 1.1$, the factor is $1 - 2.2 = -1.2$: the distance *grows* and flips sign every step, so training **diverges**.

**Momentum, first two steps** (same function, $\beta=0.9$, $\eta=0.1$, $v_0=0$):
1. $g = -6$, so $v = 0.9\cdot0 + (-6) = -6$ and $w = 0 + 0.6 = 0.6$.
2. $g = -4.8$, so $v = 0.9(-6) - 4.8 = -10.2$ and $w = 0.6 + 1.02 = 1.62$. This is further than plain GD's 1.08: the ball has built up speed.

**Adam, first step** ($g = -6$, $\eta = 0.1$, $t = 1$):
1. $m = 0.9\cdot0 + 0.1\cdot(-6) = -0.6$.
2. $v = 0.999\cdot0 + 0.001\cdot36 = 0.036$.
3. Bias correction: $\hat m = -0.6/(1-0.9) = -6$ and $\hat v = 0.036/(1-0.999) = 36$.
4. Step: $\eta\,\hat m/(\sqrt{\hat v}+\epsilon) = 0.1\cdot(-6/6) = -0.1$, so $w = 0 + 0.1 = 0.1$.
5. Insight: Adam's first step is about $\eta$ in size *whatever the gradient scale*. Without bias correction, $m$ and $v$ would be biased towards 0 early on.

### Analogy
- **GD = walking downhill blindfolded with a fixed stride.** If the stride is too short, you never arrive. If it is too long, you overshoot the valley and climb the other side.
- **Mini-batch = asking a few random hikers for directions** instead of surveying everyone. It is a bit noisy but much faster.
- **Momentum = a heavy ball rolling downhill.** It keeps rolling through small bumps and doesn't zig-zag in narrow valleys.
- **Adam = a ball with smart shoes.** It takes careful steps where the ground has been bumpy (large gradient variance) and confident steps where it has been steady.

### Misconceptions
- "Adam doesn't need a learning rate." It still does. A wrong $\eta$ still fails.
- "Lower loss on training data means a better model." Only validation performance says that (section 9).
- "SGD finds the global minimum." For neural networks, there is no such guarantee. In practice, many minima found by SGD generalise well.
- "Weight decay in Adam = L2 regularization." Not exactly. That is the point of AdamW.

### Sources
- Goodfellow et al., ch. 8 Optimization for Training Deep Models — https://www.deeplearningbook.org/contents/optimization.html
- d2l.ai, ch. 12 Optimization Algorithms — https://d2l.ai/chapter_optimization/index.html
- d2l.ai, 12.6 Momentum — https://d2l.ai/chapter_optimization/momentum.html
- d2l.ai, 12.10 Adam — https://d2l.ai/chapter_optimization/adam.html
- Stanford CS231n, "Optimization: Stochastic Gradient Descent" — https://cs231n.github.io/optimization-1/
- Stanford CS231n, "Neural Networks Part 3: Learning and Evaluation" (update rules) — https://cs231n.github.io/neural-networks-3/
- Kingma & Ba (2014), "Adam: A Method for Stochastic Optimization" — https://arxiv.org/abs/1412.6980
- Loshchilov & Hutter (2017), "Decoupled Weight Decay Regularization" (AdamW) — https://arxiv.org/abs/1711.05101
- Sutskever et al. (2013), "On the importance of initialization and momentum in deep learning", ICML — https://proceedings.mlr.press/v28/sutskever13.html
- Hinton, Srivastava, Swersky, Neural Networks for ML, Lecture 6 (RMSProp) slides — https://www.cs.toronto.edu/~tijmen/csc321/slides/lecture_slides_lec6.pdf
- Robbins & Monro (1951), "A Stochastic Approximation Method" — https://doi.org/10.1214/aoms/1177729586
- Smith (2015), "Cyclical Learning Rates for Training Neural Networks" — https://arxiv.org/abs/1506.01186
- PyTorch docs, `torch.optim` — https://docs.pytorch.org/docs/stable/optim.html

---

## 9. Initialization, normalization, regularization, overfitting, splits, metrics

### Distilled

**Initialization**
- If all weights start equal, every neuron in a layer computes the same thing and gets the same gradient forever (**symmetry**). So weights must start **random**.
- Weights that are too big make activations and gradients **explode**. Weights that are too small make them **vanish**. Good schemes keep the signal variance roughly constant from layer to layer.
- **Xavier/Glorot** (2010) suits tanh/sigmoid: $\text{Var}(w) = 2/(n_\text{in}+n_\text{out})$. The uniform version uses limit $\sqrt{6/(n_\text{in}+n_\text{out})}$.
- **He/Kaiming** (2015) suits ReLU: $\text{Var}(w) = 2/n_\text{in}$. The extra 2 compensates for ReLU zeroing half of its inputs.
- PyTorch's `nn.Linear` already uses a Kaiming-uniform-style default, so beginners rarely need to change it.

**Normalization**
- **Input normalization:** scale the inputs, e.g. pixels from 0–255 to 0–1, or standardise to mean 0 and std 1 per feature.
- **Batch normalization** (2015) normalizes each feature over the mini-batch, then applies a learned scale $\gamma$ and shift $\beta$. It allows higher learning rates and has a mild regularizing effect. It behaves differently in `train()` and `eval()` mode (running statistics).
- **Layer normalization** normalizes over the features of *each example*. It does not depend on the batch, which makes it the standard in Transformers.

**Regularization and overfitting**
- **Overfitting** means low training error but high validation error: the model memorised the noise. **Underfitting** means both errors are high: the model is too simple or under-trained.
- Remedies for overfitting:
  - more data
  - data augmentation
  - weight decay
  - dropout
  - early stopping
  - a smaller model
- **L2 / weight decay** adds $\frac{\lambda}{2}\|w\|^2$ to the loss, so the gradient gains a $+\lambda w$ term and the weights shrink a little each step.
- **Dropout** (Srivastava et al. 2014) randomly zeroes units with probability $p$ during training. This acts like training a big ensemble of thinned networks. PyTorch uses *inverted* dropout (it scales survivors by $1/(1-p)$), so nothing changes at test time.
- **Early stopping:** stop when the validation loss stops improving, and keep the best checkpoint.

**Splits**
- **Train** data fits the weights. **Validation** data is used to choose hyperparameters and to early-stop. **Test** data is touched *once* for the final honest score.
- Typical splits are 80/10/10 or 70/15/15. MNIST comes with 60,000 training and 10,000 test images.
- **Leakage**, e.g. the same chess position appearing in both train and test, inflates scores.

**Metrics**
- **Accuracy** can mislead on imbalanced classes.
- **Precision** = TP/(TP+FP): "when it says yes, how often is it right?"
- **Recall** = TP/(TP+FN): "of the real yeses, how many did it catch?"
- **F1** is their harmonic mean.
- A **confusion matrix** shows which classes get confused, e.g. 4 vs 9.
- **Top-k accuracy** is useful for doodles and autocomplete.
- **Perplexity** $= e^{\text{cross-entropy}}$ is used for language models.

### Math, micro-step by micro-step
**He init:** a layer with $n_\text{in} = 256$.
1. $\text{Var} = 2/256 = 0.0078125$.
2. $\text{std} = \sqrt{0.0078125} \approx 0.0884$.
3. Sample $w \sim \mathcal N(0, 0.0884^2)$.

**Xavier uniform:** $n_\text{in}=256$, $n_\text{out}=128$, so the limit is $\sqrt{6/384} = \sqrt{0.015625} = 0.125$ and $w \sim U(-0.125, 0.125)$.

**BatchNorm on one feature** with batch values $[1, 2, 3, 6]$:
1. Mean: $\mu = 12/4 = 3$.
2. Variance: $((−2)^2 + (−1)^2 + 0^2 + 3^2)/4 = 14/4 = 3.5$.
3. Std: $\sqrt{3.5} \approx 1.871$ (ignoring the small $\epsilon$).
4. Normalize: $[-2, -1, 0, 3]/1.871 = [-1.069, -0.535, 0, 1.604]$.
5. Scale and shift with $\gamma = 2$, $\beta = 1$: $[-1.138, -0.069, 1, 4.207]$.

**Inverted dropout** with $p = 0.5$ on activations $[1, 2, 3, 4]$ and random mask $[1, 0, 1, 0]$:
1. Mask: $[1, 0, 3, 0]$.
2. Scale by $1/(1-0.5) = 2$: $[2, 0, 6, 0]$.
3. The expected value of each unit equals its original value, so evaluation uses the network without the mask.

**Weight decay:** $w = 2$, $\lambda = 0.01$, $\eta = 0.1$, data gradient $= 0$.
1. Decay gradient: $\lambda w = 0.02$.
2. Update: $w = 2 - 0.1\cdot0.02 = 1.998$. A small, steady shrink.

**Metrics** with TP = 40, FP = 10, FN = 20, TN = 30:
1. Accuracy $= (40+30)/100 = 0.70$.
2. Precision $= 40/50 = 0.80$.
3. Recall $= 40/60 = 0.667$.
4. F1 $= 2\cdot0.8\cdot0.667/(0.8+0.667) = 1.067/1.467 = 0.727$.

### Analogy
- **Initialization = tuning a guitar before playing.** If every string has the same pitch (symmetric weights), no chord is possible. If strings are way too tight or too loose (huge or tiny weights), the sound is distorted or silent.
- **Overfitting = memorising the answer key.** A student who memorised last year's exam answers scores 100% on that exam and fails a new one. The validation set is the mock exam, and the test set is the real exam, taken once.
- **Dropout = practising with random teammates missing.** Every player learns to contribute instead of relying on one star. *Limit:* it is a rough intuition, not the full ensemble theory.
- **Weight decay = a rubber band** pulling every weight gently back toward zero, so that only weights the data really needs stay large.
- **BatchNorm = grading on a curve.** The scores are re-centred and rescaled per class (batch) before being passed on.
- **Precision vs recall = a fishing net.** A fine net (high recall) catches all the fish plus lots of junk. Picking only fish by hand (high precision) misses some fish.

### Misconceptions
- "Use the test set to choose the best epoch." That leaks the test set into model selection. Use validation.
- "Dropout should be on during evaluation." Call `model.eval()`, which turns dropout off and makes BatchNorm use its running statistics.
- "99% accuracy is great." Not if 99% of the examples belong to one class. Check the confusion matrix and per-class recall.
- "Zero initialization is a safe default." It breaks symmetry-breaking for weights. Zero is fine for *biases*.
- "BatchNorm works because of 'internal covariate shift'." That was the original motivation, but later work disputes the explanation. Present it as "it empirically helps; the reasons are debated" (Santurkar et al. 2018).

### Sources
- Glorot & Bengio (2010), "Understanding the difficulty of training deep feedforward neural networks", AISTATS — https://proceedings.mlr.press/v9/glorot10a.html
- He, Zhang, Ren, Sun (2015), "Delving Deep into Rectifiers" — https://arxiv.org/abs/1502.01852
- Ioffe & Szegedy (2015), "Batch Normalization" — https://arxiv.org/abs/1502.03167
- Ba, Kiros, Hinton (2016), "Layer Normalization" — https://arxiv.org/abs/1607.06450
- Santurkar et al. (2018), "How Does Batch Normalization Help Optimization?" — https://arxiv.org/abs/1805.11604
- Srivastava et al. (2014), "Dropout: A Simple Way to Prevent Neural Networks from Overfitting", JMLR 15 — https://jmlr.org/papers/v15/srivastava14a.html
- Goodfellow et al., ch. 7 Regularization for Deep Learning — https://www.deeplearningbook.org/contents/regularization.html
- d2l.ai, 5.4 Numerical Stability and Initialization — https://d2l.ai/chapter_multilayer-perceptrons/numerical-stability-and-init.html
- d2l.ai, 5.6 Dropout — https://d2l.ai/chapter_multilayer-perceptrons/dropout.html
- d2l.ai, 3.7 Weight Decay — https://d2l.ai/chapter_linear-regression/weight-decay.html
- d2l.ai, 3.6 Generalization — https://d2l.ai/chapter_linear-regression/generalization.html
- d2l.ai, 8.5 Batch Normalization — https://d2l.ai/chapter_convolutional-modern/batch-norm.html
- Stanford CS231n, "Neural Networks Part 2: Setting up the Data and the Loss" — https://cs231n.github.io/neural-networks-2/
- PyTorch docs, `torch.nn.init` — https://docs.pytorch.org/docs/stable/nn.init.html
- scikit-learn, "Metrics and scoring" — https://scikit-learn.org/stable/modules/model_evaluation.html
- Google ML Crash Course, "Accuracy, precision, recall" — https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall
- Stanford CS229 lecture notes (bias–variance, regularization) — https://cs229.stanford.edu/main_notes.pdf
- Zhang et al. (2017), "Understanding deep learning requires rethinking generalization" — https://arxiv.org/abs/1611.03530

---

## 10. The PyTorch training loop

### Distilled
- A **tensor** (`torch.Tensor`) is a NumPy-like n-D array that can live on a GPU (`.to("cuda")`) and can record operations for autograd.
- **Autograd:** a tensor with `requires_grad=True` records the graph of operations. `loss.backward()` fills `.grad` for every leaf parameter. Wrap inference in `torch.no_grad()` (or `torch.inference_mode()`).
- **`nn.Module`** is the base class for models. Define the layers in `__init__` and the computation in `forward`. `model.parameters()` yields all trainable weights.
- **Loss functions** live in `torch.nn`: `nn.CrossEntropyLoss` for classification (takes logits) and `nn.MSELoss` for regression.
- **Optimizers** live in `torch.optim`: `SGD`, `Adam`, `AdamW`.
- **`Dataset`** defines `__len__` and `__getitem__`. **`DataLoader`** wraps it to give **shuffled mini-batches** (`batch_size`, `shuffle=True` for training). `torchvision.datasets.MNIST` gives you MNIST in one line.
- **The five-line heart of training**, repeated for every batch:
  1. `pred = model(X)`
  2. `loss = loss_fn(pred, y)`
  3. `optimizer.zero_grad()`
  4. `loss.backward()`
  5. `optimizer.step()`
- Switch with **`model.train()`** for training and **`model.eval()`** for validation and testing. This matters for dropout and BatchNorm.
- **Device:** put the model *and* every batch on the same device. Our companion code is CPU-friendly by default.
- **Reproducibility:** `torch.manual_seed(0)`. Save weights with `torch.save(model.state_dict(), path)`.
- The official "Learn the Basics" tutorial walks through exactly this sequence: tensors → datasets → transforms → model → autograd → optimization → save/load.

### Math, micro-step by micro-step: what one iteration does numerically
Use the model $\hat y = wx$ with $w=0.5$, one batch $x=[1,2]$, $y=[2,4]$, MSE loss, SGD with $\eta=0.1$:
1. Forward: $\hat y = [0.5, 1.0]$.
2. Loss: $((0.5-2)^2 + (1-4)^2)/2 = (2.25 + 9)/2 = 5.625$.
3. `zero_grad`: $w.\text{grad} = 0$.
4. `backward`: $\partial L/\partial w = \frac{1}{2}\sum 2(\hat y_i - y_i)x_i = (-1.5\cdot1) + (-3\cdot2) = -7.5$.
5. `step`: $w = 0.5 - 0.1(-7.5) = 1.25$.
6. Next forward: $\hat y = [1.25, 2.5]$, so the loss is $(0.5625 + 2.25)/2 = 1.406$. It went down. ✓ (The true $w$ is 2.)

```python
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

train_ds = datasets.MNIST("data", train=True, download=True, transform=transforms.ToTensor())
train_dl = DataLoader(train_ds, batch_size=64, shuffle=True)

model = nn.Sequential(nn.Flatten(), nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 10))
loss_fn = nn.CrossEntropyLoss()                 # expects raw logits
opt = torch.optim.Adam(model.parameters(), lr=1e-3)

for epoch in range(2):
    model.train()
    for X, y in train_dl:
        loss = loss_fn(model(X), y)
        opt.zero_grad()
        loss.backward()
        opt.step()
    print(f"epoch {epoch}: last batch loss {loss.item():.3f}")
```
(The project tracks' companion code is the tested source of truth. This snippet is illustrative.)

### Analogy
- **The training loop = a practice routine:** attempt (forward), get graded (loss), wipe the old notes (zero_grad), work out what went wrong (backward), adjust (step). Repeat for every flash-card stack (batch) and every lap through the deck (epoch).
- **DataLoader = a card dealer** who shuffles the deck and hands out stacks of 64 cards.
- **`nn.Module` = a LEGO baseplate:** you snap layers onto it, and `forward` describes how the pieces connect.

### Misconceptions
- "Forgetting `zero_grad` is harmless." The gradients accumulate across steps and training goes haywire.
- "`loss` is a Python number." It is a tensor attached to the graph. Use `loss.item()` for logging, or you keep graphs alive and leak memory.
- "`model.eval()` disables gradients." It does not. It changes layer behaviour. Use `torch.no_grad()` to skip gradient tracking.
- "Softmax must be the last layer of the model." For training with `CrossEntropyLoss`, output logits. Apply softmax only for displaying probabilities.

### Sources
- PyTorch Tutorials, "Learn the Basics" — https://docs.pytorch.org/tutorials/beginner/basics/intro.html
- PyTorch Tutorials, "Tensors" — https://docs.pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html
- PyTorch Tutorials, "Datasets & DataLoaders" — https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html
- PyTorch Tutorials, "Build the Neural Network" — https://docs.pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html
- PyTorch Tutorials, "Automatic Differentiation with torch.autograd" — https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html
- PyTorch Tutorials, "Optimizing Model Parameters" — https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- PyTorch docs, `torch.nn.Module` — https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html
- PyTorch docs, `torch.utils.data` — https://docs.pytorch.org/docs/stable/data.html
- d2l.ai (PyTorch edition) — https://d2l.ai/

---

## 11. Debugging training

### Distilled
- **Neural net training "fails silently".** Code with bugs often still runs and produces a mediocre model, so debugging has to be deliberate (Karpathy, "A Recipe for Training Neural Networks", 2019).
- **Look at the data first.** Plot samples with their labels, and check the label distribution, the value ranges after normalization, and that images aren't transposed.
- **Check the initial loss.** For $C$ balanced classes with cross-entropy, expect $\ln C$ (2.303 for 10 classes). Something far off points to a bad init or a wrong loss input (e.g. softmax applied twice).
- **Overfit a single small batch.** A correct model and loop should reach about 0 loss on 1 batch of 2–32 examples. If it can't, there is a bug, not a data problem.
- **Start simple:**
  - a tiny model
  - no augmentation or regularization
  - a fixed seed
  - then add one thing at a time
- **Watch the curves:**
  - train and val loss both high → underfitting, so use a bigger model or train longer
  - train low and val rising → overfitting, so regularize (section 9)
  - loss → NaN → lower the LR, clip the gradients, check for $\log 0$ or division by zero
  - loss flat → LR too low, dead ReLUs, or a forgotten `zero_grad`/`step`
- **Learning-rate sweep:** try values a factor of about 3–10 apart (1e-4, 3e-4, 1e-3, 3e-3). Plot loss vs LR (Smith 2015).
- **Gradient checking:** compare autograd with the finite difference $(L(w+h) - L(w-h))/2h$. In PyTorch, use `torch.autograd.gradcheck` with float64.
- **Shapes:** print shapes at every layer the first time through. Broadcasting can silently turn a `(N,)` minus `(N,1)` into an `(N,N)` matrix.
- **Classic PyTorch bugs:**
  - forgetting `model.eval()` during validation
  - labels as floats for `CrossEntropyLoss` (it needs `long` class indices)
  - not shuffling the training data
  - data and model on different devices
  - mixing up `view` and `permute`
- **Gradient clipping** (`torch.nn.utils.clip_grad_norm_`) prevents exploding gradients, especially in RNNs and Transformers.
- **Visualise** activations and gradient norms per layer. Tiny norms mean vanishing gradients, and huge norms mean exploding gradients (CS231n "Neural Networks Part 3" covers babysitting the learning process).

### Math, micro-step by micro-step: numerical gradient check
Check the gradient of $L(w) = w^3$ at $w = 2$.
1. Analytic: $L'(w) = 3w^2 = 12$.
2. Choose $h = 10^{-3}$.
3. $L(2.001) = 8.012006001$ and $L(1.999) = 7.988005999$.
4. Centered difference: $(8.012006001 - 7.988005999)/0.002 = 0.024000002/0.002 = 12.000001$.
5. Relative error: $|12.000001 - 12| / 12 \approx 8\times10^{-8}$, which is tiny, so it passes. CS231n suggests a relative error below about $10^{-7}$ is excellent, and above about $10^{-2}$ usually means a bug.

**Initial loss check:** 10 classes with a uniform guess gives $p = 0.1$ each, so $L = -\ln 0.1 = 2.303$. If the first batch shows $L = 25$, the logits are far too large (bad init or unscaled inputs).

### Analogy
- **Debugging training = a doctor's checkup.** Take the vital signs first (initial loss, shapes, data samples). Then do a stress test (overfit one batch). Then read the long-term chart (loss curves). Treat one thing at a time so you know which treatment worked.
- **Overfitting one batch = checking that the car can drive around the block** before you plan a road trip. If it can't, the engine (code) is broken.
- **NaN loss = a smoke alarm.** It doesn't tell you where the fire is, only that something is very wrong (usually the learning rate is too high, or there's a log of zero).

### Misconceptions
- "If the code runs, the model is correct." Silent bugs are the norm in DL.
- "Bad results mean we need a bigger model." Check the data and the pipeline first. Most failures are bugs or data issues.
- "Tweak many hyperparameters at once to save time." You won't know which change mattered. Change one thing at a time.
- "Validation loss going up slightly means stop immediately." Use patience (several epochs) and keep the best checkpoint.

### Sources
- Karpathy (2019), "A Recipe for Training Neural Networks" — https://karpathy.github.io/2019/04/25/recipe/
- Stanford CS231n, "Neural Networks Part 3: Learning and Evaluation" (gradient checks, sanity checks, babysitting learning) — https://cs231n.github.io/neural-networks-3/
- Goodfellow et al., ch. 11 Practical Methodology — https://www.deeplearningbook.org/contents/guidelines.html
- PyTorch docs, `torch.autograd.gradcheck` — https://docs.pytorch.org/docs/stable/generated/torch.autograd.gradcheck.gradcheck.html
- PyTorch docs, `clip_grad_norm_` — https://docs.pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html
- Nielsen, ch. 5 "Why are deep neural networks hard to train?" — http://neuralnetworksanddeeplearning.com/chap5.html
- Google, "Deep Learning Tuning Playbook" — https://github.com/google-research/tuning_playbook

---

## Notes for lesson writers (curriculum mapping)

| Section here | Suggested track and lesson |
|---|---|
| 1 | Beginner L1 "What is AI?" (with the interactive timeline) |
| 2 | Beginner L2–L3 "Python you need", "NumPy arrays and shapes" |
| 3 | Beginner L4 "Vectors and the dot product", L5 "Matrices" |
| 4 | Beginner L6 "Slopes and derivatives", L7 "Chain rule and gradients" |
| 5 | Beginner L8 "Probability, softmax, loss functions" |
| 6 | Beginner L9 "The neuron", L10 "Building an MLP" |
| 7 | Intermediate L1 "Backprop by hand", L2 "Build micrograd" |
| 8 | Intermediate L3 "Gradient descent & optimizers" |
| 9 | Intermediate L4 "Init & normalization", L5 "Overfitting & regularization", L6 "Evaluation & metrics" |
| 10 | Intermediate L7 "The PyTorch training loop" (bridge to the MNIST project) |
| 11 | Intermediate L8 "Debugging training" |

**Analogy accuracy guardrails** (follow the review rubric: analogies must not mislead):
- Always say where the analogy breaks: the "Limit:" notes above.
- Never say that neural networks "think" or "understand". Say "learn patterns from data".
- Never present the brain analogy as fact.

---

## 12. Bibliography (deduplicated)

### Textbooks and course notes
1. Goodfellow, I., Bengio, Y., Courville, A. (2016). *Deep Learning*. MIT Press. https://www.deeplearningbook.org/
   - ch. 1 https://www.deeplearningbook.org/contents/intro.html
   - ch. 2 https://www.deeplearningbook.org/contents/linear_algebra.html
   - ch. 3 https://www.deeplearningbook.org/contents/prob.html
   - ch. 4 https://www.deeplearningbook.org/contents/numerical.html
   - ch. 5 https://www.deeplearningbook.org/contents/ml.html
   - ch. 6 https://www.deeplearningbook.org/contents/mlp.html
   - ch. 7 https://www.deeplearningbook.org/contents/regularization.html
   - ch. 8 https://www.deeplearningbook.org/contents/optimization.html
   - ch. 11 https://www.deeplearningbook.org/contents/guidelines.html
2. Zhang, A., Lipton, Z. C., Li, M., Smola, A. J. *Dive into Deep Learning*. Cambridge University Press / d2l.ai. https://d2l.ai/
   - Introduction https://d2l.ai/chapter_introduction/index.html
   - Data manipulation https://d2l.ai/chapter_preliminaries/ndarray.html
   - Linear algebra https://d2l.ai/chapter_preliminaries/linear-algebra.html
   - Calculus https://d2l.ai/chapter_preliminaries/calculus.html
   - Autograd https://d2l.ai/chapter_preliminaries/autograd.html
   - Probability https://d2l.ai/chapter_preliminaries/probability.html
   - Softmax regression https://d2l.ai/chapter_linear-classification/softmax-regression.html
   - MLP https://d2l.ai/chapter_multilayer-perceptrons/mlp.html
   - Backprop https://d2l.ai/chapter_multilayer-perceptrons/backprop.html
   - Init https://d2l.ai/chapter_multilayer-perceptrons/numerical-stability-and-init.html
   - Dropout https://d2l.ai/chapter_multilayer-perceptrons/dropout.html
   - Weight decay https://d2l.ai/chapter_linear-regression/weight-decay.html
   - Generalization https://d2l.ai/chapter_linear-regression/generalization.html
   - BatchNorm https://d2l.ai/chapter_convolutional-modern/batch-norm.html
   - Optimization https://d2l.ai/chapter_optimization/index.html
   - Momentum https://d2l.ai/chapter_optimization/momentum.html
   - Adam https://d2l.ai/chapter_optimization/adam.html
3. Nielsen, M. (2015). *Neural Networks and Deep Learning*. Determination Press. http://neuralnetworksanddeeplearning.com/
   - ch. 1 http://neuralnetworksanddeeplearning.com/chap1.html
   - ch. 2 http://neuralnetworksanddeeplearning.com/chap2.html
   - ch. 3 http://neuralnetworksanddeeplearning.com/chap3.html
   - ch. 4 http://neuralnetworksanddeeplearning.com/chap4.html
   - ch. 5 http://neuralnetworksanddeeplearning.com/chap5.html
4. Stanford CS231n, *Convolutional Neural Networks for Visual Recognition*, course notes:
   - Python/NumPy https://cs231n.github.io/python-numpy-tutorial/
   - Linear classify https://cs231n.github.io/linear-classify/
   - Optimization 1 https://cs231n.github.io/optimization-1/
   - Backprop https://cs231n.github.io/optimization-2/
   - NN 1 https://cs231n.github.io/neural-networks-1/
   - NN 2 https://cs231n.github.io/neural-networks-2/
   - NN 3 https://cs231n.github.io/neural-networks-3/
5. Ng, A., Ma, T. Stanford CS229 *Machine Learning* lecture notes. https://cs229.stanford.edu/main_notes.pdf

### Video courses and code
6. Sanderson, G. (3Blue1Brown):
   - Neural networks https://www.3blue1brown.com/topics/neural-networks
   - Linear algebra https://www.3blue1brown.com/topics/linear-algebra
   - Calculus https://www.3blue1brown.com/topics/calculus
7. Karpathy, A. *Neural Networks: Zero to Hero*. https://karpathy.ai/zero-to-hero.html
8. Karpathy, A. *micrograd*. https://github.com/karpathy/micrograd
9. Karpathy, A. (2019). "A Recipe for Training Neural Networks". https://karpathy.github.io/2019/04/25/recipe/
10. Google Research, "Deep Learning Tuning Playbook". https://github.com/google-research/tuning_playbook

### Math prerequisites
11. Khan Academy:
    - Linear algebra https://www.khanacademy.org/math/linear-algebra
    - Calculus 1 https://www.khanacademy.org/math/calculus-1
    - Multivariable calculus https://www.khanacademy.org/math/multivariable-calculus
    - Statistics & probability https://www.khanacademy.org/math/statistics-probability

### Official documentation
12. Python Software Foundation, *The Python Tutorial*. https://docs.python.org/3/tutorial/index.html
13. NumPy:
    - absolute basics https://numpy.org/doc/stable/user/absolute_beginners.html
    - broadcasting https://numpy.org/doc/stable/user/basics.broadcasting.html
    - copies & views https://numpy.org/doc/stable/user/basics.copies.html
    - matmul https://numpy.org/doc/stable/reference/generated/numpy.matmul.html
14. PyTorch Tutorials, "Learn the Basics":
    - intro https://docs.pytorch.org/tutorials/beginner/basics/intro.html
    - tensors https://docs.pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html
    - data https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html
    - model https://docs.pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html
    - autograd https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html
    - optimization https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
15. PyTorch API docs:
    - CrossEntropyLoss https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html
    - optim https://docs.pytorch.org/docs/stable/optim.html
    - nn.init https://docs.pytorch.org/docs/stable/nn.init.html
    - nn.Module https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html
    - data https://docs.pytorch.org/docs/stable/data.html
    - gradcheck https://docs.pytorch.org/docs/stable/generated/torch.autograd.gradcheck.gradcheck.html
    - clip_grad_norm_ https://docs.pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html
16. scikit-learn, "Metrics and scoring". https://scikit-learn.org/stable/modules/model_evaluation.html
17. Google, Machine Learning Crash Course:
    - course home https://developers.google.com/machine-learning/crash-course
    - classification metrics https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall

### Original papers
18. McCulloch, W. S., Pitts, W. (1943). A logical calculus of the ideas immanent in nervous activity. https://doi.org/10.1007/BF02478259
19. Turing, A. M. (1950). Computing Machinery and Intelligence. *Mind*. https://doi.org/10.1093/mind/LIX.236.433
20. McCarthy, J., Minsky, M., Rochester, N., Shannon, C. (1955). A Proposal for the Dartmouth Summer Research Project on AI. http://jmc.stanford.edu/articles/dartmouth/dartmouth.pdf
21. Robbins, H., Monro, S. (1951). A Stochastic Approximation Method. https://doi.org/10.1214/aoms/1177729586
22. Rosenblatt, F. (1958). The perceptron. *Psychological Review* 65(6). https://doi.org/10.1037/h0042519
23. Samuel, A. L. (1959). Some Studies in Machine Learning Using the Game of Checkers. https://doi.org/10.1147/rd.33.0210
24. Rumelhart, D. E., Hinton, G. E., Williams, R. J. (1986). Learning representations by back-propagating errors. *Nature* 323. https://doi.org/10.1038/323533a0
25. Hochreiter, S., Schmidhuber, J. (1997). Long Short-Term Memory. https://doi.org/10.1162/neco.1997.9.8.1735
26. LeCun, Y., Bottou, L., Bengio, Y., Haffner, P. (1998). Gradient-based learning applied to document recognition. https://doi.org/10.1109/5.726791
27. Hinton, G. E., Osindero, S., Teh, Y.-W. (2006). A fast learning algorithm for deep belief nets. https://doi.org/10.1162/neco.2006.18.7.1527
28. Deng, J. et al. (2009). ImageNet: A large-scale hierarchical image database. https://doi.org/10.1109/CVPR.2009.5206848
29. Glorot, X., Bengio, Y. (2010). Understanding the difficulty of training deep feedforward neural networks. https://proceedings.mlr.press/v9/glorot10a.html
30. Nair, V., Hinton, G. E. (2010). Rectified Linear Units Improve Restricted Boltzmann Machines. https://www.cs.toronto.edu/~hinton/absps/reluICML.pdf
31. Krizhevsky, A., Sutskever, I., Hinton, G. E. (2012). ImageNet Classification with Deep Convolutional Neural Networks. https://papers.nips.cc/paper/2012/hash/c399862d3b9d6b76c8436e924a68c45b-Abstract.html
32. Hinton, G., Srivastava, N., Swersky, K. Lecture 6 (RMSProp), Neural Networks for Machine Learning. https://www.cs.toronto.edu/~tijmen/csc321/slides/lecture_slides_lec6.pdf
33. Sutskever, I., Martens, J., Dahl, G., Hinton, G. (2013). On the importance of initialization and momentum in deep learning. https://proceedings.mlr.press/v28/sutskever13.html
34. Kingma, D. P., Ba, J. (2014). Adam: A Method for Stochastic Optimization. https://arxiv.org/abs/1412.6980
35. Srivastava, N. et al. (2014). Dropout. *JMLR* 15. https://jmlr.org/papers/v15/srivastava14a.html
36. Ioffe, S., Szegedy, C. (2015). Batch Normalization. https://arxiv.org/abs/1502.03167
37. He, K., Zhang, X., Ren, S., Sun, J. (2015). Delving Deep into Rectifiers. https://arxiv.org/abs/1502.01852
38. He, K. et al. (2015). Deep Residual Learning for Image Recognition. https://arxiv.org/abs/1512.03385
39. Smith, L. N. (2015). Cyclical Learning Rates for Training Neural Networks. https://arxiv.org/abs/1506.01186
40. Baydin, A. G. et al. (2018). Automatic differentiation in machine learning: a survey. https://arxiv.org/abs/1502.05767
41. Silver, D. et al. (2016). Mastering the game of Go with deep neural networks and tree search. https://doi.org/10.1038/nature16961
42. Ba, J. L., Kiros, J. R., Hinton, G. E. (2016). Layer Normalization. https://arxiv.org/abs/1607.06450
43. Hendrycks, D., Gimpel, K. (2016). Gaussian Error Linear Units. https://arxiv.org/abs/1606.08415
44. Zhang, C. et al. (2017). Understanding deep learning requires rethinking generalization. https://arxiv.org/abs/1611.03530
45. Vaswani, A. et al. (2017). Attention Is All You Need. https://arxiv.org/abs/1706.03762
46. Loshchilov, I., Hutter, F. (2017). Decoupled Weight Decay Regularization. https://arxiv.org/abs/1711.05101
47. Santurkar, S. et al. (2018). How Does Batch Normalization Help Optimization? https://arxiv.org/abs/1805.11604

### History and awards (secondary)
48. ACM, 2018 A.M. Turing Award (Bengio, Hinton, LeCun). https://awards.acm.org/about/2018-turing
49. Nobel Prize in Physics 2024 (Hopfield, Hinton). https://www.nobelprize.org/prizes/physics/2024/summary/
50. Wikipedia:
    - History of artificial intelligence https://en.wikipedia.org/wiki/History_of_artificial_intelligence
    - Perceptrons (book) https://en.wikipedia.org/wiki/Perceptrons_%28book%29
    - AI winter https://en.wikipedia.org/wiki/AI_winter
    - Backpropagation https://en.wikipedia.org/wiki/Backpropagation
