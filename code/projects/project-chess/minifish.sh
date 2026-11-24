#!/bin/sh
# Starts the engine for chess GUIs (Cute Chess, En Croissant, fastchess).
cd "$(dirname "$0")" && exec python3 -u uci.py
