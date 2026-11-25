# Code autocompletion with a tiny GPT

Companion code for the course track **Code autocompletion**
(`src/content/lessons/project-code-autocomplete/`). You build a ~1.8M-parameter
GPT, train it on a laptop CPU on Python's own standard library, and use it to
complete Python code from the command line.

| File | What it does | Lesson |
|---|---|---|
| `corpus.py` | Collects the standard library's `.py` files via `sysconfig`, cleans them to a 97-character alphabet, splits train/val by file | Building a code corpus |
| `model.py` | The GPT: embeddings, causal self-attention, MLP, weight-tied head, `generate` | Writing a tiny GPT |
| `train.py` | Training loop: random windows, AdamW, warm-up + cosine, checkpoints, `--resume`, `--smoke` | Training the code model |
| `complete.py` | Streaming CLI: `--prompt`, interactive mode, `--samples`, `--watch FILE`, `--bench`, `--quantize` | Sampling; Capstone |
| `evaluate.py` | Parse rate: how many generated function bodies are valid Python (`ast.parse`) | Sampling and parse rate |
| `tokenizer.py` | Character tokenizer and a from-scratch BPE trainer/encoder | Stage 2: BPE |

## Requirements

Python 3.10+ and PyTorch (CPU build is enough). No dataset download: the corpus
is the standard library of the Python you run the scripts with.

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu   # or follow pytorch.org
```

Run every command from this folder.

## Quick start

```bash
python train.py --smoke        # ~200 KB, 300 steps: checks everything works (a few minutes)
python train.py                # full char-level run: 4,000 steps, ~1.8M params (about 1 hour on a laptop CPU)
python complete.py --prompt "def is_even(n):"
python complete.py --samples 3 --prompt "class Stack:\n    def push(self, item):"
python complete.py --watch scratch.py   # save scratch.py to get a suggestion for its last line
python evaluate.py --n 100     # parse rate on functions from the validation files
python complete.py --bench     # ms/token for 1/4/default threads and int8 quantization
```

Stage 2 (BPE tokens):

```bash
python tokenizer.py --merges 512      # look at the merges it learns
python train.py --tokenizer bpe       # same model size and steps, BPE tokens
python evaluate.py --ckpt checkpoints/bpe.pt
```

Training can be stopped with Ctrl+C at any time; `python train.py --resume`
(add `--tokenizer bpe` for the BPE run) continues from the last checkpoint.
Debugging demo: `python train.py --smoke --no-causal-mask --max-iters 1500`
shows what happens when the model can see the future.

## Measured results

Measured on the course's test machine: Windows 11 laptop CPU (8 PyTorch threads),
CPython 3.13.3 standard library, PyTorch 2.15.0 CPU build. The CPU was shared
with other heavy jobs during the full runs, so an idle machine should be faster.

| What | Result |
|---|---|
| Corpus | 568 files: 511 train (8,664,390 chars), 57 val (989,019 chars); 97-character alphabet, 208 placeholder chars |
| BPE tokenizer | 512 merges in 17 s, vocabulary 609, 2.28 chars/token on val (2,048 merges: 58 s, 2.90 chars/token) |
| Smoke run | 300 steps in 44 s (1.4 min on a busy CPU); train loss 4.47 -> 2.16, val 2.19 (3.16 bits/char) |
| Full char run | 1,823,040 params, 4,000 steps x 4,096 tokens in 90 min; val loss 1.147 nats = **1.65 bits/char** |
| Full BPE run | 1,921,344 params, same steps and batch, 62 min; val **1.48 bits/char** |
| Parse rate (100 val functions, T=0.4, top-k 20) | smoke 0%, char after 500 steps 7%, char 38% (300 chars), char 46% (684 chars), BPE 69% (132 tokens ~ 300 chars), BPE 81% (300 tokens) |
| No-mask bug demo | `--smoke --no-causal-mask --max-iters 1500`: val loss 0.05 at step 500 (masked: 1.90), gibberish samples |
| Latency (`--bench`, 8 threads) | char 6.3 ms/token, BPE 6.1 ms/token (~2.7 ms/char); int8: 3.6x smaller weights but ~2x slower at this size |

Numbers vary with your Python version (different standard library), CPU and
random seed. Treat them as the order of magnitude to expect.

## What to expect from the model, honestly

The model learns the *form* of Python: indentation, closing brackets, `self.`
inside methods, docstrings, `raise ValueError(...)`. It does not understand what
code is for, forgets everything older than its context window (128 tokens), and
invents functions that do not exist. Production assistants share the
architecture but are thousands of times larger, are trained on far more code,
can use the code after the cursor (fill-in-the-middle) and are evaluated with
unit tests. The capstone lesson compares them in detail.

## Licence of the training data

CPython's standard library is distributed under the PSF License Agreement
(<https://docs.python.org/3/license.html>), which allows use and derivative
works. The corpus (`data/`) and trained weights (`checkpoints/`) are generated
locally and are **not** committed to this repository (see `.gitignore`).

## Credits

Model and training loop modelled on Andrej Karpathy's
[nanoGPT](https://github.com/karpathy/nanoGPT) and
[minGPT](https://github.com/karpathy/minGPT) (MIT); the BPE trainer follows
[minbpe](https://github.com/karpathy/minbpe) and Sennrich et al. (2016).
