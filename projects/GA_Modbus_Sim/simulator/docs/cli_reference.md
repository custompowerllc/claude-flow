# GA Modbus Simulator - CLI Reference

## Overview

The GA Modbus BMS Simulator provides a comprehensive command-line interface for configuration and operation. This reference covers all available options and their usage.

## Basic Usage

```bash
python3 run_simulator.py [OPTIONS]
```

## Command Categories

### Utility Commands

Commands for system information and discovery.

#### `--list-ports`

Lists all available serial ports on the system.

**Usage:**
```bash
python3 run_simulator.py --list-ports
```

**Output:**
```
Available Serial Ports:
==================================================
Port            Description              Hardware ID
COM3           Silicon Labs CP210x      USB VID:PID=10C4:EA60
COM4           USB Serial Port          USB VID:PID=0403:6001
COM5           Bluetooth Serial         BTHENUM\{...}

Recommendations:
  • Use COM4 or COM5 for simulation (COM3 may have real GA device)
  • Prefer USB-to-Serial adapters for reliability
  • Avoid Bluetooth ports for high-speed communication
```

**Details:**
- Shows port name, description, and hardware ID
- Identifies potential conflicts with real GA devices
- Provides recommendations for optimal port selection
- Cross-platform compatible (Windows COM, Linux /dev/tty*, macOS /dev/cu.*)

#### `--list-scenarios`

Lists all available battery simulation scenarios.

**Usage:**
```bash
python3 run_simulator.py --list-scenarios
```

**Output:**
```
Available Battery Scenarios:
==================================================
1. Idle - Balanced
   State: idle
   Voltage: 3.8V
   Current: 0.0A
   SOC: 50%
   Cell Delta: 5.0mV

2. Charging - 1A
   State: charging
   Voltage: 3.9V
   Current: 1.0A
   SOC: 65%
   Cell Delta: 15.0mV
...
```

**Details:**
- Shows all predefined scenarios with key parameters
- Includes battery state, voltage, current, SOC, and cell voltage delta
- Helps select appropriate scenario for testing needs

### Server Configuration

Options for configuring the Modbus server behavior.

#### `--port PORT`

**Required**. Specifies the serial port for Modbus communication.

**Usage:**
```bash
# Windows
python3 run_simulator.py --port COM4

# Linux
python3 run_simulator.py --port /dev/ttyUSB0

# macOS
python3 run_simulator.py --port /dev/cu.usbserial-1234
```

**Details:**
- Must be a valid, available serial port
- Port availability is validated before starting
- Use `--list-ports` to find available options

#### `--baudrate RATE`

Sets the serial communication baud rate.

**Default:** `9600`

**Usage:**
```bash
python3 run_simulator.py --port COM4 --baudrate 19200
```

**Supported Values:**
- `9600` (default, matches GA BMS standard)
- `19200`
- `38400`
- `57600`
- `115200`

**Details:**
- Must match the client application's baud rate
- GA BMS devices typically use 9600 baud
- Higher rates may improve performance but reduce reliability

#### `--parity {N,E,O}`

Sets the serial parity bit configuration.

**Default:** `E` (Even)

**Usage:**
```bash
python3 run_simulator.py --port COM4 --parity N  # No parity
python3 run_simulator.py --port COM4 --parity E  # Even parity
python3 run_simulator.py --port COM4 --parity O  # Odd parity
```

**Details:**
- `E` (Even) is standard for GA BMS communication
- Must match client configuration
- Affects error detection capability

#### `--stopbits BITS`

Sets the number of stop bits.

**Default:** `1`

**Usage:**
```bash
python3 run_simulator.py --port COM4 --stopbits 1
python3 run_simulator.py --port COM4 --stopbits 2
```

**Details:**
- `1` is standard for most applications
- `2` may be required for some legacy systems
- Must match client configuration

#### `--bytesize BITS`

Sets the number of data bits per byte.

**Default:** `8`

**Usage:**
```bash
python3 run_simulator.py --port COM4 --bytesize 8
python3 run_simulator.py --port COM4 --bytesize 7
```

**Details:**
- `8` is standard for modern systems
- `7` may be required for legacy applications
- Must match client configuration

#### `--slave-id ID`

Sets the Modbus slave ID.

**Default:** `1`

**Usage:**
```bash
python3 run_simulator.py --port COM4 --slave-id 1
python3 run_simulator.py --port COM4 --slave-id 5
```

**Details:**
- Must match the slave ID expected by client
- GA BMS devices typically use ID 1
- Range: 1-247 (per Modbus specification)

### Simulation Settings

Options for controlling battery simulation behavior.

#### `--scenario NAME`

Sets the initial battery scenario.

**Default:** First available scenario (typically "Idle - Balanced")

**Usage:**
```bash
python3 run_simulator.py --port COM4 --scenario "Charging - 1A"
python3 run_simulator.py --port COM4 --scenario charging  # Partial match
```

**Available Scenarios:**
- `Idle - Balanced`
- `Charging - 1A`
- `Discharging - 2A`
- `Balancing - High Delta`
- `Low Battery`
- `Full Battery`

**Details:**
- Case-insensitive matching
- Supports partial name matching
- Use `--list-scenarios` to see all options
- Scenario can be changed during runtime (future feature)

### Logging and Debug

Options for controlling log output and debugging.

#### `--verbose`, `-v`

Enables verbose (DEBUG level) logging.

**Default:** INFO level logging

**Usage:**
```bash
python3 run_simulator.py --port COM4 --verbose
python3 run_simulator.py --port COM4 -v  # Short form
```

**Impact:**
- Shows detailed operational information
- Includes register update cycles
- Provides thread and state management details
- May impact performance during high-frequency operations

**Debug Output Example:**
```
DEBUG - Updated 36 registers
DEBUG - Updated simulation for scenario: Charging - 1A
DEBUG - Updated register afe_cell_volt1 = 3850
DEBUG - Updated register afe_pack_volt = 30800
DEBUG - Updated register afe_current = 1000
```

## Complete Examples

### Basic Startup
```bash
# Minimal configuration - start on COM4 with defaults
python3 run_simulator.py --port COM4
```

### Charging Simulation
```bash
# Simulate charging scenario with verbose logging
python3 run_simulator.py --port COM4 --scenario "Charging - 1A" --verbose
```

### High-Speed Configuration
```bash
# Higher baud rate for faster communication
python3 run_simulator.py --port COM4 --baudrate 19200 --scenario charging
```

### Custom Serial Settings
```bash
# Custom serial configuration for specific hardware
python3 run_simulator.py --port /dev/ttyUSB0 --baudrate 38400 --parity N --stopbits 2
```

### Multiple Device Simulation
```bash
# Simulate device with different slave ID
python3 run_simulator.py --port COM5 --slave-id 2 --scenario "Low Battery"
```

## Error Handling

### Common Error Messages

**Port Not Found:**
```
Error: --port is required to start the simulator
Use --list-ports to see available ports
```
*Solution: Specify a valid port with `--port`*

**Invalid Port:**
```
Port validation failed: Port COM99 not found
```
*Solution: Use `--list-ports` to find available ports*

**Port In Use:**
```
Port validation failed: Port COM3 is not available: [Errno 5] Access denied
```
*Solution: Close other applications using the port or try a different port*

**Invalid Scenario:**
```
Warning: Could not set scenario 'invalid_scenario', using default
```
*Solution: Use `--list-scenarios` to see valid options*

### Validation Behavior

The simulator performs several validation checks:

1. **Port Existence:** Verifies the specified port exists
2. **Port Availability:** Checks if the port can be opened
3. **Configuration Compatibility:** Validates serial parameters
4. **Scenario Matching:** Finds closest matching scenario name

## Integration with GA Applications

### Compatible Commands

The simulator is designed to work seamlessly with existing GA applications:

```bash
# Start simulator
python3 run_simulator.py --port COM4 --scenario charging

# In another terminal, test with GA app
cd ../src
python3 modbus_query_test.py --port COM4
python3 modbus_standalone_logger.py --port COM4 --sn SIM001 --rma 12345
```

### Port Recommendations

The simulator provides intelligent port recommendations:
- Avoids ports likely used by real GA devices
- Prefers USB-to-Serial adapters
- Considers port description and hardware ID
- Warns about potential conflicts

## Advanced Usage

### Scripting and Automation

```bash
#!/bin/bash
# Start simulator for automated testing

# Find available port
PORT=$(python3 run_simulator.py --list-ports | grep -o 'COM[0-9]' | head -1)

# Start with specific scenario
python3 run_simulator.py --port $PORT --scenario "Charging - 1A" --verbose &
SIMULATOR_PID=$!

# Run tests
python3 ../src/modbus_query_test.py --port $PORT

# Cleanup
kill $SIMULATOR_PID
```

### Configuration Files

For repeated use with specific settings, consider creating wrapper scripts:

```bash
#!/bin/bash
# charging_sim.sh - Start charging simulation
python3 run_simulator.py \
    --port COM4 \
    --scenario "Charging - 1A" \
    --baudrate 9600 \
    --verbose
```

### Docker Integration

```dockerfile
FROM python:3.9-slim

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

# Configure for container environment
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python3", "run_simulator.py"]
CMD ["--port", "/dev/ttyUSB0", "--verbose"]
```

```bash
# Run in Docker with device access
docker run --device=/dev/ttyUSB0 ga-simulator --scenario charging
```

This CLI reference provides comprehensive coverage of all available options and their practical usage in the GA Modbus BMS Simulator.