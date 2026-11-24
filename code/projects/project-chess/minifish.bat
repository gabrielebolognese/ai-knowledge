@echo off
rem Starts the engine for chess GUIs (Cute Chess, Arena, En Croissant, fastchess).
rem Uses the Python on your PATH; replace "python" with a full path if needed.
cd /d "%~dp0"
python -u uci.py
