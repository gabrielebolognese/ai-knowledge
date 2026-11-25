---
term: state_dict
short: >-
  In PyTorch, a dictionary that maps each layer's parameter and buffer names (such as "0.weight") to their tensors. Saving it with torch.save is the recommended way to store a model.
level: intermediate
aliases: [state dict, checkpoint]
related: [pytorch, weight]
sources:
  - id: pt-save-load
    title: Saving and Loading Models
    publisher: PyTorch
    url: https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html
    accessed: 2026-11-25
    type: docs
  - id: pt-module
    title: torch.nn.Module
    publisher: PyTorch
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html
    accessed: 2026-11-25
    type: docs
---
Optimizers have a `state_dict()` too (learning rate, momentum buffers), which is why a full training checkpoint saves both. Loading needs a model of the same architecture: `model.load_state_dict(torch.load(path, weights_only=True))`.
