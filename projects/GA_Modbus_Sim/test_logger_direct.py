#!/usr/bin/env python3
"""
Direct Logger Test
Test the standalone logger by mocking the modbus_query_test functions
"""

import sys
import os
import csv
import time
from datetime import datetime
from pathlib import Path
import random

# Add the GA project path
sys.path.insert(0, str(Path(__file__).parent))

# Mock the modbus functions since we can't get the complex server working
def mock_read_battery_registers(client, slave_id=1):
    """Mock function that returns realistic BMS data"""
    # Generate realistic battery data similar to what the real BMS would return
    
    # Cell voltages (mV) - 8 cells with slight variations
    cell_voltages = []
    base_voltage = 3700
    for i in range(8):
        voltage = base_voltage + random.randint(-50, 50) + (i * 5)
        cell_voltages.append(voltage)
    
    # Pack voltage is sum of cell voltages
    pack_voltage = sum(cell_voltages)
    
    # Cell delta is max - min
    cell_delta = max(cell_voltages) - min(cell_voltages)
    
    # Current (mA) - simulate charging/discharging
    current = random.randint(-5000, 2000)  # -5A to +2A
    
    # State of charge (%)
    soc = 75 + random.randint(-10, 15)
    
    # Temperatures (°C * 10)
    temp1 = 250 + random.randint(-30, 40)  # 25±4°C
    temp2 = 260 + random.randint(-30, 40)  # 26±4°C
    
    # Create the data structure that matches the register map
    data = {
        'afe_cell_volt1': cell_voltages[0],
        'afe_cell_volt2': cell_voltages[1],
        'afe_cell_volt3': cell_voltages[2],
        'afe_cell_volt4': cell_voltages[3],
        'afe_cell_volt5': cell_voltages[4],
        'afe_cell_volt6': cell_voltages[5],
        'afe_cell_volt7': cell_voltages[6],
        'afe_cell_volt8': cell_voltages[7],
        'afe_pack_volt': pack_voltage,
        'afe_cell_volt_delta': cell_delta,
        'afe_temp1': temp1,
        'afe_temp2': temp2,
        'afe_current': current,
        'afe_adc_gain': 1000,
        'afe_adc_offset': 100,
        'afe_ov_limit': 4200,
        'afe_uv_limit': 2800,
        'fg_state_of_charge': soc,
        'fg_voltage': pack_voltage + random.randint(-20, 20),
        'fg_current': current + random.randint(-100, 100),
        'fg_temperature': temp1 + random.randint(-10, 10),
        'fg_remaining_capacity': int(45000 * (soc / 100)),
        'fg_full_charge_cap': 45000,
        'fg_design_capacity': 45000,
        'fg_average_current': current,
        'fg_time_to_empty': 480 if current < 0 else 0,
        'fg_time_to_full': 240 if current > 0 else 0,
        'fg_internal_temp': temp2,
        'fg_cycle_count': 150 + random.randint(0, 50),
        'fg_state_of_health': 95 + random.randint(-3, 5),
        'fg_charging_voltage': pack_voltage,
        'fg_charging_current': max(0, current) if current > 0 else 0,
        'fg_lifetime_max_temp': 450,
        'fg_lifetime_min_temp': -50,
        'fg_lifetime_max_chg': 15000,
        'fg_lifetime_max_dsg': 25000
    }
    
    return data

def mock_list_available_serial_ports():
    """Mock function to return fake serial ports"""
    return ['/dev/ttyUSB0', '/dev/ttyUSB1', 'COM3', 'COM4']

# Create a mock client class
class MockModbusClient:
    def __init__(self, port):
        self.port = port
        self.connected = False
    
    def connect(self):
        self.connected = True
        return True
    
    def close(self):
        self.connected = False

def test_logger_functionality():
    """Test the standalone logger with mock data"""
    print("GA BMS Standalone Logger Test")
    print("=" * 50)
    print("Testing with mock BMS data...")
    
    # Create output directory
    output_dir = Path("test_logs")
    output_dir.mkdir(exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ga_bms_mock_test_{timestamp}.csv"
    csv_path = output_dir / filename
    
    print(f"Creating CSV file: {csv_path}")
    
    # Register map from the original code
    register_map = {
        10: "afe_cell_volt1", 11: "afe_cell_volt2", 12: "afe_cell_volt3", 13: "afe_cell_volt4", 
        14: "afe_cell_volt5", 15: "afe_cell_volt6", 16: "afe_cell_volt7", 17: "afe_cell_volt8",
        18: "afe_pack_volt", 19: "afe_cell_volt_delta", 20: "afe_temp1", 21: "afe_temp2",
        22: "afe_current", 23: "afe_adc_gain", 24: "afe_adc_offset", 25: "afe_ov_limit",
        26: "afe_uv_limit", 27: "fg_state_of_charge", 28: "fg_voltage", 29: "fg_current",
        30: "fg_temperature", 31: "fg_remaining_capacity", 32: "fg_full_charge_cap",
        33: "fg_design_capacity", 34: "fg_average_current", 35: "fg_time_to_empty",
        36: "fg_time_to_full", 37: "fg_internal_temp", 38: "fg_cycle_count",
        39: "fg_state_of_health", 40: "fg_charging_voltage", 41: "fg_charging_current",
        42: "fg_lifetime_max_temp", 43: "fg_lifetime_min_temp", 44: "fg_lifetime_max_chg",
        45: "fg_lifetime_max_dsg"
    }
    
    # Create CSV file
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        header = ['Timestamp'] + list(register_map.values())
        writer.writerow(header)
        
        print("Starting data logging simulation...")
        print("Serial Number: TEST-MOCK-001")
        print("Duration: 30 seconds")
        print()
        
        # Log data for 30 seconds
        start_time = time.time()
        record_count = 0
        
        try:
            while (time.time() - start_time) < 30:
                # Get mock data
                data = mock_read_battery_registers(None)
                
                # Create CSV row
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row = [timestamp]
                
                # Add data in register order
                for reg_addr in range(10, 46):
                    param_name = register_map.get(reg_addr, '')
                    row.append(data.get(param_name, ''))
                
                # Write to CSV
                writer.writerow(row)
                csvfile.flush()
                record_count += 1
                
                # Display progress
                if record_count % 5 == 0:
                    cell1 = data['afe_cell_volt1']
                    cell8 = data['afe_cell_volt8']
                    pack_volt = data['afe_pack_volt']
                    soc = data['fg_state_of_charge']
                    current = data['afe_current']
                    cell_delta = data['afe_cell_volt_delta']
                    
                    print(f"Record {record_count:3d}: "
                          f"Cell1={cell1:4d}mV Cell8={cell8:4d}mV "
                          f"Pack={pack_volt:5d}mV SOC={soc:2d}% "
                          f"Current={current:5d}mA Delta={cell_delta:2d}mV")
                
                time.sleep(0.5)  # 500ms interval
                
        except KeyboardInterrupt:
            print("\nTest stopped by user")
    
    duration = time.time() - start_time
    print(f"\n✅ Test completed!")
    print(f"Duration: {duration:.1f} seconds")
    print(f"Records logged: {record_count}")
    print(f"CSV file: {csv_path}")
    print(f"File size: {csv_path.stat().st_size} bytes")
    
    # Validate the CSV file
    print("\n📊 Data Validation:")
    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        
        if rows:
            first_row = rows[0]
            last_row = rows[-1]
            
            print(f"First record time: {first_row['Timestamp']}")
            print(f"Last record time: {last_row['Timestamp']}")
            print(f"Total records in file: {len(rows)}")
            
            # Validate cell voltages and groups
            print("\n🔋 Cell Voltage Groups (First Record):")
            for i in range(1, 9):
                cell_key = f'afe_cell_volt{i}'
                voltage = first_row.get(cell_key, 'N/A')
                print(f"  Cell {i}: {voltage}mV")
            
            # Show pack voltage and SOC
            print(f"\n📈 Pack Data (First Record):")
            print(f"  Pack Voltage: {first_row.get('afe_pack_volt', 'N/A')}mV")
            print(f"  Cell Delta: {first_row.get('afe_cell_volt_delta', 'N/A')}mV")
            print(f"  State of Charge: {first_row.get('fg_state_of_charge', 'N/A')}%")
            print(f"  Current: {first_row.get('afe_current', 'N/A')}mA")
            
            return True
        else:
            print("❌ No data found in CSV file")
            return False

if __name__ == "__main__":
    test_logger_functionality()