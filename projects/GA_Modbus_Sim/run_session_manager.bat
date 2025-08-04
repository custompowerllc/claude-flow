@echo off
REM Battery Testing Session Manager Launcher Script (Windows)
REM Launches the session manager GUI application for battery pack testing

setlocal EnableDelayedExpansion

echo Battery Testing Session Manager Launcher
echo ============================================

REM Check if we're in the correct directory
if not exist "src\session_manager.py" (
    echo Error: Please run this script from the GA_Modbus_Python_App directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Find Python interpreter
set PYTHON_CMD=
for %%P in (python python3 py) do (
    %%P --version >nul 2>&1
    if !errorlevel! equ 0 (
        set PYTHON_CMD=%%P
        goto :found_python
    )
)

echo Error: Python is required but not found
pause
exit /b 1

:found_python
echo Found Python: %PYTHON_CMD%

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    set PYTHON_CMD=python
) else if exist "new_venv\Scripts\activate.bat" (
    echo Activating virtual environment (new_venv)...
    call new_venv\Scripts\activate.bat
    set PYTHON_CMD=python
) else (
    echo No virtual environment found. Using system Python.
)

REM Check for required dependencies
echo Checking dependencies...

REM Try to import required packages
%PYTHON_CMD% -c "from PyQt6.QtWidgets import QApplication" >nul 2>&1
if !errorlevel! neq 0 (
    echo Installing PyQt6...
    %PYTHON_CMD% -m pip install PyQt6
)

%PYTHON_CMD% -c "import pymodbus" >nul 2>&1
if !errorlevel! neq 0 (
    echo Installing pymodbus...
    %PYTHON_CMD% -m pip install pymodbus
)

%PYTHON_CMD% -c "import serial" >nul 2>&1
if !errorlevel! neq 0 (
    echo Installing pyserial...
    %PYTHON_CMD% -m pip install pyserial
)

echo All required dependencies are available

REM Use existing P3E-Report directory structure
if not exist "P3E-Report\test-artifacts" (
    echo Error: P3E-Report\test-artifacts directory not found
    echo Please ensure the P3E-Report directory structure exists
    pause
    exit /b 1
)

REM Create any missing pack directories in P3E-Report structure
for %%P in (0515 0518 0520 0533 0535 0561 0564 0583) do call :create_pack_dirs %%P
goto :after_function

:create_pack_dirs
if not exist "P3E-Report\test-artifacts\%1" mkdir "P3E-Report\test-artifacts\%1" >nul 2>&1
if not exist "P3E-Report\test-artifacts\%1\charge" mkdir "P3E-Report\test-artifacts\%1\charge" >nul 2>&1
if not exist "P3E-Report\test-artifacts\%1\discharge" mkdir "P3E-Report\test-artifacts\%1\discharge" >nul 2>&1
if not exist "P3E-Report\test-artifacts\%1\screenshots" mkdir "P3E-Report\test-artifacts\%1\screenshots" >nul 2>&1
goto :eof

:after_function

echo.
echo Battery Testing Session Manager - P3E Report Integration
echo ========================================================
echo - Manages 8 battery packs: 0515, 0518, 0520, 0533, 0535, 0561, 0564, 0583
echo - Uses P3E-Report/test-artifacts directory structure
echo - Integrates with rma-pack-status.json configuration
echo - Supports up to 2 concurrent testing sessions
echo - Integrates with standalone logger and dashboard
echo - Provides BMS health monitoring and test readiness assessment
echo.

REM Launch the session manager
echo Launching Battery Testing Session Manager...
echo.

if "%1"=="--debug" (
    %PYTHON_CMD% -m src.session_manager --debug
) else (
    %PYTHON_CMD% -m src.session_manager
)

pause