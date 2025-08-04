@echo off
REM Modbus BMS Simulator - Windows COM Port Setup Script
REM Configures virtual COM ports for Modbus RTU testing

echo ========================================
echo Modbus BMS Simulator - Windows COM Setup
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Checking system requirements...

REM Check if Python is installed
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and ensure it's in your PATH
    echo.
    pause
    exit /b 1
)

echo Python installation found.

REM Check if pip is available
pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    echo.
    pause
    exit /b 1
)

echo pip installation found.

REM Install required packages for COM port simulation
echo.
echo Installing COM port simulation packages...
pip install pyserial
if %errorLevel% neq 0 (
    echo ERROR: Failed to install pyserial
    pause
    exit /b 1
)

pip install com0com-python
if %errorLevel% neq 0 (
    echo WARNING: com0com-python installation failed
    echo This is optional - manual COM port pairing may be needed
)

echo.
echo Checking for virtual COM port software...

REM Check if com0com is installed (popular virtual COM port software)
if exist "C:\Program Files\com0com\setupc.exe" (
    echo com0com detected at C:\Program Files\com0com\
    set COM0COM_PATH="C:\Program Files\com0com\setupc.exe"
    goto :setup_com_ports
)

if exist "C:\Program Files (x86)\com0com\setupc.exe" (
    echo com0com detected at C:\Program Files (x86)\com0com\
    set COM0COM_PATH="C:\Program Files (x86)\com0com\setupc.exe"
    goto :setup_com_ports
)

REM Check for other virtual COM port software
echo.
echo Virtual COM port software not detected.
echo.
echo MANUAL SETUP REQUIRED:
echo 1. Install virtual COM port software such as:
echo    - com0com (free): http://com0com.sourceforge.net/
echo    - Virtual Serial Port Driver (commercial)
echo    - Advanced Virtual COM Port
echo.
echo 2. Create a COM port pair (e.g., COM1 and COM2)
echo.
echo 3. Configure one port for the simulator server
echo 4. Configure the other port for the client/testing
echo.
goto :create_config

:setup_com_ports
echo.
echo Setting up virtual COM port pair...

REM Create COM port pair using com0com
echo Creating COM port pair COM10 ^<-^> COM11...
%COM0COM_PATH% install PortName=COM10 PortName=COM11

if %errorLevel% equ 0 (
    echo ✓ Virtual COM port pair created successfully
    echo   Server side: COM10
    echo   Client side: COM11
) else (
    echo WARNING: COM port setup may have failed
    echo Manual configuration may be required
)

:create_config
echo.
echo Creating simulator configuration files...

REM Create COM port configuration for the simulator
echo Creating Windows COM configuration...

REM Create the config directory if it doesn't exist
if not exist "..\..\config" mkdir "..\..\config"

REM Create Windows-specific COM port configuration
(
echo # Windows COM Port Configuration for Modbus BMS Simulator
echo # Generated automatically by setup_com_windows.bat
echo.
echo [modbus_rtu]
echo # Primary COM port for simulator server
echo port = COM10
echo baudrate = 9600
echo bytesize = 8
echo parity = N
echo stopbits = 1
echo timeout = 1.0
echo.
echo [modbus_rtu_client]
echo # Client COM port for testing
echo port = COM11
echo baudrate = 9600
echo bytesize = 8
echo parity = N
echo stopbits = 1
echo timeout = 1.0
echo.
echo [com_port_settings]
echo # Available COM ports for testing
echo available_ports = COM1,COM2,COM3,COM4,COM5,COM6,COM7,COM8,COM9,COM10,COM11,COM12
echo preferred_server_port = COM10
echo preferred_client_port = COM11
echo.
echo # Virtual COM port software detection
echo virtual_com_software = auto_detect
echo com0com_path = C:\Program Files\com0com\setupc.exe
) > "..\..\config\com_ports_windows.ini"

echo ✓ Configuration file created: config\com_ports_windows.ini

REM Create a test script for COM port verification
echo.
echo Creating COM port test script...
(
echo import serial
echo import time
echo import sys
echo.
echo def test_com_ports^(^):
echo     """Test if COM port pair is working"""
echo     try:
echo         # Try to open both COM ports
echo         server_port = serial.Serial^('COM10', 9600, timeout=1^)
echo         client_port = serial.Serial^('COM11', 9600, timeout=1^)
echo         
echo         print^("✓ Both COM ports opened successfully"^)
echo         
echo         # Test communication
echo         test_message = b'HELLO'
echo         server_port.write^(test_message^)
echo         time.sleep^(0.1^)
echo         
echo         received = client_port.read^(len^(test_message^)^)
echo         if received == test_message:
echo             print^("✓ COM port communication test passed"^)
echo             return True
echo         else:
echo             print^(f"✗ Communication test failed. Sent: {test_message}, Received: {received}"^)
echo             return False
echo             
echo     except serial.SerialException as e:
echo         print^(f"✗ COM port test failed: {e}"^)
echo         return False
echo     finally:
echo         try:
echo             server_port.close^(^)
echo             client_port.close^(^)
echo         except:
echo             pass
echo.
echo if __name__ == '__main__':
echo     print^("Testing COM port configuration..."^)
echo     success = test_com_ports^(^)
echo     sys.exit^(0 if success else 1^)
) > "..\test_com_ports.py"

echo ✓ Test script created: scripts\test_com_ports.py

REM Create a batch file to run the test
(
echo @echo off
echo echo Testing COM port configuration...
echo python ..\test_com_ports.py
echo if %%errorLevel%% equ 0 ^(
echo     echo.
echo     echo ✓ COM port setup is working correctly
echo ^) else ^(
echo     echo.
echo     echo ✗ COM port setup has issues
echo     echo Please check your virtual COM port software configuration
echo ^)
echo pause
) > "test_com_setup.bat"

echo ✓ Test batch file created: setup\test_com_setup.bat

echo.
echo ========================================
echo Windows COM Port Setup Complete!
echo ========================================
echo.
echo Configuration Summary:
echo - Server COM Port: COM10
echo - Client COM Port: COM11
echo - Baudrate: 9600
echo - Configuration file: config\com_ports_windows.ini
echo.
echo Next Steps:
echo 1. Test COM port configuration: run "test_com_setup.bat"
echo 2. If test fails, manually configure virtual COM ports
echo 3. Start the Modbus BMS Simulator with RTU mode
echo.
echo Troubleshooting:
echo - Ensure virtual COM port software is running
echo - Check Windows Device Manager for COM port status
echo - Verify no other applications are using the COM ports
echo - Try different COM port numbers if needed
echo.

REM Optional: Run the test immediately
echo Would you like to test the COM port configuration now? (Y/N)
set /p choice="Enter your choice: "
if /i "%choice%"=="Y" (
    echo.
    echo Running COM port test...
    call test_com_setup.bat
)

echo.
echo Setup script completed.
pause