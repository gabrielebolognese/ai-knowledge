"""Step 3: a character-level recurrent network (GRU or LSTM), in the spirit of Karpathy's char-rnn.

    python char_rnn.py --data names                 # GRU on names: compare with bigram.py and mlp_lm.py
    python char_rnn.py --data shakespeare           # 2-layer LSTM on TinyShakespeare (downloads 1.1 MB)
    python char_rnn.py --smoke                      # 60 steps on names: a setup check (seconds)
    python char_rnn.py --data shakespeare --cell gru --steps 500   # experiments

The text is one long stream of characters. It is cut into `batch` parallel rows and read in
chunks of `seq_len` characters; the hidden state is carried from one chunk to the next but
gradients stop at the chunk border (truncated backpropagation through time).
Saves checkpoints/rnn-<data>.pt, which generate.py can sample from.
"""
import argparse
import copy
import math
import time

import torch
from torch import nn
from torch.nn import functional as F

from sampling import sample_next
from text_data import (CHECKPOINTS, CharVocab, load_names, load_shakespeare, names_stream,
                       split_names, split_text)

PRESETS = {   # sizes chosen to train in a few minutes on a laptop CPU
    "names":       dict(cell="gru",  emb=32, hidden=128, layers=1, dropout=0.0, seq_len=32,  batch=32, steps=3000, lr=3e-3),
    "shakespeare": dict(cell="lstm", emb=64, hidden=256, layers=2, dropout=0.1, seq_len=100, batch=32, steps=2000, lr=2e-3),
}


class CharRNN(nn.Module):
    def __init__(self, vocab_size, emb=32, hidden=128, layers=1, cell="gru", dropout=0.0):
        super().__init__()
        self.cell = cell
        self.emb = nn.Embedding(vocab_size, emb)
        rnn = nn.GRU if cell == "gru" else nn.LSTM
        self.rnn = rnn(emb, hidden, num_layers=layers, batch_first=True,   # input shape (batch, time, features)
                       dropout=dropout if layers > 1 else 0.0)
        self.head = nn.Linear(hidden, vocab_size)

    def forward(self, idx, state=None):            # idx: (batch, time)
        x = self.emb(idx)                          # (batch, time, emb)
        out, state = self.rnn(x, state)            # out: (batch, time, hidden); state = the memory
        return self.head(out), state               # logits for the next character at every position


def detach(state):
    """Keep the memory's values but cut the gradient history (the TBPTT border)."""
    if state is None:
        return None
    return tuple(s.detach() for s in state) if isinstance(state, tuple) else state.detach()


def batchify(ids, batch):
    """Cut one long id sequence into `batch` equal rows that are read side by side."""
    n = len(ids) // batch
    return torch.tensor(ids[: n * batch]).view(batch, n)


@torch.no_grad()
def evaluate(model, data, seq_len):
    """Average loss per character over a whole batchified stream, carrying the state."""
    model.eval()
    state, total, count = None, 0.0, 0
    for i in range(0, data.size(1) - 1, seq_len):
        x = data[:, i : i + seq_len]
        y = data[:, i + 1 : i + 1 + seq_len]
        x = x[:, : y.size(1)]
        logits, state = model(x, state)
        total += F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1), reduction="sum").item()
        count += y.numel()
    return total / count


@torch.no_grad()
def generate(model, vocab, prompt, length, temperature=1.0, top_k=None, generator=None, stop_id=None):
    """Feed the prompt, then sample one character at a time, feeding each back in."""
    model.eval()
    ids = vocab.encode(prompt)
    logits, state = model(torch.tensor([ids]))
    out = []
    for _ in range(length):
        ix = sample_next(logits[0, -1], temperature, top_k, generator)
        if ix == stop_id:
            break
        out.append(ix)
        logits, state = model(torch.tensor([[ix]]), state)
    return vocab.decode(out)


def load_data(name):
    if name == "names":
        words = load_names()
        train_w, dev_w, _ = split_names(words)                    # the same split as bigram.py and mlp_lm.py
        return CharVocab.for_names(words), names_stream(train_w), names_stream(dev_w)
    text = load_shakespeare()
    train_t, val_t = split_text(text)
    return CharVocab.for_text(text), train_t, val_t


def main():
    p = argparse.ArgumentParser(description="Character-level GRU/LSTM language model")
    p.add_argument("--data", choices=sorted(PRESETS), default="names")
    for key in ("cell", "emb", "hidden", "layers", "dropout", "seq_len", "batch", "steps", "lr"):
        p.add_argument("--" + key.replace("_", "-"), type=type(PRESETS["names"][key]) if key != "cell" else str,
                       default=None, help="default: the preset for --data")
    p.add_argument("--clip", type=float, default=1.0, help="gradient-norm clipping threshold")
    p.add_argument("--temperature", type=float, default=0.8, help="for the samples printed at the end")
    p.add_argument("--top-k", type=int, default=None)
    p.add_argument("--seed", type=int, default=1337)
    p.add_argument("--smoke", action="store_true", help="names, 60 steps")
    a = p.parse_args()
    if a.smoke:
        a.data, a.steps = "names", 60
    for key, value in PRESETS[a.data].items():
        if getattr(a, key) is None:
            setattr(a, key, value)
    torch.manual_seed(a.seed)

    vocab, train_text, val_text = load_data(a.data)
    train = batchify(vocab.encode(train_text), a.batch)
    val = batchify(vocab.encode(val_text), 16)
    model = CharRNN(len(vocab), a.emb, a.hidden, a.layers, a.cell, a.dropout)
    CHECKPOINTS.mkdir(exist_ok=True)
    path = CHECKPOINTS / f"rnn-{a.data}{'-smoke' if a.smoke else ''}.pt"
    config = dict(vocab_size=len(vocab), emb=a.emb, hidden=a.hidden, layers=a.layers, cell=a.cell, dropout=a.dropout)

    def save(state_dict, val_loss, step):          # called at every new best, so a stopped run keeps its best model
        torch.save({"kind": "rnn", "data": a.data, "itos": vocab.itos, "config": config,
                    "state": state_dict, "val_loss": val_loss, "step": step}, path)

    print(f"data {a.data}: {len(train_text):,} train / {len(val_text):,} val characters, {len(vocab)} symbols")
    print(f"model: {a.layers}-layer {a.cell.upper()}, hidden {a.hidden}, "
          f"{sum(p.numel() for p in model.parameters()):,} parameters")
    optimizer = torch.optim.Adam(model.parameters(), lr=a.lr)

    first = evaluate(model, val[:, :2000], a.seq_len)
    print(f"step     0  val loss {first:.4f}  (uniform guess: ln {len(vocab)} = {math.log(len(vocab)):.4f})")
    start, state, pos, running = time.time(), None, 0, []
    best = (first, 0, copy.deepcopy(model.state_dict()))         # (val loss, step, weights)
    for step in range(1, a.steps + 1):
        if pos + a.seq_len + 1 > train.size(1):                 # reached the end: start again from the top
            pos, state = 0, None
        x = train[:, pos : pos + a.seq_len]
        y = train[:, pos + 1 : pos + 1 + a.seq_len]
        pos += a.seq_len
        model.train()
        state = detach(state)                                   # memory kept, gradient history cut
        logits, state = model(x, state)
        loss = F.cross_entropy(logits.reshape(-1, len(vocab)), y.reshape(-1))
        optimizer.zero_grad()
        loss.backward()                                         # backpropagation through seq_len steps
        nn.utils.clip_grad_norm_(model.parameters(), a.clip)    # tame exploding gradients
        optimizer.step()
        running.append(loss.item())
        if step % max(1, a.steps // 6) == 0 or step == a.steps:
            val_loss = evaluate(model, val, a.seq_len)
            print(f"step {step:5d}  train loss {sum(running) / len(running):.4f}  "
                  f"val loss {val_loss:.4f}  ({time.time() - start:.0f} s)")
            running = []
            if val_loss < best[0]:                              # early stopping: remember the best weights
                best = (val_loss, step, copy.deepcopy(model.state_dict()))
                save(best[2], val_loss, step)

    val_loss, best_step, weights = best
    model.load_state_dict(weights)
    print(f"best val loss {val_loss:.4f} nats/char at step {best_step} (perplexity {math.exp(val_loss):.2f}, "
          f"{val_loss / math.log(2):.3f} bits/char), {time.time() - start:.0f} s of training")

    g = torch.Generator().manual_seed(a.seed)
    if a.data == "names":
        names = [generate(model, vocab, ".", 30, a.temperature, a.top_k, g, stop_id=0) for _ in range(10)]
        print(f"samples (T={a.temperature}):", ", ".join(names))
    else:
        print(f"--- sample (T={a.temperature}) ---")
        print("ROMEO:" + generate(model, vocab, "ROMEO:", 400, a.temperature, a.top_k, g))

    save(weights, val_loss, best_step)
    print(f"saved {path.name} (weights from step {best_step})")
    if a.smoke:
        assert val_loss < first, "the validation loss should fall during training"
        print("smoke test passed: loss fell from", f"{first:.2f} to {val_loss:.2f}")


if __name__ == "__main__":
    main()
