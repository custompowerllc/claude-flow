# GA BMS Modbus Logger for Node-RED

This Node-RED flow replicates the functionality of the `modbus_standalone_logger.py` Python script, providing a visual, flow-based approach to logging GA BMS (Battery Management System) data via Modbus RTU.

## Features

- **Complete Modbus Register Reading**:
  - Input Registers (10-69): Battery voltage, current, temperature, cell voltages
  - Coil Registers (10-24): Charge/discharge status flags  
  - AFE Status Registers (8-87): AFE chip status information
  - FG Status Registers (104-183): Fuel gauge status data
  - AFE Config Registers (88-103): AFE configuration settings

- **Data Scaling & Processing**:
  - Voltage conversion: mV to V
  - Current scaling with signed 16-bit handling
  - FG current calibration (504.2 units/amp)
  - Temperature scaling for different ranges

- **CSV Logging**:
  - Automatic filename generation with timestamp-serial-RMA format
  - Configurable output directory
  - Extended register logging can be enabled/disabled
  - Real-time data display in debug panel

## Installation

1. Ensure Node-RED is installed with the required dependencies:
```bash
cd projects/nodered
npm install
```

2. Start Node-RED:
```bash
npm start
# or
node start-nodered.js
```

3. Open Node-RED in your browser (default: http://localhost:1880)

4. The flow should automatically load. If not, import the `flows.json` file.

## Configuration

### Serial Port Setup

1. Double-click the "GA BMS Modbus RTU" configuration node
2. Update the serial port settings:
   - **Serial Port**: Your COM port (e.g., `/dev/ttyUSB0`, `COM3`)
   - **Baud Rate**: 9600 (default)
   - **Data Bits**: 8
   - **Stop Bits**: 1
   - **Parity**: Even
   - **Slave ID**: 1 (default)

### Logger Configuration

Click the "Initialize Configuration" inject node to set default values, or update them manually:

- **Serial Number**: Battery pack serial number (e.g., "0573")
- **RMA Number**: RMA tracking number (e.g., "8765")
- **Output Path**: Directory for CSV files (default: "./logs")
- **Read Extended**: Enable/disable extended register reading
- **Slave ID**: Modbus slave address (default: 1)

## Usage

### Starting Data Logging

1. Ensure configuration is initialized (click "Initialize Configuration")
2. Update configuration values as needed
3. Click "Start Logging" to begin data collection
4. Data will be logged every 500ms to a CSV file
5. Monitor progress in the debug panel

### Stopping Data Logging

1. Click "Stop Logging" to stop data collection
2. The flow will display total records logged and duration

### CSV File Format

Files are saved with the naming convention:
```
YYYYMMDD_HHMMSS-[serial_number]-[rma_number].csv
```

Example: `20250118_143022-0573-8765.csv`

### CSV Columns

The CSV file contains the following columns:

**Basic Registers (always included):**
- Timestamp
- fg_voltage through P13_temperature (60 input registers)

**Extended Registers (when enabled):**
- Coil registers (15 boolean values as 0/1)
- AFE status registers (10 hex values)
- FG status registers (10 hex values)
- AFE config registers (2 hex values)

## Data Flow Description

1. **Timer (500ms)**: Triggers polling cycle
2. **Check Logging Status**: Only proceeds if logging is enabled
3. **Read Input Registers**: Function Code 4, addresses 10-69
4. **Process & Scale Data**: Applies proper scaling to raw values
5. **Read Extended Registers** (if enabled):
   - Coils (FC 1): Addresses 10-24
   - AFE Status (FC 2): Addresses 8-87
   - FG Status (FC 2): Addresses 104-183
   - AFE Config (FC 2): Addresses 88-103
6. **Format CSV**: Combines all data into CSV row
7. **Write to File**: Appends data to CSV file
8. **Display Status**: Shows live data and record count

## Troubleshooting

### Common Issues

1. **"Port not found" error**:
   - Verify serial port is connected
   - Check port name in configuration
   - Ensure user has permissions for serial port access

2. **No data being read**:
   - Verify Modbus device is powered and connected
   - Check baud rate and parity settings
   - Confirm slave ID matches device configuration

3. **CSV file not created**:
   - Ensure output directory exists or can be created
   - Check file system permissions
   - Verify disk space is available

### Debug Options

- Enable debug output on Modbus nodes to see raw communication
- Check "Live Data" debug node for parsed values
- Monitor "Modbus Errors" debug node for communication issues

## Differences from Python Implementation

While this Node-RED flow replicates the core functionality of `modbus_standalone_logger.py`, there are some differences:

1. **Visual Configuration**: Settings are configured through Node-RED UI instead of command-line arguments
2. **No Moving Average Filter**: The cell delta spike filtering is not implemented (can be added if needed)
3. **No WebSocket Support**: WebSocket streaming is not included (can be added with websocket nodes)
4. **No History Tracking**: Previous sessions are not stored (can be added with file storage)

## Extending the Flow

### Adding Moving Average Filter

To add cell delta spike filtering:
1. Add a function node after "Process Input Registers"
2. Implement moving average logic for `afe_cell_volt_delta`
3. Store history in flow context

### Adding WebSocket Support

To stream data via WebSocket:
1. Install `node-red-contrib-websocket`
2. Add websocket out node after CSV formatter
3. Configure WebSocket server endpoint

### Adding Dashboard

To create a real-time dashboard:
1. Install `node-red-dashboard`
2. Add gauge/chart nodes for key parameters
3. Connect to processed data flow

## Performance Notes

- The flow polls every 500ms by default (adjustable in timer node)
- Extended register reading adds ~4 additional Modbus transactions
- CSV writing is append-only for efficiency
- Consider increasing poll interval for long-term logging

## Support

For issues or questions about the Modbus protocol implementation, refer to the original Python source:
`projects/GA_Modbus_Python_App/src/modbus_standalone_logger.py`