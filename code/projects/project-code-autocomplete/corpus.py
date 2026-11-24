"""Build a Python code corpus from the standard library already on your machine.

No download is needed: every CPython install ships its standard library as
.py source files. sysconfig tells us where they are.

Licence: CPython is distributed under the PSF License Agreement
(https://docs.python.org/3/license.html), which allows use and derivative
works. We only train a private model locally; the corpus and the trained
weights are never committed to the repository.

Run:  python corpus.py                 # full corpus (about 10 MB)
      python corpus.py --max-chars 200000
"""
import argparse
import os
import random
import sysconfig
from pathlib import Path

SKIP_DIRS = {"site-packages", "test", "tests", "idlelib", "__pycache__"}
MAX_FILE_BYTES = 200_000            # very large files are mostly generated tables
UNK = "¤"                     # "¤" stands in for any character outside the alphabet
ALPHABET = "\n" + "".join(chr(c) for c in range(32, 127)) + UNK   # 97 characters
_ALLOWED = set(ALPHABET)
SEPARATOR = "# <|file|> {}\n"       # marks the start of each file in the corpus


def stdlib_files():
    """All .py files of the standard library, sorted, skipping tests and IDLE."""
    root = Path(sysconfig.get_paths()["stdlib"])
    files = []
    for folder, subdirs, names in os.walk(root):
        subdirs[:] = [d for d in subdirs if d not in SKIP_DIRS]   # never descend into these
        for name in names:
            path = Path(folder, name)
            if name.endswith(".py") and path.stat().st_size <= MAX_FILE_BYTES:
                files.append(path)
    return root, sorted(files)


def clean(text):
    """Normalise line endings and tabs, and map rare characters to UNK."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")
    return "".join(ch if ch in _ALLOWED else UNK for ch in text)


def build_corpus(max_chars=None, val_fraction=0.1, seed=1337):
    """Return (train_text, val_text, stats). The split is by file, never inside a file."""
    root, files = stdlib_files()
    rng = random.Random(seed)
    rng.shuffle(files)                          # same order on every run (fixed seed)
    docs, total = [], 0
    for path in files:
        try:
            raw = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue                            # a handful of files are not UTF-8
        rel = path.relative_to(root).as_posix()
        doc = SEPARATOR.format(rel) + clean(raw).rstrip("\n") + "\n\n"
        if max_chars is not None and total + len(doc) > max_chars and docs:
            break
        docs.append(doc)
        total += len(doc)
    n_val = max(1, round(len(docs) * val_fraction))
    val_docs, train_docs = docs[:n_val], docs[n_val:]
    train_text, val_text = "".join(train_docs), "".join(val_docs)
    stats = {
        "stdlib": str(root),
        "files": len(docs),
        "train_files": len(train_docs),
        "val_files": len(val_docs),
        "train_chars": len(train_text),
        "val_chars": len(val_text),
        "unk_chars": train_text.count(UNK) + val_text.count(UNK),
    }
    return train_text, val_text, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--max-chars", type=int, default=None, help="size cap in characters")
    parser.add_argument("--val-fraction", type=float, default=0.1)
    parser.add_argument("--out", default=str(Path(__file__).parent / "data"))
    args = parser.parse_args()

    train_text, val_text, stats = build_corpus(args.max_chars, args.val_fraction)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "train.txt").write_text(train_text, encoding="utf-8", newline="\n")
    (out / "val.txt").write_text(val_text, encoding="utf-8", newline="\n")
    for key, value in stats.items():
        print(f"{key:>12}: {value:,}" if isinstance(value, int) else f"{key:>12}: {value}")
    print(f"  vocabulary: {len(ALPHABET)} characters (printable ASCII + newline + {UNK})")
    print(f"Wrote {out / 'train.txt'} and {out / 'val.txt'}")


if __name__ == "__main__":
    main()
