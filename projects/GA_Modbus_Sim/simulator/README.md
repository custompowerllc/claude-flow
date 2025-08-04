# GA Modbus BMS Simulator

A Modbus RTU server that simulates GA BMS device responses for testing and development purposes. This simulator is 100% compatible with the existing GA Modbus applications and responds to the exact same queries.

## 🚀 Quick Start

### 1. List Available Ports
```bash
python3 run_simulator.py --list-ports
```

### 2. List Available Scenarios
```bash
python3 run_simulator.py --list-scenarios
```

### 3. Start Simulator
```bash
# Start with default scenario
python3 run_simulator.py --port /dev/cu.debug-console

# Start with specific scenario
python3 run_simulator.py --port /dev/cu.debug-console --scenario "Charging - 1A"
```

### 4. Test with GA App
Once the simulator is running, you can test it with the GA Modbus application:

```bash
# From the main project directory
cd ../src
python3 modbus_standalone_logger.py --port /dev/cu.debug-console --sn SIM001 --rma 12345
```

## 📋 Features

### ✅ Complete Compatibility
- Responds to `read_input_registers` at address 9 with count 36
- Returns all 36 registers from the original register_map
- Compatible with `modbus_query_test.py` and `modbus_standalone_logger.py`

### 🔋 Realistic Battery Simulation
- **6 predefined scenarios**: Idle, Charging, Discharging, Balancing, Low Battery, Full Battery
- **Dynamic register values**: Voltages, currents, temperatures change over time
- **Realistic behavior**: Cell voltage deltas, SOC changes, thermal effects

### 🔌 Smart Port Management
- **Auto-detection**: Finds available serial ports
- **Conflict avoidance**: Detects real GA devices and suggests safe ports
- **Cross-platform**: Works on Windows (COMx), Linux (/dev/ttyUSBx), macOS (/dev/cu.x)

### 📊 Register Coverage
All 36 registers from addresses 10-45:
- **AFE registers**: Cell voltages, pack voltage, current, temperatures
- **Fuel gauge registers**: SOC, capacity, time estimates, cycle count
- **Configuration**: ADC settings, voltage limits

## 🧪 Testing

Run the test suite to verify functionality:
```bash
python3 test_simulator.py
```

## 📖 Architecture

### Core Components

1. **ModbusSimulatorServer** (`src/core/modbus_server.py`)
   - Modbus RTU server using pymodbus
   - Handles client connections and register requests
   - Manages server lifecycle and threading

2. **RegisterHandler** (`src/core/register_handler.py`)
   - Manages register values and simulation
   - Implements realistic battery behavior
   - Supports multiple scenarios

3. **ComPortManager** (`src/utils/com_port_manager.py`)
   - Detects available serial ports
   - Identifies potential device conflicts
   - Provides port recommendations

### Register Mapping

The simulator uses the exact same register mapping as the main application:

| Address | Register Name | Description |
|---------|---------------|-------------|
| 10-17 | afe_cell_volt1-8 | Individual cell voltages (mV) |
| 18 | afe_pack_volt | Total pack voltage (mV) |
| 19 | afe_cell_volt_delta | Cell voltage delta (mV) |
| 20-21 | afe_temp1-2 | AFE temperatures (0.1°C) |
| 22 | afe_current | Pack current (mA) |
| 27 | fg_state_of_charge | State of charge (%) |
| 28 | fg_voltage | Fuel gauge voltage (mV) |
| 29 | fg_current | Fuel gauge current (mA) |
| ... | ... | (32 more registers) |

## 🔧 Configuration

### Command Line Options

```bash
python3 run_simulator.py --help
```

**Basic Options:**
- `--port`: Serial port (required)
- `--scenario`: Battery scenario name
- `--baudrate`: Baud rate (default: 9600)
- `--slave-id`: Modbus slave ID (default: 1)

**Utility Commands:**
- `--list-ports`: Show available ports
- `--list-scenarios`: Show available scenarios
- `--verbose`: Enable debug logging

### Logging Configuration

The simulator supports comprehensive logging with multiple configuration options:

**Log Levels:**
- `INFO` (default): Standard operational messages
- `DEBUG` (verbose): Detailed diagnostic information
- `WARNING`: Important alerts
- `ERROR`: Error conditions

**Logging Options:**
```bash
# Enable verbose logging (DEBUG level)
python3 run_simulator.py --port COM4 --verbose

# Standard logging (INFO level) - default
python3 run_simulator.py --port COM4
```

**Log Output Includes:**
- Server startup/shutdown events
- Port validation and status
- Register updates and simulation state changes
- Modbus query handling
- Scenario transitions
- Error conditions and diagnostics

**Log File Locations:**
- Console output (default)
- No automatic file logging (configure via logging.basicConfig if needed)

**Custom Logging Setup:**
For advanced logging configuration, modify the logging setup in `run_simulator.py`:
```python
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simulator.log'),
        logging.StreamHandler()
    ]
)
```

### Available Scenarios

1. **Idle - Balanced**: Resting state, balanced cells
2. **Charging - 1A**: Active charging at 1A
3. **Discharging - 2A**: Active discharge at 2A
4. **Balancing - High Delta**: High cell voltage delta (50mV)
5. **Low Battery**: Low SOC scenario (10%)
6. **Full Battery**: High SOC scenario (95%)

## 🛠 Development

### Adding New Scenarios

Edit `src/core/register_handler.py` and add to `get_predefined_scenarios()`:

```python
BatteryScenario(
    name="Custom Scenario",
    state=BatteryState.CHARGING,
    base_voltage=3.8,
    current=1.5,
    soc=70,
    cell_delta=0.025
)
```

### Modifying Register Behavior

The `RegisterHandler` class manages all register simulation logic. Key methods:

- `_simulate_cell_voltages()`: Cell voltage simulation
- `_simulate_current_and_soc()`: Current and SOC simulation  
- `_simulate_temperature()`: Temperature simulation
- `update_simulation()`: Main update loop

## 📦 Dependencies

```bash
pip install pymodbus pyserial
```

## 🐛 Troubleshooting

### Port Issues
- **"Port not found"**: Use `--list-ports` to see available ports
- **"Permission denied"**: Port may be in use by another application
- **"No suitable port"**: Try USB-to-Serial adapters

### Connection Issues
- **Client timeout**: Check port, baudrate, and parity settings
- **Wrong data**: Verify slave ID matches (default: 1)
- **No response**: Ensure simulator is running and port is correct

### Logging Issues
- **No log output**: Ensure logging level is appropriate for your needs
- **Too much output**: Disable verbose mode or filter specific loggers
- **Missing debug info**: Enable verbose mode with `--verbose` flag
- **Performance impact**: DEBUG logging may slow down high-frequency operations

### Common Solutions
```bash
# Check if port is available
python3 run_simulator.py --list-ports

# Test with different port
python3 run_simulator.py --port /dev/cu.usbserial-xxx --scenario idle

# Enable debug logging for troubleshooting
python3 run_simulator.py --port /dev/cu.debug-console --verbose

# Verify with GA app
cd ../src && python3 modbus_query_test.py --port /dev/cu.debug-console
```

## 📝 Phase 1 Completion Status

✅ **Core Requirements Met:**
- [x] ModbusSimulatorServer class implemented
- [x] Register_map imported from modbus_query_test.py
- [x] Handles read_input_registers at address 9 with count 36
- [x] Returns realistic register values
- [x] 100% compatible with standalone logger
- [x] COM port management and conflict detection
- [x] Multiple battery scenarios supported
- [x] Comprehensive testing suite

The Phase 1 implementation provides a solid foundation for the BMS simulator that can fully replace a real device for testing and development purposes.