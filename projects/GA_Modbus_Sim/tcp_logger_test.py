#!/usr/bin/env python3
"""
TCP Modbus Logger Test
A simple test script to demonstrate logging from TCP Modbus server
"""

import time
import csv
import json
from datetime import datetime
from pathlib import Path
from pymodbus.client import ModbusTcpClient

# Register map from the original application
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

class TCPModbusLogger:
    """Simple TCP Modbus logger for testing"""
    
    def __init__(self, host='127.0.0.1', port=5020):
        self.host = host
        self.port = port
        self.client = None
        self.csv_file = None
        self.csv_writer = None
        self.record_count = 0
        
    def connect(self):
        """Connect to Modbus TCP server"""
        try:
            self.client = ModbusTcpClient(host=self.host, port=self.port)
            if self.client.connect():
                print(f"✅ Connected to {self.host}:{self.port}")
                return True
            else:
                print(f"❌ Failed to connect to {self.host}:{self.port}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        if self.client:
            self.client.close()
            print("Disconnected from server")
    
    def read_data(self):
        """Read data from Modbus server"""
        if not self.client:
            return None
            
        try:
            # Read input registers starting at address 9 (to get data at registers 10-45)
            response = self.client.read_input_registers(
                address=9,
                count=36,
                device_id=1
            )
            
            if response.isError():
                print(f"Modbus read error: {response}")
                return None
            
            # Parse the data
            values = response.registers
            data = {}
            
            for i, value in enumerate(values):
                register_address = 10 + i
                parameter_name = register_map.get(register_address, f"Unknown_Register_{register_address}")
                data[parameter_name] = value
            
            return data
            
        except Exception as e:
            print(f"Error reading data: {e}")
            return None
    
    def start_logging(self, filename=None):
        """Start CSV logging"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ga_bms_test_log_{timestamp}.csv"
        
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        csv_path = logs_dir / filename
        
        try:
            self.csv_file = open(csv_path, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            
            # Write header
            header = ['Timestamp'] + list(register_map.values())
            self.csv_writer.writerow(header)
            self.csv_file.flush()
            
            print(f"✅ Started logging to: {csv_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error starting logging: {e}")
            return False
    
    def log_data_point(self):
        """Log a single data point"""
        if not self.csv_writer:
            return False
        
        data = self.read_data()
        if not data:
            return False
        
        try:
            # Prepare CSV row
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = [timestamp]
            
            # Add data in register order
            for reg_addr in range(10, 46):
                param_name = register_map.get(reg_addr, '')
                row.append(data.get(param_name, ''))
            
            # Write to CSV
            self.csv_writer.writerow(row)
            self.csv_file.flush()
            self.record_count += 1
            
            return True
            
        except Exception as e:
            print(f"Error logging data: {e}")
            return False
    
    def stop_logging(self):
        """Stop CSV logging"""
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None
            print(f"✅ Stopped logging. Total records: {self.record_count}")
    
    def run_continuous_logging(self, duration_seconds=60, interval=0.5):
        """Run continuous logging for specified duration"""
        print(f"Starting continuous logging for {duration_seconds} seconds (interval: {interval}s)")
        print("Press Ctrl+C to stop early")
        
        start_time = time.time()
        
        try:
            while (time.time() - start_time) < duration_seconds:
                if self.log_data_point():
                    # Get latest data for display
                    data = self.read_data()
                    if data:
                        cell1 = data.get('afe_cell_volt1', 0)
                        cell8 = data.get('afe_cell_volt8', 0)
                        pack_volt = data.get('afe_pack_volt', 0)
                        soc = data.get('fg_state_of_charge', 0)
                        current = data.get('afe_current', 0)
                        
                        print(f"Record {self.record_count:3d}: "
                              f"Cell1={cell1:4d}mV Cell8={cell8:4d}mV "
                              f"Pack={pack_volt:5d}mV SOC={soc:2d}% "
                              f"Current={current:5d}mA")
                else:
                    print(f"Failed to log data point {self.record_count + 1}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nLogging stopped by user")
        
        print(f"Logging completed. Duration: {time.time() - start_time:.1f}s")

def test_connection():
    """Test basic connection to server"""
    logger = TCPModbusLogger()
    
    print("Testing connection to mock server...")
    if not logger.connect():
        print("❌ Cannot connect to server. Make sure the mock server is running:")
        print("    python3 simple_test_simulator.py")
        return False
    
    # Test a single read
    print("Testing data read...")
    data = logger.read_data()
    if data:
        print("✅ Successfully read data from server")
        print("\nSample data:")
        
        # Display key parameters
        key_params = [
            'afe_cell_volt1', 'afe_cell_volt8', 'afe_pack_volt', 
            'afe_cell_volt_delta', 'fg_state_of_charge', 'afe_current'
        ]
        
        for param in key_params:
            value = data.get(param, 'N/A')
            print(f"  {param}: {value}")
        
        logger.disconnect()
        return True
    else:
        print("❌ Failed to read data")
        logger.disconnect()
        return False

def main():
    """Main test function"""
    print("GA BMS TCP Modbus Logger Test")
    print("=" * 50)
    
    # Test connection first
    if not test_connection():
        return
    
    print("\nStarting logging test...")
    logger = TCPModbusLogger()
    
    try:
        # Connect
        if not logger.connect():
            return
        
        # Start logging
        if not logger.start_logging():
            return
        
        # Run continuous logging for 30 seconds
        logger.run_continuous_logging(duration_seconds=30, interval=0.5)
        
    except Exception as e:
        print(f"Error during logging: {e}")
    finally:
        logger.stop_logging()
        logger.disconnect()
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()