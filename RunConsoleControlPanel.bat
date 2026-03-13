@echo off
if exist .venv (
    .venv\Scripts\activate
    python ControlPanel/GLady_ConsoleControlPanel.py %*
) else (
    echo No existing virtual environment found. Please run "Setup.bat"
)
pause
