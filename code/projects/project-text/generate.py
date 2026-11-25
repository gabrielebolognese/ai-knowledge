"""Sample text from any trained generator: bigram, MLP or GRU/LSTM, with temperature and top-k.

    python generate.py --model checkpoints/mlp.pt                       # 10 names
    python generate.py --model checkpoints/mlp.pt --prefix ma --num 5   # names that start with "ma"
    python generate.py --model checkpoints/bigram.pt --temperature 0.5 --top-k 5
    python generate.py --model checkpoints/rnn-shakespeare.pt --prompt "ROMEO:" --length 500
    python generate.py --model checkpoints/rnn-shakespeare.pt --temperature 0   # greedy: watch it loop

Train the models first with bigram.py, mlp_lm.py and char_rnn.py.
"""
import argparse
from pathlib import Path

import torch

from char_rnn import CharRNN, generate
from mlp_lm import MLPLanguageModel, sample_name as mlp_sample_name
from sampling import sample_next
from text_data import CHECKPOINTS, CharVocab


def bigram_name(log_probs, vocab, generator, temperature, top_k, prefix="", max_len=30):
    out = list(prefix)
    ix = vocab.stoi[prefix[-1]] if prefix else 0
    while len(out) < max_len:
        ix = sample_next(log_probs[ix], temperature, top_k, generator)   # only the last character matters
        if ix == 0:
            break
        out.append(vocab.itos[ix])
    return "".join(out)


def main():
    p = argparse.ArgumentParser(description="Generate names or text from a trained character model")
    p.add_argument("--model", type=Path, default=CHECKPOINTS / "mlp.pt", help="a .pt file from checkpoints/")
    p.add_argument("--num", type=int, default=10, help="how many names (name models)")
    p.add_argument("--prefix", default="", help="name models: every name starts with these letters")
    p.add_argument("--prompt", default="\n", help="text models: the text to continue")
    p.add_argument("--length", type=int, default=400, help="text models: characters to generate")
    p.add_argument("--temperature", type=float, default=1.0, help="0 = greedy, <1 safer, >1 wilder")
    p.add_argument("--top-k", type=int, default=None, help="sample only among the k most likely characters")
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args()
    if not a.model.exists():
        raise SystemExit(f"{a.model} not found: train it first (bigram.py, mlp_lm.py or char_rnn.py)")

    ckpt = torch.load(a.model, map_location="cpu")
    vocab = CharVocab(ckpt["itos"])
    g = torch.Generator().manual_seed(a.seed)
    bad = [c for c in a.prefix if c not in vocab.stoi or c == "."]
    if bad:
        raise SystemExit(f"--prefix may only use the letters a-z (got {bad})")
    print(f"{a.model.name}: kind {ckpt['kind']}, temperature {a.temperature}, top-k {a.top_k}")

    if ckpt["kind"] == "bigram":
        names = [bigram_name(ckpt["log_probs"], vocab, g, a.temperature, a.top_k, a.prefix) for _ in range(a.num)]
    elif ckpt["kind"] == "mlp":
        model = MLPLanguageModel(**ckpt["config"])
        model.load_state_dict(ckpt["state"])
        names = [mlp_sample_name(model, vocab, g, a.temperature, a.top_k, a.prefix) for _ in range(a.num)]
    elif ckpt["kind"] == "rnn":
        model = CharRNN(**ckpt["config"])
        model.load_state_dict(ckpt["state"])
        if ckpt["data"] == "names":
            names = [a.prefix + generate(model, vocab, "." + a.prefix, 30, a.temperature, a.top_k, g, stop_id=0)
                     for _ in range(a.num)]
        else:
            unknown = sorted({c for c in a.prompt if c not in vocab.stoi})
            if unknown:
                raise SystemExit(f"the prompt uses characters the model never saw: {unknown}")
            print(a.prompt + generate(model, vocab, a.prompt, a.length, a.temperature, a.top_k, g))
            return
    else:
        raise SystemExit(f"{a.model.name} is not a generator checkpoint (kind {ckpt['kind']!r})")
    print("\n".join(names))


if __name__ == "__main__":
    main()
