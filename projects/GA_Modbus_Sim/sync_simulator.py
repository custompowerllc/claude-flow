#!/usr/bin/env python3
"""
Synchronous Modbus TCP Server
Simple working version for testing the logger
"""

import threading
import time
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext

def create_bms_data():
    """Create realistic BMS register data"""
    # Create input registers block (function code 4)
    registers = ModbusSequentialDataBlock(0, [0] * 100)
    
    # Set realistic BMS data at registers 10-45 (36 registers)
    bms_data = [
        3700, 3710, 3720, 3705, 3715, 3725, 3700, 3710,  # Cell voltages 1-8 (regs 10-17)
        29640,  # Pack voltage (reg 18) - sum of cells
        25,     # Cell delta (reg 19)
        250, 260,  # Temperatures (regs 20-21) 25.0°C, 26.0°C
        -2500,  # Current (reg 22) -2.5A (discharging)
        1000, 100,  # ADC gain/offset (regs 23-24)
        4200, 2800,  # OV/UV limits (regs 25-26)
        75,     # SOC (reg 27) 75%
        29650,  # FG voltage (reg 28)
        -2450,  # FG current (reg 29)
        255,    # FG temp (reg 30) 25.5°C
        33750,  # Remaining capacity (reg 31) 75% of 45Ah
        45000,  # Full charge capacity (reg 32)
        45000,  # Design capacity (reg 33)
        -2500,  # Avg current (reg 34)
        480, 0, # Time to empty/full (regs 35-36) 8hrs, 0hrs
        260,    # Internal temp (reg 37) 26.0°C
        156,    # Cycle count (reg 38)
        96,     # SOH (reg 39) 96%
        29640, 0,  # Charging V/I (regs 40-41)
        450, -50, 15000, 25000  # Lifetime stats (regs 42-45)
    ]
    
    # Set the data starting at register 10
    for i, value in enumerate(bms_data):
        registers.setValues(10 + i, [value])
    
    return registers

def data_updater(registers):
    """Update data periodically to simulate changing values"""
    counter = 0
    
    while True:
        try:
            counter += 1
            
            # Update cell voltages with small variations
            for i in range(8):  # Cells 1-8 at registers 10-17
                base_voltage = 3700 + (i * 5)  # Base voltage per cell
                variation = (counter % 20) - 10  # ±10mV variation
                new_voltage = base_voltage + variation
                registers.setValues(10 + i, [new_voltage])
            
            # Update pack voltage (sum of cells)
            pack_voltage = sum([3700 + (i * 5) + ((counter % 20) - 10) for i in range(8)])
            registers.setValues(18, [pack_voltage])
            
            # Update SOC slowly
            soc = 75 + (counter // 100) % 25  # Slowly changing SOC
            registers.setValues(27, [soc])
            
            # Update current with some variation
            current = -2500 + ((counter % 30) - 15) * 10  # ±150mA variation
            registers.setValues(22, [current])
            
            # Print status every 10 updates
            if counter % 10 == 0:
                cell1_voltage = 3700 + ((counter % 20) - 10)
                print(f"Update {counter}: Cell1={cell1_voltage}mV, Pack={pack_voltage}mV, SOC={soc}%, Current={current}mA")
            
        except Exception as e:
            print(f"Error updating data: {e}")
        
        time.sleep(0.5)  # Update every 500ms

def main():
    """Run the mock server"""
    print("Starting GA BMS Mock TCP Server")
    print("Port: 5020")
    print("Registers: 10-45 (36 registers)")
    print("Function: Read Input Registers (4)")
    
    # Create the data store
    registers = create_bms_data()
    
    # Create server context with devices dict
    context = ModbusServerContext(devices={1: registers}, single=False)
    
    # Start data updater thread
    updater_thread = threading.Thread(target=data_updater, args=(registers,))
    updater_thread.daemon = True
    updater_thread.start()
    
    print("\nServer running... Press Ctrl+C to stop")
    print("Test with: python3 tcp_logger_test.py")
    print()
    
    try:
        # Start the server
        StartTcpServer(context=context, address=("0.0.0.0", 5020))
    except KeyboardInterrupt:
        print("\nServer stopped by user")

if __name__ == "__main__":
    main()