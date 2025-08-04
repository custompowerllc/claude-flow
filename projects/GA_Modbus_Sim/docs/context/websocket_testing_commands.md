# WebSocket Integration Testing Commands

## Quick Reference for WebSocket Testing

### 1. Start the Modbus Logger with WebSocket
```bash
python src/modbus_standalone_logger.py --port COM3 --websocket-enabled --serial-number 0001 --rma-number test
```

### 2. Test WebSocket Connection
```bash
# Quick connection test (5 seconds)
python test_websocket_integration.py --url ws://localhost:8765 --quick

# Comprehensive test (30 seconds)
python test_websocket_integration.py --url ws://localhost:8765 --duration 30

# Load test with multiple clients
python test_websocket_integration.py --url ws://localhost:8765 --load-test --clients 5 --duration 15
```

### 3. Start Dashboard with WebSocket
```bash
python src/modbus_dashboard.py logs/20250804_111910-0001-test.csv --websocket ws://localhost:8765
```

### 4. Debug WebSocket Issues
```bash
python debug_websocket.py
```

### 5. Automated Testing (Windows)
```bash
# Batch file
test_websocket_com3.bat

# PowerShell
.\test_websocket_com3.ps1
```

## Expected Results

### Logger Console Output (Success)
```
✓ Connected to COM3
WebSocket server started on ws://localhost:8765
✓ WebSocket server started on ws://localhost:8765
✓ Started logging to: 20250804_111910-0001-test.csv
ℹ Starting continuous logging every 0.5s. Press Ctrl+C to stop.

DEBUG: register_client called
WebSocket client connected from ('::1', 63348, 0, 0). Total clients: 1
DEBUG: Preparing welcome message...
DEBUG: Sending welcome message...
✓ Sent welcome message to client
DEBUG: Waiting for connection to close...
```

### Dashboard Status (Success)
```
🟢 WebSocket CONNECTED | Serial: 0001 | RMA: test
Records: 123 | Pack V: 26.50V | Current: -1.50A | Cell Δ: 25mV | SOC: 85%
```

### Test Results (Success)
```
✅ Test 1: Connection Test - PASS
✅ Test 2: Message Reception Test - PASS  
✅ Test 3: Data Validation Test - PASS

Performance Metrics:
- Messages per second: 2.00
- Success rate: 100.0%
- Total messages received: 60
```

## Troubleshooting Common Issues

### Issue: Connection Refused
```
❌ DEBUG: OS Error (server not running?): [Errno 10061] No connection could be made
```
**Solution:** Ensure the logger with WebSocket is running first

### Issue: No Messages Received
```
⚠ WebSocket connection closed by server
✗ No messages received during test period
```
**Solution:** Check logger console for errors, ensure Modbus device is connected

### Issue: CSV File Not Found
```
Error: CSV file not found: data.csv
```
**Solution:** Use a valid CSV file path: `logs/[latest_file].csv`

## File Locations

- **Logger:** `src/modbus_standalone_logger.py`
- **Dashboard:** `src/modbus_dashboard.py`  
- **Test Scripts:** `test_websocket_integration.py`, `debug_websocket.py`
- **CSV Files:** `logs/` directory
- **Automation:** `test_websocket_com3.bat`, `test_websocket_com3.ps1`