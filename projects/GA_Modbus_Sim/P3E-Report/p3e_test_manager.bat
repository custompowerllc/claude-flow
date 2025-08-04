@echo off
REM P3E Test Manager - Batch version for Windows
REM Usage: p3e_test_manager.bat

cls
echo ===============================================
echo          P3E Battery Test Manager
echo ===============================================
echo.

echo Select operation:
echo 1. Run Dashboard (view CSV data)
echo 2. Run Standalone Logger (collect new data)
echo 3. Exit
echo.
set /p operation="Enter choice (1-3): "

if "%operation%"=="3" goto :exit

echo.
echo Available pack serial numbers:
echo   0515, 0518, 0520, 0533, 0535, 0561, 0564, 0583
echo.
set /p serial="Enter pack serial number (e.g., 0520): "

echo.
echo Select test type:
echo 1. Charge test
echo 2. Discharge test
echo 3. General test (root folder)
set /p testtype="Enter choice (1-3): "

if "%testtype%"=="1" set folder=charge
if "%testtype%"=="2" set folder=discharge
if "%testtype%"=="3" set folder=.

if "%operation%"=="1" goto :dashboard
if "%operation%"=="2" goto :logger
goto :exit

:dashboard
set search_path=test-artifacts\%serial%
if not "%folder%"=="." set search_path=test-artifacts\%serial%\%folder%

echo.
echo Select monitoring mode:
echo 1. Historical view (analyze complete file)
echo 2. Real-time monitoring (watch live updates)
set /p mode="Enter choice (1-2): "

if "%mode%"=="1" (
    set mode_flag=--historical
) else (
    set mode_flag=
)

REM Find latest CSV file
for /f "tokens=*" %%i in ('dir /b /od "%search_path%\*%serial%*.csv" 2^>nul') do set latest_csv=%%i

if "%latest_csv%"=="" (
    echo No CSV files found in %search_path%
    pause
    goto :exit
)

set full_path=%cd%\%search_path%\%latest_csv%
echo.
echo Selected file: %latest_csv%
echo Full path: %full_path%
echo.
echo Launching dashboard...

REM Change to parent directory
cd ..

REM Check for python3 or python
where python3 >nul 2>&1
if %errorlevel%==0 (
    set python_cmd=python3
) else (
    set python_cmd=python
)

echo Using Python command: %python_cmd%

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist "new_venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call new_venv\Scripts\activate.bat
)

REM Run dashboard
if "%mode_flag%"=="" (
    %python_cmd% -m src.modbus_dashboard "%full_path%"
) else (
    %python_cmd% -m src.modbus_dashboard "%full_path%" %mode_flag%
)

REM Return to P3E-Report directory
cd P3E-Report
goto :end

:logger
echo.
set /p com_port="Enter COM port (e.g., COM3): "
if "%com_port%"=="" set com_port=COM3

set output_path=P3E-Report\test-artifacts\%serial%
if not "%folder%"=="." set output_path=P3E-Report\test-artifacts\%serial%\%folder%

echo.
echo Output will be saved to: %output_path%
echo Press Ctrl+C to stop logging
echo.
echo Starting standalone logger for pack %serial%...

REM Change to parent directory
cd ..

REM Check for python3 or python
where python3 >nul 2>&1
if %errorlevel%==0 (
    set python_cmd=python3
) else (
    set python_cmd=python
)

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist "new_venv\Scripts\activate.bat" (
    call new_venv\Scripts\activate.bat
)

REM Run logger
%python_cmd% -m src.modbus_standalone_logger --port %com_port% --serial-number %serial% --rma-number 8765 --output-path %output_path%

REM Return to P3E-Report directory
cd P3E-Report
goto :end

:exit
echo Exiting...
exit /b 0

:end
echo.
pause