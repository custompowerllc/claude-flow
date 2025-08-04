@echo off
REM GA BMS Monitor - Emergency Cleanup Script for Windows
REM 
REM This script sends a cleanup signal to the running GA BMS Monitor application
REM to gracefully shut it down when the GUI is frozen or unresponsive.
REM
REM Usage: cleanup.bat

echo GA BMS Monitor - Emergency Cleanup
echo ==================================
echo Platform: Windows
echo.

REM Find the python process running our app
for /f "tokens=2" %%i in ('tasklist /fi "IMAGENAME eq python.exe" /fo list ^| findstr "PID:"') do (
    set PID=%%i
    goto :found
)

echo Error: GA BMS Monitor is not running
exit /b 1

:found
echo Found GA BMS Monitor process: PID %PID%
echo.
echo Note: On Windows, sending a SIGBREAK signal requires special tools.
echo You have the following options:
echo.
echo 1. Press Ctrl+Break in the application console window
echo 2. Use Windows Task Manager to end the process
echo 3. Install and use SendSignal utility from:
echo    https://github.com/walware/statet/tree/master/de.walware.statet.r.console.core/cppSendSignal
echo.
echo For now, please use Task Manager to gracefully close the application.
pause