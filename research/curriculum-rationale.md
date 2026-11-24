# Curriculum rationale

This document explains why `src/data/curriculum.json` looks the way it does. The JSON is the map that every content step writes against. This file gives the reasoning, the trade-offs and the coverage checks behind it. The sources are the five research files: `01-foundations.md`, `02-architectures-and-datasets.md`, `03-chess-engine.md`, `04-setup.md` and `05-ux-design-brief.md`.

## 1. The shape in one table

| Track | Kind | Modules | Lessons | Reading time | Planned exercises |
|---|---|---|---|---|---|
| `setup` | core, **optional** | 4 | 9 | 2 h 19 min | 22 |
| `beginner` | core | 4 | 14 | 4 h 31 min | 45 |
| `intermediate` | core | 4 | 12 | 4 h 45 min | 38 |
| `advanced` | core | 4 | 12 | 5 h 00 min | 38 |
| `project-digits-letters` | project | 2 | 6 | 2 h 10 min | 17 |
| `project-doodles` | project | 2 | 5 | 1 h 45 min | 14 |
| `project-text` | project | 2 | 6 | 2 h 20 min | 18 |
| `project-code-autocomplete` | project | 2 | 6 | 2 h 25 min | 18 |
| `project-chess` | project | 2 | 9 | 3 h 45 min | 27 |
| **Total** | | **26** | **79** | **29 h** | **237** |

- **Every lesson is 10–30 minutes** of reading and exercises. The checker rejects anything outside that range. The setup lessons run 10–25 minutes, core lessons 12–30 and project lessons 15–30.
- The minutes cover reading and exercises only. Project lessons also have **hands-on time** for downloads, CPU training runs and engine matches. Research 02 §11 and 03 d3 give the estimates: about 0.5–2 min per epoch for the vision CNNs, 30–60 min for the code GPT, and 1–1.5 h for a 100-game chess match. Lessons show these as "Run it" estimates, separate from reading time.
- **Certificate path:** beginner + intermediate + advanced is 38 lessons and about 14 h 16 min of reading. One project adds 1 h 45 min to 3 h 45 min. That fits a free certification course: weeks of evenings, not months.

## 2. Design principles

1. **One spine, many doors.** Beginner → intermediate → advanced is a single ordered spine. Every other track is a door into it: setup comes before it and is optional, and the projects branch off it and can be entered directly.
2. **Prerequisites are hard and always earlier.** A lesson's `prerequisites` list only what you truly need, and each prerequisite is taught earlier in the global order (setup → beginner → intermediate → advanced → projects), or earlier in the same track. `scripts/lib/check-curriculum.mjs` enforces this, so there are no gaps and no cycles. The recommended order is the JSON order.
3. **Setup is truly optional.** No lesson outside setup lists a setup lesson as a prerequisite. Lessons that need software say so with `needs` (`python`, `numpy`, `torch`, `chess`), and `environmentHelp` maps each need to the setup lesson **or** the Colab lesson. The checker enforces this too.
4. **Projects are independent.** A project lesson can depend on core lessons and on earlier lessons of its own track, never on another project. So any project can be the learner's first, or only, one.
5. **Math piece by piece, in the order the networks need it.** Vectors → matrices → derivatives → chain rule → probability/softmax all come before the neuron. Each math lesson ends in the place where the next neural-network lesson uses it: the dot product becomes the neuron, matmul becomes a layer, the chain rule becomes backprop, softmax becomes cross-entropy. This follows research 01's curriculum-mapping table, with two changes explained in §4.
6. **Build first, then generalise.** The beginner capstone trains a classifier in NumPy with hand-derived gradients before PyTorch appears. Intermediate rebuilds the same thing with autograd. That way learners know what `loss.backward()` does before they rely on it (research 01 §7, §10; micrograd).
7. **Bite-sized and complete.** Each lesson has 3–5 learning goals, at least 3 key sources and at least 2 planned exercises of the schema types (`mcq`, `numeric`, `short`, `reveal`). These match the validator's rules for written lessons (≥ 3 sources, ≥ 2 exercises) and the UX brief's "2–4 exercise cards" (05 §5.3).

## 3. Skip paths and entry points

The UX brief puts three chips on the dashboard: *Skip setup*, *I know the math* and *Go straight to a project* (05 §5.2). The brief also rules out locks ("No `locked` state", 05 C1), and the user asked for full control. So `skipPaths` in the JSON defines five starting points, and none of them hides or locks anything:

| Skip path | Skips | Starts at | For |
|---|---|---|---|
| `skip-setup` | setup track | `what-is-ai` | already installed, or using Colab |
| `know-python` | setup, `python-for-ml`, `numpy-arrays` | `vectors-dot-product` | programmers new to ML |
| `know-the-math` | setup, the 5 math lessons | `artificial-neuron` | STEM students |
| `intermediate-start` | setup, beginner | `multilayer-perceptron` | intermediate learners who have trained a model before |
| `straight-to-project` | setup | the chosen project's `quickStart` | people who want to build now |

Under `skipPolicy`, skipping changes only where the path starts and what "Up next" suggests. It **never marks lessons complete**. Learners can still mark any lesson complete themselves, which also counts towards the self-issued certificate. That is the "full control" the user asked for, and it matches the certificate wording decision ("Self-issued certificate of completion, stated on the certificate").

### Project quick starts

Each project track has:
- **`quickStart`**: the core lessons whose content the project uses **directly**. The checker requires it to contain every direct non-project prerequisite of the track's lessons, so a learner who reads just these lessons can start lesson 1 and never meet an unexplained prerequisite. Their own prerequisites are assumed background. A learner without that background follows `recommendedPath`.
- **`recommendedPath`**: the full route (track ids or lesson slugs, ending with the project) for someone starting from zero.

| Project | quickStart (count, reading time) | Notes |
|---|---|---|
| Digits and letters | 8 lessons, 3 h 10 min | python, NumPy, MLP, nn.Module/DataLoader, training loop, metrics, CNNs, saving models |
| Doodles | 8 lessons, 3 h 15 min | the same vision core plus overfitting/regularization (augmentation lesson) |
| Small text | 10 lessons, 3 h 55 min | probability/softmax and loss (bigram counts), embeddings and RNNs (MLP LM, LSTM, BiLSTM). **No Transformer needed.** |
| Code autocompletion | 10 lessons, 4 h | the sequence half of advanced: embeddings, attention, Transformers, BPE, sampling, efficient inference |
| Chess | 7 lessons, 2 h 50 min | `quickStartNote`: lessons 1–5 (the classic engine) need only `python-for-ml` and `game-tree-search`, so you can start building straight away and pick up the deep-learning lessons before lesson 6 |

## 4. Track by track

### Setup (optional, 9 lessons)
This follows the lesson skeleton in research 04 §9 closely: before you start → terminal → Python → VS Code → venv → PyTorch → libraries and verify → Colab → troubleshooting. Two changes:
- The skeleton's item 8 (optional Git/WSL) and item 10 (troubleshooting FAQ) are merged into **`setup-troubleshooting`**. Both are "help when something is off", and merging them keeps the lesson count close to the brief's "~8" (9 rather than 10).
- Every setup lesson lists the **screenshot IDs** from research 04 §8 that it needs (`screenshots`), so the setup writer knows exactly which of the 33 captures go where. All 33 IDs are assigned.

The decisions research 04 already verified are carried into the lesson descriptions: Python 3.14.10 as the recommendation (3.12–3.15 also work, avoid 3.14.1); the Windows install manager as route A with the legacy installer as the fallback; CPU as the default compute; install `chess`, not `python-chess`; the project folder outside OneDrive; always `python -m pip`.

### Beginner (14 lessons, 4 modules)
- **What AI is** (2): definitions and timeline, then *data, features and labels: learning as function fitting*. The brief asks for data/features/labels explicitly. It comes second because every later lesson talks about inputs, labels and train/validation/test splits.
- **Python and NumPy for ML** (2): Python only to the depth the course uses. **Recursion** (the chess search needs it) and **classes** (`nn.Module` needs them) are named goals, so later lessons can assume them.
- **The math, piece by piece** (5): vectors/dot product → matrices/matmul → derivatives → chain rule/partials/gradients → probability/softmax. Research 01 splits these into L4–L8. We kept their order but put softmax in its own lesson, ahead of the neuron, so cross-entropy has its pieces ready.
- **Neural networks from scratch** (5): the existing sample lessons `artificial-neuron` and `gradient-descent` are kept with the same slugs, titles, level and module, plus `perceptron-activations`, `loss-functions` and the capstone `first-model-numpy`.

Changes from research 01's mapping:
- Research 01 put "Building an MLP" in beginner. We moved the **MLP to intermediate**, next to backprop, because the brief lists MLP and backprop together under intermediate, and an MLP without backprop can only be run, not trained.
- **Loss functions** got their own lesson between softmax and gradient descent, so gradient descent has something to descend.

### Intermediate (12 lessons, 4 modules)
These are exactly the brief's topics, in dependency order. *MLP → backprop* (with a micrograd-style mini engine) → *PyTorch tensors/autograd → nn.Module/Dataset/DataLoader → training loop* (MNIST MLP at about 97%, the bridge to the digits project) → *metrics → overfitting/regularization → optimizers → init/normalization* → *hyperparameters → debugging → saving/loading*.
- The PyTorch topics are split into **two lessons** (tensors and autograd; modules and data) so each stays under 30 minutes.
- Metrics come **before** regularization, because you cannot diagnose overfitting without a validation metric.
- `saving-loading-models` depends only on the training loop. It sits last in the track but is short, and every project capstone needs it.

### Advanced (12 lessons, 4 modules)
These are exactly the brief's 12 topics. The order follows research 02 §12's teaching order, adapted:
- **Vision:** CNNs → LeNet-to-ResNet (BatchNorm, residuals, global average pooling).
- **Sequences and language:** embeddings and neural LMs (Bengio) → RNN/LSTM/GRU → attention → Transformer/GPT → tokenization/BPE → language modelling, perplexity and sampling. Research 02 placed tokenization after the tiny GPT. We kept it there, so learners first see a working character-level model and then learn why subwords help. *Language modelling and sampling* closes the module because it needs both the Transformer and tokens.
- **Games:** game-tree search (minimax, negamax, alpha-beta on tic-tac-toe) → an **RL/self-play overview** (AlphaZero and Leela vs Stockfish's alpha-beta + NNUE). The RL lesson is deliberately an overview without code. A real RL training loop is beyond a CPU-sized free course, and the chess project uses supervised learning on Stockfish evaluations (research 03 a9–a10).
- **Reusing and shipping:** transfer learning → efficient inference (quantization, pruning, distillation, ONNX, with NNUE's int16/int8 scheme as the real-world example). Efficient inference is a prerequisite of the chess search lesson and the code-completion CLI, so it pays off immediately.

`game-tree-search` needs only `python-for-ml`. It sits in advanced for its level of abstraction, but it is reachable early, which is what makes the chess quick start short.

### Project: handwritten digits and letters (6 lessons)
MNIST data → MLP baseline (97–98%) → CNN (≈99%, the 421,642-parameter model from research 02 §11) → evaluation/confusion matrix → EMNIST letters (orientation transpose, labels 1–26 → 0–25, ≈92–94% ceiling) → **capstone drawing app** with MNIST-identical preprocessing and the distribution-shift callout (research 02 §10.1, §12). Digits and letters share one code directory and one model file, so letters is "change the dataset, keep the model", the cleanest demonstration of how far a model generalises.

### Project: doodles (5 lessons)
Quick, Draw! data streamed with HTTP Range requests (≈9.4 MB per class instead of 1–1.5 GB, research 02 §10.3) → doodle CNN (≈88–93% on 10 classes) → augmentation and regularization → reading the confusion matrix → **capstone live guessing app** with Quick, Draw!-style preprocessing (bounding box, not centre of mass). The CC BY 4.0 attribution line is a planned content item.

### Project: small-text models (6 lessons)
Two halves, matching the brief's "small texts":
- **Generating:** bigram name generator (loss 3.30 → ≈2.45) → Bengio-style MLP (≈2.1–2.2) → **character-level LSTM on TinyShakespeare**.
- **Classifying:** SST-2 data → bag-of-embeddings classifier (≈78–82%) → **capstone BiLSTM** that classifies your own sentences.

*Decision:* research 02 §11 suggests a tiny GPT for Shakespeare. The text track uses a **char-LSTM** instead (Karpathy's char-rnn approach) and keeps the GPT for the code track. This avoids teaching the same model twice, lets the text project skip the Transformer lessons (a much shorter quick start), and exercises the RNN lesson. Comparing against the GPT is a stretch goal.

### Project: code autocompletion (6 lessons)
Corpus from the learner's own CPython standard library (no download, PSF licence, research 02 §10.5) → tiny GPT in one file → CPU training with checkpoints → sampling and the **`ast.parse` parse-rate metric** → stage-2 BPE tokenizer for code → **capstone CLI** with the inference speed-ups from `efficient-inference`. The model sizes (≈1.8M parameters with characters, ≈4–5M with BPE) and the 30–60 min CPU budget come from research 02 §11.

### Project: mini chess engine (9 lessons)
This is research 03's 10-milestone build path compressed into 9 lessons:

| Lesson | Milestone(s) |
|---|---|
| `chess-board-moves` | M1: FEN, legal moves, perft(3) = 8,902 |
| `chess-evaluation` | M2: material + PST, side-to-move sign test |
| `chess-alpha-beta` | M3: negamax + alpha-beta, mate/draw handling, puzzles |
| `chess-ordering-quiescence` | M4 + M5: MVV-LVA/killers/history, quiescence (both short, 1–2 h and 1 h) |
| `chess-iterative-deepening` | M6: iterative deepening, Zobrist, TT with mate-score adjustment |
| `chess-dataset` | M7: Lichess eval DB (CC0) streaming, cp → side-to-move, 768 features |
| `chess-train-evaluator` | M8: 768→256→32→1 with EmbeddingBag and ClippedReLU, WDL-space loss |
| `chess-nn-search` | M9 + optional upgrade (c): NumPy inference in search, the NNUE accumulator idea, 100-game match |
| `chess-uci-elo` | M10: UCI wrapper, fastchess compliance, Elo vs Stockfish `UCI_Elo` anchors, SPRT |

The engine plays legal chess from lesson 3, so learners always have something that works. Pitfall d4 (sign bugs, TT mate scores, repetition, NN on non-quiet positions, too few games, time losses, GPL) is assigned to the lessons where each one bites. The "do not claim current Stockfish net sizes / learner Elo as fact" rule from 03's appendix is part of the capstone goals.

## 5. Coverage of the user's request

| Request | Where |
|---|---|
| Starts with setup, installing Python and everything needed, with direct links and screenshots | `setup` (9 lessons, every screenshot ID from 04 §8 assigned, sources are the direct download pages) |
| …or skip it and do the course | `setup.optional`, `skipPaths.skip-setup`, no lesson outside setup depends on setup |
| …or do the single projects immediately | every project has `quickStart` + `recommendedPath`; `skipPaths.straight-to-project` |
| Beginner to advanced, also for intermediate learners | beginner → intermediate → advanced spine; `skipPaths.intermediate-start` |
| Recognise handwritten numbers | `project-digits-letters`: `mnist-*`, `handwriting-app` |
| Recognise letters | `emnist-letters`, `handwriting-app` |
| Recognise doodles | `project-doodles` |
| Small texts | `project-text` (names and Shakespeare generators, short-sentence sentiment classifier) |
| Code autocompletion | `project-code-autocomplete` |
| Chess engine with a neural network, a mini Stockfish | `project-chess` (alpha-beta + NN evaluator + UCI + Elo) |
| Math piece by piece, with analogies for beginners | beginner math module. The `covers` notes name the analogy for each lesson, and the validator already requires an `<Analogy>` in every beginner and intermediate lesson |
| Everything sourced, Wikipedia style | each lesson lists ≥ 3 key sources from a 265-entry `sourceRegistry`, each pointing to its research section |
| Exercise library, full control | 237 planned exercises with types and counts; no locks; skip never auto-completes |
| Certificate | `certificateRequirement`: all of beginner, intermediate and advanced, plus ≥ 1 complete project track; setup never required |

## 6. The certificate requirement

```json
"certificateRequirement": {
  "allLessonsInTracks": ["beginner", "intermediate", "advanced"],
  "projectTracks": ["project-digits-letters", "project-doodles", "project-text", "project-code-autocomplete", "project-chess"],
  "minProjectTracksCompleted": 1,
  "setupRequired": false
}
```

Why: the three core tracks are the knowledge the certificate vouches for, and one finished project proves the learner can build something with it. Requiring all five projects would roughly double the path, and the projects overlap a lot by design (three are vision CNNs or sequence models). Setup is excluded because Colab users never need it. "Complete a project track" means every lesson in that track is marked complete. The certificate generator step should read these fields instead of hard-coding them.

## 7. Sources

- Each lesson's `sources` are **key** sources: the ones the research files already used for that topic. Each one points to an entry in `sourceRegistry` (title, https URL, publisher, and the research section it came from). Writers copy them into frontmatter, add `accessed` dates, cite each one in the text, and may add more.
- The registry is https-only, because the lesson validator rejects http sources. So two http-only references from the research are **not** used as lesson sources: Nielsen's *Neural Networks and Deep Learning* and Karpathy's 2015 RNN post at its http URL (the https URL is used instead and returned 200). Sutton and Barto's RL book did not answer over https, so the RL overview cites OpenAI Spinning Up and Wikipedia instead.
- **Sources added in this step** (research did not cover these topics; every URL returned HTTP 200 on 2026-11-24), marked `"research": "added (curriculum step)"` in the registry:
  - Transfer learning: the PyTorch transfer-learning tutorial, Yosinski et al. 2014, torchvision models, d2l fine-tuning, Wikipedia.
  - Efficient inference: PyTorch quantization, Jacob et al. 2017, Han et al. 2015 (Deep Compression), Hinton et al. 2015 (distillation), torch.onnx.
  - RL: OpenAI Spinning Up, Wikipedia.
  - Saving models: the PyTorch saving/loading tutorial and serialization notes.
  - Others: Python tutorial (control flow, classes), Wikipedia on supervised learning, features, perplexity, word embeddings, minimax and alpha-beta, and the *Deep Learning* book's CNN and RNN chapters.
  
  The writers of `transfer-learning`, `efficient-inference`, `reinforcement-learning-self-play` and `saving-loading-models` should read these primary pages directly, because no research file distils them.

## 8. How the map is enforced

- `node scripts/lib/check-curriculum.mjs` runs the structural checks on their own. `node scripts/validate-content.mjs` runs them as part of content validation. Both currently pass: 79 lessons, 0 errors.
- The checks: all 9 tracks in order; unique kebab-case slugs; 10–30 min; 3–5 goals; ≥ 2 planned exercises of schema types; ≥ 3 sources that resolve in `sourceRegistry`; prerequisites exist and come earlier; nothing outside setup depends on setup; no cross-project dependencies; project `codeFiles` sit under `codeDir`; `quickStart` covers every direct core prerequisite; `recommendedPath` ends with its track; `skipPaths` resolve; the certificate requirement has the right shape. Negative tests (a forward prerequisite, a setup dependency, a cross-project link, a gap in quickStart, a 45-minute lesson, a certificate with 0 projects, a missing track, an unknown source) all fail as they should.
- Unwritten lessons are reported as "planned". `--complete` makes them, and their planned `codeFiles`, mandatory. Content steps should run `node scripts/validate-content.mjs --track <id> --complete` when they finish a track, and final QA should run it without `--track`.
- For written lessons, the validator warns when the frontmatter level, module or prerequisites drift from the curriculum. Today it warns that the two sample lessons do not yet list `vectors-dot-product`/`data-features-labels` and `loss-functions`/`chain-rule-gradients`. Those lessons do not exist yet, and listing them would be a validator error. The beginner-track writer should add them once the lessons exist.

## 9. Notes for the content steps

- Code paths are planned, not yet written. Core lessons that show code use `code/core/<track>/…`, and projects use `code/projects/<name>/…` (`digits-letters`, `doodles`, `text`, `code-autocomplete`, `chess`). Research 03 already used `code/projects/chess/`, so the folder names drop the `project-` prefix. Every companion script should have a `--smoke` mode that runs in under 60 s (research 02 §11).
- Lesson `covers` notes are a brief, not prose. Where a number is an estimate in the research (accuracy, CPU time, Elo), the lesson must present it as an estimate until the smoke-test step measures it.
- Analogies named in `covers` come from the research analogy banks (01 per topic, 03 appendix). Follow the guardrails: say where each analogy breaks, never say networks "think" or "understand", and never present the brain analogy as fact (01, notes for lesson writers).
- If a writer renames, splits or merges a lesson, update `curriculum.json` in the same commit and rerun `node scripts/lib/check-curriculum.mjs`.
