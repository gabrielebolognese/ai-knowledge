"""Classify the sentiment of your own sentences with a trained model.

    python classify.py "a warm, funny and clever film" "not good at all"
    python classify.py --model checkpoints/bag.pt "not bad at all"
    python classify.py                      # interactive: type sentences, empty line to quit

Train a model first: python train_classifier.py --model bilstm   (or --model bag).
"""
import argparse
from pathlib import Path

import torch

from classifier import MODELS
from sst2_data import Vocab, tokenize
from text_data import CHECKPOINTS


def load(path):
    ckpt = torch.load(path, map_location="cpu")
    if ckpt.get("kind") != "classifier":
        raise SystemExit(f"{path} is not a classifier checkpoint")
    model = MODELS[ckpt["model"]](**ckpt["config"])
    model.load_state_dict(ckpt["state"])
    model.eval()
    return model, Vocab(ckpt["itos"]), ckpt


@torch.no_grad()
def classify(model, vocab, sentence):
    ids = vocab.encode(sentence)
    logits = model(torch.tensor([ids]), torch.tensor([len(ids)]))[0]
    p_positive = torch.softmax(logits, dim=0)[1].item()
    unknown = [tok for tok, i in zip(tokenize(sentence), ids) if i == 1]
    return p_positive, unknown


def show(model, vocab, sentence):
    p, unknown = classify(model, vocab, sentence)
    label = "positive" if p >= 0.5 else "negative"
    note = f"   (unknown words: {', '.join(unknown)})" if unknown else ""
    print(f"{label:8s} {max(p, 1 - p):6.1%}  {sentence}{note}")


def main():
    p = argparse.ArgumentParser(description="Positive or negative? Classify short sentences")
    p.add_argument("sentences", nargs="*")
    p.add_argument("--model", type=Path, default=None, help="default: checkpoints/bilstm.pt, else bag.pt")
    a = p.parse_args()
    path = a.model
    if path is None:
        path = next((c for c in (CHECKPOINTS / "bilstm.pt", CHECKPOINTS / "bag.pt") if c.exists()), None)
    if path is None or not path.exists():
        raise SystemExit("no trained model found: run  python train_classifier.py --model bilstm  first")
    model, vocab, ckpt = load(path)
    acc = ckpt["results"]["test"]["accuracy"]
    print(f"{path.name}: {ckpt['model']} model, test accuracy {acc:.1%}")

    if a.sentences:
        for s in a.sentences:
            show(model, vocab, s)
        return
    print("type a sentence (empty line to quit)")
    while True:
        try:
            s = input("> ").strip()
        except EOFError:
            break
        if not s:
            break
        show(model, vocab, s)


if __name__ == "__main__":
    main()
