# Doodle recognition (Quick, Draw!)

Companion code for the course track **Doodle recognition**
(`src/content/lessons/project-doodles/`). You download a small slice of Google's
Quick, Draw! dataset, train a small CNN on 10 classes of doodles on a laptop CPU,
improve it with augmentation and batch normalization, read its confusion matrix,
and play with a tkinter app that guesses while you draw.

## Dataset and attribution

> **Quick, Draw! dataset by Google, licensed under
> [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).**
> Source: https://github.com/googlecreativelab/quickdraw-dataset

The dataset holds about 50 million drawings in 345 categories, collected from
players of the [Quick, Draw!](https://quickdraw.withgoogle.com/) game. CC BY 4.0
allows sharing and adapting, including commercially, as long as you give credit,
link to the licence and indicate changes. This project credits the dataset in the
code, in `data/quickdraw/ATTRIBUTION.txt` (written by `download.py`), in the
course figures that show doodles, and in the drawing app's window. If you share a
model or app built from it, keep the credit line.

The dataset's README warns that the drawings were individually moderated but
"may still contain inappropriate content".

The data was introduced to research by D. Ha and D. Eck, *A Neural Representation
of Sketch Drawings* (2017), https://arxiv.org/abs/1704.03477 (sketch-rnn).

## Download size

`download.py` never downloads whole class files (80-270 MB each). It uses HTTP
Range requests to fetch the `.npy` header plus only the first N drawings:

| Command | Download |
|---|---|
| `python download.py --smoke` | 2 classes × 500 = **0.8 MB** |
| `python download.py` (default) | 10 classes × 12,000 = **94 MB** |
| `python download.py --per-class 5000` | 10 × 5,000 = 39 MB |
| `python download.py --classes pear` | one more class, 9.4 MB |

Data goes to `data/`, checkpoints to `checkpoints/`, plots and logs to
`outputs/`; all three are git-ignored.

## Files

| File | What it does | Lesson |
|---|---|---|
| `download.py` | Range-request download of the first N bitmaps per class; `--smoke`, `--classes`, `--per-class`; writes ATTRIBUTION.txt | The Quick, Draw! dataset |
| `data.py` | Loads the `.npy` files with `mmap_mode`, balanced 9k/1k/2k train/validation/test split per class, optional augmentation wrapper; `python data.py` prints statistics | The Quick, Draw! dataset |
| `models.py` | `DoodleCNN`: the digits project's CNN (421,642 params) with optional batch normalization; checkpoint save/load | Training a doodle classifier |
| `train.py` | Training CLI with per-epoch train/validation accuracy: `--epochs`, `--augment`, `--batch-norm`, `--dropout`, `--classes`, `--per-class`, `--smoke`, `--tag` | Training; Augmentation |
| `augment.py` | Label-preserving random affine transform (±10°, ±2 px, 90-110% scale); `python augment.py` saves examples | Augmentation |
| `evaluate.py` | Test accuracy, per-class accuracy, confusion matrix, top confusions, confidence when right/wrong, plots of the worst mistakes; `--samples` | Reading the confusion matrix |
| `preprocess.py` | Strokes → 28×28 exactly like the official bitmaps; `--check` compares with the real bitmaps | Capstone app |
| `draw_app.py` | tkinter canvas → strokes → preprocessing → live top-3 guesses, with the dataset credit; `--selftest` runs without a window, `--check` tests tkinter and the preprocessing without a window or a checkpoint | Capstone app |

## Requirements

Python 3.10+ with the packages in `code/requirements.txt` (PyTorch, torchvision,
NumPy, Pillow, matplotlib). The CPU build of PyTorch is enough. `draw_app.py`
needs tkinter, which ships with the python.org installers; on Debian/Ubuntu
install `python3-tk`. Run every command from this folder.

## Quick start

```bash
python download.py --smoke && python train.py --smoke   # setup check: about 10 s in total
python download.py                                      # 94 MB, under a minute on a fast connection
python data.py                                          # split sizes and pixel statistics
python train.py                                         # baseline CNN, 5 epochs, about 4 minutes
python train.py --augment --batch-norm --epochs 15 --tag aug-bn-e15   # regularized model, ~27 min
python evaluate.py                                      # confusion matrix and worst mistakes
python preprocess.py --check                            # does the app's preprocessing match the dataset?
python draw_app.py                                      # draw!
```

## Measured results

Measured on the course's test machine: Windows 11 laptop CPU, Python 3.13,
PyTorch 2.15.0 CPU build, torchvision 0.29.2, seed 0. Times are rough (other jobs
shared the CPU at times). Validation = 10,000 doodles, test = 20,000 (2,000 per class).

| Run | Result |
|---|---|
| `download.py` (default) | 10 × 12,000 doodles, 9.4 MB per class, 18 s in total |
| `train.py --smoke` | 2 classes, 2 epochs: 95.8% test accuracy on 166 doodles; about 10 s per command including start-up |
| `train.py` (baseline, 5 epochs) | validation 92.72, 94.01, 95.17, 95.28, **95.75%**; test **95.67%**; 4 min 16 s |
| `--dropout 0` | train 96.90%, validation 95.89%, test 95.67% (slight overfitting, gap +1.0) |
| `--batch-norm` | validation 95.91%, test 95.72%; 5.1 min |
| `--augment` | validation 95.66%, test 95.44%; 7.9 min (augmentation doubles the epoch time) |
| `--augment --batch-norm` | validation 95.48%, test 95.27%; 8.7 min (still underfitting after 5 epochs) |
| `--epochs 15 --tag e15` (baseline, 15 epochs) | best validation 96.48% (plateau from epoch 8), train 97.46%, test **96.36%**; 187 wrong answers with >90% confidence; 12 min |
| `--augment --batch-norm --epochs 15 --tag aug-bn-e15` | validation **96.78%** (still rising), train 93.36%, test **96.39%**; 107 confident mistakes; 27 min. Preferred by `draw_app.py` |
| `--per-class 1200 --epochs 15` (900 train/class), no regularisation | train 98.97%, validation 92.80%, test 91.55% (clear overfitting) |
| same + dropout | train 94.99%, validation 93.80%, test 91.75% |
| same + dropout + augmentation | train 89.52%, validation **94.80%**, test 92.90% |
| same + dropout + augmentation + batch norm | validation 93.90%, test **93.05%** |
| `evaluate.py` (baseline) | weakest class cloud 93.2%, best house 97.9%; top confusions star→cat 59, cloud→fish 50, fish→cat 40; 261 non-cats called cat; confidence 97.7% when right, 57.2% when wrong |
| 11 classes (`--classes ... pear`) | test 94.96%; pear 90.8%; pear→apple 114, apple→pear 48 |
| `preprocess.py --check` (2,000 drawings) | mean pixel difference from the official bitmaps 0.0079; model accuracy 97.2% on official bitmaps, 97.4% on our renderings, 50.4% with a naively shrunk canvas |
| `draw_app.py --selftest` (baseline) | circle + hands → clock, star → star, square + roof → house, trunk + crown → tree (all 100%) |


## Sources

- The Quick, Draw! Dataset (README, licence, bitmap description): https://github.com/googlecreativelab/quickdraw-dataset
- Bitmap generation snippet linked from the README: https://github.com/googlecreativelab/quickdraw-dataset/issues/19#issuecomment-402247262
- Ha & Eck (2017), *A Neural Representation of Sketch Drawings*: https://arxiv.org/abs/1704.03477
- CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
- Ioffe & Szegedy (2015), *Batch Normalization*: https://arxiv.org/abs/1502.03167
- torchvision `RandomAffine`: https://docs.pytorch.org/vision/stable/generated/torchvision.transforms.v2.RandomAffine.html
