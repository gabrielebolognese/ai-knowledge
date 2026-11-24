"""A tiny GPT (decoder-only Transformer) in one file, modelled on Karpathy's nanoGPT.

Shapes: B = batch size, T = context length (tokens), C = n_embd (channels),
H = n_head, V = vocab_size. The default config has about 1.8M parameters.
"""
import math
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class GPTConfig:
    vocab_size: int = 97
    block_size: int = 128      # longest context the model can see (T)
    n_layer: int = 4
    n_head: int = 4
    n_embd: int = 192
    dropout: float = 0.0
    causal: bool = True        # set False only to watch the "no mask" bug in train.py


class CausalSelfAttention(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        assert cfg.n_embd % cfg.n_head == 0
        self.n_head, self.causal = cfg.n_head, cfg.causal
        self.qkv = nn.Linear(cfg.n_embd, 3 * cfg.n_embd)     # query, key, value in one matmul
        self.proj = nn.Linear(cfg.n_embd, cfg.n_embd)        # output projection (W_O)
        self.dropout = nn.Dropout(cfg.dropout)
        mask = torch.tril(torch.ones(cfg.block_size, cfg.block_size, dtype=torch.bool))
        self.register_buffer("mask", mask.view(1, 1, cfg.block_size, cfg.block_size), persistent=False)

    def forward(self, x, explicit=False):
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)                          # 3 x (B, T, C)
        # split C channels into H heads of size C // H: (B, T, C) -> (B, H, T, C//H)
        q, k, v = (t.view(B, T, self.n_head, C // self.n_head).transpose(1, 2) for t in (q, k, v))
        if explicit:
            att = q @ k.transpose(-2, -1) / math.sqrt(k.size(-1))     # (B, H, T, T) scores
            if self.causal:
                att = att.masked_fill(~self.mask[:, :, :T, :T], float("-inf"))   # hide the future
            att = self.dropout(F.softmax(att, dim=-1))                 # each row sums to 1
            y = att @ v                                                # (B, H, T, C//H)
        else:  # the same computation in one fused, faster call
            y = F.scaled_dot_product_attention(
                q, k, v, is_causal=self.causal, dropout_p=self.dropout.p if self.training else 0.0)
        y = y.transpose(1, 2).contiguous().view(B, T, C)               # re-join heads: (B, T, C)
        return self.dropout(self.proj(y))


class MLP(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.fc = nn.Linear(cfg.n_embd, 4 * cfg.n_embd)
        self.proj = nn.Linear(4 * cfg.n_embd, cfg.n_embd)
        self.dropout = nn.Dropout(cfg.dropout)

    def forward(self, x):
        return self.dropout(self.proj(F.gelu(self.fc(x))))


class Block(nn.Module):
    """Pre-LayerNorm Transformer block, as in GPT-2: talk (attention), then think (MLP)."""

    def __init__(self, cfg):
        super().__init__()
        self.ln1, self.attn = nn.LayerNorm(cfg.n_embd), CausalSelfAttention(cfg)
        self.ln2, self.mlp = nn.LayerNorm(cfg.n_embd), MLP(cfg)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))     # residual connection around attention
        x = x + self.mlp(self.ln2(x))      # residual connection around the MLP
        return x


class GPT(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.wte = nn.Embedding(cfg.vocab_size, cfg.n_embd)     # token embeddings
        self.wpe = nn.Embedding(cfg.block_size, cfg.n_embd)     # learned position embeddings
        self.drop = nn.Dropout(cfg.dropout)
        self.blocks = nn.ModuleList(Block(cfg) for _ in range(cfg.n_layer))
        self.ln_f = nn.LayerNorm(cfg.n_embd)
        self.lm_head = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)
        self.lm_head.weight = self.wte.weight                   # weight tying (Press & Wolf 2016)
        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(m):
        if isinstance(m, (nn.Linear, nn.Embedding)):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)
        if isinstance(m, nn.Linear) and m.bias is not None:
            nn.init.zeros_(m.bias)

    def num_params(self):
        return sum(p.numel() for p in self.parameters())    # tied weights are counted once

    def forward(self, idx, targets=None):
        B, T = idx.shape
        assert T <= self.cfg.block_size, f"context {T} > block_size {self.cfg.block_size}"
        pos = torch.arange(T, device=idx.device)
        x = self.drop(self.wte(idx) + self.wpe(pos))           # (B, T, C)
        for block in self.blocks:
            x = block(x)
        logits = self.lm_head(self.ln_f(x))                    # (B, T, V)
        loss = None
        if targets is not None:   # next-token loss at every position at once
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=0.8, top_k=20):
        """Yield new token ids one at a time (so callers can stream them)."""
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.cfg.block_size:]           # crop to the last block_size tokens
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / max(temperature, 1e-6)  # last position only
            if top_k:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = float("-inf")     # keep the k most likely tokens
            probs = F.softmax(logits, dim=-1)
            next_id = torch.multinomial(probs, num_samples=1)  # (B, 1)
            idx = torch.cat([idx, next_id], dim=1)
            yield next_id


if __name__ == "__main__":
    # Shape check with a tiny config, then the parameter count of the real one.
    torch.manual_seed(0)
    tiny = GPT(GPTConfig(vocab_size=10, block_size=8, n_layer=1, n_head=2, n_embd=8))
    x = torch.randint(0, 10, (2, 8))
    logits, loss = tiny(x, x)
    print("logits shape:", tuple(logits.shape), "(B, T, V)")
    print(f"untrained loss {loss.item():.3f} vs ln(V) = {math.log(10):.3f}")
    a = tiny.blocks[0].attn
    h = tiny.ln_f(tiny.wte(x) + tiny.wpe(torch.arange(8)))
    same = torch.allclose(a(h, explicit=True), a(h, explicit=False), atol=1e-5)
    print("explicit mask == scaled_dot_product_attention:", same)
    model = GPT(GPTConfig())
    print(f"default config: {model.num_params():,} parameters")
