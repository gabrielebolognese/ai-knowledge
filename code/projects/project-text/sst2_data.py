"""Short texts for sentiment classification: SST-2 (downloaded) and two small bundled sets.

    python sst2_data.py          # downloads SST-2 (7.4 MB) once, prints sizes, vocabulary and examples

Datasets
- SST-2, the binary Stanford Sentiment Treebank from the GLUE benchmark (Socher et al. 2013).
  No licence is stated, so it is downloaded for study and never redistributed.
- bundled/sentiment-labelled-sentences/ (Kotzias et al. 2015, UCI, CC BY 4.0): 3,000 review
  sentences from Amazon, Yelp and IMDb. Used for the offline --smoke run and as an
  out-of-domain test.
- bundled/challenge.tsv (own work, CC0): 48 sentences that test negation and contrast.
"""
import random
import re
import zipfile
from collections import Counter

import torch

from text_data import BUNDLED, DATA, download

SST2_URL = "https://dl.fbaipublicfiles.com/glue/data/SST-2.zip"
SST2_ZIP = DATA / "SST-2.zip"
UCI_DIR = BUNDLED / "sentiment-labelled-sentences"
PAD, UNK = "<pad>", "<unk>"                     # ids 0 and 1


def tokenize(text):
    """Lowercase words and punctuation, split the way SST-2 is ("isn't" -> "is n't")."""
    text = text.lower().replace("’", "'")
    text = re.sub(r"n't\b", " n't", text)
    text = re.sub(r"'(s|re|ve|ll|d|m)\b", r" '\1", text)
    return re.findall(r"n't|'[a-z]+|[a-z0-9]+(?:[-'][a-z0-9]+)*|[^\sa-z0-9]", text)


def read_tsv(lines, header=True):
    """(sentence, label) pairs from 'sentence<TAB>label' lines; the label is the last field."""
    pairs = []
    for line in lines[1:] if header else lines:
        if "\t" in line:
            sentence, label = line.rsplit("\t", 1)
            pairs.append((sentence.strip(), int(label)))
    return pairs


def load_sst2():
    """GLUE SST-2: 67,349 labelled training phrases and 872 validation sentences."""
    download(SST2_URL, SST2_ZIP)
    with zipfile.ZipFile(SST2_ZIP) as z:
        read = lambda name: z.read(name).decode("utf-8").split("\n")
        return read_tsv(read("SST-2/train.tsv")), read_tsv(read("SST-2/dev.tsv"))


def load_uci(sources=("amazon_cells", "yelp", "imdb")):
    """The bundled Kotzias et al. sentences. split('\\n'), not splitlines(): imdb has U+0085 inside lines."""
    pairs = []
    for s in sources:
        lines = (UCI_DIR / f"{s}_labelled.txt").read_text(encoding="utf-8").split("\n")
        pairs += read_tsv(lines, header=False)
    return pairs


def load_challenge():
    return read_tsv((BUNDLED / "challenge.tsv").read_text(encoding="utf-8").split("\n"))


def split_off(pairs, frac, seed=0):
    """Shuffle and cut off `frac` of the pairs, e.g. a validation set carved from training data."""
    pairs = list(pairs)
    random.Random(seed).shuffle(pairs)
    n = int(len(pairs) * frac)
    return pairs[n:], pairs[:n]


class Vocab:
    """Word -> id. Built from the TRAINING split only, so test words the model never saw become <unk>."""

    def __init__(self, itos):
        self.itos = list(itos)
        self.stoi = {w: i for i, w in enumerate(self.itos)}

    @classmethod
    def build(cls, sentences, min_freq=1):
        counts = Counter(tok for s in sentences for tok in tokenize(s))
        words = sorted((w for w, c in counts.items() if c >= min_freq), key=lambda w: (-counts[w], w))
        return cls([PAD, UNK] + words)

    def __len__(self):
        return len(self.itos)

    def encode(self, sentence):
        return [self.stoi.get(tok, 1) for tok in tokenize(sentence)] or [1]   # empty input -> one <unk>


def make_batches(pairs, vocab, batch_size, shuffle=False, seed=0):
    """Yield (ids, lengths, labels). Shorter sentences are padded with id 0 up to the longest in the batch."""
    order = list(range(len(pairs)))
    if shuffle:
        random.Random(seed).shuffle(order)
    for i in range(0, len(order), batch_size):
        chunk = [pairs[j] for j in order[i : i + batch_size]]
        encoded = [vocab.encode(s) for s, _ in chunk]
        lengths = torch.tensor([len(e) for e in encoded])
        ids = torch.zeros(len(chunk), int(lengths.max()), dtype=torch.long)   # 0 = <pad>
        for row, e in enumerate(encoded):
            ids[row, : len(e)] = torch.tensor(e)
        yield ids, lengths, torch.tensor([y for _, y in chunk])


def main():
    train, test = load_sst2()
    train, val = split_off(train, 0.05)
    vocab = Vocab.build(s for s, _ in train)
    lens = sorted(len(tokenize(s)) for s, _ in train)
    print(f"SST-2: train {len(train):,} / val (carved from train) {len(val):,} / test (GLUE dev) {len(test):,}")
    print(f"  positive share: train {sum(y for _, y in train) / len(train):.1%}, "
          f"test {sum(y for _, y in test) / len(test):.1%}")
    print(f"  tokens per training item: median {lens[len(lens) // 2]}, max {lens[-1]}")
    unk = sum(vocab.encode(s).count(1) for s, _ in test)
    total = sum(len(vocab.encode(s)) for s, _ in test)
    print(f"  vocabulary (train only): {len(vocab):,} entries; {unk / total:.1%} of test tokens are <unk>")
    for s, y in train[:3]:
        print(f"  {y}  {s!r}")
    ids, lengths, labels = next(make_batches(test[:4], vocab, 4))
    print("  a padded batch of 4:", tuple(ids.shape), "lengths", lengths.tolist(), "labels", labels.tolist())
    uci, challenge = load_uci(), load_challenge()
    print(f"bundled: {len(uci):,} UCI review sentences, {len(challenge)} challenge sentences")
    print("tokenize(\"I didn't like it, it's dull!\") ->", tokenize("I didn't like it, it's dull!"))


if __name__ == "__main__":
    main()
