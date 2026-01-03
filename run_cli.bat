@echo off
set "VENV_PYTHON=%~dp0venv\Scripts\python.exe"
set "PYTHONPATH=%~dp0"
"%VENV_PYTHON%" src/cli.py
pause
