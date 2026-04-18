@echo off
setlocal enabledelayedexpansion

echo ==================
echo GLady Setup Script
echo ==================
echo.

set "PYTHON_VERSION=3.12"
set "PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
set "PYTHON_CMD="

echo Looking for Python %PYTHON_VERSION%...

REM --- Prefer Python launcher (most reliable) ---
where py >nul 2>&1
if not errorlevel 1 (
    py -%PYTHON_VERSION% --version >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=py -%PYTHON_VERSION%"
        echo Found Python %PYTHON_VERSION% using py launcher
    )
)

REM --- Fallback: check python in PATH ---
if "!PYTHON_CMD!"=="" (
    for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do (
        set "PY_VER=%%v"
    )

    if "!PY_VER!"=="%PYTHON_VERSION%.0" (
        set "PYTHON_CMD=python"
        echo Found Python %PYTHON_VERSION% in PATH
    )
)

REM --- Fallback: common install locations ---
if "!PYTHON_CMD!"=="" (
    for %%p in (
        "C:\Python312"
        "C:\Program Files\Python312"
        "C:\Program Files (x86)\Python312"
    ) do (
        if exist "%%~p\python.exe" (
            set "PYTHON_CMD=%%~p\python.exe"
            echo Found Python at %%~p
            goto :found_python
        )
    )
)

REM --- If still not found, download installer ---
if "!PYTHON_CMD!"=="" (
    echo Python %PYTHON_VERSION% not found.
    echo.
    echo Downloading Python installer...

    powershell -ExecutionPolicy Bypass -Command "Invoke-WebRequest '%PYTHON_INSTALLER_URL%' -OutFile 'python-installer.exe'"

    if exist python-installer.exe (
        echo Running installer...
        echo IMPORTANT: Check "Add Python to PATH"
        start /wait python-installer.exe
        del python-installer.exe

        echo.
        echo Python installed. Please run this script again.
        pause
        exit /b
    ) else (
        echo Failed to download Python installer.
        pause
        exit /b
    )
)

:found_python

echo Using: !PYTHON_CMD!
!PYTHON_CMD! --version
echo.

REM --- Run generator ---
echo Running Requirements Generator...
if exist .\Source\RequirementsGenerator.py (
    !PYTHON_CMD! .\Source\RequirementsGenerator.py
)

REM --- Recreate venv ---
if exist .venv (
    echo Removing existing virtual environment...
    rmdir /s /q .venv
)

echo Creating virtual environment...
!PYTHON_CMD! -m venv .venv

echo.

REM --- Upgrade pip tools ---
echo Upgrading pip...
.venv\Scripts\python -m pip install --upgrade pip setuptools wheel

REM --- Install requirements ---
echo Installing dependencies...
if exist requirements_gen.txt (
    .venv\Scripts\python -m pip install -r requirements_gen.txt
)

echo.
echo ==========================
echo Setup complete!
echo ==========================
pause