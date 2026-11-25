---
term: Convolutional neural network (CNN)
short: >-
  A neural network whose layers slide small learned filters (kernels) across an image, reusing the same weights at every position. This makes it far better and smaller than a fully connected network on images.
level: intermediate
aliases: [CNN, ConvNet, convolutional layer]
related: [max-pooling, relu, weight]
sources:
  - id: cs231n
    title: "CS231n: Convolutional Neural Networks for Visual Recognition"
    publisher: Stanford University
    url: https://cs231n.github.io/convolutional-networks/
    accessed: 2026-11-25
    type: course
  - id: wikipedia
    title: Convolutional neural network
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Convolutional_neural_network
    accessed: 2026-11-25
    type: wikipedia
---
A convolutional layer computes each output value from a small patch of its input (local connectivity) and uses the same kernel at every position (weight sharing). Stacking convolution, ReLU and pooling layers builds features from edges up to whole shapes; a fully connected layer at the end turns them into class scores.
