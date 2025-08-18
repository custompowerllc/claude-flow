# Test Data Injection - Step by Step

## Step 1: Add Test Data Inject Node

1. **Open Node-RED Editor**: http://localhost:1880
2. **From the left palette**, drag an **"inject"** node onto the canvas
3. **Double-click the inject node** to configure it

## Step 2: Configure the Inject Node

**Set these values exactly:**

- **Name**: `Test Modbus Data`
- **Repeat**: `none` (single injection)
- **Payload dropdown**: Change to **"JSON"**
- **JSON field**: Paste this exact JSON:

```json
{
  "input_registers": {
    "fg_voltage": 12.5,
    "fg_current": 2.3,
    "fg_design_capacity": 100,
    "fg_remaining_capacity": 85,
    "fg_full_charge_capacity": 100,
    "fg_state_of_charge": 85,
    "fg_temperature": 25,
    "fg_charge_cycle": 50,
    "fg_state_of_health": 95,
    "afe_chip_status": 1,
    "afe_fet_status": 1,
    "afe_pack_volt": 12.4,
    "afe_current": 2.2,
    "afe_temperature": 26,
    "afe_cell_volt_1": 3.1,
    "afe_cell_volt_2": 3.2,
    "afe_cell_volt_3": 3.1,
    "afe_cell_volt_4": 3.2,
    "afe_cell_volt_5": 3.0,
    "afe_cell_volt_6": 3.1
  },
  "coils": {
    "charge_discharge_enable": true,
    "chg_enable": true,
    "dsg_enable": false
  },
  "timestamp": "2025-08-18T11:36:00.000Z"
}
```

## Step 3: Connect and Test

1. **Click "Done"** to save the inject node
2. **Drag a wire** from the **inject node output** to the **"Format CSV Data" node input**
3. **Click "Deploy"** (red button top right)
4. **Click the blue button** on the left side of the inject node to fire it

## Step 4: Check Results

After clicking the inject button:

1. **Check the debug panel** (right sidebar) for:
   - "CSV formatter config check" warning
   - Any error messages
   
2. **Check the CSV file**:
   ```bash
   tail -3 /home/ahu/development/claude-flow/projects/nodered/logs/modbus_data.csv
   ```

## Expected Success:
- ✅ New data row in CSV file with test values
- ✅ Debug messages showing data processing
- ✅ No error messages

## If It Works:
You'll see a new row in the CSV with the test data values, proving the entire CSV pipeline works perfectly!

## If It Doesn't Work:
We'll see specific error messages in the debug panel to troubleshoot further.

This test bypasses all Modbus complexity and directly tests your CSV formatter and file writer.