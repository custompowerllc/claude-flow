@echo off
REM GA Standalone Modbus Logger Runner Script for Windows Command Prompt
REM This script runs the standalone Modbus logger with dependency checking

echo 🔋 GA Standalone Modbus Logger
echo =====================================

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Remove trailing backslash
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python is available
python --version

REM Check if pip is available
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not available
    pause
    exit /b 1
)

echo ✅ pip is available

echo.
echo 🔍 Checking dependencies...

REM Check for pymodbus
python -c "import pymodbus" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  pymodbus is missing - installing...
    python -m pip install pymodbus
    if errorlevel 1 (
        echo ❌ Failed to install pymodbus
        pause
        exit /b 1
    )
    echo ✅ pymodbus installed successfully
) else (
    echo ✅ pymodbus is available
)

REM Check for pyserial
python -c "import serial" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  pyserial is missing - installing...
    python -m pip install pyserial
    if errorlevel 1 (
        echo ❌ Failed to install pyserial
        pause
        exit /b 1
    )
    echo ✅ pyserial installed successfully
) else (
    echo ✅ pyserial is available
)

REM Check for optional rich package
python -c "import rich" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  rich is missing (optional) - installing for enhanced experience...
    python -m pip install rich
    if errorlevel 1 (
        echo ⚠️  Failed to install rich - continuing without enhanced formatting
    ) else (
        echo ✅ rich installed successfully
    )
) else (
    echo ✅ rich is available
)

REM Check for optional TOML packages
python -c "import tomli, tomli_w" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  TOML libraries missing (optional) - installing for config persistence...
    python -m pip install tomli tomli-w
    if errorlevel 1 (
        echo ⚠️  Failed to install TOML libraries - continuing without config persistence
    ) else (
        echo ✅ TOML libraries installed successfully
    )
) else (
    echo ✅ TOML libraries are available
)

REM Try to activate virtual environment if it exists
if exist "%SCRIPT_DIR%\venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call "%SCRIPT_DIR%\venv\Scripts\activate.bat"
    echo ✅ Virtual environment activated
) else if exist "%SCRIPT_DIR%\new_venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call "%SCRIPT_DIR%\new_venv\Scripts\activate.bat"
    echo ✅ Virtual environment activated
) else (
    echo ⚠️  No virtual environment found. Using system Python.
)

echo.
echo 🚀 Starting Standalone Modbus Logger...

REM Change to script directory
cd /d "%SCRIPT_DIR%"

REM Run the logger with provided arguments
if "%*"=="" (
    python src\modbus_standalone_logger.py
) else (
    python src\modbus_standalone_logger.py %*
)

REM Check exit code and handle errors
if errorlevel 1 (
    echo.
    echo ❌ Logger exited with error code: %errorlevel%
    echo Press any key to exit...
    pause >nul
    exit /b %errorlevel%
) else (
    echo.
    echo ✅ Logger completed successfully
)

REM Deactivate virtual environment if it was activated
if defined VIRTUAL_ENV (
    deactivate
)