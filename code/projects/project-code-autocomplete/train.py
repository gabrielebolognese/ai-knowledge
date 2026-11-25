"""Train the tiny GPT on the Python standard library, on a CPU.

    python train.py --smoke                 # ~200 KB, 300 steps, a few minutes at most: checks your setup
    python train.py                         # full run: char-level, ~1.8M params, 4,000 steps (about 1 hour)
    python train.py --tokenizer bpe         # stage 2: BPE tokens (train the char model first)
    python train.py --resume                # continue from the last checkpoint
    python train.py --smoke --no-causal-mask   # the classic bug: watch the loss collapse

Press Ctrl+C at any time: the current state is saved and --resume picks it up.
"""
import argparse
import math
import time
from pathlib import Path

import torch

from corpus import build_corpus
from model import GPT, GPTConfig
from tokenizer import BPETokenizer, CharTokenizer, load_tokenizer

HERE = Path(__file__).parent


def get_args():
    p = argparse.ArgumentParser(description="Train a tiny GPT on Python code")
    p.add_argument("--smoke", action="store_true", help="tiny, fast run to check that everything works")
    p.add_argument("--tokenizer", choices=["char", "bpe"], default="char")
    p.add_argument("--merges", type=int, default=512, help="BPE merges (vocabulary = 97 + merges)")
    p.add_argument("--max-chars", type=int, default=None, help="corpus size cap in characters")
    p.add_argument("--max-iters", type=int, default=4000)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--block-size", type=int, default=128)
    p.add_argument("--n-layer", type=int, default=4)
    p.add_argument("--n-head", type=int, default=4)
    p.add_argument("--n-embd", type=int, default=192)
    p.add_argument("--dropout", type=float, default=0.0)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--min-lr", type=float, default=1e-4)
    p.add_argument("--warmup", type=int, default=100)
    p.add_argument("--weight-decay", type=float, default=0.1)
    p.add_argument("--eval-interval", type=int, default=500)
    p.add_argument("--eval-iters", type=int, default=40)
    p.add_argument("--ckpt", default=None, help="checkpoint path (default checkpoints/<tokenizer>[-smoke].pt)")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--no-causal-mask", action="store_true", help="debug demo: let the model see the future")
    p.add_argument("--threads", type=int, default=None, help="torch.set_num_threads (default: PyTorch's choice)")
    p.add_argument("--seed", type=int, default=1337)
    a = p.parse_args()
    if a.smoke:  # ~200 KB of code, a smaller model, a few hundred steps (flags you pass still win)
        smoke = dict(max_chars=200_000, max_iters=300, batch_size=16, block_size=64,
                     n_embd=128, eval_interval=100, eval_iters=10, warmup=20)
        for key, value in smoke.items():
            if getattr(a, key) == p.get_default(key):
                setattr(a, key, value)
    a.ckpt = Path(a.ckpt or HERE / "checkpoints" / f"{a.tokenizer}{'-smoke' if a.smoke else ''}.pt")
    return a


def lr_at(step, a):
    """Linear warm-up, then cosine decay from lr to min_lr."""
    if step < a.warmup:
        return a.lr * (step + 1) / a.warmup
    progress = min(1.0, (step - a.warmup) / max(1, a.max_iters - a.warmup))
    return a.min_lr + 0.5 * (a.lr - a.min_lr) * (1 + math.cos(math.pi * progress))


def get_batch(data, block_size, batch_size):
    """Random windows of block_size tokens; targets are the same windows shifted by one."""
    ix = torch.randint(len(data) - block_size - 1, (batch_size,))
    x = torch.stack([data[i:i + block_size] for i in ix])
    y = torch.stack([data[i + 1:i + block_size + 1] for i in ix])
    return x, y


@torch.no_grad()
def estimate_loss(model, splits, a):
    model.eval()
    out = {}
    for name, data in splits.items():
        losses = [model(*get_batch(data, a.block_size, a.batch_size))[1].item() for _ in range(a.eval_iters)]
        out[name] = sum(losses) / len(losses)
    model.train()
    return out


def main():
    a = get_args()
    torch.manual_seed(a.seed)
    if a.threads:
        torch.set_num_threads(a.threads)

    # 1. data and tokenizer ------------------------------------------------------
    train_text, val_text, stats = build_corpus(a.max_chars)
    print(f"corpus: {stats['train_files']} train files ({stats['train_chars']:,} chars), "
          f"{stats['val_files']} val files ({stats['val_chars']:,} chars)")
    ckpt = torch.load(a.ckpt, weights_only=False) if a.resume and a.ckpt.exists() else None
    if ckpt:
        tok = load_tokenizer(ckpt["tokenizer"])
    elif a.tokenizer == "bpe":
        t0 = time.time()
        tok = BPETokenizer.train(train_text, a.merges)          # training split only: no leakage
        print(f"BPE: {len(tok.merges)} merges in {time.time() - t0:.0f}s")
    else:
        tok = CharTokenizer()
    train_ids = torch.tensor(tok.encode(train_text), dtype=torch.long)
    val_ids = torch.tensor(tok.encode(val_text), dtype=torch.long)
    chars_per_token = len(val_text) / len(val_ids)
    print(f"tokenizer: {a.tokenizer}, vocabulary {tok.vocab_size}, {chars_per_token:.2f} chars per token")

    # 2. model and optimizer -----------------------------------------------------
    cfg = GPTConfig(vocab_size=tok.vocab_size, block_size=a.block_size, n_layer=a.n_layer,
                    n_head=a.n_head, n_embd=a.n_embd, dropout=a.dropout, causal=not a.no_causal_mask)
    if ckpt:
        cfg = GPTConfig(**ckpt["config"])
    model = GPT(cfg)
    decay = [p for p in model.parameters() if p.dim() >= 2]      # matrices get weight decay
    no_decay = [p for p in model.parameters() if p.dim() < 2]    # biases and LayerNorm do not
    opt = torch.optim.AdamW([{"params": decay, "weight_decay": a.weight_decay},
                             {"params": no_decay, "weight_decay": 0.0}], lr=a.lr, betas=(0.9, 0.99))
    start, best = 0, float("inf")
    if ckpt:
        model.load_state_dict(ckpt["model"])
        opt.load_state_dict(ckpt["optimizer"])
        start, best = ckpt["step"], ckpt["best_val"]
        print(f"resumed from {a.ckpt} at step {start}")
    n = model.num_params()
    tokens = a.max_iters * a.batch_size * a.block_size
    print(f"model: {n:,} parameters; starting loss should be about ln({tok.vocab_size}) = {math.log(tok.vocab_size):.2f}")
    print(f"budget: {a.max_iters} steps x {a.batch_size * a.block_size} tokens = {tokens / 1e6:.1f}M tokens, "
          f"about 6 x params x tokens = {6 * n * tokens:.1e} FLOPs")
    if not cfg.causal:
        print("WARNING: causal mask OFF. The model can read the answer, so the loss will look too good.")

    def save(step):
        a.ckpt.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"model": model.state_dict(), "optimizer": opt.state_dict(), "config": vars(cfg),
                    "tokenizer": tok.to_dict(), "step": step, "best_val": best,
                    "chars_per_token": chars_per_token}, a.ckpt)

    # 3. training loop -------------------------------------------------------------
    splits = {"train": train_ids, "val": val_ids}
    first = estimate_loss(model, splits, a)
    print(f"step {start:5d} | train {first['train']:.3f} | val {first['val']:.3f}")
    t0 = time.time()
    step = start
    try:
        for step in range(start, a.max_iters):
            for group in opt.param_groups:
                group["lr"] = lr_at(step, a)
            x, y = get_batch(train_ids, a.block_size, a.batch_size)
            _, loss = model(x, y)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            if (step + 1) % a.eval_interval == 0 or step + 1 == a.max_iters:
                losses = estimate_loss(model, splits, a)
                bpc = losses["val"] / chars_per_token / math.log(2)   # bits per character
                best = min(best, losses["val"])
                elapsed = time.time() - t0
                print(f"step {step + 1:5d} | train {losses['train']:.3f} | val {losses['val']:.3f} "
                      f"| val {bpc:.2f} bits/char | {elapsed / 60:.1f} min")
                save(step + 1)
        step = a.max_iters
    except KeyboardInterrupt:
        print("\ninterrupted: saving so you can --resume")   # the unfinished step is redone
    save(step)
    print(f"saved {a.ckpt} (step {step}) in {(time.time() - t0) / 60:.1f} min")

    if a.smoke and step == a.max_iters:
        final = estimate_loss(model, splits, a)
        assert final["train"] < first["train"] - 0.5, "loss did not go down: check your setup"
        print(f"smoke test OK: train loss {first['train']:.2f} -> {final['train']:.2f}")


if __name__ == "__main__":
    main()
