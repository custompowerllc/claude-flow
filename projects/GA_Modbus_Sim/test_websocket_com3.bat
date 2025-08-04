@echo off
echo ==========================================================
echo WebSocket Integration Test Script for COM3
echo ==========================================================
echo.

REM Set the COM port for testing
set COM_PORT=COM3
set SERIAL_NUMBER=test-device
set RMA_NUMBER=ws-test

echo Step 1: Starting Modbus Logger with WebSocket enabled on %COM_PORT%
echo Command: python src\modbus_standalone_logger.py --port %COM_PORT% --websocket-enabled --serial-number %SERIAL_NUMBER% --rma-number %RMA_NUMBER%
echo.
echo Press Enter to start the logger (or Ctrl+C to cancel)
pause

REM Start the logger in a new window
start "Modbus Logger (COM3)" cmd /k "python src\modbus_standalone_logger.py --port %COM_PORT% --websocket-enabled --serial-number %SERIAL_NUMBER% --rma-number %RMA_NUMBER%"

echo.
echo Waiting 5 seconds for logger to initialize...
timeout /t 5 /nobreak >nul

echo.
echo Step 2: Testing WebSocket connection
echo Running comprehensive WebSocket test...
python test_websocket_integration.py --url ws://localhost:8765 --duration 30

echo.
echo Step 3: Starting Dashboard with WebSocket integration
echo Command: python src\modbus_dashboard.py data.csv --websocket ws://localhost:8765
echo.
echo Press Enter to start the dashboard (or Ctrl+C to cancel)
pause

REM Start the dashboard in a new window
start "Dashboard (WebSocket)" cmd /k "python src\modbus_dashboard.py data.csv --websocket ws://localhost:8765"

echo.
echo ==========================================================
echo WebSocket Integration Test Setup Complete!
echo ==========================================================
echo.
echo Running processes:
echo - Modbus Logger: COM3 with WebSocket server on port 8765
echo - Dashboard: Connected to WebSocket for real-time updates
echo.
echo Next Steps:
echo 1. Verify data is flowing between logger and dashboard
echo 2. Check for any connection errors or data issues
echo 3. Test reconnection by stopping/starting components
echo.
echo Press any key to run additional connection tests...
pause

echo.
echo Running quick connection test...
python test_websocket_integration.py --url ws://localhost:8765 --quick

echo.
echo Running load test with 3 clients...
python test_websocket_integration.py --url ws://localhost:8765 --load-test --clients 3 --duration 10

echo.
echo ==========================================================
echo Test complete! Check the running windows for live data.
echo Press any key to exit...
pause