---
term: "Virtual environment"
short: >-
  A private folder (usually .venv) holding a Python interpreter and the packages for one project, so projects never clash. Created with python -m venv .venv and switched on by activating it.
level: beginner
aliases: [venv, .venv, virtualenv]
related: [pip, python-interpreter]
sources:
  - id: py-venv
    title: "venv: Creation of virtual environments"
    publisher: Python Software Foundation
    url: https://docs.python.org/3/library/venv.html
    accessed: 2026-11-24
    type: docs
  - id: pypa-venv-guide
    title: "Install packages in a virtual environment using pip and venv"
    publisher: Python Packaging Authority
    url: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
    accessed: 2026-11-24
    type: docs
---
An active environment shows its name in the prompt, for example `(.venv) PS C:\dev\ai-knowledge>`. Deleting the folder removes everything in it, so a broken environment can always be rebuilt from `requirements.txt`.
