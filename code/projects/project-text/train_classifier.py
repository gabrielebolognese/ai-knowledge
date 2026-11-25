"""Train a sentiment classifier on SST-2: the bag-of-embeddings baseline or the BiLSTM.

    python train_classifier.py --model bag        # 5 epochs; see the lesson for timings
    python train_classifier.py --model bilstm     # 3 epochs
    python train_classifier.py --smoke            # bundled UCI sentences, offline, well under 2 minutes

The best epoch (by validation accuracy) is kept and evaluated once on the test set, on the
bundled challenge sentences (negation, contrast) and on the UCI review sentences (other domains).
Saves checkpoints/<model>[-smoke].pt for classify.py and outputs/metrics-<model>[-smoke].json.
"""
import argparse
import copy
import json
import time

import torch
from torch.nn import functional as F

from classifier import MODELS, count_parameters
from sst2_data import Vocab, load_challenge, load_sst2, load_uci, make_batches, split_off
from text_data import CHECKPOINTS, HERE

DEFAULTS = {"bag": dict(epochs=5, lr=5e-3, dropout=0.0, batch_size=64),
            "bilstm": dict(epochs=3, lr=2e-3, dropout=0.3, batch_size=128)}


def get_args():
    p = argparse.ArgumentParser(description="Train a short-text sentiment classifier")
    p.add_argument("--model", choices=sorted(MODELS), default="bag")
    p.add_argument("--epochs", type=int, default=None)
    p.add_argument("--lr", type=float, default=None, help="Adam learning rate")
    p.add_argument("--dropout", type=float, default=None)
    p.add_argument("--emb", type=int, default=64)
    p.add_argument("--hidden", type=int, default=128, help="BiLSTM only: hidden size per direction")
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--smoke", action="store_true", help="train on 2,400 bundled UCI sentences, 3 epochs")
    a = p.parse_args()
    for key, value in DEFAULTS[a.model].items():
        if getattr(a, key) is None:
            setattr(a, key, value)
    if a.smoke:
        a.epochs = min(a.epochs, 3)
    a.name = a.model + ("-smoke" if a.smoke else "")
    return a


@torch.no_grad()
def predict(model, pairs, vocab, batch_size=256):
    model.eval()
    preds = []
    for ids, lengths, _ in make_batches(pairs, vocab, batch_size):
        preds += model(ids, lengths).argmax(1).tolist()
    return preds


def metrics(preds, pairs):
    """Accuracy, plus precision/recall/F1 for the positive class and the confusion counts."""
    gold = [y for _, y in pairs]
    tp = sum(p == 1 and g == 1 for p, g in zip(preds, gold))
    fp = sum(p == 1 and g == 0 for p, g in zip(preds, gold))
    fn = sum(p == 0 and g == 1 for p, g in zip(preds, gold))
    tn = len(gold) - tp - fp - fn
    precision = tp / (tp + fp) if tp + fp else 0.0     # of the sentences called positive, how many are?
    recall = tp / (tp + fn) if tp + fn else 0.0        # of the positive sentences, how many were found?
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"accuracy": (tp + tn) / len(gold), "precision": precision, "recall": recall, "f1": f1,
            "tp": tp, "fp": fp, "fn": fn, "tn": tn, "n": len(gold)}


def main():
    a = get_args()
    torch.manual_seed(a.seed)
    if a.smoke:                                         # offline: the bundled CC BY 4.0 sentences
        train, test = split_off(load_uci(), 0.1, seed=1)
        out_of_domain = []
    else:
        train, test = load_sst2()                       # GLUE's validation set serves as our test set
        out_of_domain = load_uci()
    train, val = split_off(train, 0.05, seed=a.seed)    # carve a validation set out of training data
    challenge = load_challenge()

    vocab = Vocab.build(s for s, _ in train)            # training split only: no peeking at test words
    model = MODELS[a.model](len(vocab), a.emb, **({"hidden": a.hidden} if a.model == "bilstm" else {}),
                            dropout=a.dropout)
    print(f"{a.name}: train {len(train):,} / val {len(val):,} / test {len(test):,}; "
          f"vocabulary {len(vocab):,}; {count_parameters(model):,} parameters")
    optimizer = torch.optim.Adam(model.parameters(), lr=a.lr)

    best, history, start = None, [], time.time()
    for epoch in range(1, a.epochs + 1):
        model.train()
        total, seen = 0.0, 0
        for ids, lengths, labels in make_batches(train, vocab, a.batch_size, shuffle=True, seed=a.seed + epoch):
            loss = F.cross_entropy(model(ids, lengths), labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total += loss.item() * len(labels)
            seen += len(labels)
        val_acc = metrics(predict(model, val, vocab), val)["accuracy"]
        history.append({"epoch": epoch, "train_loss": total / seen, "val_accuracy": val_acc,
                        "seconds": round(time.time() - start, 1)})
        print(f"epoch {epoch}  train loss {total / seen:.4f}  val accuracy {val_acc:.2%}  ({time.time() - start:.0f} s)")
        if best is None or val_acc > best[1]:
            best = (epoch, val_acc, copy.deepcopy(model.state_dict()))

    model.load_state_dict(best[2])
    results = {"best_epoch": best[0], "val_accuracy": best[1], "test": metrics(predict(model, test, vocab), test)}
    t = results["test"]
    print(f"best epoch {best[0]} -> test accuracy {t['accuracy']:.2%}  precision {t['precision']:.2%}  "
          f"recall {t['recall']:.2%}  F1 {t['f1']:.2%}")
    print(f"  confusion: {t['tp']} true pos, {t['fn']} missed pos, {t['fp']} false pos, {t['tn']} true neg")

    preds = predict(model, challenge, vocab)
    results["challenge"] = metrics(preds, challenge)
    print(f"challenge set (negation and contrast): {results['challenge']['accuracy']:.2%} of {len(challenge)}")
    wrong = [(s, y) for (s, y), p in zip(challenge, preds) if p != y]
    for s, y in wrong[:8]:
        print(f"  wrong: {s!r} (true label {'positive' if y else 'negative'})")
    if out_of_domain:
        results["uci_out_of_domain"] = metrics(predict(model, out_of_domain, vocab), out_of_domain)
        print(f"UCI Amazon/Yelp/IMDb sentences (other domains): {results['uci_out_of_domain']['accuracy']:.2%}")

    CHECKPOINTS.mkdir(exist_ok=True)
    config = {"vocab_size": len(vocab), "emb_dim": a.emb, "dropout": a.dropout}
    if a.model == "bilstm":
        config["hidden"] = a.hidden
    torch.save({"kind": "classifier", "model": a.model, "config": config, "itos": vocab.itos,
                "state": model.state_dict(), "results": results}, CHECKPOINTS / f"{a.name}.pt")
    (HERE / "outputs").mkdir(exist_ok=True)
    (HERE / "outputs" / f"metrics-{a.name}.json").write_text(json.dumps({"history": history, **results}, indent=2))
    print(f"saved checkpoints/{a.name}.pt and outputs/metrics-{a.name}.json ({time.time() - start:.0f} s)")
    if a.smoke:
        assert history[-1]["train_loss"] < history[0]["train_loss"], "training loss should fall"
        assert t["accuracy"] > 0.6, "test accuracy should be well above the 50% coin flip"
        print("smoke test passed")


if __name__ == "__main__":
    main()
