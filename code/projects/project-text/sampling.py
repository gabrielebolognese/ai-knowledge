"""Turning a model's scores (logits) into the next character: temperature and top-k sampling.

    python sampling.py      # prints the worked example from the lesson (logits 2, 1, 0)

Every generator in this project (bigram, MLP, GRU/LSTM) calls sample_next(), so the
sampling rules are written once.
"""
import torch


def adjust_probs(logits, temperature=1.0, top_k=None):
    """Probabilities after temperature scaling and an optional top-k cut.

    logits: 1-D tensor of raw scores, one per symbol.
    temperature: < 1 sharpens the distribution (safer), > 1 flattens it (wilder).
    top_k: keep only the k highest-scoring symbols, then renormalise.
    """
    logits = logits.double() / temperature                 # 1. divide every score by T
    if top_k is not None and top_k < logits.numel():
        kth_best = torch.topk(logits, top_k).values[-1]     # 2. the k-th largest score
        logits = logits.masked_fill(logits < kth_best, float("-inf"))   # drop the rest
    return torch.softmax(logits, dim=-1)                    # 3. softmax: exp, then divide by the sum


def sample_next(logits, temperature=1.0, top_k=None, generator=None):
    """Draw one symbol id. temperature=0 means greedy: always take the highest score."""
    if temperature == 0:
        return int(torch.argmax(logits))
    probs = adjust_probs(logits, temperature, top_k)
    return int(torch.multinomial(probs, num_samples=1, generator=generator))


def main():
    logits = torch.tensor([2.0, 1.0, 0.0])
    print("logits for A, B, C:", logits.tolist())
    for t in (1.0, 0.5, 2.0):
        p = adjust_probs(logits, temperature=t)
        print(f"T = {t:<4} ->", ", ".join(f"{x:.3f}" for x in p.tolist()))
    p = adjust_probs(logits, temperature=1.0, top_k=2)
    print("T = 1, top-k = 2 ->", ", ".join(f"{x:.3f}" for x in p.tolist()))

    g = torch.Generator().manual_seed(0)
    draws = [sample_next(logits, 1.0, None, g) for _ in range(10_000)]
    share = [draws.count(i) / len(draws) for i in range(3)]
    print("10,000 draws at T = 1 ->", ", ".join(f"{x:.3f}" for x in share), "(close to 0.665, 0.245, 0.090)")


if __name__ == "__main__":
    main()
