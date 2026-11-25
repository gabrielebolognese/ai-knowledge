# Handwritten digits and letters

Companion code for the course track **Handwritten digits and letters**
(`src/content/lessons/project-digits-letters/`). You train an MLP and a small CNN
on MNIST digits and EMNIST letters on a laptop CPU, evaluate them with a
confusion matrix, and read your own handwriting with a tkinter drawing app.

| File | What it does | Lesson |
|---|---|---|
| `data.py` | Downloads MNIST / EMNIST letters with torchvision; normalisation, the EMNIST orientation fix and label shift, subsets for `--smoke`, the manual EMNIST fallback | Meet MNIST; From digits to letters |
| `models.py` | The 784→128→10 MLP (101,770 params) and the 2-block CNN (421,642 params); checkpoint save/load; `python models.py` prints parameter counts and shapes | MLP baseline; A CNN at 99% |
| `train.py` | Training CLI: `--dataset mnist\|letters`, `--model mlp\|cnn`, `--epochs`, `--kernel-size`, `--smoke` | MLP baseline; A CNN at 99%; EMNIST |
| `evaluate.py` | Test accuracy, per-class accuracy, confusion matrix (text + plot) and the most confident mistakes | Evaluating the digit model |
| `preprocess.py` | Turns a drawing into a 28×28 image framed like MNIST or EMNIST; `--check` measures what each step is worth | Capstone |
| `draw_app.py` | tkinter canvas → preprocessing → top-3 predictions, with a preview of what the model sees; `--selftest` runs without a window, `--check` tests tkinter and the preprocessing without a window or a checkpoint | Capstone |

## Requirements

Python 3.10+ with the packages in `code/requirements.txt` (PyTorch, torchvision,
NumPy, Pillow, matplotlib). The CPU build of PyTorch is enough. `draw_app.py` also
needs tkinter, which ships with the python.org installers; on Debian/Ubuntu install
`python3-tk`.

Run every command from this folder. Datasets are downloaded into `data/`,
checkpoints go to `checkpoints/` and plots to `outputs/`; all three are git-ignored.

## Quick start

```bash
python train.py --smoke                        # 1,000 images, 1 epoch: checks everything in seconds
python data.py                                 # look at MNIST: shapes, pixel range, outputs/samples-mnist.png
python train.py --model mlp                    # MLP baseline, about 1 minute
python train.py                                # CNN on MNIST, 3 epochs, about 3 minutes
python evaluate.py                             # confusion matrix and worst mistakes
python draw_app.py                             # draw digits
python train.py --dataset letters --epochs 5   # EMNIST letters (downloads ~560 MB first), about 9 minutes
python draw_app.py --ckpt checkpoints/letters-cnn.pt
python preprocess.py --check                   # accuracy with and without preprocessing
```

If the EMNIST download fails, download "Binary format as the original MNIST
dataset" (`gzip.zip`) from https://www.nist.gov/itl/products-and-services/emnist-dataset,
put it, still zipped, in `data/EMNIST/raw/`, and run the command again.

## Measured results

Measured on the course's test machine: Windows 11 laptop CPU, Python 3.13,
PyTorch 2.15.0 CPU build, torchvision 0.29.2, default seed 0. Other jobs were
sharing the CPU at times, so treat times as an order of magnitude.

| Run | Result |
|---|---|
| `train.py --smoke` (CNN / MLP / letters CNN) | 75.7% / 78.8% / 23.4% after 1 epoch on 1,000 images; about 9 s per command including start-up |
| `train.py --model mlp` (3 epochs) | 96.19%, 97.12%, **97.37%**; 70 s in total |
| `train.py` (CNN, 3 epochs) | 98.43%, 98.67%, **98.91%**; 2 min 46 s; 109 test mistakes (MLP: 263) |
| `train.py --epochs 5` | seed 0: 98.43, 98.67, 98.91, 99.06, **99.02%** (4 min 26 s); `--seed 1`: **99.09%** (4 min 52 s) |
| `train.py --kernel-size 5` | 454,922 params; 98.98% after 3 epochs; 3 min 25 s |
| `train.py --dataset letters --epochs 5` | 90.88%, 92.26%, 92.84%, 93.19%, **93.75%**; 9 min 11 s |
| `evaluate.py` (digits CNN) | weakest class 9 (97.2%); top confusions 9→4 (14), 9→7 (8), 7→2 (6) |
| `evaluate.py` (letters CNN) | weakest classes i 70.4%, g 79.9%, l 81.0%, q 87.7%; top confusions i→l (213), l→i (128), g→q (115) |
| `preprocess.py --check` (digits CNN, 1,000 redrawn test images) | stored 99.1%, full preprocessing **99.2%**, canvas shrunk 14.7%, shrunk + inverted 39.8% |
| `preprocess.py --check` (letters CNN) | stored 93.1%, full preprocessing **92.2%**, canvas shrunk 4.1%, shrunk + inverted 41.0% |
| `draw_app.py --selftest` (digits CNN) | a vertical bar → 1 (100%), a drawn 7 → 7 (100%) |

## How the drawing is matched to the training data

`preprocess.py` repeats the way each dataset was built, then applies the
training transform from `data.py` (same `STATS`, so the two cannot drift):

1. grayscale, inverted to white ink on black;
2. cropped to the ink (pixels above 30);
3. digits: scaled to fit 20×20, pasted into 28×28, shifted so the centre of mass is at (14, 14),
   which is the measured average of the MNIST training set;
   letters: centred in a square with a border of 3/24 of its size and scaled to 28×28 (bicubic),
   so the longest side matches the 23.7-pixel average of the EMNIST training letters;
4. `ToTensor()` + `Normalize(mean, std)` of the training set (no transpose: drawings are upright).

## Sources

- LeCun, Bottou, Bengio, Haffner (1998), *Gradient-based learning applied to document recognition*, https://doi.org/10.1109/5.726791
- Cohen, Afshar, Tapson, van Schaik (2017), *EMNIST: an extension of MNIST to handwritten letters*, https://arxiv.org/abs/1702.05373
- torchvision datasets: https://docs.pytorch.org/vision/stable/generated/torchvision.datasets.MNIST.html and https://docs.pytorch.org/vision/stable/generated/torchvision.datasets.EMNIST.html
- PyTorch MNIST example: https://github.com/pytorch/examples/tree/main/mnist

Neither MNIST's original page nor NIST's EMNIST page states a licence, so this
repository never redistributes the images; the scripts download them at run time.
