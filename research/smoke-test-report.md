# Companion code smoke-test report

Date: 2026-11-25. Runner: `code/run_smoke_tests.py`. Result: **40 passed, 0 failed, 0 skipped in 338 s** in the main checkout. A second run in a clean copy of the committed code (no `data/`, no `checkpoints/`) gave **35 passed, 0 failed, 1 skipped in 242 s**.

## How to run it

```bash
# from the repository folder, once:
python -m venv .venv
.venv\Scripts\python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu   # Windows
.venv\Scripts\python -m pip install -r code/requirements.txt
# then:
.venv\Scripts\python code/run_smoke_tests.py            # macOS/Linux: .venv/bin/python
.venv\Scripts\python code/run_smoke_tests.py chess text # only some projects
.venv\Scripts\python code/run_smoke_tests.py --list     # show the commands without running them
.venv\Scripts\python code/run_smoke_tests.py -v         # print every step's output
.venv\Scripts\python code/run_smoke_tests.py --big-downloads   # also run the EMNIST steps on a fresh clone
```

Each step is a command a learner would type. It runs as its own subprocess from the project folder, with a timeout (60 to 1,200 s depending on the step), `MPLBACKEND=Agg` and UTF-8 output. A step passes when the exit code is 0 and, where one is set, the output matches the expected pattern. Examples: `smoke test passed`, `perft(3) = 8902`, `int8-Linear accuracy`. The script prints a PASS / FAIL / SKIP table and exits with 1 if any step failed.

## Environment

| | |
|---|---|
| OS | Windows 11 Home 10.0.26200, 8 CPU threads, no GPU |
| Python | 3.13.3, venv at `.venv/` (git-ignored) |
| Packages | torch 2.15.0+cpu and torchvision 0.29.2+cpu (from `https://download.pytorch.org/whl/cpu`), numpy 2.5.4, matplotlib 3.11.2, pillow 13.0.0, tqdm 4.70.1, chess 1.11.2, zstandard 0.25.0, jupyterlab 4.6.6, ipykernel 7.4.0 |
| `pip check` | No broken requirements found. |

**Requirements reconciliation.** I collected every `import` and `from` statement in `code/projects/*`, `code/core/*`, `code/setup` and `code/samples`. The only third-party modules are torch, torchvision, numpy, matplotlib, PIL (pillow), tqdm, chess and zstandard. All of them are already in `code/requirements.txt`, so the file did not change. tkinter is in the standard library. Python's own installer includes it on Windows and macOS; on Linux it is the `python3-tk` package. `code/core/intermediate/metrics.py` imports scikit-learn inside `try/except ImportError` as an optional cross-check, so it is not a requirement. The per-project `pip install` lines in the chess and autocomplete READMEs are subsets of the same list.

## Results (main checkout)

| Project | Step | Result | Time |
|---|---|---|---|
| setup | `python setup/verify_setup.py` ("All checks passed.") | PASS | 8.5 s |
| samples | `neuron.py`, `gradient_descent.py` | PASS | 0.5 s |
| digits-letters | `train.py --smoke` (CNN, MNIST): 75.7% after 1 epoch on 1,000 images | PASS | 9.6 s |
| digits-letters | `train.py --smoke --model mlp`: 78.8% | PASS | 10.1 s |
| digits-letters | `train.py --smoke --dataset letters` (EMNIST letters CNN) | PASS | 12.3 s |
| digits-letters | `evaluate.py --ckpt checkpoints/mnist-cnn-smoke.pt --smoke --no-plots` (confusion matrix) | PASS | 8.7 s |
| digits-letters | `preprocess.py --check --n 200` with the smoke CNN | PASS | 10.8 s |
| digits-letters | `draw_app.py --check` (tkinter + preprocessing, no window) | PASS | 7.5 s |
| digits-letters | `draw_app.py --selftest` with the smoke CNN (drawn 7 -> 7) | PASS | 7.5 s |
| core-advanced | `tictactoe_search.py` (all four searches agree: draw) | PASS | 1.6 s |
| core-advanced | `quantize_cnn.py --checkpoint <digits smoke CNN>` (float32 vs int8 accuracy) | PASS | 12.9 s |
| core-advanced | `transfer_digits_to_letters.py` (200 letters, 1 epoch, scratch/frozen/finetune) | PASS | 10.0 s |
| doodles | `download.py --smoke` (2 classes x 500, 0.8 MB, HTTP Range) | PASS | 0.5 s |
| doodles | `train.py --smoke`: 95.8% on 166 test doodles | PASS | 9.6 s |
| doodles | `evaluate.py --ckpt checkpoints/doodles-smoke.pt --smoke --no-plots` | PASS | 4.3 s |
| doodles | `draw_app.py --check` (tkinter + stroke preprocessing, no window) | PASS | 4.1 s |
| doodles | `draw_app.py --selftest` with the smoke CNN | PASS | 4.2 s |
| text | `bigram.py --smoke` (dev loss 2.47 < uniform 3.30) | PASS | 4.6 s |
| text | `mlp_lm.py --smoke` (loss 3.30 -> 2.36) | PASS | 14.4 s |
| text | `char_rnn.py --smoke` (GRU, loss 3.30 -> 2.30) | PASS | 24.0 s |
| text | `train_classifier.py --smoke` (bag of embeddings, 82.0% test) | PASS | 19.5 s |
| text | `train_classifier.py --smoke --model bilstm` | PASS | 47.2 s |
| text | `generate.py` with the MLP and GRU smoke checkpoints | PASS | 9.3 s |
| text | `classify.py --model checkpoints/bag-smoke.pt "..." "..."` | PASS | 4.2 s |
| code-autocomplete | `model.py` self-test (explicit mask == fused attention, 1,823,040 params) | PASS | 4.7 s |
| code-autocomplete | `train.py --smoke` (300 steps, train loss 4.47 -> 2.16) | PASS | 39.3 s |
| code-autocomplete | `complete.py --ckpt checkpoints/char-smoke.pt --prompt ...` | PASS | 5.8 s |
| code-autocomplete | `complete.py ... --quantize` (int8 dynamic) | PASS | 6.9 s |
| code-autocomplete | `evaluate.py --ckpt checkpoints/char-smoke.pt --n 5` (parse rate, 0% for the smoke net as the README says) | PASS | 11.0 s |
| chess | `data.py --smoke` (bundled CC0 Lichess sample: 4,000 read, 2,255 quiet kept) | PASS | 1.3 s |
| chess | `train.py --smoke` (205,121 params, beats the "always equal" baseline, mirror check) | PASS | 10.9 s |
| chess | perft(3) from the start position = **8,902** (`bench.perft`) | PASS | 0.4 s |
| chess | raw UCI handshake: `uci` -> `uciok`, `isready` -> `readyok`, `position startpos` + `go depth 3` -> legal `bestmove` (twice, NN evaluator loaded) | PASS | 1.0 s |
| chess | GUI launcher: `minifish.bat` (Windows) / `minifish.sh` answers `uciok` and `readyok` | PASS | 0.6 s |
| chess | `eval_nn.py --weights checkpoints/smoke.npz` (single and batched paths agree) | PASS | 0.5 s |
| chess | `search.py --depth 3` (finds Ra8# and the mate in 2, takes the free queen) | PASS | 1.2 s |
| chess | `search.py --depth 2 --nn checkpoints/smoke.npz` | PASS | 1.6 s |
| chess | `bench.py --smoke` (perft suite up to depth 3, speed, accumulator vs full refresh: 0 cp difference, python-chess UCI check) | PASS | 6.9 s |

Clean copy: the same steps passed, and MNIST (11 MB) and the doodle smoke set downloaded on first use. The EMNIST letters step was skipped with its reason printed: EMNIST is a 562 MB download, so a fresh clone runs it only with `--big-downloads` or after `python data.py --dataset letters`. The transfer step was added to the runner after the clean-copy run and is skipped the same way when EMNIST is missing. Everything else needs no network, because the chess sample and the text datasets are bundled.

## Are the smoke datasets honest miniatures?

Every `--smoke` flag only shrinks the amount of data and the number of steps. Each smoke run goes through the same data loader, preprocessing, model class, loss, optimizer, checkpoint format and inference code as the full run:

- **digits-letters**: 1,000 real MNIST (or EMNIST) training images and 1 epoch, using the same `data.py` transforms, including the EMNIST orientation fix. Evaluation uses 1,000 real test images.
- **doodles**: the real Quick, Draw! bitmaps, 2 classes x 500. `download.py` uses the same HTTP Range code and `train.py` uses the same split and augmentation hooks as the full 10 x 12,000 download.
- **text**: the generators train on the bundled `names.txt` (the real course dataset) with fewer steps. The classifiers train on the bundled UCI sentiment sentences (CC BY 4.0). These are real labelled data, used offline instead of downloading SST-2.
- **code-autocomplete**: about 175 KB of the local Python standard library, read by the same `corpus.py` file-level split. The model is smaller (813,952 parameters) and trains for 300 steps, with the same training loop and checkpoint format.
- **chess**: 4,000 real records from the Lichess evaluation database (CC0), filtered for quiet positions by the same `data.py` code, with the same 768->256->32->1 network and the same NumPy export that `uci.py` loads.

Each smoke script also checks that it learned something. The loss must fall, or accuracy or loss must beat chance or a baseline. A broken pipeline therefore fails the step even when it exits cleanly.

## Bugs found and fixed

1. **Chess GUI launchers ignored the course's virtual environment.** `minifish.bat` and `minifish.sh` ran a bare `python`/`python3` from PATH. A chess GUI started from the desktop does not activate the venv, so a learner who installed the packages only in `.venv`, as the setup track teaches, got an engine that crashed on `import chess`. Both launchers now use `<repo>/.venv` (three folders up) when it exists and fall back to PATH. `minifish.sh` is committed as executable. I tested the .bat with only `C:\Windows\System32` on PATH: it answered `uciok`, `readyok` and `bestmove e2e4`. The chess README and lesson `chess-uci-elo` now explain this.
2. **The tkinter apps could not be checked without a window and a trained model.** Both `draw_app.py` files gained `--check`. It imports tkinter and `PIL.ImageTk`, sends a code-drawn digit or the four demo doodles through the real preprocessing, checks the 28x28 output (size, ink fraction, value range) and feeds it to an untrained model of the right architecture. The lessons `handwriting-app` and `doodle-app` and both READMEs list the new flag.
3. **An off-by-one CodeFile range.** `mnist-dataset.mdx` showed `data.py` lines 78-86, which ended on a blank line. It now shows 78-85, with the same highlights (81, 84).

No smoke script, threshold or check was weakened. Apart from these fixes, every project ran as committed.

## Lesson code stays in sync

- **CodeFile excerpts.** Before editing, I took a snapshot of the code shown by all 124 `<CodeFile>` references, including highlighted lines. After all edits I compared again: **0 of 124 changed**. The new `check()` functions sit after every line the lessons quote. A separate scan found no range past the end of a file and no highlight outside its range or on a blank line. Two ranges ended on a blank line: one is fixed above, and the other (`beginner/gradient-descent.mdx`) belongs to the beginner writer.
- **Commands quoted in lessons.** I checked all 138 `python <script>.py --flags` commands in the lessons against each script's argparse flags. None is stale: the three hits for `char_rnn.py --cell/--steps/--hidden` are flags generated in a loop, and `script.py` in the terminal lesson is a generic example.
- **Numbers.** The smoke numbers in the READMEs match this run exactly: 75.7% and 78.8% for digits, 95.8% on 166 doodles, 82.0% for the bag classifier, losses 3.30 -> 2.36 and 3.30 -> 2.30 for the text generators, 4.47 -> 2.16 for the code model, and 2,255 quiet chess positions. With the trained 2M-position net, `eval_nn.py` scores a queen up/down as +708 / -667 cp. The smoke net cannot tell (+5 / +11 cp), which `train.py --smoke` itself warns about.
- `node scripts/validate-content.mjs --track` passes for project-digits-letters, project-doodles and project-chess (0 failures; the warnings are the existing missing-prerequisite ones).

## Not covered by the smoke suite

- Full-length training runs (minutes to hours each) were not repeated. Their numbers come from the project steps that measured them.
- `project-doodles/preprocess.py --check` needs the full 94 MB download plus network. `bench.py --match` needs a Stockfish binary.
- The interactive programs (`play.py`, the tkinter windows, `complete.py --watch`, `classify.py` without arguments) cannot be driven by the runner. I checked `play.py` by hand with piped input (`e2e4`, then the engine replied `d5`).
- `code/core/beginner` and `code/core/intermediate` were not committed yet and belong to the writers still working on those tracks. Add their scripts to `steps()` in `run_smoke_tests.py` once they land.
