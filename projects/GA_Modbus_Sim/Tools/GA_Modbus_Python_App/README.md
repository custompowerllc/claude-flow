# GA Modbus Python Application

## Project Overview

The GA Modbus Python Application is a tool designed for reading and logging data from Modbus devices, specifically focused on battery management systems. This application communicates with battery management hardware via the Modbus RTU protocol over a serial connection, collecting various battery parameters and storing them in CSV format for analysis and monitoring.

## Key Features

- **Modbus RTU Communication**: Connects to battery management systems using the Modbus RTU protocol over serial connections
- **Automatic Port Detection**: Can automatically detect available serial ports
- **Continuous Data Logging**: Logs battery data at configurable intervals
- **Configurable Settings**: Uses TOML configuration file for easy customization
- **CSV Data Export**: Exports data in a structured CSV format with timestamps
- **Error Handling**: Includes robust error handling for serial connection issues
- **Command-line Interface**: Provides command-line arguments for flexible usage

## Battery Parameters Monitored

The application monitors a comprehensive set of battery parameters including:

- Individual cell voltages (8 cells)
- Pack voltage
- Cell voltage delta
- Temperature readings
- Current measurements
- State of Charge (SOC)
- Fuel gauge readings
- Battery capacity metrics
- Charging parameters
- Battery health indicators
- Cycle count

## Technical Architecture

### Main Components

1. **modbus_query_test.py**: The main application script that handles Modbus communication, data reading, and continuous logging
2. **ga_modbus_csv_writer.py**: Helper module for formatting and writing battery data to CSV files
3. **config.toml**: Configuration file for application settings

### Dependencies

- **pymodbus**: For Modbus RTU protocol communication
- **pyserial**: For serial port communication
- **tomli**: For parsing TOML configuration files

## Usage

### Basic Usage

```bash
python modbus_query_test.py
```

This will start continuous logging using the settings from the config.toml file.

### Command-line Options

```bash
python modbus_query_test.py --list-ports  # List available serial ports
python modbus_query_test.py --port COM3 --baudrate 9600 --interval 1.0  # Custom settings
python modbus_query_test.py --output custom_filename.csv  # Specify output file
```

### Configuration

The application can be configured by editing the `config.toml` file:

```toml
# Output settings
output_path = "log"

# Modbus settings
[modbus]
port = "COM3"
query_interval = 0.5
slave_id = 1
baudrate = 9600
parity = "E"
stopbits = 1
bytesize = 8
```

## Data Format

The application logs data in CSV format with the following columns:

- Timestamp
- Cell voltages (Cell1_V through Cell8_V)
- Pack voltage (Pack_V)
- Cell voltage delta (Cell_Delta_V)
- Temperature readings (Temp1, Temp2)
- Current
- State of Charge (SOC)
- Various fuel gauge readings (FG_Voltage, FG_Current, etc.)
- Battery health metrics

## Troubleshooting

- If no serial ports are detected, ensure your device is properly connected
- Check that the correct COM port is specified in the configuration
- Verify that the Modbus settings (baudrate, parity, etc.) match your device's requirements
- For connection issues, try the --list-ports option to see available ports

## Development

This application is designed to be extensible. The modular architecture allows for:

- Adding support for additional Modbus registers
- Implementing different data export formats
- Extending the application with visualization capabilities
- Integration with other monitoring systems

## License

[Include license information here]
