@echo off

if exist .venv (
    .venv\Scripts\activate
    python Source/main.py %*
) else (
    echo No existing virtual environment found. Please run "Setup.bat"
)
pause