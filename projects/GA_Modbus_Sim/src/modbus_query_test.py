#!/usr/bin/env python3
"""
GA Modbus Python Application for reading and logging data from Modbus devices
"""
import csv
import os
import time
from datetime import datetime
import logging
import sys
import argparse

# Import Modbus libraries
from pymodbus.client import ModbusSerialClient  # Updated API import for pymodbus 3.x
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from pymodbus import logging as pymodbus_logging

# Import tomli for TOML config
import tomli

# Import Serial libraries with proper error handling
try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Error: PySerial not installed. Please install it with: pip install pyserial")
    sys.exit(1)

# Import custom modules
try:
    from .ga_modbus_csv_writer import write_modbus_data_to_csv
    from .core.balance_detector import BalanceDetector
except ImportError:
    # Fallback if custom module isn't available
    def write_modbus_data_to_csv(data, filename):
        """Fallback function if the module is not available"""
        log_to_csv(data, filename)
    
    class BalanceDetector:
        """Fallback balance detector if module is not available"""
        def __init__(self, config):
            self.enabled = False
        def update(self, data):
            return None
        def get_active_event(self):
            return None

# Configure logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Register map for Modbus registers
register_map = {
    10: "afe_cell_volt1",
    11: "afe_cell_volt2",
    12: "afe_cell_volt3",
    13: "afe_cell_volt4",
    14: "afe_cell_volt5",
    15: "afe_cell_volt6",
    16: "afe_cell_volt7",
    17: "afe_cell_volt8",
    18: "afe_pack_volt",
    19: "afe_cell_volt_delta",
    20: "afe_temp1",
    21: "afe_temp2",
    22: "afe_current",
    23: "afe_adc_gain",
    24: "afe_adc_offset",
    25: "afe_ov_limit",
    26: "afe_uv_limit",
    27: "fg_state_of_charge",
    28: "fg_voltage",
    29: "fg_current",
    30: "fg_temperature",
    31: "fg_remaining_capacity",
    32: "fg_full_charge_cap",
    33: "fg_design_capacity",
    34: "fg_average_current",
    35: "fg_time_to_empty",
    36: "fg_time_to_full",
    37: "fg_internal_temp",
    38: "fg_cycle_count",
    39: "fg_state_of_health",
    40: "fg_charging_voltage",
    41: "fg_charging_current",
    42: "fg_lifetime_max_temp",
    43: "fg_lifetime_min_temp",
    44: "fg_lifetime_max_chg",
    45: "fg_lifetime_max_dsg"
}

# Number of registers
num_registers = len(register_map)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="GA Modbus Python Application for reading and logging data from Modbus devices",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--port",
        help="Serial port to use (e.g., COM3). If not specified, will auto-detect.",
        default=None
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        help="Baud rate for serial communication (default: 9600)",
        default=9600
    )
    parser.add_argument(
        "--parity",
        choices=['N', 'E', 'O'],
        help="Parity setting (N=None, E=Even, O=Odd) (default: E)",
        default='E'
    )
    parser.add_argument(
        "--stopbits",
        type=int,
        help="Number of stop bits (default: 1)",
        default=1
    )
    parser.add_argument(
        "--bytesize",
        type=int,
        help="Number of data bits (default: 8)",
        default=8
    )
    parser.add_argument(
        "--slave-id",
        type=int,
        help="Modbus slave ID (default: 1)",
        default=1
    )
    parser.add_argument(
        "--interval",
        type=float,
        help="Query interval in seconds (default: 0.5)",
        default=0.5
    )
    parser.add_argument(
        "--output",
        help="Output CSV file path. If not specified, will use timestamp-based name in log directory.",
        default=None
    )
    parser.add_argument(
        "--list-ports",
        action="store_true",
        help="List available serial ports and exit"
    )
    return parser.parse_args()

def list_available_serial_ports():
    """List all available serial ports on the system"""
    try:
        ports = list(serial.tools.list_ports.comports())
        if not ports:
            print("No serial ports found.")
            return []

        print("Available serial ports:")
        for i, port in enumerate(ports):
            print(f"  {i+1}. {port.device} - {port.description}")

        return [port.device for port in ports]
    except Exception as e:
        print(f"Error listing serial ports: {e}")
        return []

def parse_id_registers(start_register, values):
    """Parse register values into named parameters"""
    mapped_values = {}
    for i, value in enumerate(values):
        register_address = start_register + i
        parameter_name = register_map.get(register_address, f"Unknown Register {register_address}")
        mapped_values[parameter_name] = value
        print(f"{parameter_name}: {value}")
    return mapped_values

def load_config():
    """Load configuration from the TOML file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(script_dir), 'config.toml')
    try:
        with open(config_path, 'rb') as f:
            config = tomli.load(f)
        # Convert relative path to absolute
        config['output_path'] = os.path.join(script_dir, config['output_path'])
        return config
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        # Return default configuration
        return {
            'output_path': os.path.join(script_dir, 'log'),
            'modbus': {
                'port': 'COM3',
                'baudrate': 9600,
                'parity': 'E',
                'stopbits': 1,
                'bytesize': 8,
                'slave_id': 1,
                'query_interval': 0.5
            }
        }

def ensure_log_directory(output_path):
    """Create log directory if it doesn't exist"""
    os.makedirs(output_path, exist_ok=True)
    return output_path

def log_to_csv(mapped_data, csv_filename):
    """Log the Modbus data to a CSV file"""
    if not csv_filename:
        config = load_config()
        csv_filename = os.path.join(config['output_path'],
                                   f"modbus_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Ensure directory exists
    os.makedirs(os.path.dirname(csv_filename), exist_ok=True)

    write_header = not os.path.exists(csv_filename)
    with open(csv_filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            header = ['Timestamp'] + list(register_map.values())
            writer.writerow(header)

        row_data = [timestamp]
        for reg_addr in range(10, 10 + num_registers):
            row_data.append(mapped_data.get(register_map.get(reg_addr, ''), ''))

        writer.writerow(row_data)

    return csv_filename

def cleanup_port(port):
    """Attempt to clean up and release a serial port"""
    try:
        # Try to open and close the port to force a release
        test_client = serial.Serial(port)
        test_client.close()
    except:
        pass

def read_battery_registers(csv_filename=None, port=None, baudrate=9600, parity='E', stopbits=1, bytesize=8, slave_id=1):
    """Read registers from the battery via Modbus"""
    # Check for available serial ports first
    available_ports = list_available_serial_ports()
    if not available_ports:
        print("Error: No serial ports available. Please connect a serial device and try again.")
        return None

    # Get port from arguments or config
    if not port:
        config = load_config()
        modbus_config = config.get('modbus', {})
        port = modbus_config.get('port', 'COM13')

    # Auto-detect port if empty or not specified
    if not port:
        if len(available_ports) > 0:
            port = available_ports[0]
            print(f"Auto-detected serial port: {port}")
        else:
            print("Error: No serial ports available for auto-detection.")
            return None

    # Check if configured port is available
    if port not in available_ports:
        print(f"Warning: Configured port {port} not found. Available ports: {', '.join(available_ports)}")
        if len(available_ports) > 0:
            port = available_ports[0]
            print(f"Using first available port: {port}")

    print(f"Connecting to Modbus device on {port} "
          f"(baudrate={baudrate}, parity={parity}, stopbits={stopbits}, bytesize={bytesize})")

    # Try to cleanup the port first
    cleanup_port(port)

    # Initialize Modbus client with updated API
    client = ModbusSerialClient(
        port=port,
        baudrate=baudrate,
        parity=parity,
        stopbits=stopbits,
        bytesize=bytesize,
        timeout=1,  # Add timeout
        retries=3   # Add retries
    )

    try:
        connected = client.connect()
        if not connected:
            print(f"Error: Failed to connect to {port}. Please check your serial connection.")
            cleanup_port(port)  # Try to cleanup on connection failure
            return None

        # Try reading registers
        response = client.read_input_registers(
            address=9,
            count=num_registers,
            slave=slave_id  # Use slave ID from config
        )

        if response.isError():
            print(f"Error reading Modbus registers: {response}")
        else:
            # Process response with Big Endian decoder
            values = response.registers
            converted_values = client.convert_from_registers(
                registers=values,
                data_type=client.DATATYPE.INT16,
                word_order="big"
            )
            print("Input Register Values:")
            mapped_data = parse_id_registers(10, values)
            print("\nMapped Register Values:")
            for param, value in mapped_data.items():
                print(f"{param}: {value}")

            write_modbus_data_to_csv(mapped_data, csv_filename)
            return mapped_data  # Return the data for balance detection

    except serial.SerialException as e:
        print(f"Serial error: {e}")
        print("Please check your serial connection and port settings.")
        cleanup_port(port)  # Try to cleanup on serial error
    except Exception as e:
        print(f"Error: {e}")
        cleanup_port(port)  # Try to cleanup on any error
    finally:
        client.close()

    return csv_filename

def continuous_logging(port=None, baudrate=9600, parity='E', stopbits=1, bytesize=8, slave_id=1, interval=0.5, output_file=None):
    """Continuously log battery data at regular intervals"""
    config = load_config()
    output_path = ensure_log_directory(config['output_path'])
    query_interval = interval

    current_csv = output_file or os.path.join(output_path, f"modbus_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    # Initialize balance detector
    balance_detector = BalanceDetector(config)

    print(f"Starting continuous logging every {query_interval} seconds. Press Ctrl+C to stop.")
    print(f"Logging to file: {current_csv}")
    
    if balance_detector.enabled:
        print(f"Balance detection enabled: delta_threshold={balance_detector.cell_delta_threshold_mv}mV, "
              f"current_threshold={balance_detector.current_threshold_a}A")

    # First check if serial ports are available
    available_ports = list_available_serial_ports()
    if not available_ports:
        print("Error: No serial ports available. Please connect a serial device and try again.")
        return

    retry_count = 0
    max_retries = 5  # Increased from 3 to 5
    base_delay = 0.5  # Base delay for exponential backoff

    while True:
        try:
            result = read_battery_registers(
                current_csv,
                port=port,
                baudrate=baudrate,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize,
                slave_id=slave_id
            )
            if result is None:
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"Failed to read registers after {max_retries} attempts.")
                    print("Resetting connection and retry count...")
                    retry_count = 0
                    time.sleep(5)  # Longer delay before full reset
                    continue
                
                # Calculate exponential backoff delay
                delay = min(base_delay * (2 ** (retry_count - 1)), 10)  # Cap at 10 seconds
                print(f"Retrying in {delay:.1f} seconds... (Attempt {retry_count} of {max_retries})")
                time.sleep(delay)
            else:
                retry_count = 0  # Reset retry count on success
                
                # Process balance detection if data is available
                if result and balance_detector.enabled:
                    balance_event = balance_detector.update(result)
                    active_event = balance_detector.get_active_event()
                    
                    if active_event:
                        current_a = abs(result.get('afe_current', 0.0))
                        if current_a > 1:  # Convert from mA to A if needed
                            current_a = current_a / 1000.0
                        cell_delta_mv = result.get('afe_cell_volt_delta', 0.0)
                        if cell_delta_mv < 1.0 and cell_delta_mv > 0:
                            cell_delta_mv = cell_delta_mv * 1000.0
                        
                        print(f"🔄 BALANCE ACTIVE: Current={current_a:.3f}A, Cell Delta={cell_delta_mv:.1f}mV, Duration={(datetime.now() - active_event.start_time).total_seconds():.0f}s")
                    
                    # Print completed balance events
                    if balance_event and not balance_event.active:
                        duration = (balance_event.end_time - balance_event.start_time).total_seconds()
                        reduction = balance_event.delta_reduction_mv or 0
                        print(f"✅ BALANCE COMPLETED: Duration={duration:.0f}s, Delta Reduction={reduction:.1f}mV")
                
                time.sleep(query_interval)

        except KeyboardInterrupt:
            print("\nLogging stopped by user")
            break
        except Exception as e:
            print(f"Error during logging: {e}")
            retry_count += 1
            if retry_count >= max_retries:
                print("Too many errors. Resetting connection...")
                retry_count = 0
                time.sleep(5)  # Longer delay before full reset
            else:
                delay = min(base_delay * (2 ** (retry_count - 1)), 10)
                print(f"Retrying in {delay:.1f} seconds... (Attempt {retry_count} of {max_retries})")
                time.sleep(delay)

def main():
    """Main function"""
    args = parse_arguments()
    
    # If --list-ports is specified, just list ports and exit
    if args.list_ports:
        list_available_serial_ports()
        return

    # Start continuous logging with command line arguments
    continuous_logging(
        port=args.port,
        baudrate=args.baudrate,
        parity=args.parity,
        stopbits=args.stopbits,
        bytesize=args.bytesize,
        slave_id=args.slave_id,
        interval=args.interval,
        output_file=args.output
    )

if __name__ == "__main__":
    main() 