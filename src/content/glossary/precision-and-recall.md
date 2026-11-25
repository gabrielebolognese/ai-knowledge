---
term: Precision and recall
short: >-
  Two classification metrics. Precision = TP / (TP + FP): when the model says yes, how often is it right? Recall = TP / (TP + FN): of the real yeses, how many did it find?
level: intermediate
aliases: [precision, recall, sensitivity, true positive rate]
related: [confusion-matrix, f1-score]
sources:
  - id: wiki-pr
    title: Precision and recall
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Precision_and_recall
    accessed: 2026-11-25
    type: wikipedia
  - id: mlcc-metrics
    title: "Classification: Accuracy, recall, precision, and related metrics"
    publisher: Google Machine Learning Crash Course
    url: https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall
    accessed: 2026-11-25
    type: course
---
The two usually trade off: raising the decision threshold makes a model say "yes" less often, which tends to raise precision and lower recall. Which one matters more depends on the cost of each error, for example missed tumours (recall) against wrongly blocked emails (precision).
