"""Confusion matrix, precision, recall and F1 computed by hand with NumPy.

Companion code for the lesson "Evaluation: accuracy, precision, recall and the confusion matrix".
Run:  python code/core/intermediate/metrics.py
Needs NumPy only. If scikit-learn is installed, the script also cross-checks its numbers.
"""
import numpy as np


def confusion_matrix(y_true, y_pred, n_classes):
    """cm[i, j] = how many examples of true class i were predicted as class j."""
    cm = np.zeros((n_classes, n_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    return cm


def per_class_scores(cm):
    tp = np.diag(cm).astype(float)               # correct predictions sit on the diagonal
    fp = cm.sum(axis=0) - tp                     # predicted as class c, but were something else
    fn = cm.sum(axis=1) - tp                     # really class c, but predicted as something else
    precision = np.divide(tp, tp + fp, out=np.zeros_like(tp), where=(tp + fp) > 0)
    recall = np.divide(tp, tp + fn, out=np.zeros_like(tp), where=(tp + fn) > 0)
    f1 = np.divide(2 * precision * recall, precision + recall,
                   out=np.zeros_like(tp), where=(precision + recall) > 0)
    return tp, fp, fn, precision, recall, f1


# 1. A spam filter on 100 emails (class 1 = spam, class 0 = not spam).
#    The counts match the lesson: TP = 40, FN = 20, FP = 10, TN = 30.
y_true = np.array([1] * 60 + [0] * 40)
y_pred = np.array([1] * 40 + [0] * 20 + [1] * 10 + [0] * 30)
cm = confusion_matrix(y_true, y_pred, 2)
print("spam filter, rows = true class (0 = ham, 1 = spam), columns = predicted:")
print(cm)
tp, fp, fn, p, r, f1 = per_class_scores(cm)
print(f"accuracy  {np.mean(y_true == y_pred):.3f}")
print(f"precision {p[1]:.3f}  recall {r[1]:.3f}  F1 {f1[1]:.3f}   (spam class)")

# 2. The accuracy trap: 1,000 emails, only 10 are spam, and a "model" that always says "not spam".
y_true = np.array([1] * 10 + [0] * 990)
y_pred = np.zeros(1000, dtype=int)
tp, fp, fn, p, r, f1 = per_class_scores(confusion_matrix(y_true, y_pred, 2))
print(f"\nalways 'not spam': accuracy {np.mean(y_true == y_pred):.3f}, spam recall {r[1]:.3f}")

# 3. Three classes: macro average (mean of per-class scores) vs micro average (pooled counts).
y_true3 = np.array([0] * 80 + [1] * 15 + [2] * 5)
y_pred3 = np.array([0] * 78 + [1] * 2 + [1] * 10 + [0] * 5 + [2] * 1 + [0] * 4)
cm3 = confusion_matrix(y_true3, y_pred3, 3)
tp, fp, fn, p, r, f1 = per_class_scores(cm3)
print("\nthree classes, confusion matrix:")
print(cm3)
print("per-class recall   ", np.round(r, 3))
print(f"macro recall {r.mean():.3f}   micro recall {tp.sum() / (tp.sum() + fn.sum()):.3f} (= accuracy)")

try:                                             # optional cross-check against scikit-learn
    from sklearn.metrics import precision_recall_fscore_support
    _, r_macro, _, _ = precision_recall_fscore_support(y_true3, y_pred3, average="macro", zero_division=0)
    print(f"scikit-learn macro recall {r_macro:.3f}")
except ImportError:
    print("(install scikit-learn to cross-check: python -m pip install scikit-learn)")
