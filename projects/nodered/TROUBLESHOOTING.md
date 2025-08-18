# Node-RED Modbus Logger Troubleshooting

## Current Error: `Cannot read properties of undefined (reading 'csv')`

### ✅ **FIXED ISSUES:**
1. CSV writer filename configuration ✅
2. CSV formatter payload setup ✅
3. Logs directory creation ✅

### 🔧 **STEP-BY-STEP FIX PROCESS:**

#### Step 1: Initialize the System
1. **Click "Initialize Configuration"** inject node (top-left)
2. **Wait 2 seconds**
3. **Check debug panel** for initialization message

#### Step 2: Start Logging Process
1. **Click "Start Logging"** inject node
2. **Look for green status** on "Start Logger" function node
3. **Check debug panel** for "Log Started" message

#### Step 3: Verify Data Flow
The data should flow like this:
```
Timer (500ms) → Check Logging → Read Modbus → Process Data → Format CSV → Write File
```

### 🐛 **COMMON ISSUES & SOLUTIONS:**

#### Issue 1: No Configuration
**Symptoms:** CSV formatter gets empty config
**Solution:** Click "Initialize Configuration" first

#### Issue 2: Logging Not Enabled  
**Symptoms:** Timer runs but no data flows
**Solution:** Click "Start Logging" after initialization

#### Issue 3: Modbus Connection Issues
**Symptoms:** Modbus errors in debug panel
**Solution:** 
- Update serial port (COM3, /dev/ttyUSB0, etc.)
- Check device is connected and powered
- Verify baud rate (9600) and slave ID (1)

#### Issue 4: File Permission Issues
**Symptoms:** File write errors
**Solution:** Check output directory permissions

### 🧪 **TESTING THE FIX:**

1. **Refresh Node-RED**: Press F5 in browser
2. **Deploy Changes**: Click red "Deploy" button
3. **Initialize**: Click "Initialize Configuration"
4. **Start**: Click "Start Logging"
5. **Monitor**: Watch debug panel for:
   - "Configuration initialized" 
   - "Log Started"
   - "Logged record #1", "#2", etc.

### 📁 **Expected CSV Location:**
Files should appear in:
```
/home/ahu/development/claude-flow/projects/nodered/logs/
```

With filename format:
```
YYYYMMDD_HHMMSS-SerialNumber-RMANumber.csv
```

### 🚨 **IF STILL NOT WORKING:**

Try this simple test:
1. **Double-click CSV formatter node**
2. **Add this debug line at the end:**
```javascript
node.warn("CSV Data: " + JSON.stringify({filename: msg.filename, payload: msg.payload}));
```
3. **Deploy and test**
4. **Check debug panel** for the warning message

This will show exactly what data is being sent to the file writer.