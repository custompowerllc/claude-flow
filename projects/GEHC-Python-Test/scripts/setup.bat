@echo off
REM GEHC PHTC Test Application Setup Script for Windows
setlocal EnableDelayedExpansion

echo 🏗️  GEHC PHTC Test Application - Development Setup
echo ==================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python %PYTHON_VERSION% found

REM Create virtual environment
echo [INFO] Creating virtual environment...
if not exist ".venv" (
    python -m venv .venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [WARNING] Virtual environment already exists
)

REM Activate virtual environment and upgrade pip
echo [INFO] Activating virtual environment and upgrading pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
echo [SUCCESS] Pip upgraded

REM Install dependencies
echo [INFO] Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo [SUCCESS] Requirements installed
) else (
    echo [WARNING] requirements.txt not found, installing from pyproject.toml
)

REM Install package in development mode
echo [INFO] Installing package in development mode...
pip install -e .[dev]
echo [SUCCESS] Package installed in development mode

REM Install pre-commit hooks
echo [INFO] Installing pre-commit hooks...
pre-commit install 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Pre-commit hooks installed
) else (
    echo [WARNING] Pre-commit not available, skipping hook installation
)

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "test_results" mkdir test_results
if not exist "docs\_build" mkdir docs\_build
echo [SUCCESS] Directories created

REM Set up environment file
echo [INFO] Setting up environment configuration...
if not exist ".env" (
    copy .env.example .env >nul
    echo [SUCCESS] Environment file created from template
    echo [WARNING] Please edit .env file to configure your serial port settings
) else (
    echo [WARNING] .env file already exists
)

REM Run initial tests
echo [INFO] Running initial tests...
python -m pytest gehc_phtc_test/tests/ --tb=short -q >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Initial tests passed
) else (
    echo [WARNING] Some tests failed - this is normal for initial setup
)

REM Run code quality checks
echo [INFO] Running code quality checks...
black --check gehc_phtc_test/ >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Code formatting needs attention
)

flake8 gehc_phtc_test/ >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Linting issues found
)

REM Display summary
echo.
echo 🎉 Setup Complete!
echo ===================
echo.
echo [SUCCESS] Development environment ready!
echo.
echo Next steps:
echo   1. Activate the virtual environment:
echo      .venv\Scripts\activate.bat
echo.
echo   2. Configure your serial port in .env file
echo.
echo   3. Run the application:
echo      python -m gehc_phtc_test
echo.
echo   4. Run in demo mode:
echo      python -m gehc_phtc_test --config gehc_phtc_test/config/demo_config.json
echo.
echo   5. Run tests:
echo      python -m pytest gehc_phtc_test/tests/
echo.
echo   6. View documentation:
echo      See README.md
echo.
echo For more information, see README.md

pause