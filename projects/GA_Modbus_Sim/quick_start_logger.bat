@echo off
REM Quick start script that skips dependency checking

echo GA Standalone Modbus Logger - Quick Start
echo =========================================
echo.
echo Skipping dependency checks...
echo Running logger directly...
echo.

cd /d "%~dp0"
python src\modbus_standalone_logger.py %*