"""Data for the generators: names (bundled) and TinyShakespeare (downloaded), plus a char vocabulary.

    python text_data.py               # statistics for names.txt (and TinyShakespeare once downloaded)
    python text_data.py --download    # fetch TinyShakespeare (1.1 MB) into data/

Licences: see bundled/LICENSES.md. names.txt is MIT (makemore) over public-domain SSA data;
TinyShakespeare is public-domain text from the MIT-licensed char-rnn repository.
"""
import argparse
import random
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLED = HERE / "bundled"
DATA = HERE / "data"                  # git-ignored: downloads land here
CHECKPOINTS = HERE / "checkpoints"    # git-ignored: trained models land here

NAMES_FILE = BUNDLED / "names.txt"
NAMES_URL = "https://raw.githubusercontent.com/karpathy/makemore/master/names.txt"
SHAKESPEARE_URL = ("https://raw.githubusercontent.com/karpathy/char-rnn/master/"
                   "data/tinyshakespeare/input.txt")
SHAKESPEARE_FILE = DATA / "tinyshakespeare.txt"


def download(url, dest):
    """Download url to dest once; later calls reuse the file."""
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading {url}")
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url, timeout=60) as r, open(tmp, "wb") as f:
        f.write(r.read())
    tmp.replace(dest)
    print(f"saved {dest} ({dest.stat().st_size:,} bytes)")
    return dest


def load_names():
    """The 32,033 names, lowercase a-z, one per line."""
    if not NAMES_FILE.exists():                       # only if someone deleted the bundled copy
        download(NAMES_URL, NAMES_FILE)
    return NAMES_FILE.read_text(encoding="utf-8").split()


def split_names(words, seed=42):
    """Shuffle once with a fixed seed, then 80% train / 10% dev / 10% test (as in makemore)."""
    words = list(words)
    random.Random(seed).shuffle(words)
    n1, n2 = int(0.8 * len(words)), int(0.9 * len(words))
    return words[:n1], words[n1:n2], words[n2:]


class CharVocab:
    """Maps characters to integer ids and back. For names, id 0 is '.', the start/end token."""

    def __init__(self, chars):
        self.itos = list(chars)
        self.stoi = {c: i for i, c in enumerate(self.itos)}

    @classmethod
    def for_names(cls, words):
        return cls(["."] + sorted(set("".join(words))))     # '.' + 26 letters = 27 symbols

    @classmethod
    def for_text(cls, text):
        return cls(sorted(set(text)))                        # TinyShakespeare: 65 symbols

    def __len__(self):
        return len(self.itos)

    def encode(self, s):
        return [self.stoi[c] for c in s]

    def decode(self, ids):
        return "".join(self.itos[i] for i in ids)


def names_stream(words):
    """All names in one string, separated by '.', e.g. '.emma.olivia.' (used by the RNN)."""
    return "." + ".".join(words) + "."


def load_shakespeare():
    """The whole TinyShakespeare file as one string (1,115,394 characters)."""
    download(SHAKESPEARE_URL, SHAKESPEARE_FILE)
    return SHAKESPEARE_FILE.read_text(encoding="utf-8")


def split_text(text, frac=0.9):
    """First 90% for training, last 10% for validation (as nanoGPT's shakespeare_char does)."""
    n = int(frac * len(text))
    return text[:n], text[n:]


def main():
    p = argparse.ArgumentParser(description="Statistics for the text-generation data")
    p.add_argument("--download", action="store_true", help="download TinyShakespeare into data/")
    a = p.parse_args()

    words = load_names()
    tr, dev, te = split_names(words)
    vocab = CharVocab.for_names(words)
    lengths = [len(w) for w in words]
    print(f"names.txt: {len(words):,} names, {len(vocab)} symbols ('.' + {len(vocab) - 1} letters)")
    print(f"  lengths: shortest {min(lengths)}, longest {max(lengths)}, mean {sum(lengths) / len(words):.2f}")
    print(f"  split: train {len(tr):,} / dev {len(dev):,} / test {len(te):,}")
    print(f"  first five: {words[:5]}")

    if a.download or SHAKESPEARE_FILE.exists():
        text = load_shakespeare()
        tv = CharVocab.for_text(text)
        t_tr, t_val = split_text(text)
        print(f"TinyShakespeare: {len(text):,} characters, {len(tv)} symbols")
        print(f"  split: train {len(t_tr):,} / val {len(t_val):,}")
        print("  symbols:", repr("".join(tv.itos)))
    else:
        print("TinyShakespeare: not downloaded yet (python text_data.py --download)")


if __name__ == "__main__":
    main()
