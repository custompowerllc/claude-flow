# WebSocket Integration Test Script for COM3
# PowerShell version for better cross-platform support

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "WebSocket Integration Test Script for COM3" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# Set the COM port for testing
$COM_PORT = "COM3"
$SERIAL_NUMBER = "test-device"
$RMA_NUMBER = "ws-test"

Write-Host "Step 1: Starting Modbus Logger with WebSocket enabled on $COM_PORT" -ForegroundColor Yellow
Write-Host "Command: python src\modbus_standalone_logger.py --port $COM_PORT --websocket-enabled --serial-number $SERIAL_NUMBER --rma-number $RMA_NUMBER" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Enter to start the logger (or Ctrl+C to cancel)" -ForegroundColor Green
Read-Host

# Start the logger in a new window
Start-Process -FilePath "cmd" -ArgumentList "/k", "python src\modbus_standalone_logger.py --port $COM_PORT --websocket-enabled --serial-number $SERIAL_NUMBER --rma-number $RMA_NUMBER" -WindowStyle Normal

Write-Host ""
Write-Host "Waiting 5 seconds for logger to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Step 2: Testing WebSocket connection" -ForegroundColor Yellow
Write-Host "Running comprehensive WebSocket test..." -ForegroundColor Gray
try {
    python test_websocket_integration.py --url ws://localhost:8765 --duration 30
} catch {
    Write-Host "WebSocket test failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 3: Starting Dashboard with WebSocket integration" -ForegroundColor Yellow
Write-Host "Command: python src\modbus_dashboard.py data.csv --websocket ws://localhost:8765" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Enter to start the dashboard (or Ctrl+C to cancel)" -ForegroundColor Green
Read-Host

# Start the dashboard in a new window
Start-Process -FilePath "cmd" -ArgumentList "/k", "python src\modbus_dashboard.py data.csv --websocket ws://localhost:8765" -WindowStyle Normal

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "WebSocket Integration Test Setup Complete!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Running processes:" -ForegroundColor Cyan
Write-Host "- Modbus Logger: COM3 with WebSocket server on port 8765" -ForegroundColor White
Write-Host "- Dashboard: Connected to WebSocket for real-time updates" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Verify data is flowing between logger and dashboard" -ForegroundColor White
Write-Host "2. Check for any connection errors or data issues" -ForegroundColor White
Write-Host "3. Test reconnection by stopping/starting components" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to run additional connection tests..." -ForegroundColor Green
Read-Host

Write-Host ""
Write-Host "Running quick connection test..." -ForegroundColor Yellow
try {
    python test_websocket_integration.py --url ws://localhost:8765 --quick
} catch {
    Write-Host "Quick test failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Running load test with 3 clients..." -ForegroundColor Yellow
try {
    python test_websocket_integration.py --url ws://localhost:8765 --load-test --clients 3 --duration 10
} catch {
    Write-Host "Load test failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Test complete! Check the running windows for live data." -ForegroundColor Green
Write-Host "Press any key to exit..." -ForegroundColor Cyan
Read-Host