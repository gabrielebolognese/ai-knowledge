"""Autocomplete Python code with your trained tiny GPT.

    python complete.py --prompt "def is_even(n):"     # one completion, streamed
    python complete.py                                 # interactive: paste code, then an empty line
    python complete.py --watch my_script.py            # suggest the rest of the file's last line on every save
    python complete.py --bench                         # latency: float32 vs int8 dynamic quantization

Options: --temperature (0.2-0.6 suits code), --top-k, --samples (alternatives, like an IDE list),
--ckpt (default: checkpoints/char.pt, falling back to the smoke checkpoint).
"""
import argparse
import io
import sys
import time
import warnings
from pathlib import Path

import torch

from model import GPT, GPTConfig
from tokenizer import load_tokenizer

HERE = Path(__file__).parent
FILE_MARK = "# <|file|>"


def indent_of(line):
    return len(line) - len(line.lstrip(" "))


def block_indent(prompt):
    """Lines that start at this indentation or less end the block being completed."""
    lines = [l for l in prompt.split("\n") if l.strip()]
    if not lines:
        return -1                          # empty prompt: only a blank line stops
    last = lines[-1]
    if last.rstrip().endswith(":"):        # a block header such as "def f(x):"
        return indent_of(last)
    return indent_of(last) - 1 if indent_of(last) > 0 else -1


class Completer:
    def __init__(self, ckpt_path, quantize=False):
        ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        self.tok = load_tokenizer(ckpt["tokenizer"])
        self.model = GPT(GPTConfig(**ckpt["config"]))
        self.model.load_state_dict(ckpt["model"])
        self.model.eval()                                  # inference mode: no dropout
        if quantize:
            self.model = quantize_int8(self.model)
        self.step = ckpt["step"]

    def stream(self, prompt, max_new=200, temperature=0.4, top_k=20, stop="block"):
        """Yield pieces of text. stop: 'line' (end of line), 'block' (dedent or blank line) or 'none'."""
        ids = self.tok.encode(prompt) or self.tok.encode("\n")
        idx = torch.tensor([ids], dtype=torch.long)
        base = block_indent(prompt)
        text, sent = "", 0                                 # generated text, chars already yielded
        for next_id in self.model.generate(idx, max_new, temperature, top_k):
            text += self.tok.decode([next_id.item()])
            cut = find_stop(text, stop, base, at_line_start=prompt.endswith("\n") or not prompt)
            if cut is not None:
                if cut > sent:
                    yield text[sent:cut]
                return
            # hold back a line that so far is only indentation: it may turn out to be a dedent
            safe = text.rfind("\n") + 1 if stop == "block" and not text[text.rfind("\n") + 1:].strip() else len(text)
            if safe > sent:
                yield text[sent:safe]
                sent = safe
        if len(text) > sent:
            yield text[sent:]

    def complete(self, prompt, **kw):
        return "".join(self.stream(prompt, **kw))


def find_stop(text, stop, base, at_line_start):
    """Return where to cut the completion, or None to keep going."""
    if FILE_MARK in text:
        return text.index(FILE_MARK)
    if stop == "line":
        return text.index("\n") if "\n" in text else None
    if stop == "none":
        return None
    if "\n\n\n" in text:                                   # two blank lines: the block is over
        return text.index("\n\n\n")
    start = 0 if at_line_start else 1                      # piece 0 may just finish the prompt's last line
    pos = 0
    for i, line in enumerate(text.split("\n")):
        if i >= start and line.strip() and indent_of(line) <= base:
            return pos                                     # dedent: this line no longer belongs to the block
        pos += len(line) + 1
    return None


def quantize_int8(model):
    """Dynamic int8 quantization of every nn.Linear (weights stored as int8, activations quantized on the fly)."""
    try:
        from torch.ao.quantization import quantize_dynamic
    except ImportError:
        sys.exit("This PyTorch build no longer ships torch.ao.quantization; see the lesson for torchao.")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)


def size_mb(model):
    buf = io.BytesIO()
    torch.save(model.state_dict(), buf)
    return buf.tell() / 1e6


def bench(path, prompt, n_tokens=150, repeats=3):
    """Milliseconds per generated token, float32 vs int8, with the same seed."""
    for label, quant in (("float32", False), ("int8 dynamic", True)):
        c = Completer(path, quantize=quant)
        idx = torch.tensor([c.tok.encode(prompt)], dtype=torch.long)
        times = []
        for r in range(repeats):
            torch.manual_seed(0)
            t0 = time.perf_counter()
            out = [i.item() for i in c.model.generate(idx, n_tokens, 0.4, 20)]
            times.append((time.perf_counter() - t0) / n_tokens * 1000)
        print(f"{label:>13}: {min(times):6.2f} ms/token | state_dict {size_mb(c.model):5.2f} MB")
        print("               sample:", repr(c.tok.decode(out)[:80]))


def watch(c, path, args):
    path = Path(path)
    print(f"watching {path} - save the file to get a suggestion for its last line (Ctrl+C to stop)")
    last = None
    while True:
        try:
            mtime = path.stat().st_mtime
        except FileNotFoundError:
            mtime = None
        if mtime and mtime != last:
            last = mtime
            text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\t", "    ").rstrip("\n")
            line = text.split("\n")[-1]
            suggestion = c.complete(text, max_new=80, temperature=args.temperature, top_k=args.top_k, stop="line")
            n = text.count("\n") + 1
            print(f"line {n}: {line}\033[2m{suggestion}\033[0m" if sys.stdout.isatty() else f"line {n}: {line}|{suggestion}")
        time.sleep(0.5)


def main():
    p = argparse.ArgumentParser(description="Autocomplete Python with the tiny GPT")
    p.add_argument("--ckpt", default=None)
    p.add_argument("--prompt", default=None, help='code to complete; "\\n" is read as a newline')
    p.add_argument("--watch", default=None, metavar="FILE")
    p.add_argument("--bench", action="store_true")
    p.add_argument("--temperature", type=float, default=0.4)
    p.add_argument("--top-k", type=int, default=20)
    p.add_argument("--max-new", type=int, default=200, help="maximum new tokens")
    p.add_argument("--samples", type=int, default=1, help="alternative completions to show")
    p.add_argument("--stop", choices=["block", "line", "none"], default="block")
    p.add_argument("--quantize", action="store_true", help="int8 dynamic quantization")
    p.add_argument("--threads", type=int, default=None)
    p.add_argument("--seed", type=int, default=None)
    args = p.parse_args()

    if args.threads:
        torch.set_num_threads(args.threads)
    if args.seed is not None:
        torch.manual_seed(args.seed)
    path = Path(args.ckpt) if args.ckpt else next(
        (q for q in (HERE / "checkpoints" / n for n in ("char.pt", "bpe.pt", "char-smoke.pt")) if q.exists()), None)
    if path is None or not path.exists():
        sys.exit("No checkpoint found. Train one first: python train.py --smoke (or python train.py)")
    if args.bench:
        bench(path, args.prompt or "def __init__(self, ")
        return
    c = Completer(path, quantize=args.quantize)
    print(f"loaded {path.name} (trained {c.step} steps)", file=sys.stderr)
    if args.watch:
        watch(c, args.watch, args)
        return

    def run(prompt):
        for s in range(args.samples):
            if args.samples > 1:
                print(f"\n--- suggestion {s + 1} ---")
            print(prompt, end="")
            t0, n = time.perf_counter(), 0
            for piece in c.stream(prompt, args.max_new, args.temperature, args.top_k, args.stop):
                print(piece, end="", flush=True)              # stream as it is generated
                n += len(piece)
            print(f"\n[{n} chars in {time.perf_counter() - t0:.2f}s]", file=sys.stderr)

    if args.prompt is not None:
        run(args.prompt.replace("\\n", "\n"))
        return
    print("Paste or type code. An empty line completes it; Ctrl+C quits.", file=sys.stderr)
    while True:
        try:
            lines = []
            while True:
                line = input("... " if lines else ">>> ")
                if not line and lines:
                    break
                lines.append(line)
            prompt = "\n".join(lines)
            run(prompt + ("\n" if prompt.rstrip().endswith(":") else ""))
        except (KeyboardInterrupt, EOFError):
            print()
            return


if __name__ == "__main__":
    main()
