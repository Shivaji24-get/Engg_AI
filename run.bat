@echo off

:: Set the title of the command window
title AI Engineering Assistant

:: Set Python executable path (adjust if needed)
set PYTHON_EXE=python

:: Try to find Python if not in PATH
%PYTHON_EXE% --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set PYTHON_EXE=C:\Python313\python.exe
    %PYTHON_EXE% --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        set PYTHON_EXE=C:\Python312\python.exe
        %PYTHON_EXE% --version >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            set PYTHON_EXE=C:\Python311\python.exe
            %PYTHON_EXE% --version >nul 2>&1
            if %ERRORLEVEL% NEQ 0 (
                echo Error: Python is not found in PATH or standard locations.
                echo Please install Python 3.8 or higher from https://www.python.org/downloads/
                echo or update the PYTHON_EXE variable in this script.
                pause
                exit /b 1
            )
        )
    )
)

echo ===================================
echo Setting up AI Engineering Assistant...
echo Detected Python: %PYTHON_EXE%
%PYTHON_EXE% --version
echo ===================================

:: Python version check
%PYTHON_EXE% -c "import sys; exit(0) if sys.version_info >= (3, 8) else exit(1)" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python 3.8 or higher is required.
    echo Your current Python version is:
    %PYTHON_EXE% --version
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    %PYTHON_EXE% -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
    
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to activate virtual environment.
        pause
        exit /b 1
    )
    
    echo Upgrading pip...
    python -m pip install --upgrade pip
    if %ERRORLEVEL% NEQ 0 (
        echo Warning: Failed to upgrade pip. Continuing anyway...
    )
    
    echo Installing dependencies...
    if exist requirements.txt (
        echo Installing from requirements.txt...
        pip install -r requirements.txt
    ) else (
        echo requirements.txt not found. Installing basic dependencies...
        pip install flask flask-cors python-dotenv openai rich
    )
    
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to install dependencies.
        pause
        exit /b 1
    )
else
    echo Activating existing virtual environment...
    call venv\Scripts\activate.bat
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to activate virtual environment.
        pause
        exit /b 1
    )
)

:: Create necessary directories
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads

:: Install the package in development mode
echo.
echo Installing package in development mode...
pip install -e .
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Failed to install package in development mode. The package may not be in development mode.
    echo This is not a critical error. Continuing...
)

:: Start the application
echo.
echo ===================================
echo Starting AI Engineering Assistant...
echo ===================================
echo Application will be available at:
echo http://localhost:5001
echo.
echo Press Ctrl+C to stop the server.
echo ===================================
echo.

python -m src.main

:: If execution reaches here, the server was stopped
pause
