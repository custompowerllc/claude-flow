# Debug CSV Logging Issue

## Problem: CSV File Not Being Created

The "Start Logger" shows it's running but no CSV file is created. This indicates the issue is in the data pipeline, not the file writing itself.

## Debugging Steps:

### 1. Check the Node-RED Debug Panel
Look for these specific messages in the debug sidebar:

**Expected Success Messages:**
- ✅ "CSV formatter config check: ..." (warning message)
- ✅ "Logged record #1", "Logged record #2", etc.
- ✅ No red error messages

**Problem Indicators:**
- ❌ No "Logged record #X" messages = data not reaching CSV writer
- ❌ Modbus error messages = communication problem
- ❌ "Is Logging Enabled?" not passing = logging disabled

### 2. Manual Test Steps

**Step 1: Initialize Configuration**
1. Click "Initialize Configuration" inject node
2. Check debug panel for configuration setup messages

**Step 2: Start Logging**  
1. Click "Start Logging" inject node
2. Should see: "Logging to: ./logs/[timestamp]-0000-NONE.csv"

**Step 3: Check Timer**
1. The "Poll Every 500ms" should be running automatically
2. Look for timer-related messages every 500ms

**Step 4: Check Modbus Connection**
1. Look for Modbus-related errors or timeouts
2. The serial port "COM3" might not exist on Linux

### 3. Quick Fix: Test Without Modbus

To test if the CSV writing works without Modbus:

1. **Disconnect the timer from Modbus** temporarily
2. **Connect timer directly to "Format CSV Data"**
3. **Inject test data** to see if files are created

### 4. Check File Permissions

```bash
# Check if logs directory is writable
ls -la logs/
# Check current working directory
pwd
# Check if Node-RED has write permissions
touch logs/test_write.txt && rm logs/test_write.txt
```

### 5. Alternative Logging Location

The file might be created in Node-RED's working directory instead of ./logs:

```bash
# Check Node-RED working directory
find . -name "*2025*" -type f -mtime -1
# Check if file is created in data directory
ls -la data/
```

## Most Likely Issues:

1. **Modbus not connected** (COM3 doesn't exist on Linux)
2. **Logging not actually enabled** (config.logging_enabled = false)
3. **Timer not triggering data flow**
4. **File being created in different location**

## Quick Test Commands:

```bash
# Monitor file creation in real-time
inotifywait -m logs/ &

# Check what Node-RED process is doing
ps aux | grep node-red

# Check if any CSV files are being created anywhere
find /home/ahu -name "*.csv" -mtime -1 2>/dev/null
```