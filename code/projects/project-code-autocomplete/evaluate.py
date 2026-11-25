"""Measure how often the model writes a function body that is valid Python.

For functions in the VALIDATION files (never seen in training) we give the model
the code before the function plus its `def ...:` line, let it write the body,
and check the result with ast.parse. Parsing is a low bar: it says nothing about
whether the code is correct, only that it is syntactically Python.

    python evaluate.py                       # 100 functions, default checkpoint
    python evaluate.py --ckpt checkpoints/bpe.pt --n 200 --show 5
"""
import argparse
import ast
import random
import re
import textwrap
from collections import Counter
from pathlib import Path

from complete import FILE_MARK, Completer
from corpus import build_corpus

HERE = Path(__file__).parent


def function_prompts(val_text):
    """(prompt, header) pairs: everything before a function's body, and its def line(s)."""
    out = []
    for doc in val_text.split(FILE_MARK)[1:]:
        source = FILE_MARK + doc
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        lines = source.split("\n")
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                header = "\n".join(lines[node.lineno - 1:node.body[0].lineno - 1]).rstrip()
                if not header.endswith(":"):
                    continue                     # one-line defs such as "def f(): pass"
                prefix = "\n".join(lines[:node.lineno - 1])
                out.append((prefix + "\n" + header + "\n", header))
    return out


def check(header, body):
    """Return None if header + body parses, else the reason it does not."""
    if "\n" not in body and body.strip():
        return "no complete line"
    body = body[:body.rfind("\n") + 1]           # drop an unfinished last line (token limit)
    try:
        ast.parse(textwrap.dedent(header + "\n" + body))
        return None
    except SyntaxError as e:                     # IndentationError is a subclass
        return re.sub(r" \(.*\)$| on line \d+", "", e.msg)   # e.g. "unterminated triple-quoted string literal"


def main():
    p = argparse.ArgumentParser(description="Parse rate of generated function bodies")
    p.add_argument("--ckpt", default=str(HERE / "checkpoints" / "char.pt"))
    p.add_argument("--n", type=int, default=100)
    p.add_argument("--max-new", type=int, default=300, help="token limit per body")
    p.add_argument("--temperature", type=float, default=0.4)
    p.add_argument("--top-k", type=int, default=20)
    p.add_argument("--show", type=int, default=3, help="examples to print")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--threads", type=int, default=None)
    args = p.parse_args()

    import torch
    torch.manual_seed(args.seed)
    if args.threads:
        torch.set_num_threads(args.threads)
    c = Completer(args.ckpt)
    _, val_text, _ = build_corpus()
    prompts = function_prompts(val_text)
    random.Random(args.seed).shuffle(prompts)
    prompts = prompts[:args.n]
    ok, lengths, reasons = 0, [], Counter()
    for i, (prompt, header) in enumerate(prompts):
        body = c.complete(prompt, max_new=args.max_new, temperature=args.temperature, top_k=args.top_k)
        reason = check(header, body)
        good = reason is None
        ok += good
        reasons[reason] += not good
        lengths.append(body.count("\n"))
        if i < args.show:
            print(f"--- example {i + 1} ({'parses' if good else 'does not parse'}) ---")
            print(header + "\n" + body.rstrip("\n"))
        if (i + 1) % 20 == 0:
            print(f"[{i + 1}/{len(prompts)}] parse rate so far {ok / (i + 1):.0%}")
    print(f"\n{Path(args.ckpt).name}: {ok}/{len(prompts)} bodies parse ({ok / len(prompts):.0%}); "
          f"average body {sum(lengths) / len(lengths):.1f} lines")
    for reason, n in reasons.most_common(5):
        if n:
            print(f"  {n:3d} x {reason}")


if __name__ == "__main__":
    main()
