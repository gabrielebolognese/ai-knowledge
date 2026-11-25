---
term: "CUDA"
short: >-
  NVIDIA's platform for running general computations on NVIDIA graphics cards. PyTorch's CUDA builds use it to train networks on the GPU; they need an NVIDIA GPU and a recent driver.
level: beginner
aliases: [GPU acceleration, NVIDIA CUDA]
related: [pytorch]
sources:
  - id: wiki-cuda
    title: "CUDA"
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/CUDA
    accessed: 2026-11-25
    type: wikipedia
  - id: cuda-release-notes
    title: "CUDA Toolkit release notes"
    publisher: NVIDIA
    url: https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html
    accessed: 2026-11-24
    type: docs
---
The PyTorch pip wheels bundle the CUDA runtime, so only the graphics *driver* has to be installed separately. `torch.cuda.is_available()` returns `True` when PyTorch can use the GPU.
