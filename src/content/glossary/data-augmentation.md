---
term: Data augmentation
short: >-
  Creating extra training examples by applying small, label-preserving changes to the existing ones, such as shifts, rotations or rescaling of an image. It acts as a regulariser and makes the model less sensitive to those changes.
level: intermediate
aliases: [augmentation]
related: [dropout, distribution-shift]
sources:
  - id: d2l-aug
    title: "Dive into Deep Learning, 14.1 Image Augmentation"
    author: Aston Zhang, Zachary Lipton, Mu Li, Alexander Smola
    publisher: d2l.ai
    url: https://d2l.ai/chapter_computer-vision/image-augmentation.html
    accessed: 2026-11-25
    type: book
  - id: tv-transforms
    title: "Transforming images, videos, boxes and more"
    publisher: PyTorch (torchvision)
    url: https://docs.pytorch.org/vision/stable/transforms.html
    accessed: 2026-11-25
    type: docs
---
Augment only the training set. Validation and test images stay unchanged, so the measured accuracy reflects real inputs. A change is only safe if it keeps the label: a 6 rotated by 180 degrees becomes a 9.
