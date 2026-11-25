"""Step 1: a bigram name generator built from counts alone (no neural network, no training loop).

    python bigram.py                  # count, evaluate, sample 10 names; under 5 seconds
    python bigram.py --smoothing 0    # what happens without smoothing (look at the dev loss)
    python bigram.py --smoke          # 2,000 names only: a setup check

Saves checkpoints/bigram.pt, which generate.py can sample from.
"""
import argparse
import math

import torch

from sampling import sample_next
from text_data import CHECKPOINTS, CharVocab, load_names, split_names


def count_bigrams(words, vocab):
    """N[a, b] = how often character b followed character a ('.' marks the start and the end)."""
    V = len(vocab)
    N = torch.zeros((V, V), dtype=torch.int64)
    for w in words:
        chars = ["."] + list(w) + ["."]                # emma -> . e m m a .
        for a, b in zip(chars, chars[1:]):             # (.,e) (e,m) (m,m) (m,a) (a,.)
            N[vocab.stoi[a], vocab.stoi[b]] += 1
    return N


def counts_to_probs(N, smoothing=1.0):
    """Each row becomes a probability distribution over the next character."""
    P = (N + smoothing).double()                       # add-k smoothing: no probability is exactly 0
    return P / P.sum(dim=1, keepdim=True)              # divide by the row total


def average_nll(words, P, vocab):
    """Average negative log-likelihood per predicted character (natural log, in nats)."""
    probs = P.tolist()                                 # plain lists are faster to index in a loop
    total, n = 0.0, 0
    for w in words:
        chars = ["."] + list(w) + ["."]
        for a, b in zip(chars, chars[1:]):
            p = probs[vocab.stoi[a]][vocab.stoi[b]]
            total += -math.log(p) if p > 0 else math.inf   # an unseen pair costs infinitely much
            n += 1
    return total / n


def sample_name(P, vocab, generator, temperature=1.0, top_k=None, max_len=30):
    out, ix = [], 0                                    # start at '.'
    while len(out) < max_len:
        ix = sample_next(torch.log(P[ix]), temperature, top_k, generator)
        if ix == 0:                                    # '.' again: the name is finished
            break
        out.append(vocab.itos[ix])
    return "".join(out)


def main():
    p = argparse.ArgumentParser(description="Bigram name generator from counts")
    p.add_argument("--smoothing", type=float, default=1.0, help="pseudo-count added to every cell")
    p.add_argument("--num", type=int, default=10, help="names to sample")
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--top-k", type=int, default=None)
    p.add_argument("--seed", type=int, default=2147483647)
    p.add_argument("--smoke", action="store_true", help="use only 2,000 names")
    a = p.parse_args()

    words = load_names()
    vocab = CharVocab.for_names(words)
    train, dev, test = split_names(words)
    if a.smoke:
        train, dev = train[:2000], dev[:500]

    N = count_bigrams(train, vocab)
    P = counts_to_probs(N, a.smoothing)
    print(f"counted {int(N.sum()):,} bigrams from {len(train):,} training names ({len(vocab)} symbols)")
    top = torch.topk(N.flatten(), 5)
    pairs = [f"{vocab.itos[i // len(vocab)]}{vocab.itos[i % len(vocab)]} {c:,}"
             for c, i in zip(top.values.tolist(), top.indices.tolist())]
    print("most common pairs:", ", ".join(pairs))
    print(f"P(first letter = 'a') = {P[0, vocab.stoi['a']]:.4f}   P(end | 'n') = {P[vocab.stoi['n'], 0]:.4f}")

    uniform = math.log(len(vocab))
    train_nll, dev_nll = average_nll(train, P, vocab), average_nll(dev, P, vocab)
    print(f"uniform guess : loss {uniform:.4f}  perplexity {math.exp(uniform):.2f}")
    print(f"train         : loss {train_nll:.4f}  perplexity {math.exp(train_nll):.2f}")
    print(f"dev           : loss {dev_nll:.4f}  perplexity {math.exp(dev_nll):.2f}")

    g = torch.Generator().manual_seed(a.seed)
    print("samples:", ", ".join(sample_name(P, vocab, g, a.temperature, a.top_k) for _ in range(a.num)))

    CHECKPOINTS.mkdir(exist_ok=True)
    path = CHECKPOINTS / ("bigram-smoke.pt" if a.smoke else "bigram.pt")
    torch.save({"kind": "bigram", "itos": vocab.itos, "log_probs": torch.log(P).float(),
                "dev_loss": dev_nll}, path)
    print(f"saved {path.name}")
    if a.smoke:
        assert dev_nll < uniform, "the bigram model should beat the uniform guess"
        print("smoke test passed: dev loss is below the uniform", f"{uniform:.2f}")


if __name__ == "__main__":
    main()
