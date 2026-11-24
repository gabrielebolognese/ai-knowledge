# Research 02: Architectures (CNN, RNN/LSTM/GRU, Attention, Transformers, Tokenization) and Datasets for Each Project

> **Purpose.** This file is the sourced backbone of the **advanced** track and of four project tracks: **handwritten digits + letters**, **doodles**, **small texts** and **code autocompletion**. The chess engine has its own research file. It uses the same structure as `01-foundations.md`:
> **Distilled** (short original summary) · **Math, micro-step by micro-step** (with a tiny worked example checked by hand) · **Analogy** (with its limits) · **Misconceptions** · **Sources**.
>
> Lesson writers: the wording here is original and paraphrases the sources. Do not copy text from the sources. Cite them with links in the lesson's footnotes. Math uses `$...$` (KaTeX). If you change a worked example's numbers, recompute them.
>
> Research date: 2026-11-24. The dataset section records what was verified that day and what stays uncertain (licences especially). Numbers labelled **"expected"** are targets for the companion code. The "Verify all companion code runs" step must confirm them on a real CPU, and the lessons must quote the measured numbers, not these estimates.

---

## Table of contents

1. [Convolutional neural networks (CNNs)](#1-convolutional-neural-networks-cnns)
2. [Landmark CNNs: LeNet-5, AlexNet, ResNet](#2-landmark-cnns-lenet-5-alexnet-resnet)
3. [Recurrent networks: RNN, LSTM, GRU](#3-recurrent-networks-rnn-lstm-gru)
4. [Neural language models: Bengio 2003 → makemore](#4-neural-language-models-bengio-2003--makemore)
5. [Attention: Bahdanau 2014 → scaled dot-product attention](#5-attention-bahdanau-2014--scaled-dot-product-attention)
6. [The Transformer and GPT (decoder-only) models](#6-the-transformer-and-gpt-decoder-only-models)
7. [Tokenization: characters, words, BPE, byte-level BPE](#7-tokenization-characters-words-bpe-byte-level-bpe)
8. [Sampling from a language model: temperature, top-k, top-p](#8-sampling-from-a-language-model-temperature-top-k-top-p)
9. [PyTorch module reference cheat-sheet](#9-pytorch-module-reference-cheat-sheet)
10. [Datasets: URL, licence, size, format, loading](#10-datasets-url-licence-size-format-loading)
11. [Recommended CPU-sized models and expected results per project](#11-recommended-cpu-sized-models-and-expected-results-per-project)
12. [Teaching order and common pitfalls](#12-teaching-order-and-common-pitfalls)
13. [Bibliography (deduplicated)](#13-bibliography-deduplicated)

---

## 1. Convolutional neural networks (CNNs)

### Distilled
- A fully-connected (MLP) layer on a 28×28 image treats every pixel as an unrelated input. It does not know that neighbouring pixels belong together, and a "7" moved two pixels to the right looks like a completely new input to it.
- A **convolutional layer** slides a small grid of weights (a **kernel** or **filter**, e.g. 3×3) over the image. At each position it computes one number: the weighted sum of the pixels under the kernel plus a bias. The grid of all those numbers is a **feature map** (CS231n; d2l.ai ch. 7).
- Two ideas make CNNs work:
  - **Local connectivity**: each output looks only at a small patch, its **receptive field**.
  - **Weight sharing**: the *same* kernel is used at every position, so a "vertical edge detector" learned in one corner works everywhere. This is what gives approximate **translation equivariance**: shift the input and the feature map shifts with it.
- A layer has many kernels (e.g. 32). Each produces one output **channel**. A kernel in the next layer spans *all* input channels: a 3×3 kernel over 32 channels has 3×3×32 weights.
- **Pooling** (e.g. 2×2 max-pool, stride 2) halves the width and height by keeping the biggest value in each 2×2 block. It makes the network cheaper and a little tolerant to small shifts.
- Stacking conv → ReLU → pool repeatedly builds a hierarchy: early layers respond to edges and strokes, middle layers to corners and loops, late layers to whole parts ("the closed loop of a 9") (Zeiler & Fergus 2014 visualized this).
- At the end, the feature maps are **flattened** and fed into one or two fully-connected layers that output class scores (logits), trained with cross-entropy exactly as in `01-foundations.md`.
- What PyTorch calls "convolution" is mathematically **cross-correlation**: the kernel is not flipped. Because the kernel is learned, this does not matter, but mention it in a footnote for mathematically curious learners (d2l.ai §7.2; PyTorch `Conv2d` docs).

### Math, micro-step by micro-step

**Step 1: one output value.** For a single-channel input $X$ and a $k\times k$ kernel $K$ with bias $b$, the output at row $i$, column $j$ is:

$$Y_{i,j} = b + \sum_{u=0}^{k-1}\sum_{v=0}^{k-1} K_{u,v}\, X_{i+u,\; j+v}$$

Read it as: "lay the kernel on the image with its top-left corner at $(i,j)$, multiply the overlapping numbers pairwise, add them all up, add the bias."

**Step 2: a worked example** (bias 0, stride 1, no padding).

Input $X$ (4×4), and a vertical-edge kernel $K$ (3×3):

```
X =  1 2 0 1        K =  1 0 -1
     0 1 3 1             1 0 -1
     2 1 0 0             1 0 -1
     1 0 1 2
```

The kernel adds the left column of the patch and subtracts the right column.
- $Y_{0,0}$: patch rows 0–2, cols 0–2. Left column $1+0+2=3$, right column $0+3+0=3$, so $3-3=\mathbf{0}$.
- $Y_{0,1}$: cols 1–3. Left $2+1+1=4$, right $1+1+0=2$, so $\mathbf{2}$.
- $Y_{1,0}$: rows 1–3, cols 0–2. Left $0+2+1=3$, right $3+0+1=4$, so $\mathbf{-1}$.
- $Y_{1,1}$: rows 1–3, cols 1–3. Left $1+1+0=2$, right $1+0+2=3$, so $\mathbf{-1}$.

$$Y=\begin{pmatrix}0 & 2\\ -1 & -1\end{pmatrix}$$

A 4×4 input and a 3×3 kernel give a 2×2 output, because the kernel fits in only 2 positions across and 2 down.

**Step 3: the output-size formula.** For input width $W$, kernel $K$, padding $P$ (zeros added on each side) and stride $S$ (how far the kernel jumps):

$$W_{\text{out}} = \left\lfloor \frac{W - K + 2P}{S} \right\rfloor + 1$$

Micro-steps: $W+2P$ is the padded width. Subtract $K$ to get how much room the kernel has to slide. Divide by $S$ to count the jumps. Add 1 for the starting position. The same formula applies to height (Dumoulin & Visin 2016; CS231n; PyTorch `Conv2d` "Shape" section, which also adds a dilation term).

Checks:
- Example above: $\lfloor(4-3+0)/1\rfloor+1 = 2$. ✓
- MNIST with "same" padding: $W=28, K=3, P=1, S=1$ gives $(28-3+2)/1+1 = 28$. The size is preserved.
- 2×2 max-pool with stride 2: $(28-2)/2+1 = 14$; again: $(14-2)/2+1=7$.
- LeNet-5's first layer: 32×32 input, 5×5 kernel, no padding gives $32-5+1=28$ (LeCun et al. 1998).
- AlexNet's first layer: $K=11, S=4, P=0$. With a 227-pixel input, $(227-11)/4+1 = 55$, the paper's 55×55 maps. The paper says 224, which does not divide evenly; this is a well-known erratum and a nice "check the arithmetic yourself" exercise (CS231n notes discuss it).

**Step 4: parameter count.** A conv layer with $C_{in}$ input channels, $C_{out}$ kernels of size $K\times K$:

$$\text{params} = (K\cdot K\cdot C_{in} + 1)\cdot C_{out}$$

The $+1$ is each kernel's bias. Example: `Conv2d(32, 64, 3)` gives $(3\cdot3\cdot32+1)\cdot 64 = 289\cdot 64 = 18{,}496$.

Compare: a fully-connected layer from a 28×28 image to 32 hidden units already has $784\cdot32+32 = 25{,}120$ weights, and it would need a separate weight for every pixel position. Weight sharing is why CNNs are both smaller and better at images.

**Step 5: receptive field.** Two stacked 3×3 convs see a 5×5 patch of the original image, and three see 7×7. Two 3×3 layers cost $2\cdot 9 C^2 = 18C^2$ weights versus $25C^2$ for one 5×5, and they add an extra non-linearity. This is the VGG argument (Simonyan & Zisserman 2014), and it is why modern CNNs use mostly 3×3 kernels.

### Analogy
- **Flashlight in a dark room.** The kernel is a small flashlight with a stencil. You sweep it across the picture row by row, and at each spot a meter reads "how much does what I see match my stencil?" The feature map is the sheet of meter readings. *Limit:* real kernels are learned, not designed, and many look nothing like a neat stencil.
- **Pooling = summarising a neighbourhood report.** "In this 2×2 block, the strongest edge signal was 0.9." You lose exact position and keep "it was there". *Limit:* that lost position matters for some tasks (e.g. segmentation), which is why some modern nets avoid pooling.

### Misconceptions
- "CNNs are rotation-invariant." They are not. They are roughly shift-tolerant only. A 6 rotated 180° looks like a 9, and EMNIST's transposed images (§10.2) really do confuse a model that was trained on a different orientation.
- "More filters is always better." On 28×28 grayscale data, 32–64 filters per layer is plenty. Beyond that you mostly add CPU time.
- "Padding adds information." Zero-padding only keeps the size and lets border pixels be used as often as central ones.

### Sources
CS231n *Convolutional Neural Networks* notes https://cs231n.github.io/convolutional-networks/ · d2l.ai ch. 7 https://d2l.ai/chapter_convolutional-neural-networks/index.html · Dumoulin & Visin, *A guide to convolution arithmetic* https://arxiv.org/abs/1603.07285 · PyTorch `Conv2d` https://docs.pytorch.org/docs/stable/generated/torch.nn.Conv2d.html · PyTorch `MaxPool2d` https://docs.pytorch.org/docs/stable/generated/torch.nn.MaxPool2d.html · Zeiler & Fergus 2014 https://arxiv.org/abs/1311.2901 · Simonyan & Zisserman (VGG) https://arxiv.org/abs/1409.1556 · Wikipedia https://en.wikipedia.org/wiki/Convolutional_neural_network

---

## 2. Landmark CNNs: LeNet-5, AlexNet, ResNet

### Distilled
- **LeNet-5 (LeCun, Bottou, Bengio, Haffner 1998)**, *Gradient-Based Learning Applied to Document Recognition*, Proc. IEEE 86(11):2278–2324.
  - Input: 32×32 grayscale. Layers: conv 5×5 (6 maps) → subsample → conv 5×5 (16 maps) → subsample → fully-connected 120 → 84 → 10 outputs. About 60k trainable parameters.
  - The same paper introduced the **MNIST** benchmark built from NIST data (§10.1) and reported about 0.95% test error for LeNet-5 (0.8% with distortion-augmented training).
  - It was deployed to read bank cheques. This is the historical hook for the digits project.
- **AlexNet (Krizhevsky, Sutskever, Hinton 2012)**, NeurIPS.
  - It won ILSVRC-2012 with 15.3% top-5 error, against 26.2% for the runner-up.
  - About 60M parameters, 5 conv + 3 fully-connected layers, trained on two GTX 580 GPUs.
  - Key ingredients that are still taught: **ReLU** (faster training than tanh), **dropout** in the FC layers, **data augmentation** (crops, flips), and GPU training.
  - It is the usual date for "the deep learning boom".
- **ResNet (He, Zhang, Ren, Sun 2015; CVPR 2016)**, *Deep Residual Learning for Image Recognition*.
  - Observation: making a plain CNN deeper (e.g. 20 → 56 layers) made even *training* error worse. This is the **degradation problem**, and it is not overfitting.
  - Fix: each block learns a *residual* $F(x)$ and outputs $y = F(x) + x$ through a **skip (shortcut) connection**.
  - 152-layer ResNets won ILSVRC-2015 (3.57% top-5 error with an ensemble).
  - Residual connections are now everywhere, including every Transformer block (§6).
- **BatchNorm** (Ioffe & Szegedy 2015) normalizes each channel over the mini-batch and lets deeper CNNs train faster. ResNet uses it after every conv. For our tiny CNNs it is optional but helps (see `01-foundations.md` §9).

### Math, micro-step by micro-step
**Why a skip connection helps gradients.**
1. Block output: $y = F(x) + x$.
2. Derivative with respect to the input: $\dfrac{\partial y}{\partial x} = \dfrac{\partial F}{\partial x} + 1$ (identity matrix $I$ in the vector case).
3. Backprop multiplies these factors layer after layer. Without the "+1", many factors smaller than 1 multiply to almost 0 (vanishing gradient).
4. With the "+1", there is always a path where the gradient passes through unchanged. If the best thing a block can do is nothing, it only has to learn $F(x)=0$, which is easy (He et al. 2015 §3.1).

### Analogy
- **ResNet = editing a draft instead of rewriting it.** Each block receives the current draft $x$ and only writes *corrections* $F(x)$. If a block has nothing useful to add, it leaves the draft alone. *Limit:* the corrections are not small in general; it is a framing, not a constraint.

### Misconceptions
- "AlexNet invented CNNs." CNNs were trained with backprop by 1989 (LeCun et al., zip codes). AlexNet's contribution was scale, GPUs and training tricks.
- "We need a ResNet for MNIST." Not at all. A two-conv-layer network reaches about 99% (§11). Teach ResNet in the advanced track as a concept, with an optional tiny residual block exercise.

### Sources
LeCun et al. 1998 (PDF) http://vision.stanford.edu/cs598_spring07/papers/Lecun98.pdf · DOI https://doi.org/10.1109/5.726791 · LeCun et al. 1989, *Backpropagation Applied to Handwritten Zip Code Recognition* https://doi.org/10.1162/neco.1989.1.4.541 · Krizhevsky et al. 2012 https://papers.nips.cc/paper_files/paper/2012/hash/c399862d3b9d6b76c8436e924a68c45b-Abstract.html · He et al. 2015 https://arxiv.org/abs/1512.03385 · Ioffe & Szegedy 2015 https://arxiv.org/abs/1502.03167 · d2l.ai modern CNNs https://d2l.ai/chapter_convolutional-modern/index.html · Wikipedia LeNet https://en.wikipedia.org/wiki/LeNet · Wikipedia AlexNet https://en.wikipedia.org/wiki/AlexNet · Wikipedia Residual network https://en.wikipedia.org/wiki/Residual_neural_network

---

## 3. Recurrent networks: RNN, LSTM, GRU

### Distilled
- Text is a **sequence**: the meaning of a character depends on what came before. A **recurrent neural network (RNN)** reads one token at a time and carries a **hidden state** vector $h_t$, its running memory, from step to step.
- A vanilla RNN uses the same weights at every time step (weight sharing across time, like a CNN shares across space).
- Problem: training through many steps multiplies many Jacobians together, so gradients **vanish** or **explode** (Bengio, Simard, Frasconi 1994; Hochreiter 1991). Vanilla RNNs struggle to remember beyond about 10–20 steps.
- **LSTM (Hochreiter & Schmidhuber 1997)** adds a separate **cell state** $c_t$, a "conveyor belt" that is changed only by element-wise gated additions, so information and gradients can flow over long ranges.
  - The **forget gate** was added later by Gers, Schmidhuber & Cummins (2000). Today "LSTM" means the version with a forget gate.
- **GRU (Cho et al. 2014)** is a lighter variant with two gates (reset, update) and no separate cell state. It often performs comparably with fewer parameters (Chung et al. 2014).
- Karpathy's 2015 blog post *The Unreasonable Effectiveness of Recurrent Neural Networks* trained character-level LSTMs (char-rnn) on Shakespeare, Linux source code and LaTeX. It is the classic motivating demo for our small-text and code tracks and introduced the **TinyShakespeare** file (§10.4).
- RNNs process tokens one after another, so they cannot be parallelized over the sequence during training. This is the main reason Transformers replaced them (§6). For the course, LSTMs remain valuable for teaching **state** and **gating**, and they are a fine baseline for the sentiment classifier.

### Math, micro-step by micro-step
**Vanilla RNN.**
$$h_t = \tanh(W_{xh} x_t + W_{hh} h_{t-1} + b_h), \qquad \text{logits}_t = W_{hy} h_t + b_y$$
Step by step: mix the new input ($W_{xh}x_t$) with the old memory ($W_{hh}h_{t-1}$), squash with tanh, and use the result both to predict and as the memory for the next step.

**LSTM** (the PyTorch `nn.LSTM` convention). $\sigma$ is the sigmoid, which outputs values in 0..1 that act like "valves". $\odot$ is element-wise multiplication.

1. Forget gate: $f_t = \sigma(W_f [x_t, h_{t-1}] + b_f)$. "How much of each old memory slot to keep."
2. Input gate: $i_t = \sigma(W_i [x_t, h_{t-1}] + b_i)$. "How much new information to let in."
3. Candidate: $g_t = \tanh(W_g [x_t, h_{t-1}] + b_g)$. "What the new information is" (in −1..1).
4. Cell update: $c_t = f_t \odot c_{t-1} + i_t \odot g_t$. Keep some old, add some new.
5. Output gate: $o_t = \sigma(W_o [x_t, h_{t-1}] + b_o)$.
6. Hidden state: $h_t = o_t \odot \tanh(c_t)$. "Show a filtered view of the memory."

**Worked scalar example** (hidden size 1). Suppose this step's gate values come out as $f=0.9$, $i=0.2$, $g=0.5$, $o=0.8$, and the old cell is $c_{t-1}=1.0$.
- $c_t = 0.9\cdot1.0 + 0.2\cdot0.5 = 0.9 + 0.1 = 1.0$
- $h_t = 0.8\cdot\tanh(1.0) = 0.8\cdot 0.7616 \approx 0.609$

Notice step 4 is an *addition*: $\partial c_t/\partial c_{t-1} = f_t$. If the forget gate stays near 1, the gradient passes almost unchanged through many steps. That is the whole trick.

**Parameter count.** PyTorch keeps two bias vectors per gate. For input size $I$ and hidden size $H$, one layer has $4H(I+H) + 8H$ parameters. Example: $I=64, H=128$ gives $4\cdot128\cdot192 + 1024 = 98{,}304+1{,}024 = 99{,}328$.

**GRU** (PyTorch convention):
- reset $r_t=\sigma(W_{ir}x_t+b_{ir}+W_{hr}h_{t-1}+b_{hr})$
- update $z_t=\sigma(W_{iz}x_t+b_{iz}+W_{hz}h_{t-1}+b_{hz})$
- candidate $n_t=\tanh(W_{in}x_t+b_{in}+r_t\odot(W_{hn}h_{t-1}+b_{hn}))$
- new state $h_t=(1-z_t)\odot n_t + z_t\odot h_{t-1}$

The last line is a weighted average of "new" and "old". When $z$ is near 1 the unit just copies its memory forward.

### Analogy
- **LSTM = a notebook with three valves.** An *eraser* valve (forget gate) decides what to rub out, a *pen* valve (input gate) decides what to write, and a *window* valve (output gate) decides what the rest of the network may read right now. *Limit:* the "slots" are not human-readable facts; each is a blend of many features.
- **Vanishing gradient = the telephone game.** A message whispered through 50 people ends up as noise. The LSTM's cell state is a written note passed hand to hand instead.

### Misconceptions
- "LSTMs remember forever." In practice, character LSTMs keep useful context for a few hundred steps at most. Long-range structure (e.g. matching a bracket opened 2,000 characters earlier) is weak, as Karpathy's code samples show.
- "GRU is always worse." The empirical comparison (Chung et al. 2014) found them broadly similar. Choose by speed.
- `nn.LSTM(batch_first=False)` is the default: input shape is `(seq, batch, feature)` unless you pass `batch_first=True`. This is a top source of silent bugs.

### Sources
Hochreiter & Schmidhuber 1997 https://doi.org/10.1162/neco.1997.9.8.1735 · Gers, Schmidhuber, Cummins 2000 https://doi.org/10.1162/089976600300015015 · Bengio, Simard, Frasconi 1994 https://doi.org/10.1109/72.279181 · Cho et al. 2014 https://arxiv.org/abs/1406.1078 · Chung et al. 2014 https://arxiv.org/abs/1412.3555 · Olah, *Understanding LSTM Networks* https://colah.github.io/posts/2015-08-Understanding-LSTMs/ · Karpathy 2015 http://karpathy.github.io/2015/05/21/rnn-effectiveness/ · char-rnn https://github.com/karpathy/char-rnn · d2l.ai LSTM https://d2l.ai/chapter_recurrent-modern/lstm.html · d2l.ai GRU https://d2l.ai/chapter_recurrent-modern/gru.html · PyTorch `LSTM` https://docs.pytorch.org/docs/stable/generated/torch.nn.LSTM.html · PyTorch `GRU` https://docs.pytorch.org/docs/stable/generated/torch.nn.GRU.html · Graves 2013 https://arxiv.org/abs/1308.0850 · Wikipedia https://en.wikipedia.org/wiki/Long_short-term_memory

---

## 4. Neural language models: Bengio 2003 → makemore

### Distilled
- A **language model** assigns probabilities to the next token given the previous ones: $P(x_t \mid x_{<t})$. Generate text by sampling one token, appending it, and repeating.
- **Counting (n-gram) models** look up how often each next character followed the previous $n-1$. They are quick, but the table explodes and they cannot generalize to unseen contexts.
- **Bengio, Ducharme, Vincent & Jauvin (2003)**, *A Neural Probabilistic Language Model* (JMLR 3:1137–1155):
  - Each word gets a learned **embedding** vector.
  - The embeddings of the previous $n-1$ words are concatenated, passed through a tanh hidden layer, and a softmax predicts the next word.
  - Similar words get similar vectors, so the model generalizes ("the cat is walking" helps "a dog was running").
  - This is the ancestor of every modern LM.
- **Karpathy's makemore** (repo plus the *Neural Networks: Zero to Hero* videos) rebuilds this progression on a list of about 32k names, at the character level: **bigram counts → bigram neural net → MLP (Bengio-style) → … → Transformer**. It is the ideal skeleton for the "small texts: generator" project, and it runs on a CPU in minutes.

### Math, micro-step by micro-step
1. **Vocabulary.** For names: 26 letters + 1 special "." token marking start/end = 27 symbols.
2. **Context window** of 3 characters, e.g. `"..e"` → predict `"m"` (for "emma").
3. **Embedding table** $C \in \mathbb{R}^{27\times 10}$: each character becomes a 10-number vector. Three characters give a 30-number input.
4. **Hidden layer:** $h = \tanh(x W_1 + b_1)$ with 200 units.
5. **Output:** logits $= h W_2 + b_2$ (27 numbers), then softmax gives probabilities, and the loss is cross-entropy against the true next character.
6. **Parameter count:** $C$: $27\cdot10=270$; $W_1,b_1$: $30\cdot200+200=6{,}200$; $W_2,b_2$: $200\cdot27+27=5{,}427$. **Total 11,897.** That matches the count shown in Karpathy's makemore part-2 video, a good "check yourself" exercise.
7. **Sanity check for the starting loss.** An untrained model should be uniform over 27 symbols, so the loss is $-\ln(1/27)=\ln 27 \approx 3.30$. If the first printed loss is much larger (say 20), the init is too confident; see `01-foundations.md` §11.
8. **Perplexity** $= e^{\text{loss}}$: "on average the model is as unsure as if it were picking among this many characters." Loss 2.1 gives perplexity $\approx 8.2$, versus 27 for random guessing.

Bengio's original form, for reference: $y = b + Wx + U\tanh(d + Hx)$. The $Wx$ term is an optional direct (skip) connection from the embeddings to the output.

### Analogy
- **Embeddings = coordinates on a map of meaning.** Each symbol gets a pin on a map. Training moves pins so that symbols used in similar ways end up close together (vowels cluster in the names model, which learners can plot in 2D, as Karpathy does). *Limit:* the map has 10+ dimensions; 2D plots are projections.

### Sources
Bengio et al. 2003 https://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf · makemore https://github.com/karpathy/makemore · Neural Networks: Zero to Hero https://karpathy.ai/zero-to-hero.html · Mikolov et al. 2013 (word2vec) https://arxiv.org/abs/1301.3781 · PyTorch `Embedding` https://docs.pytorch.org/docs/stable/generated/torch.nn.Embedding.html · d2l.ai language models https://d2l.ai/chapter_recurrent-neural-networks/language-model.html · Wikipedia https://en.wikipedia.org/wiki/Language_model

---

## 5. Attention: Bahdanau 2014 → scaled dot-product attention

### Distilled
- Early neural translation (Sutskever et al. 2014; Cho et al. 2014) used an encoder RNN that squeezed a whole sentence into **one fixed vector**, and a decoder RNN that unpacked it. Long sentences suffered, because one vector is a bottleneck.
- **Bahdanau, Cho & Bengio (2014)**, *Neural Machine Translation by Jointly Learning to Align and Translate*: at every output step, the decoder computes a **weight for every input position** (how relevant is source word $j$ right now?) and takes a weighted average of the encoder states.
  - That weighted average is the **context vector**. The weights are "soft alignment", and they can be plotted as a heat map.
  - This "additive" attention scores with a small MLP: $e_{ij} = v^\top\tanh(W s_{i-1} + U h_j)$.
- **Luong et al. (2015)** simplified the score to a dot product.
- **Vaswani et al. (2017)** made attention the *only* mixing mechanism (no recurrence) and introduced **scaled dot-product attention** with **queries, keys and values**.

### Math, micro-step by micro-step

$$\text{Attention}(Q,K,V) = \operatorname{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

1. Each token's vector $x$ is projected three ways: query $q = xW_Q$ ("what am I looking for?"), key $k = xW_K$ ("what do I contain?"), value $v = xW_V$ ("what I'll hand over if chosen").
2. **Score** = dot product $q\cdot k$: large when the query and key point the same way.
3. **Scale** by $\sqrt{d_k}$. If the components of $q$ and $k$ are independent with mean 0 and variance 1, then $q\cdot k$ has variance $d_k$. Dividing by $\sqrt{d_k}$ brings the variance back to 1, so the softmax does not saturate into near one-hot outputs with tiny gradients (Vaswani et al. 2017, footnote 4).
4. **Softmax** over the scores turns them into weights that are positive and sum to 1.
5. **Weighted sum** of the values gives the output for this token.

**Worked example** with 3 tokens and $d_k = 4$, so $\sqrt{d_k}=2$. Query of token 3: $q=[1,0,1,0]$.

| key | $q\cdot k$ | ÷2 | $e^{(\cdot)}$ | weight |
|---|---|---|---|---|
| $k_1=[1,0,1,0]$ | 2 | 1 | 2.718 | 2.718/6.437 = **0.422** |
| $k_2=[0,1,0,1]$ | 0 | 0 | 1.000 | 1/6.437 = **0.155** |
| $k_3=[1,1,1,1]$ | 2 | 1 | 2.718 | **0.422** |

With values $v_1=[1,0]$, $v_2=[0,1]$, $v_3=[1,1]$:

$$\text{out} = 0.422[1,0] + 0.155[0,1] + 0.422[1,1] = [0.844,\; 0.577]$$

Token 3 mostly listens to tokens 1 and 3.

6. **Causal mask** (for GPT-style generation): token $t$ must not see the future. Set the scores for positions $> t$ to $-\infty$ before the softmax, so their weights become exactly 0. In code: `scores.masked_fill(mask == 0, float('-inf'))`, as in nanoGPT, or `F.scaled_dot_product_attention(q, k, v, is_causal=True)`.
7. **Multi-head attention:** run $h$ attentions in parallel on slices of size $d_k = d_{model}/h$, concatenate the results, and project with $W_O$. Different heads can specialise, for example "previous token", "matching bracket" or "same variable name".
8. **Cost:** the score matrix is $T\times T$, so the time and memory are quadratic in the context length $T$. This is why our CPU models use $T = 64$–256.

### Analogy
- **Library search.** Your *query* is the question you type. Every book has a *key* (its catalogue card) and a *value* (its contents). You don't pick one book; you take a blend of the contents, weighted by how well each card matches your question. *Limit:* the queries, keys and values are all learned, so the "question" is not something a human wrote.
- **Causal mask = reading with a card covering the rest of the page.**

### Misconceptions
- "Attention weights explain the model's reasoning." They are one signal among many and are not faithful explanations by themselves (Jain & Wallace 2019).
- "$\sqrt{d_k}$ is a magic constant." It is just variance control (step 3).

### Sources
Bahdanau et al. 2014 https://arxiv.org/abs/1409.0473 · Luong et al. 2015 https://arxiv.org/abs/1508.04025 · Sutskever et al. 2014 https://arxiv.org/abs/1409.3215 · Vaswani et al. 2017 https://arxiv.org/abs/1706.03762 · Olah & Carter, *Attention and Augmented RNNs* (Distill) https://distill.pub/2016/augmented-rnns/ · d2l.ai attention chapter https://d2l.ai/chapter_attention-mechanisms-and-transformers/index.html · PyTorch `scaled_dot_product_attention` https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html · PyTorch `MultiheadAttention` https://docs.pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html · Jain & Wallace 2019 https://arxiv.org/abs/1902.10186 · Wikipedia https://en.wikipedia.org/wiki/Attention_(machine_learning)

---

## 6. The Transformer and GPT (decoder-only) models

### Distilled
- **Vaswani et al. (2017)**, *Attention Is All You Need*: an encoder–decoder for translation built only from attention and feed-forward layers.
  - Base model: $d_{model}=512$, 6 layers, 8 heads, feed-forward size 2048.
  - It reached 28.4 BLEU on WMT14 English→German and trained far faster than RNNs because all positions are processed in parallel.
- A **Transformer block** = [multi-head self-attention → add residual → LayerNorm] then [MLP (expand ×4, nonlinearity, project back) → add residual → LayerNorm].
  - The **residual** connections are from ResNet (§2). **LayerNorm** (Ba et al. 2016) normalizes each token's vector.
- **Positions:** attention by itself ignores order (it is a weighted *set* operation). The original paper added fixed **sinusoidal positional encodings**. GPT models use **learned position embeddings**: one vector per position, added to the token embedding.
- **GPT (decoder-only):** keep only the decoder stack with a causal mask, and train it to predict the next token.
  - GPT-2 (Radford et al. 2019) scaled this to 1.5B parameters trained on WebText (about 40 GB of text) and used **byte-level BPE** with a 50,257-token vocabulary.
  - GPT-2 moved LayerNorm to the *input* of each sub-block ("pre-LN") and added a final LayerNorm. nanoGPT follows this, and pre-LN trains more stably for small models too.
- **Karpathy's code family**, our implementation reference (MIT licensed):
  - **minGPT** (2020): an educational, readable GPT.
  - **nanoGPT** (2022/23): a minimal, fast GPT-2 reproduction with a `shakespeare_char` example, including an explicit CPU configuration in its README.
  - **makemore**: character-level models from bigram to Transformer.
  - The video *Let's build GPT: from scratch, in code, spelled out* (2023) builds a character-level GPT on TinyShakespeare step by step.
  - Note: Karpathy's README marks nanoGPT as superseded by his newer **nanochat** for full LLM training. For a tiny CPU model, nanoGPT/minGPT-style code is still the clearest reference.
- **Weight tying:** sharing the token-embedding matrix with the output layer saves parameters and usually helps (Press & Wolf 2016). nanoGPT does this.

### Math, micro-step by micro-step
**Forward pass of a tiny GPT** for a batch of token ids, shape `(B, T)`:
1. `tok = wte[idx]` → `(B, T, d)`; `pos = wpe[0..T-1]` → `(T, d)`; `x = tok + pos`.
2. For each of $L$ blocks: `x = x + attn(ln1(x))`, then `x = x + mlp(ln2(x))`, where `mlp` = Linear(d→4d) → GELU → Linear(4d→d).
3. `logits = lm_head(ln_f(x))` → `(B, T, V)`.
4. Loss = cross-entropy between `logits[:, t]` and the target `idx[:, t+1]` for *every* position at once. One sequence gives $T$ training examples. That is the efficiency win over RNN training.

**Sinusoidal positional encoding** (original paper): $PE_{(pos,2i)} = \sin(pos/10000^{2i/d})$ and $PE_{(pos,2i+1)} = \cos(pos/10000^{2i/d})$. Each dimension pair is a clock hand turning at a different speed, so every position gets a unique pattern.

**Parameter count rule of thumb.** Per block, attention has $4d^2$ (Q, K, V, O) and the MLP has $2\cdot d\cdot 4d = 8d^2$, so about $12d^2$ per block, ignoring biases and LayerNorm.
- nanoGPT `shakespeare_char` config ($L=6$, $d=384$): $12\cdot6\cdot384^2 = 10{,}616{,}832$, plus token embeddings $65\cdot384=24{,}960$ ≈ **10.6M**. nanoGPT prints "number of parameters: 10.65M". ✓
- Our CPU config ($L=4$, $d=128$): $12\cdot4\cdot128^2 = 786{,}432$ ≈ **0.8M**, plus embeddings.

**Expected starting loss:** with a vocabulary of $V$ characters, the untrained loss is about $\ln V$. For TinyShakespeare, $V=65$ gives $\ln 65 \approx 4.17$, the value seen at step 0 in the "Let's build GPT" video and nanoGPT logs.

### Analogy
- **A Transformer block = a meeting followed by private thinking.** In the *attention* part, every token "talks" to the earlier tokens and gathers what is relevant. In the *MLP* part, each token "thinks alone" about what it heard. The residual stream is the shared notepad that every block reads from and adds to. *Limit:* the "talking" is linear algebra; there is no symbolic communication.

### Misconceptions
- "GPT understands code like a compiler." A tiny GPT learns statistical patterns: indentation, `def … :` then an indented body, common names. It will happily produce code that does not run. Teach this honestly in the code-autocomplete track.
- "You need a GPU." For models under about 5M parameters with context ≤256, a modern laptop CPU trains a useful model in about 10–60 minutes (to be measured in the smoke-test step).

### Sources
Vaswani et al. 2017 https://arxiv.org/abs/1706.03762 · Radford et al. 2019 (GPT-2) https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf · Radford et al. 2018 (GPT-1) https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf · Ba, Kiros, Hinton 2016 (LayerNorm) https://arxiv.org/abs/1607.06450 · Hendrycks & Gimpel (GELU) https://arxiv.org/abs/1606.08415 · Press & Wolf 2016 https://arxiv.org/abs/1608.05859 · Alammar, *The Illustrated Transformer* https://jalammar.github.io/illustrated-transformer/ · Alammar, *The Illustrated GPT-2* https://jalammar.github.io/illustrated-gpt2/ · Harvard NLP, *The Annotated Transformer* https://nlp.seas.harvard.edu/annotated-transformer/ · nanoGPT https://github.com/karpathy/nanoGPT · minGPT https://github.com/karpathy/minGPT · nanochat https://github.com/karpathy/nanochat · *Let's build GPT* video https://www.youtube.com/watch?v=kCc8FmEb1nY · PyTorch `TransformerEncoderLayer` https://docs.pytorch.org/docs/stable/generated/torch.nn.TransformerEncoderLayer.html · PyTorch `Transformer` https://docs.pytorch.org/docs/stable/generated/torch.nn.Transformer.html · PyTorch `LayerNorm` https://docs.pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html · Wikipedia https://en.wikipedia.org/wiki/Transformer_(deep_learning_architecture)

**Implementation note for lesson writers:** PyTorch's `nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward, batch_first=True, norm_first=True)` plus a causal mask from `nn.Transformer.generate_square_subsequent_mask(T)` is a valid "decoder-only" GPT block. However, writing the block by hand in about 40 lines (as nanoGPT does) teaches more, and it is what the code track should show, with the built-in module mentioned as an alternative.

---

## 7. Tokenization: characters, words, BPE, byte-level BPE

### Distilled
- A model sees integers, not text. A **tokenizer** maps text ↔ a sequence of token ids from a fixed **vocabulary**.
- **Character-level:** tiny vocabulary (65 for Shakespeare, about 100 for Python source) and no unknown tokens, but sequences are long, so the model must spend capacity learning spelling.
- **Word-level:** short sequences, but a huge vocabulary, and unseen words become `<unk>`. This breaks on code identifiers like `get_user_by_id`.
- **Subword / BPE (Sennrich, Haddow & Birch 2016):** start from characters and repeatedly **merge the most frequent adjacent pair** into a new symbol. Frequent words become single tokens and rare words split into pieces. It was originally a 1994 compression algorithm (Gage). It is the standard for modern LMs.
- **Byte-level BPE (GPT-2):** the base alphabet is the 256 possible bytes, so *any* string, including emoji and Windows paths, can be encoded with no `<unk>` at all. GPT-2 also pre-splits text with a regex so that merges do not cross categories (letters vs digits vs punctuation).
- Other algorithms: **WordPiece** (BERT) and **Unigram** (SentencePiece; Kudo 2018). The Hugging Face LLM course chapter 6 compares all three.
- **Tools:**
  - Hugging Face **`tokenizers`** (Rust-fast; trains a BPE on our corpus in seconds).
  - OpenAI **`tiktoken`** (fast encoding with GPT-2/4 vocabularies; no training).
  - Karpathy's **`minbpe`** (about 100 lines, educational; great for the lesson that implements BPE from scratch).
- **Course decision:**
  - The small-text generator stays **character-level**, which is simplest to teach.
  - The code autocompleter should first be built character-level (works out of the box) and then *optionally upgraded* to a trained BPE of about 2,000–4,000 tokens on the stdlib corpus. Comparing the two (same compute, longer effective context with BPE) is a strong advanced lesson.

### Math: BPE merges, a fully worked example
Corpus word counts (the toy example popularised by Sennrich et al.), with an end-of-word marker `_`:

```
l o w _      ×5
l o w e r _  ×2
n e w e s t _ ×6
w i d e s t _ ×3
```

**Round 1: count adjacent pairs** (weighted by word frequency):
- `e s`: 6 (newest) + 3 (widest) = **9**
- `s t`: 9
- `t _`: 9
- `w e`: 2 + 6 = 8
- `l o`: 7, `o w`: 7
- `n e`: 6, `e w`: 6, `w _`: 5
- `w i`, `i d`, `d e`: 3 each
- `e r`, `r _`: 2 each

The top count is 9 (a three-way tie; break ties by first seen). **Merge 1: `e s` → `es`.**

**Round 2.** Now `newest` = `n e w es t _` and `widest` = `w i d es t _`. Top pair `es t` (9). **Merge 2: `est`.**

**Round 3.** `est _` (9). **Merge 3: `est_`**, i.e. "est at the end of a word".

**Round 4.** `l o` (5+2 = 7) is now the top pair. **Merge 4: `lo`.**

**Round 5.** `lo w` (7). **Merge 5: `low`.**

The learned merge list is ordered: `[e s, es t, est _, l o, lo w]`.

**Encoding an unseen word, "lowest".** Start with `l o w e s t _` and apply the merges *in learned order*:
- `e s` → `l o w es t _`
- `es t` → `l o w est _`
- `est _` → `l o w est_`
- `l o` → `lo w est_`
- `lo w` → `low est_`

Result: **[`low`, `est_`]**, two meaningful pieces for a word the corpus never contained. That is BPE's generalization in one line.

The vocabulary size is a knob: base symbols + number of merges. GPT-2: 256 bytes + 50,000 merges + 1 special `<|endoftext|>` = **50,257**.

### Analogy
- **BPE = inventing abbreviations while taking notes.** You notice you keep writing "t-h-e", so you invent a single squiggle for it; later you invent one for "the␣" and so on. Common chunks get their own symbol; rare words stay spelled out. *Limit:* merges are purely frequency-based, not meaning-based ("est" is a frequent chunk, not a known suffix).

### Misconceptions
- "Tokens are words." In GPT-2's vocabulary, " the" (with a leading space) and "the" are different tokens, and long words split into several.
- "Bigger vocabulary is free." Each extra token adds a row to the embedding and output matrices. For a 4M-parameter model, a 50k vocabulary would spend $50{,}257\cdot256 \approx 12.9$M parameters on embeddings alone, more than the whole model. **Small models need small vocabularies.**

### Sources
Sennrich, Haddow, Birch 2016 https://arxiv.org/abs/1508.07909 · ACL Anthology version https://aclanthology.org/P16-1162/ · Gage 1994 *A New Algorithm for Data Compression* (C Users Journal; summarised at) https://en.wikipedia.org/wiki/Byte_pair_encoding · Kudo & Richardson 2018 (SentencePiece) https://arxiv.org/abs/1808.06226 · Kudo 2018 (Unigram) https://arxiv.org/abs/1804.10959 · Hugging Face LLM course, BPE chapter https://huggingface.co/learn/llm-course/chapter6/5 · HF course, tokenizers overview https://huggingface.co/learn/llm-course/chapter2/4 · HF `tokenizers` docs https://huggingface.co/docs/tokenizers/index · HF tokenizers quicktour (training a BPE) https://huggingface.co/docs/tokenizers/quicktour · tiktoken https://github.com/openai/tiktoken · minbpe https://github.com/karpathy/minbpe · Karpathy *Let's build the GPT Tokenizer* https://www.youtube.com/watch?v=zduSFxRajkE

---

## 8. Sampling from a language model: temperature, top-k, top-p

### Distilled
- The model outputs **logits** $z_1..z_V$; softmax turns them into probabilities. *How* we pick the next token changes the output a lot:
  - **greedy / argmax**: always the most likely token. Repetitive, often loops (`self.self.self`).
  - **pure sampling**: draw from the full distribution. Creative, but occasionally picks junk.
  - **temperature $T$**: divide the logits by $T$ before the softmax. $T<1$ sharpens (safer, more repetitive); $T>1$ flattens (wilder).
  - **top-k**: keep only the $k$ most likely tokens, renormalize, sample (Fan et al. 2018).
  - **top-p / nucleus**: keep the smallest set of tokens whose probabilities add to ≥ $p$ (Holtzman et al. 2019). The set adapts: small when the model is sure, large when it is not.
- For **code autocompletion**, use a low temperature (0.2–0.6) with top-k 10–40 to suggest likely continuations. Show 3 alternative completions sampled with different seeds, like an IDE suggestion list. For **Shakespeare/names**, use $T$ 0.8–1.0 for variety.

### Math, micro-step by micro-step
Logits $z = [2, 1, 0]$ for tokens A, B, C.

$$p_i = \frac{e^{z_i/T}}{\sum_j e^{z_j/T}}$$

| $T$ | $z/T$ | $e^{z/T}$ | sum | probabilities (A, B, C) |
|---|---|---|---|---|
| 1 | 2, 1, 0 | 7.389, 2.718, 1 | 11.107 | **0.665, 0.245, 0.090** |
| 0.5 | 4, 2, 0 | 54.598, 7.389, 1 | 62.987 | **0.867, 0.117, 0.016** |
| 2 | 1, 0.5, 0 | 2.718, 1.649, 1 | 5.367 | **0.506, 0.307, 0.186** |

As $T\to0$ this becomes greedy; as $T\to\infty$ it becomes uniform.

**Top-k with $k=2$** at $T=1$: drop C, then renormalize: $0.665/0.910 = 0.731$ and $0.245/0.910 = 0.269$.

**Top-p with $p=0.9$**: sort the probabilities and accumulate: 0.665 (< 0.9), then 0.910 (≥ 0.9, stop), so keep {A, B}. Same result as top-k here; with a flatter distribution, top-p would keep more tokens.

Code (nanoGPT style):
```python
logits = logits[:, -1, :] / temperature
if top_k is not None:
    v, _ = torch.topk(logits, top_k)
    logits[logits < v[:, [-1]]] = -float("inf")
probs = torch.softmax(logits, dim=-1)
next_id = torch.multinomial(probs, num_samples=1)
```

### Analogy
- **Temperature = how adventurous a restaurant-goer is.** At $T=0.2$ you always order the favourite dish. At $T=1$ you usually order it, sometimes something else. At $T=2$ you're nearly picking at random from the menu. Top-k = "only consider the k dishes on the specials board".

### Sources
Holtzman et al. 2019 https://arxiv.org/abs/1904.09751 · Fan, Lewis, Dauphin 2018 https://arxiv.org/abs/1805.04833 · HF blog, *How to generate text* https://huggingface.co/blog/how-to-generate · PyTorch `multinomial` https://docs.pytorch.org/docs/stable/generated/torch.multinomial.html · Wikipedia Softmax https://en.wikipedia.org/wiki/Softmax_function

---

## 9. PyTorch module reference cheat-sheet

| Module | Key arguments | Input → output shape | Gotchas |
|---|---|---|---|
| `nn.Conv2d(in_ch, out_ch, kernel_size, stride=1, padding=0)` | `padding="same"` allowed for stride 1 | `(N, C_in, H, W)` → `(N, C_out, H_out, W_out)` | Grayscale images need a channel dim: `(N,1,28,28)` |
| `nn.MaxPool2d(2)` | stride defaults to kernel_size | halves H, W | |
| `nn.BatchNorm2d(C)` | | same shape | behaves differently in `model.train()` vs `model.eval()` |
| `nn.Dropout(p)` | | same | only active in train mode |
| `nn.Flatten()` | | `(N, C, H, W)` → `(N, C·H·W)` | |
| `nn.Embedding(V, d)` | | `(N, T)` long → `(N, T, d)` | input must be integer dtype |
| `nn.LSTM(I, H, num_layers, batch_first)` | default `batch_first=False` | `(N,T,I)` → `output (N,T,H)`, `(h_n, c_n)` | for classification use `h_n[-1]` or pooled outputs |
| `nn.GRU(...)` | same as LSTM | returns `output, h_n` | |
| `nn.MultiheadAttention(d, heads, batch_first)` | `attn_mask`, `is_causal` | `(N,T,d)` → `(N,T,d)` | default `batch_first=False` |
| `F.scaled_dot_product_attention(q,k,v,is_causal=True)` | | `(N,h,T,d_k)` | uses fused kernels when available |
| `nn.TransformerEncoderLayer(d, nhead, dim_feedforward, batch_first=True, norm_first=True)` | | `(N,T,d)` | pass a causal mask for GPT-style use |
| `nn.CrossEntropyLoss()` | takes **logits**, not softmax | `(N, C)` + targets `(N,)` | for LMs: reshape to `(N·T, V)` and `(N·T,)` |

Sources: PyTorch `nn` reference https://docs.pytorch.org/docs/stable/nn.html · `CrossEntropyLoss` https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html · `BatchNorm2d` https://docs.pytorch.org/docs/stable/generated/torch.nn.BatchNorm2d.html · PyTorch Datasets & DataLoaders tutorial https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html · PyTorch CNN tutorial (CIFAR-10) https://docs.pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html · PyTorch examples, MNIST https://github.com/pytorch/examples/tree/main/mnist

---

## 10. Datasets: URL, licence, size, format, loading

**How this was verified (2026-11-24).** Every download URL below was requested with `curl -I` and returned HTTP 200. Content-Length values are quoted where they were measured. For Quick, Draw!, the first 20 drawings of `cat.npy` were fetched with an HTTP Range request and decoded, to confirm the header, dtype and stroke polarity. Licence statements come from the official pages. Where the official page does **not** state a licence, this file says so instead of guessing.

**Course-wide licence policy.** The site and repo **never redistribute dataset files**. The companion code downloads them at run time from the official source into a git-ignored `data/` folder, and each lesson's footnotes cite the dataset paper. This keeps us safe even for datasets whose licence is unclear (MNIST, EMNIST, SST-2, IMDB).

### 10.1 MNIST: handwritten digits
- **What:** 70,000 grayscale 28×28 images of the digits 0–9: **60,000 train / 10,000 test**. Built by LeCun, Cortes & Burges from NIST Special Databases 1 and 3. Each digit was size-normalized into a 20×20 box (keeping its aspect ratio) and centred by **centre of mass** in a 28×28 field. Background = 0 (black), ink = high values.
- **Official page:** https://yann.lecun.com/exdb/mnist/ (served intermittently over the years, which is why torchvision uses mirrors).
- **Mirror used by torchvision:** `https://ossci-datasets.s3.amazonaws.com/mnist/` (verified: `train-images-idx3-ubyte.gz` = 9,912,422 bytes). Total download is about 11 MB in IDX format (4 gzip files).
- **Licence:** **not stated on the original page.** Copyright is attributed to Yann LeCun and Corinna Cortes. Many redistributors label it **CC BY-SA 3.0** (e.g. Voxel51's dataset zoo); others say MIT or CC0. → *Course wording:* "MNIST is freely available for research and education; its original page does not specify a licence. We download it from the official PyTorch mirror and do not redistribute it."
- **Load:**
```python
from torchvision import datasets, transforms
tf = transforms.Compose([transforms.ToTensor(),
                         transforms.Normalize((0.1307,), (0.3081,))])  # dataset mean/std
train = datasets.MNIST("data", train=True,  download=True, transform=tf)
test  = datasets.MNIST("data", train=False, download=True, transform=tf)
```
- **Preprocessing lesson for the tkinter drawing app:** the user's drawing must be converted the *same way* as the training images: crop to the ink, scale to fit 20×20, paste centred by centre of mass in 28×28, white ink on black. Skipping this is the #1 reason "my 99% model can't read my own handwriting."
- Sources: torchvision MNIST https://docs.pytorch.org/vision/stable/generated/torchvision.datasets.MNIST.html · Wikipedia https://en.wikipedia.org/wiki/MNIST_database · Voxel51 zoo entry (licence label) https://docs.voxel51.com/dataset_zoo/datasets/mnist.html

### 10.2 EMNIST Letters: handwritten letters
- **What:** EMNIST (Cohen, Afshar, Tapson & van Schaik 2017) converts **NIST Special Database 19** into MNIST's 28×28 format.
  - Six splits: `byclass`, `bymerge`, `balanced`, `letters`, `digits`, `mnist`.
  - **Letters:** 145,600 images in **26 balanced classes**, with upper and lower case merged into one class per letter: **124,800 train / 20,800 test** (4,800 / 800 per class).
  - (TensorFlow Datasets documents different letters split sizes, 88,800 / 14,800. Trust the counts torchvision actually loads, and print `len(train)` in the lesson.)
- **Official page:** https://www.nist.gov/itl/products-and-services/emnist-dataset · paper https://arxiv.org/abs/1702.05373
- **Download:** torchvision fetches `https://biometrics.nist.gov/cs_links/EMNIST/gzip.zip`. Verified 200 OK on 2026-11-24, **561,753,746 bytes (~560 MB)**, because it contains *all* six splits.
  - This URL has broken several times (PyTorch forum reports in 2019 and Dec 2023/2024).
  - **Fallback:** download the "Binary format as the original MNIST dataset" zip manually from the NIST page and place the extracted gzip files in `data/EMNIST/raw/`. Then call `download=False`.
  - The companion code should catch the failure and print these exact instructions.
- **Licence:** the NIST page does **not** publish a licence. SD19 is a NIST product, and EMNIST was produced by Western Sydney University researchers. → *Course wording:* "free for research and education; cite Cohen et al. 2017; we don't redistribute it."
- **Two quirks every lesson must mention:**
  1. **Orientation:** the stored images are transposed relative to MNIST, so letters appear mirrored and rotated by 90°. Fix by swapping the height and width axes (a transpose). This is equivalent to a horizontal flip plus a 90° rotation.
  2. **Labels start at 1** in `letters` (1 = "a/A" … 26 = "z/Z"); there is no class 0. Subtract 1 before `CrossEntropyLoss` with 26 outputs, or use 27 outputs and ignore class 0.
- **Load:**
```python
tf = transforms.Compose([
    transforms.ToTensor(),
    transforms.Lambda(lambda x: x.transpose(1, 2)),   # fix EMNIST orientation (C,H,W) -> (C,W,H)
])
train = datasets.EMNIST("data", split="letters", train=True, download=True, transform=tf,
                        target_transform=lambda y: y - 1)   # 1..26 -> 0..25
```
  Add `transforms.Normalize(mean, std)` with values computed by the companion code (two lines of NumPy over the training set). Plain `ToTensor()` without normalization also trains fine. Note: lambdas in transforms break `DataLoader(num_workers>0)` on Windows (pickling); use small named functions in the companion code.
- **Inherent ambiguity:** merged upper/lower case makes some pairs genuinely confusable (`i`/`l`, `g`/`q`, `I`/`l` written as a bar). That is why no model reaches 99% on letters (§11), a good teaching moment about **label noise and the Bayes error**.
- Sources: torchvision EMNIST https://docs.pytorch.org/vision/stable/generated/torchvision.datasets.EMNIST.html · NIST SD19 https://www.nist.gov/srd/nist-special-database-19 · forum report of download failures https://discuss.pytorch.org/t/cannot-download-emnist-dataset-via-torchvision-dataset-using-google-colab/199400 · TFDS catalog https://www.tensorflow.org/datasets/catalog/emnist

### 10.3 Google Quick, Draw!: doodles
- **What:** about **50 million drawings in 345 categories**, collected from players of the *Quick, Draw!* game (2016–2017). Formats: raw strokes (ndjson), simplified strokes, binary, **numpy bitmaps**, and sketch-rnn `.npz`.
- **Official repo/data page:** https://github.com/googlecreativelab/quickdraw-dataset · https://quickdraw.withgoogle.com/data · category list (345 lines, verified) https://raw.githubusercontent.com/googlecreativelab/quickdraw-dataset/master/categories.txt
- **Licence:** **CC BY 4.0**. The repo's README and LICENSE state that the data is "made available by Google, Inc. under the Creative Commons Attribution 4.0 International license" (https://creativecommons.org/licenses/by/4.0/). → Attribution required: credit "Quick, Draw! dataset by Google, CC BY 4.0" with a link. Redistribution and derivatives are allowed, but we still don't commit the files (size).
- **Content warning (from the README):** the drawings were individually moderated but "may still contain inappropriate content". Mention it in the lesson.
- **Numpy bitmap files:** `https://storage.googleapis.com/quickdraw_dataset/full/numpy_bitmap/<category>.npy`. URL-encode spaces: `The%20Eiffel%20Tower.npy` (verified 200, 105,684,064 bytes).
  - Verified for `cat.npy`: **96,590,448 bytes**. The header says `dtype uint8, shape (123202, 784)`, i.e. 123,202 drawings, each a flattened 28×28 image.
  - The decoded samples show **white strokes (up to 255) on a black (0) background**, the same polarity as MNIST, with zero-valued borders.
  - Per the README, the bitmaps are rendered from the *simplified* drawings and **centred on the drawing's bounding box** (not by centre of mass, unlike MNIST). The drawing fills most of the frame.
  - Typical class file: about 80–270 MB (100k–340k drawings).
- **Recommended 10-class subset** (visually distinct, all present in `categories.txt`): `apple, banana, cat, clock, cloud, fish, house, star, tree, umbrella`.
  - Use the first **10,000 drawings per class for training and 2,000 for test**, loaded with `np.load(path, mmap_mode="r")` so the full file isn't read into RAM.
  - Download about 1–1.5 GB once, or stream just the first N rows with an HTTP Range request (header 128 bytes + N×784 bytes; this is exactly how this research verified the format). Range streaming keeps the doodle track's download at about 9.4 MB per class for 12k drawings.
- **Load:**
```python
import numpy as np, torch
from torch.utils.data import TensorDataset
CLASSES = ["apple","banana","cat","clock","cloud","fish","house","star","tree","umbrella"]
xs, ys = [], []
for label, name in enumerate(CLASSES):
    arr = np.load(f"data/quickdraw/{name}.npy", mmap_mode="r")[:12000]   # (12000, 784) uint8
    xs.append(np.asarray(arr)); ys.append(np.full(len(arr), label))
X = torch.from_numpy(np.concatenate(xs)).float().div(255).view(-1, 1, 28, 28)
y = torch.from_numpy(np.concatenate(ys)).long()
ds = TensorDataset(X, y)   # shuffle, then split 10k/2k per class
```
- **Drawing-app preprocessing:** crop the user's strokes to their bounding box, scale the longer side to fit the frame with a small margin, centre, render about 2–3 px white lines on black, downsample to 28×28 with antialiasing. Unlike MNIST, do **not** centre by mass.
- Sources: Ha & Eck 2017 (sketch-rnn paper that introduced the dataset publicly) https://arxiv.org/abs/1704.03477 · bitmap generation snippet (repo issue #19) https://github.com/googlecreativelab/quickdraw-dataset/issues/19 · TFDS `quickdraw_bitmap` https://www.tensorflow.org/datasets/catalog/quickdraw_bitmap · Hugging Face mirror (cc-by-4.0) https://huggingface.co/datasets/google/quickdraw · CC BY 4.0 deed https://creativecommons.org/licenses/by/4.0/

### 10.4 Small-text corpora

**(a) TinyShakespeare: character-level text generator**
- **What:** about 40,000 lines from Shakespeare's plays concatenated into one file, `input.txt`: **1,115,394 bytes/characters** (plain ASCII, so bytes = characters) with **65 unique characters**. Created by Karpathy for char-rnn (2015).
- **URL (verified 200, 1,115,394 bytes):** https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt
- **Licence:** Shakespeare's texts are in the **public domain**. The char-rnn repo is MIT-licensed. Safe to use and even to bundle (we still download it).
- **Load:** `text = open("data/input.txt", encoding="utf-8").read(); chars = sorted(set(text)); stoi = {c:i for i,c in enumerate(chars)}`. Split 90% train / 10% val (as nanoGPT does).
- Sources: TFDS `tiny_shakespeare` https://www.tensorflow.org/datasets/catalog/tiny_shakespeare · nanoGPT `data/shakespeare_char/prepare.py` https://github.com/karpathy/nanoGPT/blob/master/data/shakespeare_char/prepare.py

**(b) names.txt: makemore-style name generator**
- **What:** **32,033 names**, one per line, lowercase a–z (228,145 bytes). The makemore README describes them as the most common names from the US Social Security Administration's baby-name data (2018).
- **URL (verified 200):** https://raw.githubusercontent.com/karpathy/makemore/master/names.txt
- **Licence:** the makemore repo is **MIT**. The underlying SSA baby-name data is a US federal government publication (public domain in the US): https://www.ssa.gov/oact/babynames/limits.html
- **Why it's ideal for beginners:** a 27-symbol vocabulary, a model that trains in seconds, and fun output that learners can judge themselves.

**(c) Short-text sentiment classifier: SST-2 (recommended) or IMDB**
- **SST-2 (Stanford Sentiment Treebank, binary)**, Socher et al. 2013:
  - Single sentences from movie reviews (Rotten Tomatoes), labelled positive/negative.
  - GLUE split: **67,349 train / 872 validation / 1,821 test**. Test labels are hidden, so **use validation as our test set** and carve a validation set out of train.
  - The sentences are short (most under 30 words). That matches "small texts" and keeps CPU training at a few minutes.
  - **URLs:** project page https://nlp.stanford.edu/sentiment/ · GLUE zip (verified 200, 7,439,277 bytes) https://dl.fbaipublicfiles.com/glue/data/SST-2.zip (tab-separated `sentence\tlabel`) · Hugging Face `stanfordnlp/sst2` https://huggingface.co/datasets/stanfordnlp/sst2 (`load_dataset("stanfordnlp/sst2")`, requires the `datasets` package).
  - **Licence:** **not clearly stated.** The Hugging Face card lists "unknown", and the Stanford page asks users to cite the paper. → Use for education with citation; don't redistribute.
- **IMDB Large Movie Review Dataset**, Maas et al. 2011, the alternative:
  - **25,000 train / 25,000 test** labelled reviews (balanced), plus 50,000 unlabelled.
  - Reviews are long (hundreds of words), so it is better for an "intermediate/advanced" exercise than for the first classifier.
  - **URL (verified 200, 84,125,825 bytes):** https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz
  - **Licence:** no explicit licence on the page (the HF card says "other"). The page asks you to cite the ACL 2011 paper.
- **Course decision:** the small-text classifier uses **SST-2 from the GLUE zip**, because it needs only `urllib` + `zipfile`, no extra dependency. IMDB is offered as an optional "longer texts" challenge.
- Sources: Socher et al. 2013 https://aclanthology.org/D13-1170/ · GLUE benchmark https://gluebenchmark.com/ · GLUE paper https://arxiv.org/abs/1804.07461 · Maas et al. 2011 https://aclanthology.org/P11-1015/ · IMDB page https://ai.stanford.edu/~amaas/data/sentiment/

### 10.5 Code corpus for autocompletion

**(a) Recommended: the CPython standard library already on the learner's machine**
- **Where:**
```python
import sysconfig; root = sysconfig.get_paths()["stdlib"]   # e.g. C:\Users\<you>\AppData\Local\Programs\Python\Python313\Lib
```
  Walk it for `*.py` files, skipping `site-packages`, `test`, `tests` and `idlelib` (tests are huge and repetitive; the test suite is an optional component of some installers anyway).
- **Measured on this machine** (Python 3.13.3, Windows, python.org installer): **1,748 `.py` files, 34.0 MB** in total, of which **23.4 MB** are in `test`/`tests`/`idlelib` folders. That leaves **≈10.7 MB of Python source**, about 10.7M characters: roughly 10× TinyShakespeare. That is plenty for a tiny GPT, and it needs **no download**. Numbers will differ by Python version and OS; the companion code should print its own count.
- **Licence:** CPython is distributed under the **PSF License Agreement** (with historical BeOpen/CNRI/CWI notices), a permissive, GPL-compatible licence that allows use, modification and derivative works as long as the copyright notice is retained. A few modules incorporate third-party code under their own permissive licences, listed in the same document. Training a private model locally on it is unproblematic. We never ship the corpus or trained weights in the repo.
  - https://docs.python.org/3/license.html · https://github.com/python/cpython/blob/main/LICENSE
- **Pre-processing suggestions:** concatenate files with a separator line such as `# <|file|> path/to/module.py`. Normalize line endings to `\n`, and replace tabs with 4 spaces so the vocabulary stays small. Optionally drop files over 200 KB (generated tables) and map rare non-ASCII characters to a single placeholder. Use `tokenize`/`ast` to *validate* sampled completions in an exercise ("what fraction of generated functions parse?"): https://docs.python.org/3/library/ast.html · https://docs.python.org/3/library/tokenize.html · `sysconfig` https://docs.python.org/3/library/sysconfig.html

**(b) Alternatives (optional, for learners who want more or other languages)**
- **The Stack smol** (`bigcode/the-stack-smol`, Hugging Face):
  - A small subset (about 0.1%) of The Stack: **10,000 random files per language**, about 2.6 GB of code.
  - **Gated:** you must log in to Hugging Face and accept The Stack's Terms of Use.
  - The Stack only contains *permissively licensed* source files, but each file stays under its **original licence** (attribution clauses apply), and redistribution must pass on the Terms of Use.
  - Good for a "train on JavaScript too" extension; not the default because of the login step.
  - https://huggingface.co/datasets/bigcode/the-stack-smol · paper (Kocetkov et al. 2022) https://arxiv.org/abs/2211.15533
- **CodeSearchNet** (Husain et al. 2019, GitHub/Microsoft):
  - About 2M (function, docstring) pairs in 6 languages (Go, Java, JavaScript, PHP, Python, Ruby), taken from open-source repos.
  - Projects without a licence explicitly permitting redistribution were filtered out. **Licensing is per repository** (dataset-level label: "other/various"), and there are no per-example licence fields.
  - The original S3 download links were retired and the GitHub repo is archived. Use the Hugging Face copy.
  - https://github.com/github/CodeSearchNet · https://huggingface.co/datasets/code-search-net/code_search_net · paper https://arxiv.org/abs/1909.09436

---

## 11. Recommended CPU-sized models and expected results per project

Assumptions: a 2020+ laptop CPU with 4–8 cores, 8–16 GB RAM, PyTorch CPU wheels, `torch.set_num_threads()` left at default. Times are **order-of-magnitude estimates** to be replaced by measured numbers in the smoke-test step. Accuracies are from published references where cited, otherwise typical values for the architecture, labelled "expected".

| Project | Data used | Model | Params | Train budget (CPU) | Expected result |
|---|---|---|---|---|---|
| **Digits** | MNIST 60k/10k | 2×[Conv3×3 → ReLU → MaxPool] (32, 64 ch, padding 1) → FC 3136→128 → Dropout → FC 128→10 | **421,642** | 3–5 epochs, about 0.5–2 min/epoch | **≈99.0–99.3%** test accuracy. The PyTorch MNIST example (2 conv + 2 FC) reaches about 99%. An MLP baseline (784→128→10) gets about 97–98%, a useful comparison lesson. |
| **Letters** | EMNIST letters 124.8k/20.8k | Same CNN with 26 outputs (optionally 3rd conv block + BatchNorm) | **423,706** (26-out) | 5–10 epochs, about 1–3 min/epoch | **≈92–94%**. The EMNIST paper's non-deep OPIUM baseline reported 85.15% on letters; CNNs in later literature report about 93–95%. Ambiguous pairs cap accuracy. |
| **Doodles** | Quick, Draw! 10 classes × 10k train / 2k test | Same CNN family, 10 outputs; add light augmentation (small shifts/rotations) | ≈0.42M | 5–8 epochs, about 1–2 min/epoch | **≈88–93%** on the 10 distinct classes listed. Accuracy falls sharply with many or similar classes (e.g. 345 classes). Show a confusion matrix: the errors are instructive. |
| **Names generator** | names.txt (32k) | (1) bigram counts → (2) Bengio-style MLP: emb 10, context 3, hidden 200 → (3) optional tiny Transformer | **11,897** (MLP) | seconds–2 min | Loss falls from **3.30** (uniform) to about **2.45** (bigram) to about **2.1–2.2** (MLP) on dev, roughly as in Karpathy's makemore lectures. Samples look name-like. |
| **Shakespeare generator** | TinyShakespeare 1.1M chars | char-level GPT: 4 layers, 4 heads, d=128, context 64, batch 12, dropout 0 | **≈0.8M** | 2,000 iterations, about 3–10 min | **val loss ≈ 1.88** — the figure nanoGPT's README reports for exactly this CPU config. Text has words, line breaks and character names, but little sense. The same data with the GPU config (6 layers, d=384, 10.65M params) reaches about 1.47. |
| **Sentiment classifier** | SST-2 (67k train / 872 eval) | (1) bag-of-embeddings: Embedding(V≈15k, 64) → mean-pool → Linear(64→2); (2) upgrade: 1-layer BiLSTM (hidden 128) | ≈1.0M (dominated by embeddings) | 2–5 epochs, about 1–3 min | **≈78–84%** validation accuracy for these small models trained from scratch (GLUE paper baselines for SST-2 are in the 80s; fine-tuned large Transformers exceed 93%, a nice "what scale buys you" note). |
| **Code autocompletion** | stdlib ≈10.7 MB | char-level GPT: 4 layers, 4 heads, d=192, context 128 (stage 1); optional BPE vocab 2–4k with d=256, context 256 (stage 2) | ≈1.8M (char) / ≈4–5M (BPE, tied embeddings) | 30–60 min (a few thousand iterations); a checkpoint is saved so learners can stop early | Measure **validation loss in nats per character** and the **parse rate** of completed functions (via `ast.parse`). Expected: completions keep indentation, close brackets, and produce plausible stdlib-style idioms (`if __name__ == "__main__":`, `self.`, `raise ValueError(...)`); longer outputs drift semantically. |

**Parameter arithmetic for the digits CNN** (to show in the lesson):
- conv1 $(9\cdot1+1)\cdot32=320$
- conv2 $(9\cdot32+1)\cdot64=18{,}496$
- fc1 $3136\cdot128+128=401{,}536$
- fc2 $128\cdot10+10=1{,}290$
- **total 421,642**

Note that 95% of the parameters sit in fc1. That motivates **global average pooling** as an advanced optimisation: replacing flatten+fc1 with average pooling over the 7×7 maps cuts the model to about 20k parameters at a small accuracy cost (Lin et al. 2013, *Network in Network*, https://arxiv.org/abs/1312.4400).

**Why these sizes are realistic on CPU.** A forward+backward pass costs roughly 6 × params × tokens FLOPs for Transformers (Kaplan et al. 2020, https://arxiv.org/abs/2001.08361).
- For the 0.8M Shakespeare model: 2,000 iterations × 12 × 64 tokens ≈ 1.5M tokens gives about $7\times10^{12}$ FLOPs. A laptop CPU sustaining about 50–200 GFLOP/s in PyTorch finishes that in roughly 1–3 minutes of pure compute, so 3–10 minutes with overhead is plausible. This matches nanoGPT's "about 3 minutes" claim for that config.
- For the code model: 1.8M params × 5,000 iterations × 32 × 128 tokens ≈ 20M tokens gives about $2\times10^{14}$ FLOPs, roughly 20–60 min.

The smoke tests must confirm both.

**Smoke-mode guidance for the companion code (`--smoke`):** use 1–2% of the data, 1 epoch or 50 iterations, and assert that the loss decreased and the output shapes are correct. Finish in under 60 seconds on CPU, so CI and learners can verify the setup fast.

---

## 12. Teaching order and common pitfalls

**Suggested order inside the advanced track:**
1. Convolution by hand (the §1 worked example, as an exercise: compute $Y_{1,1}$)
2. Output-size formula drills
3. CNN on MNIST
4. Why depth and residuals help (ResNet concept)
5. Sequences: bigram → MLP language model (Bengio)
6. RNN/LSTM gates (scalar walk-through)
7. Attention by hand (the 3-token table)
8. Self-attention + causal mask
9. Transformer block
10. Tiny GPT on Shakespeare
11. Tokenization and the BPE worked example
12. Sampling knobs
13. Code GPT

Each project track can be entered directly. Its first lesson links back to the minimum prerequisites (e.g. the doodle track needs only "CNN on MNIST" concepts).

**Pitfalls the lessons must pre-empt** (each is a frequent forum question):
- Forgetting the channel dimension: a `(N, 28, 28)` tensor fed to `Conv2d` fails. Use `.unsqueeze(1)`.
- Applying softmax before `CrossEntropyLoss` (it expects raw logits).
- Forgetting `model.eval()` / `torch.no_grad()` at test time (Dropout and BatchNorm behave differently).
- EMNIST: not transposing (the model learns, but the drawing app fails) and labels 1–26.
- Drawing apps: wrong polarity (black ink on white) or no centring, so real-world accuracy collapses although test accuracy is 99%. The cause is **distribution shift**, which deserves its own callout box.
- LMs: off-by-one targets (`y = x[1:]` for `x[:-1]`); forgetting the causal mask (training loss drops to near zero because the model "cheats" by seeing the answer, a great debugging exercise); a context longer than `block_size` at generation time (crop to the last `block_size` tokens).
- Tokenizers: a vocabulary too big for the model size (§7); training the tokenizer on the validation set (leakage).
- Quick, Draw!: loading whole `.npy` files into RAM on 8 GB machines. Use `mmap_mode="r"` and slice.
- Windows: `DataLoader(num_workers>0)` needs the `if __name__ == "__main__":` guard and picklable (non-lambda) transforms. Default to `num_workers=0` in the companion code.

---

## 13. Bibliography (deduplicated)

**Papers: architectures**
1. LeCun, Bottou, Bengio, Haffner (1998). Gradient-Based Learning Applied to Document Recognition. *Proc. IEEE* 86(11). http://vision.stanford.edu/cs598_spring07/papers/Lecun98.pdf · https://doi.org/10.1109/5.726791
2. LeCun et al. (1989). Backpropagation Applied to Handwritten Zip Code Recognition. https://doi.org/10.1162/neco.1989.1.4.541
3. Krizhevsky, Sutskever, Hinton (2012). ImageNet Classification with Deep Convolutional Neural Networks. https://papers.nips.cc/paper_files/paper/2012/hash/c399862d3b9d6b76c8436e924a68c45b-Abstract.html
4. Zeiler & Fergus (2014). Visualizing and Understanding Convolutional Networks. https://arxiv.org/abs/1311.2901
5. Simonyan & Zisserman (2014). Very Deep Convolutional Networks (VGG). https://arxiv.org/abs/1409.1556
6. Lin, Chen, Yan (2013). Network in Network. https://arxiv.org/abs/1312.4400
7. He, Zhang, Ren, Sun (2015). Deep Residual Learning for Image Recognition. https://arxiv.org/abs/1512.03385
8. Ioffe & Szegedy (2015). Batch Normalization. https://arxiv.org/abs/1502.03167
9. Dumoulin & Visin (2016). A guide to convolution arithmetic for deep learning. https://arxiv.org/abs/1603.07285
10. Hochreiter & Schmidhuber (1997). Long Short-Term Memory. https://doi.org/10.1162/neco.1997.9.8.1735
11. Gers, Schmidhuber, Cummins (2000). Learning to Forget. https://doi.org/10.1162/089976600300015015
12. Bengio, Simard, Frasconi (1994). Learning long-term dependencies with gradient descent is difficult. https://doi.org/10.1109/72.279181
13. Cho et al. (2014). Learning Phrase Representations using RNN Encoder–Decoder. https://arxiv.org/abs/1406.1078
14. Chung, Gulcehre, Cho, Bengio (2014). Empirical Evaluation of Gated Recurrent Neural Networks. https://arxiv.org/abs/1412.3555
15. Graves (2013). Generating Sequences With Recurrent Neural Networks. https://arxiv.org/abs/1308.0850
16. Bengio, Ducharme, Vincent, Jauvin (2003). A Neural Probabilistic Language Model. *JMLR* 3. https://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf
17. Mikolov et al. (2013). Efficient Estimation of Word Representations. https://arxiv.org/abs/1301.3781
18. Sutskever, Vinyals, Le (2014). Sequence to Sequence Learning. https://arxiv.org/abs/1409.3215
19. Bahdanau, Cho, Bengio (2014). Neural Machine Translation by Jointly Learning to Align and Translate. https://arxiv.org/abs/1409.0473
20. Luong, Pham, Manning (2015). Effective Approaches to Attention-based NMT. https://arxiv.org/abs/1508.04025
21. Vaswani et al. (2017). Attention Is All You Need. https://arxiv.org/abs/1706.03762
22. Ba, Kiros, Hinton (2016). Layer Normalization. https://arxiv.org/abs/1607.06450
23. Hendrycks & Gimpel (2016). GELUs. https://arxiv.org/abs/1606.08415
24. Press & Wolf (2016). Using the Output Embedding to Improve Language Models. https://arxiv.org/abs/1608.05859
25. Radford et al. (2018). Improving Language Understanding by Generative Pre-Training. https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf
26. Radford et al. (2019). Language Models are Unsupervised Multitask Learners. https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
27. Kaplan et al. (2020). Scaling Laws for Neural Language Models. https://arxiv.org/abs/2001.08361
28. Jain & Wallace (2019). Attention is not Explanation. https://arxiv.org/abs/1902.10186

**Papers: tokenization and decoding**
29. Sennrich, Haddow, Birch (2016). Neural Machine Translation of Rare Words with Subword Units. https://arxiv.org/abs/1508.07909 · https://aclanthology.org/P16-1162/
30. Kudo (2018). Subword Regularization (Unigram LM). https://arxiv.org/abs/1804.10959
31. Kudo & Richardson (2018). SentencePiece. https://arxiv.org/abs/1808.06226
32. Fan, Lewis, Dauphin (2018). Hierarchical Neural Story Generation (top-k). https://arxiv.org/abs/1805.04833
33. Holtzman et al. (2019). The Curious Case of Neural Text Degeneration (nucleus sampling). https://arxiv.org/abs/1904.09751

**Papers: datasets**
34. Cohen, Afshar, Tapson, van Schaik (2017). EMNIST: an extension of MNIST to handwritten letters. https://arxiv.org/abs/1702.05373
35. Ha & Eck (2017). A Neural Representation of Sketch Drawings. https://arxiv.org/abs/1704.03477
36. Socher et al. (2013). Recursive Deep Models for Semantic Compositionality Over a Sentiment Treebank. https://aclanthology.org/D13-1170/
37. Wang et al. (2018). GLUE. https://arxiv.org/abs/1804.07461
38. Maas et al. (2011). Learning Word Vectors for Sentiment Analysis. https://aclanthology.org/P11-1015/
39. Kocetkov et al. (2022). The Stack: 3 TB of permissively licensed source code. https://arxiv.org/abs/2211.15533
40. Husain et al. (2019). CodeSearchNet Challenge. https://arxiv.org/abs/1909.09436

**Explainers, courses and code**
41. CS231n, CNN notes. https://cs231n.github.io/convolutional-networks/
42. Dive into Deep Learning (d2l.ai): CNNs https://d2l.ai/chapter_convolutional-neural-networks/index.html · modern CNNs https://d2l.ai/chapter_convolutional-modern/index.html · LSTM https://d2l.ai/chapter_recurrent-modern/lstm.html · GRU https://d2l.ai/chapter_recurrent-modern/gru.html · language models https://d2l.ai/chapter_recurrent-neural-networks/language-model.html · attention & Transformers https://d2l.ai/chapter_attention-mechanisms-and-transformers/index.html
43. Olah (2015). Understanding LSTM Networks. https://colah.github.io/posts/2015-08-Understanding-LSTMs/
44. Olah & Carter (2016). Attention and Augmented Recurrent Neural Networks. https://distill.pub/2016/augmented-rnns/
45. Alammar. The Illustrated Transformer https://jalammar.github.io/illustrated-transformer/ · The Illustrated GPT-2 https://jalammar.github.io/illustrated-gpt2/
46. Rush et al. The Annotated Transformer. https://nlp.seas.harvard.edu/annotated-transformer/
47. Karpathy (2015). The Unreasonable Effectiveness of RNNs. http://karpathy.github.io/2015/05/21/rnn-effectiveness/ · char-rnn https://github.com/karpathy/char-rnn
48. Karpathy. nanoGPT https://github.com/karpathy/nanoGPT · minGPT https://github.com/karpathy/minGPT · makemore https://github.com/karpathy/makemore · minbpe https://github.com/karpathy/minbpe · nanochat https://github.com/karpathy/nanochat · Zero to Hero https://karpathy.ai/zero-to-hero.html · Let's build GPT https://www.youtube.com/watch?v=kCc8FmEb1nY · Let's build the GPT Tokenizer https://www.youtube.com/watch?v=zduSFxRajkE
49. Hugging Face LLM course: BPE https://huggingface.co/learn/llm-course/chapter6/5 · tokenizers https://huggingface.co/learn/llm-course/chapter2/4 · `tokenizers` docs https://huggingface.co/docs/tokenizers/index · quicktour https://huggingface.co/docs/tokenizers/quicktour · *How to generate text* https://huggingface.co/blog/how-to-generate
50. OpenAI tiktoken. https://github.com/openai/tiktoken

**PyTorch documentation**
51. `nn` index https://docs.pytorch.org/docs/stable/nn.html · `Conv2d` https://docs.pytorch.org/docs/stable/generated/torch.nn.Conv2d.html · `MaxPool2d` https://docs.pytorch.org/docs/stable/generated/torch.nn.MaxPool2d.html · `BatchNorm2d` https://docs.pytorch.org/docs/stable/generated/torch.nn.BatchNorm2d.html · `LSTM` https://docs.pytorch.org/docs/stable/generated/torch.nn.LSTM.html · `GRU` https://docs.pytorch.org/docs/stable/generated/torch.nn.GRU.html · `Embedding` https://docs.pytorch.org/docs/stable/generated/torch.nn.Embedding.html · `MultiheadAttention` https://docs.pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html · `scaled_dot_product_attention` https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html · `TransformerEncoderLayer` https://docs.pytorch.org/docs/stable/generated/torch.nn.TransformerEncoderLayer.html · `Transformer` https://docs.pytorch.org/docs/stable/generated/torch.nn.Transformer.html · `LayerNorm` https://docs.pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html · `CrossEntropyLoss` https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html · `multinomial` https://docs.pytorch.org/docs/stable/generated/torch.multinomial.html
52. torchvision `MNIST` https://docs.pytorch.org/vision/stable/generated/torchvision.datasets.MNIST.html · `EMNIST` https://docs.pytorch.org/vision/stable/generated/torchvision.datasets.EMNIST.html
53. Tutorials: Datasets & DataLoaders https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html · CIFAR-10 classifier https://docs.pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html · pytorch/examples MNIST https://github.com/pytorch/examples/tree/main/mnist

**Dataset pages and licences**
54. MNIST https://yann.lecun.com/exdb/mnist/ · Wikipedia https://en.wikipedia.org/wiki/MNIST_database · Voxel51 entry https://docs.voxel51.com/dataset_zoo/datasets/mnist.html
55. EMNIST (NIST) https://www.nist.gov/itl/products-and-services/emnist-dataset · NIST SD19 https://www.nist.gov/srd/nist-special-database-19 · TFDS https://www.tensorflow.org/datasets/catalog/emnist
56. Quick, Draw! repo https://github.com/googlecreativelab/quickdraw-dataset · data page https://quickdraw.withgoogle.com/data · categories https://raw.githubusercontent.com/googlecreativelab/quickdraw-dataset/master/categories.txt · example file https://storage.googleapis.com/quickdraw_dataset/full/numpy_bitmap/cat.npy · HF mirror https://huggingface.co/datasets/google/quickdraw · CC BY 4.0 https://creativecommons.org/licenses/by/4.0/
57. TinyShakespeare https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt · TFDS https://www.tensorflow.org/datasets/catalog/tiny_shakespeare
58. names.txt https://raw.githubusercontent.com/karpathy/makemore/master/names.txt · SSA baby names https://www.ssa.gov/oact/babynames/limits.html
59. SST https://nlp.stanford.edu/sentiment/ · GLUE https://gluebenchmark.com/ · SST-2 zip https://dl.fbaipublicfiles.com/glue/data/SST-2.zip · HF https://huggingface.co/datasets/stanfordnlp/sst2
60. IMDB https://ai.stanford.edu/~amaas/data/sentiment/ · archive https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz
61. Python licence https://docs.python.org/3/license.html · CPython LICENSE https://github.com/python/cpython/blob/main/LICENSE · `sysconfig` https://docs.python.org/3/library/sysconfig.html · `ast` https://docs.python.org/3/library/ast.html · `tokenize` https://docs.python.org/3/library/tokenize.html
62. The Stack smol https://huggingface.co/datasets/bigcode/the-stack-smol · CodeSearchNet https://github.com/github/CodeSearchNet · HF https://huggingface.co/datasets/code-search-net/code_search_net

**Wikipedia (for in-text hyperlinks)**
63. https://en.wikipedia.org/wiki/Convolutional_neural_network · https://en.wikipedia.org/wiki/LeNet · https://en.wikipedia.org/wiki/AlexNet · https://en.wikipedia.org/wiki/Residual_neural_network · https://en.wikipedia.org/wiki/Long_short-term_memory · https://en.wikipedia.org/wiki/Language_model · https://en.wikipedia.org/wiki/Attention_(machine_learning) · https://en.wikipedia.org/wiki/Transformer_(deep_learning_architecture) · https://en.wikipedia.org/wiki/Byte_pair_encoding · https://en.wikipedia.org/wiki/Softmax_function
