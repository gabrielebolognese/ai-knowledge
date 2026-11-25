---
term: "pip"
short: >-
  Python's standard package installer. It downloads libraries such as NumPy or PyTorch from the Python Package Index (PyPI). Run it as python -m pip so it installs into the Python you are actually using.
level: beginner
aliases: [pip3, python -m pip, PyPI]
related: [virtual-environment]
sources:
  - id: pip-user-guide
    title: "pip User Guide"
    publisher: Python Packaging Authority
    url: https://pip.pypa.io/en/stable/user_guide/
    accessed: 2026-11-24
    type: docs
  - id: pip-install
    title: "pip documentation: Installation"
    publisher: Python Packaging Authority
    url: https://pip.pypa.io/en/stable/installation/
    accessed: 2026-11-24
    type: docs
---
`python -m pip install -r requirements.txt` installs every package listed in a requirements file in one go.
