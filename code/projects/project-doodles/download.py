"""Download a small slice of Google's Quick, Draw! dataset: the first N doodles of each class.

    python download.py --smoke               # 2 classes x 500 doodles (~0.8 MB): checks your setup
    python download.py                       # 10 classes x 12,000 doodles (~94 MB in total)
    python download.py --per-class 5000      # smaller: ~39 MB
    python download.py --classes cat dog     # any of the 345 categories (see categories.txt in the repo)

Each full class file holds 100,000-340,000 doodles (80-270 MB). We never fetch the whole file: an
HTTP Range request asks the server for only the first bytes, which hold the .npy header followed by
the first N rows of 784 pixels. The result is saved as a normal .npy file in data/quickdraw/.

Data: Quick, Draw! dataset by Google, licensed under CC BY 4.0
(https://github.com/googlecreativelab/quickdraw-dataset, https://creativecommons.org/licenses/by/4.0/).
"""
import argparse
import ast
import io
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
BASE_URL = "https://storage.googleapis.com/quickdraw_dataset/full/numpy_bitmap/"
CLASSES = ["apple", "banana", "cat", "clock", "cloud", "fish", "house", "star", "tree", "umbrella"]
SMOKE_CLASSES = ["apple", "star"]
PIXELS = 28 * 28                     # each doodle is one row of 784 uint8 values (0 = background)
ATTRIBUTION = (
    "Quick, Draw! dataset by Google, licensed under CC BY 4.0.\n"
    "Source: https://github.com/googlecreativelab/quickdraw-dataset\n"
    "Licence: https://creativecommons.org/licenses/by/4.0/\n"
    "This folder holds only the first N rows of each numpy_bitmap file, unchanged.\n"
)


def data_dir(smoke=False):
    return HERE / "data" / ("quickdraw-smoke" if smoke else "quickdraw")


def fetch_range(url, start, end):
    """Bytes start..end (inclusive) of a remote file, using an HTTP Range request."""
    req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}",
                                               "User-Agent": "ai-knowledge-course/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        if resp.status != 206:       # 206 Partial Content: the server honoured the range
            raise RuntimeError(f"server ignored the Range request (HTTP {resp.status}) for {url}")
        return resp.read()


def read_header(url):
    """Parse the .npy header: returns (header length in bytes, total rows in the remote file)."""
    head = fetch_range(url, 0, 1023)                 # the header is 128 bytes here; 1 KB is plenty
    if head[:6] != b"\x93NUMPY":
        raise RuntimeError(f"{url} is not a .npy file")
    major = head[6]
    if major == 1:                                   # version 1: 2-byte little-endian header size
        size, offset = int.from_bytes(head[8:10], "little"), 10
    else:                                            # versions 2 and 3: 4-byte header size
        size, offset = int.from_bytes(head[8:12], "little"), 12
    meta = ast.literal_eval(head[offset:offset + size].decode("latin1"))
    if meta["descr"] != "|u1" or meta["shape"][1] != PIXELS:
        raise RuntimeError(f"unexpected format {meta}")
    return offset + size, meta["shape"][0]


def download_class(name, n, out_dir):
    path = out_dir / f"{name}.npy"
    if path.exists() and np.load(path, mmap_mode="r").shape[0] >= n:
        print(f"  {name:<12} already here ({path.stat().st_size / 1e6:.1f} MB)")
        return path
    url = BASE_URL + urllib.parse.quote(name) + ".npy"   # spaces -> %20, e.g. "The Eiffel Tower"
    header_len, total = read_header(url)
    n = min(n, total)
    body = fetch_range(url, header_len, header_len + n * PIXELS - 1)
    arr = np.frombuffer(body, dtype=np.uint8).reshape(n, 28, 28)
    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(path, arr)                                   # saved as (n, 28, 28) uint8
    print(f"  {name:<12} {n:>6,} of {total:,} doodles  ({len(body) / 1e6:.1f} MB downloaded)")
    return path


def main():
    p = argparse.ArgumentParser(description="Download the first N Quick, Draw! bitmaps per class")
    p.add_argument("--classes", nargs="+", default=None, help=f"default: {' '.join(CLASSES)}")
    p.add_argument("--per-class", type=int, default=12000,
                   help="doodles per class (default 12,000 = 9k train + 1k validation + 2k test)")
    p.add_argument("--smoke", action="store_true", help="2 classes x 500 doodles, saved in data/quickdraw-smoke/")
    a = p.parse_args()
    classes = a.classes or (SMOKE_CLASSES if a.smoke else CLASSES)
    n = 500 if a.smoke else a.per_class
    out = data_dir(a.smoke)
    print(f"Downloading {len(classes)} classes x {n:,} doodles "
          f"(about {len(classes) * n * PIXELS / 1e6:.1f} MB) into {out}")
    for name in classes:
        download_class(name, n, out)
    (out / "ATTRIBUTION.txt").write_text(ATTRIBUTION, encoding="utf-8")
    print("Done. Quick, Draw! dataset by Google, CC BY 4.0. Note from the dataset's README: the drawings were "
          "moderated, but some may still be inappropriate.")


if __name__ == "__main__":
    main()
