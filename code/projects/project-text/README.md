# Small-text models: generate and classify short texts

Companion code for the course track **Small-text models**
(`src/content/lessons/project-text/`). You build three text generators that each
improve on the last, a counting bigram model, a Bengio-style MLP and a GRU/LSTM,
and two sentiment classifiers, a bag of embeddings and a bidirectional LSTM.
Everything trains on a laptop CPU.

| Lesson | Files |
|---|---|
| A bigram name generator from counts | `text_data.py`, `sampling.py`, `bigram.py` |
| A neural name generator (Bengio-style MLP) | `mlp_lm.py`, `generate.py` |
| A character-level Shakespeare generator with an LSTM | `char_rnn.py`, `generate.py` |
| Short texts: preparing SST-2 movie-review sentences | `sst2_data.py` |
| A bag-of-embeddings sentiment classifier | `classifier.py`, `train_classifier.py` |
| Capstone: a BiLSTM classifier for your own sentences | `classifier.py`, `train_classifier.py`, `classify.py` |

## Files

| File | What it does |
|---|---|
| `text_data.py` | Loads the bundled names (80/10/10 split, seed 42, as in makemore) and downloads TinyShakespeare (90/10 split); character vocabulary. `python text_data.py [--download]` prints statistics. |
| `sampling.py` | Temperature and top-k sampling, shared by every generator. `python sampling.py` prints the worked example from the lesson. |
| `bigram.py` | Step 1: counts character pairs, add-k smoothing, average negative log-likelihood, samples names. `--smoothing`, `--smoke`. |
| `mlp_lm.py` | Step 2: context-3 MLP with 10-dim embeddings and 200 tanh units (11,897 parameters), minibatch SGD. `--block`, `--emb`, `--hidden`, `--steps`, `--smoke`. |
| `char_rnn.py` | Step 3: GRU or LSTM over a character stream with truncated backpropagation through time, gradient clipping and early stopping. `--data names|shakespeare`, `--cell gru|lstm`, `--smoke`. |
| `generate.py` | Samples from any generator checkpoint: `--temperature`, `--top-k`, `--prefix` (names) or `--prompt` (text). |
| `sst2_data.py` | Downloads SST-2, tokenizes like SST-2 ("is n't"), builds the vocabulary from training data only, pads batches; loads the bundled sets. |
| `classifier.py` | `BagOfEmbeddings` (masked mean of word vectors → linear) and `BiLSTMClassifier` (packed BiLSTM → both final states → linear). |
| `train_classifier.py` | Trains either model, keeps the best epoch by validation accuracy, reports test accuracy, precision, recall, F1, the challenge set and the out-of-domain UCI sentences. `--model bag|bilstm`, `--smoke`. |
| `classify.py` | Classifies sentences you type, with the probability and any unknown words. |

## Data and licences

| Data | Where | Licence |
|---|---|---|
| `names.txt`, 32,033 names | **bundled** (`bundled/names.txt`) | MIT (makemore repository, copy of the licence in `bundled/makemore-LICENSE.txt`); the underlying US Social Security Administration name data is a US government work in the public domain |
| Sentiment Labelled Sentences, 3,000 sentences (Kotzias et al. 2015) | **bundled** (`bundled/sentiment-labelled-sentences/`) | CC BY 4.0, from the UCI Machine Learning Repository ([dataset 331](https://archive.ics.uci.edu/dataset/331/sentiment+labelled+sentences)); redistributed unchanged with attribution |
| `challenge.tsv`, 48 negation/contrast sentences | **bundled** | Own work, CC0 1.0 |
| TinyShakespeare, 1,115,394 characters | downloaded to `data/` | Public-domain text, from the MIT-licensed [char-rnn](https://github.com/karpathy/char-rnn) repository |
| SST-2 (GLUE), 67,349 + 872 items | downloaded to `data/` (7.4 MB zip) | **No licence stated**; cite Socher et al. 2013. Never redistributed |

Full attribution text: [`bundled/LICENSES.md`](bundled/LICENSES.md). `data/`, `checkpoints/`
and `outputs/` are git-ignored.

## Requirements

Python 3.10+ with PyTorch (the CPU build is enough); see `code/requirements.txt`.
No other packages are needed. Run every command from this folder.

## Smoke tests (each well under 2 minutes on a CPU)

```bash
python bigram.py --smoke              # 2,000 names, seconds
python mlp_lm.py --smoke              # 2,000 SGD steps, about 10 s
python char_rnn.py --smoke            # GRU on names, 60 steps, a few seconds
python train_classifier.py --smoke    # bag of embeddings on the bundled UCI sentences, offline, seconds
python train_classifier.py --smoke --model bilstm   # BiLSTM on the same, under a minute
```

The generator smoke tests need no download. Each one asserts that the loss fell
(and, for the classifier, that test accuracy is above 60%) and prints
`smoke test passed`.

## Full runs

```bash
python bigram.py                                   # dev loss 2.45
python mlp_lm.py                                   # dev loss about 2.14, about 2 minutes
python char_rnn.py --data names                    # GRU on names, dev loss about 2.02
python char_rnn.py --data shakespeare              # 2-layer LSTM, downloads 1.1 MB, about 10 min
python generate.py --model checkpoints/rnn-shakespeare.pt --prompt "ROMEO:" --temperature 0.8
python sst2_data.py                                # downloads SST-2 (7.4 MB), prints statistics
python train_classifier.py --model bag
python train_classifier.py --model bilstm
python classify.py "not bad at all" "a dull, lifeless film"
```

## Measured results

Measured on the course's test machine: Windows 11 laptop CPU, Python 3.13, PyTorch 2.15.0
CPU build, default seeds. Times are wall-clock with other jobs running on the same machine;
expect yours to differ by a factor of two either way.

**Generators** (loss = average negative log-likelihood in nats per character; lower is better)

| Model | Command | Parameters | Dev / val loss | Perplexity | Time |
|---|---|---|---|---|---|
| Uniform guess over 27 symbols | | 0 | 3.2958 | 27.0 | |
| Bigram counts, add-1 smoothing | `bigram.py` | 729 probabilities | 2.4533 | 11.6 | seconds |
| Bengio-style MLP, context 3 | `mlp_lm.py` | 11,897 | 2.1418 (test 2.1397) | 8.5 | 1 min 45 s |
| GRU, 1 layer, 128 units | `char_rnn.py --data names` | 66,555 | 2.0222 (best, step 1,500 of 3,000) | 7.6 | 1.5 min |
| LSTM, 2 layers, 256 units, TinyShakespeare | `char_rnn.py --data shakespeare` | 876,929 | 1.4979 at step 2,000 (2.16 bits/char) | 4.47 | about 10 min |

The names GRU overfits after about 1,500 steps (dev loss 2.022 at step 1,500, 2.071 at
step 3,000, while the training loss keeps falling); `char_rnn.py` keeps and saves the
best-validation weights. The Shakespeare LSTM behaves the same way: in a 3,000-step run the
validation loss was 1.694 / 1.579 / 1.518 / **1.498** / 1.503 / 1.507 at steps
500 / 1,000 / 1,500 / 2,000 / 2,500 / 3,000 (13 minutes), so the default is 2,000 steps.
For comparison, nanoGPT's README reports about 1.88 for its small CPU transformer on the
same file and split.

Shakespeare sample (T = 0.8, prompt `ROMEO:`):

```text
ROMEO:Npressive
The parents rolours when thou dost part of mine.
Give me to be my good most severer presence
Of your reasons and Bushy friends of England,
And whom for that friends to the seasons appeal.

QUEEN ELIZABETH:
No noble lord,
Being thee, nor slain? how doth my life,
```

Samples (temperature 1.0 unless noted):

- bigram: `dexze, momakurailezitynn, konimittain, llayn, ka, da, staiyaubrtthrigotai, moliellavo`
- MLP: `anueden, kis, marian, dan, shan, silaylen, kemarco, man, emiah, aden`
- MLP, `--prefix ma --temperature 0.8 --top-k 10`: `maritha, marienne, maya, mader, mariel`
- GRU (T = 0.8): `juno, jaelia, ryeen, jackoe, aleah, reyley, jaceng, zenin, videa, taquan`

**Sentiment classifiers** (SST-2; "test" = the 872 GLUE validation sentences)

| Model | Parameters | Best epoch (carved val) | Test accuracy | Precision / recall (positive) | Challenge set (48) | UCI other domains (3,000) | Time |
|---|---|---|---|---|---|---|---|
| Bag of embeddings | 941,698 | 3 of 5 (91.2%) | **78.67%** | 74.2% / 89.2% | 60.4% | 79.1% | 96 s |
| BiLSTM, 128 per direction | 1,140,738 | 3 of 3 (90.4%) | **83.14%** | 80.5% / 88.3% | 64.6% | 81.2% | 682 s |

The carved validation accuracy is optimistic: SST-2's training set contains every
labelled phrase of each sentence, and 89% of the carved validation items occur word for
word inside a training item. Report the GLUE sentences.

**Smoke tests**: `bigram.py --smoke` a few seconds; `mlp_lm.py --smoke` 2,000 steps, loss
3.30 → 2.36, about 10 s; `char_rnn.py --smoke` 60 steps, loss 3.30 → 2.30, 3 s;
`train_classifier.py --smoke` 82.0% on 300 held-out UCI sentences in about 1 s of training
(BiLSTM: 73.3%, about 25 s).

## Sources

- Y. Bengio, R. Ducharme, P. Vincent, C. Jauvin, *A Neural Probabilistic Language Model*, JMLR 3 (2003). https://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf
- A. Karpathy, makemore: https://github.com/karpathy/makemore, and *Neural Networks: Zero to Hero*: https://karpathy.ai/zero-to-hero.html
- A. Karpathy, *The Unreasonable Effectiveness of Recurrent Neural Networks* (2015): https://karpathy.github.io/2015/05/21/rnn-effectiveness/ and char-rnn: https://github.com/karpathy/char-rnn
- S. Hochreiter, J. Schmidhuber, *Long Short-Term Memory*, Neural Computation (1997). https://doi.org/10.1162/neco.1997.9.8.1735
- K. Cho et al., *Learning Phrase Representations using RNN Encoder-Decoder* (2014), the GRU. https://arxiv.org/abs/1406.1078
- R. Socher et al., *Recursive Deep Models for Semantic Compositionality Over a Sentiment Treebank*, EMNLP 2013. https://aclanthology.org/D13-1170/
- A. Wang et al., *GLUE* (2018). https://arxiv.org/abs/1804.07461
- D. Kotzias, M. Denil, N. de Freitas, P. Smyth, *From Group to Individual Labels Using Deep Features*, KDD 2015; data: https://doi.org/10.24432/C57604
