"""Tokenizers for the code model: characters first, then byte-pair encoding (BPE).

Both map text <-> lists of integer ids and share one interface:
    tok.encode(text) -> list[int]      tok.decode(ids) -> str
    tok.vocab_size                     tok.to_dict() / load_tokenizer(d)

The BPE trainer is written from scratch (after Sennrich et al. 2016 and
Karpathy's minbpe). It starts from the 97 characters of the corpus alphabet
and repeatedly merges the most frequent adjacent pair into a new token.

Run:  python tokenizer.py --merges 512      # train on the corpus and print examples
"""
import argparse
import re
import time
from collections import Counter, defaultdict

from corpus import ALPHABET, UNK


class CharTokenizer:
    """One token per character. The vocabulary is the fixed 97-character alphabet."""

    def __init__(self, alphabet=ALPHABET):
        self.alphabet = alphabet
        self.stoi = {ch: i for i, ch in enumerate(alphabet)}
        self.itos = list(alphabet)
        self.unk = self.stoi[UNK]

    @property
    def vocab_size(self):
        return len(self.itos)

    def encode(self, text):
        return [self.stoi.get(ch, self.unk) for ch in text]

    def decode(self, ids):
        return "".join(self.itos[i] for i in ids)

    def to_dict(self):
        return {"type": "char", "alphabet": self.alphabet}


# Pre-split text into chunks; merges never cross a chunk boundary. A chunk is a
# newline plus its indentation, an identifier (with one leading space), a number,
# a run of punctuation, or a run of spaces. Together they cover every character.
CHUNK_RE = re.compile(r"\n *| ?[A-Za-z_][A-Za-z0-9_]*| ?[0-9]+| ?[^\sA-Za-z0-9_]+| +")


def split_chunks(text):
    return CHUNK_RE.findall(text)


class BPETokenizer(CharTokenizer):
    """Characters plus learned merges. Token ids >= 97 are merged pairs."""

    def __init__(self, merges=(), alphabet=ALPHABET):
        super().__init__(alphabet)
        self.merges = {}                     # (id_a, id_b) -> new id, in learned order
        for a, b in merges:
            self._add_merge(a, b)
        self.cache = {}

    def _add_merge(self, a, b):
        new_id = len(self.itos)
        self.merges[(a, b)] = new_id
        self.itos.append(self.itos[a] + self.itos[b])
        return new_id

    @classmethod
    def train(cls, text, num_merges, verbose=False):
        """Learn num_merges merges from text (use the TRAINING split only)."""
        tok = cls()
        counts = Counter(split_chunks(text))                 # chunk -> frequency
        words = [[tok.stoi.get(ch, tok.unk) for ch in w] for w in counts]
        freqs = list(counts.values())
        pair_counts = Counter()
        where = defaultdict(set)                             # pair -> words containing it
        for wi, w in enumerate(words):
            for pair in zip(w, w[1:]):
                pair_counts[pair] += freqs[wi]
                where[pair].add(wi)

        for step in range(num_merges):
            if not pair_counts:
                break
            best = max(pair_counts, key=pair_counts.get)     # most frequent adjacent pair
            if pair_counts[best] < 2:
                break
            new_id = tok._add_merge(*best)
            for wi in list(where[best]):
                w, f = words[wi], freqs[wi]
                for pair in zip(w, w[1:]):                   # remove the word's old pairs
                    pair_counts[pair] -= f
                    if pair_counts[pair] <= 0:
                        del pair_counts[pair]
                merged = _merge(w, best, new_id)
                for pair in zip(merged, merged[1:]):         # add its new pairs
                    pair_counts[pair] += f
                    where[pair].add(wi)
                words[wi] = merged
            del where[best]
            if verbose and (step < 10 or (step + 1) % 100 == 0):
                print(f"merge {step + 1:4d}: {tok.itos[best[0]]!r} + {tok.itos[best[1]]!r} -> {tok.itos[new_id]!r}")
        return tok

    def _encode_chunk(self, chunk):
        ids = [self.stoi.get(ch, self.unk) for ch in chunk]
        while len(ids) >= 2:
            # apply the earliest-learned merge that occurs in the chunk
            pair = min(zip(ids, ids[1:]), key=lambda p: self.merges.get(p, float("inf")))
            if pair not in self.merges:
                break
            ids = _merge(ids, pair, self.merges[pair])
        return ids

    def encode(self, text):
        out = []
        for chunk in split_chunks(text):
            ids = self.cache.get(chunk)
            if ids is None:
                ids = self._encode_chunk(chunk)
                if len(self.cache) < 500_000:
                    self.cache[chunk] = ids
            out.extend(ids)
        return out

    def to_dict(self):
        return {"type": "bpe", "alphabet": self.alphabet, "merges": [list(p) for p in self.merges]}


def _merge(ids, pair, new_id):
    """Replace every occurrence of pair in ids with new_id."""
    out, i = [], 0
    while i < len(ids):
        if i < len(ids) - 1 and ids[i] == pair[0] and ids[i + 1] == pair[1]:
            out.append(new_id)
            i += 2
        else:
            out.append(ids[i])
            i += 1
    return out


def load_tokenizer(d):
    if d["type"] == "char":
        return CharTokenizer(d["alphabet"])
    return BPETokenizer([tuple(p) for p in d["merges"]], d["alphabet"])


def main():
    from corpus import build_corpus

    parser = argparse.ArgumentParser(description="Train a BPE tokenizer on the stdlib corpus")
    parser.add_argument("--merges", type=int, default=512)
    parser.add_argument("--max-chars", type=int, default=None)
    args = parser.parse_args()

    train_text, val_text, _ = build_corpus(args.max_chars)
    t0 = time.time()
    bpe = BPETokenizer.train(train_text, args.merges, verbose=True)
    print(f"trained {len(bpe.merges)} merges in {time.time() - t0:.1f}s; vocabulary {bpe.vocab_size}")
    char = CharTokenizer()
    sample = "    def __init__(self, name=None):\n        self.name = name\n"
    print("chars :", len(char.encode(sample)), "tokens")
    print("BPE   :", len(bpe.encode(sample)), "tokens ->", [bpe.itos[i] for i in bpe.encode(sample)])
    assert bpe.decode(bpe.encode(val_text)) == val_text, "round trip failed"
    n = len(bpe.encode(val_text))
    print(f"validation text: {len(val_text):,} chars -> {n:,} BPE tokens ({len(val_text) / n:.2f} chars per token)")


if __name__ == "__main__":
    main()
