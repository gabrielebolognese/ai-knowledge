"""Step 2: a neural name generator in the style of Bengio et al. (2003), as rebuilt in makemore.

    python mlp_lm.py              # 50,000 steps: about 2 minutes on a laptop CPU
    python mlp_lm.py --smoke      # 2,000 steps: a setup check
    python mlp_lm.py --hidden 300 --emb 16 --block 4    # experiments

Three previous characters -> embeddings (10 numbers each) -> tanh hidden layer (200) -> 27 scores.
Saves checkpoints/mlp.pt, which generate.py can sample from.
"""
import argparse
import math
import time

import torch
from torch import nn
from torch.nn import functional as F

from sampling import sample_next
from text_data import CHECKPOINTS, CharVocab, load_names, split_names


def build_dataset(words, vocab, block_size):
    """Every (context, next character) pair. 'emma' with block 3 gives ... -> e, ..e -> m, .em -> m, emm -> a, mma -> ."""
    X, Y = [], []
    for w in words:
        context = [0] * block_size                     # start with '...'
        for ch in w + ".":
            ix = vocab.stoi[ch]
            X.append(context)
            Y.append(ix)
            context = context[1:] + [ix]               # slide the window one character
    return torch.tensor(X), torch.tensor(Y)


class MLPLanguageModel(nn.Module):
    def __init__(self, vocab_size=27, block_size=3, emb_dim=10, hidden=200):
        super().__init__()
        self.block_size = block_size
        self.emb = nn.Embedding(vocab_size, emb_dim)               # table C: one learned vector per symbol
        self.hidden = nn.Linear(block_size * emb_dim, hidden)      # W1, b1
        self.out = nn.Linear(hidden, vocab_size)                   # W2, b2
        with torch.no_grad():                                      # start close to "all 27 equally likely"
            self.out.weight.mul_(0.1)
            self.out.bias.zero_()

    def forward(self, idx):                        # idx: (batch, block_size) character ids
        x = self.emb(idx)                          # (batch, block_size, emb_dim)
        x = x.flatten(1)                           # concatenate: (batch, block_size * emb_dim)
        h = torch.tanh(self.hidden(x))             # (batch, hidden)
        return self.out(h)                         # logits: (batch, vocab_size)


@torch.no_grad()
def evaluate(model, X, Y):
    model.eval()
    return F.cross_entropy(model(X), Y).item()


@torch.no_grad()
def sample_name(model, vocab, generator, temperature=1.0, top_k=None, prefix="", max_len=30):
    model.eval()
    context = [0] * model.block_size
    for ch in prefix:                              # optional start, e.g. prefix="ma"
        context = context[1:] + [vocab.stoi[ch]]
    out = list(prefix)
    while len(out) < max_len:
        logits = model(torch.tensor([context]))[0]
        ix = sample_next(logits, temperature, top_k, generator)
        if ix == 0:
            break
        out.append(vocab.itos[ix])
        context = context[1:] + [ix]
    return "".join(out)


def main():
    p = argparse.ArgumentParser(description="Bengio-style MLP name generator")
    p.add_argument("--block", type=int, default=3, help="context length in characters")
    p.add_argument("--emb", type=int, default=10, help="embedding size per character")
    p.add_argument("--hidden", type=int, default=200)
    p.add_argument("--steps", type=int, default=50_000)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--lr", type=float, default=0.1, help="SGD learning rate (divided by 10 at 70% of the steps)")
    p.add_argument("--num", type=int, default=10, help="names to sample at the end")
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--top-k", type=int, default=None)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--smoke", action="store_true", help="2,000 steps only")
    a = p.parse_args()
    if a.smoke:
        a.steps = 2_000
    torch.manual_seed(a.seed)

    words = load_names()
    vocab = CharVocab.for_names(words)
    train_w, dev_w, test_w = split_names(words)
    Xtr, Ytr = build_dataset(train_w, vocab, a.block)
    Xdev, Ydev = build_dataset(dev_w, vocab, a.block)
    Xte, Yte = build_dataset(test_w, vocab, a.block)
    print(f"examples: train {len(Ytr):,} / dev {len(Ydev):,} / test {len(Yte):,}")

    model = MLPLanguageModel(len(vocab), a.block, a.emb, a.hidden)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"parameters: {n_params:,}")
    optimizer = torch.optim.SGD(model.parameters(), lr=a.lr)
    first = evaluate(model, Xtr, Ytr)
    print(f"step      0  train loss {first:.4f}  (uniform guess: ln {len(vocab)} = {math.log(len(vocab)):.4f})")

    start = time.time()
    for step in range(1, a.steps + 1):
        if step == int(0.7 * a.steps):
            for group in optimizer.param_groups:
                group["lr"] = a.lr / 10                       # smaller steps for the last 30%
        ix = torch.randint(0, len(Ytr), (a.batch_size,))      # a random minibatch of 32 examples
        model.train()
        loss = F.cross_entropy(model(Xtr[ix]), Ytr[ix])       # forward pass and loss
        optimizer.zero_grad()
        loss.backward()                                       # gradients
        optimizer.step()                                      # update
        if step % (a.steps // 5) == 0:
            print(f"step {step:6d}  train loss {evaluate(model, Xtr, Ytr):.4f}  "
                  f"dev loss {evaluate(model, Xdev, Ydev):.4f}  ({time.time() - start:.0f} s)")

    train_loss, dev_loss, test_loss = (evaluate(model, X, Y) for X, Y in ((Xtr, Ytr), (Xdev, Ydev), (Xte, Yte)))
    print(f"final: train {train_loss:.4f} / dev {dev_loss:.4f} / test {test_loss:.4f}  "
          f"(dev perplexity {math.exp(dev_loss):.2f})")

    g = torch.Generator().manual_seed(a.seed)
    print("samples:", ", ".join(sample_name(model, vocab, g, a.temperature, a.top_k) for _ in range(a.num)))

    CHECKPOINTS.mkdir(exist_ok=True)
    path = CHECKPOINTS / ("mlp-smoke.pt" if a.smoke else "mlp.pt")
    torch.save({"kind": "mlp", "itos": vocab.itos, "dev_loss": dev_loss, "state": model.state_dict(),
                "config": {"vocab_size": len(vocab), "block_size": a.block, "emb_dim": a.emb, "hidden": a.hidden}},
               path)
    print(f"saved {path.name}")
    if a.smoke:
        assert dev_loss < first, "the dev loss should fall during training"
        print("smoke test passed: loss fell from", f"{first:.2f} to {dev_loss:.2f}")


if __name__ == "__main__":
    main()
