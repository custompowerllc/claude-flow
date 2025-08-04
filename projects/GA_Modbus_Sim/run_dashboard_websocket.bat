@echo off
echo ===============================================
echo    GA Modbus Dashboard - WebSocket Mode
echo ===============================================
echo.

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    echo Make sure venv folder exists and is properly configured
    pause
    exit /b 1
)

REM Find the most recent CSV file
echo [2/3] Finding most recent CSV file...
for /f "delims=" %%i in ('dir /b /od logs\*.csv 2^>nul') do set "latest_csv=%%i"

if not defined latest_csv (
    echo ERROR: No CSV files found in logs\ directory
    echo Please run the Modbus logger first to generate data
    pause
    exit /b 1
)

echo Found: logs\%latest_csv%
echo.

REM Start dashboard with WebSocket
echo [3/3] Starting dashboard with WebSocket integration...
echo Dashboard URL: http://localhost (if web interface available)
echo WebSocket Server: ws://localhost:8765
echo CSV Data Source: logs\%latest_csv%
echo.
echo Press Ctrl+C to stop the dashboard
echo ===============================================
echo.

python src\modbus_dashboard.py logs\%latest_csv% --websocket ws://localhost:8765

echo.
echo Dashboard stopped.
pause