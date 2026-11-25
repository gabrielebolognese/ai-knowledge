#!/bin/sh
# Starts the engine for chess GUIs (Cute Chess, En Croissant, fastchess).
# A GUI does not activate your virtual environment, so this uses the course's .venv
# (in the repository folder, three levels up) when it exists, else python3 on your PATH.
cd "$(dirname "$0")" || exit 1
PY=python3
if [ -x ../../../.venv/bin/python ]; then PY=../../../.venv/bin/python
elif [ -x ../../../.venv/Scripts/python.exe ]; then PY=../../../.venv/Scripts/python.exe
fi
exec "$PY" -u uci.py
