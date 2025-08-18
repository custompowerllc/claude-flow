# Test Data Injection for CSV Logging

## Problem: No Modbus Data Flowing

The CSV file shows only headers, which means the Modbus connection isn't providing data. Let's test the pipeline with simulated data.

## Quick Test Solution

### Add a Test Data Injector Node:

1. **Drag an "inject" node** from the palette to the canvas
2. **Configure the inject node**:
   - **Name**: "Test Modbus Data"
   - **Payload**: Select "JSON" 
   - **JSON payload**:
   ```json
   {
     "input_registers": {
       "fg_voltage": 12.5,
       "fg_current": 2.3,
       "fg_design_capacity": 100,
       "fg_remaining_capacity": 85,
       "fg_state_of_charge": 85,
       "fg_temperature": 25,
       "afe_pack_volt": 12.4,
       "afe_current": 2.2,
       "afe_temperature": 26,
       "afe_cell_volt_1": 3.1,
       "afe_cell_volt_2": 3.2,
       "afe_cell_volt_3": 3.1,
       "afe_cell_volt_4": 3.2
     },
     "timestamp": "2025-08-18T11:35:00Z"
   }
   ```

3. **Connect the inject node** directly to the **"Format CSV Data"** node
4. **Deploy** the flow
5. **Click the inject button** to send test data

### Expected Result:
- CSV file should get a new data row with the test values
- Debug panel should show "Logged record #1", etc.

## Alternative: Fix Modbus Serial Port

If you want real Modbus data, the issue is likely the serial port:

### Current Configuration:
- **Serial Port**: "COM3" (Windows format)

### Linux Serial Port Options:
```bash
# Check available serial devices
ls /dev/tty* | grep -E "(USB|ACM)"

# Common Linux serial ports:
/dev/ttyUSB0  # USB-to-serial adapter
/dev/ttyACM0  # Arduino/USB device
/dev/ttyS0    # Built-in serial port
```

### To Fix Modbus Configuration:
1. **Double-click the "GA BMS Modbus RTU" config node**
2. **Change Serial Port** from "COM3" to `/dev/ttyUSB0` (or whatever device you have)
3. **Deploy** and test

## Quick Diagnosis Command:
```bash
# Check if any serial devices are available
dmesg | grep -i "tty\|usb\|serial"
```

The test data injection will immediately tell us if the CSV pipeline works without Modbus complications.