@echo off
rem Starts the engine for chess GUIs (Cute Chess, Arena, En Croissant, fastchess).
rem A GUI does not activate your virtual environment, so this uses the course's .venv
rem (in the repository folder, three levels up) when it exists, else the Python on your PATH.
setlocal
cd /d "%~dp0"
set "PY=python"
if exist "%~dp0..\..\..\.venv\Scripts\python.exe" set "PY=%~dp0..\..\..\.venv\Scripts\python.exe"
"%PY%" -u uci.py
