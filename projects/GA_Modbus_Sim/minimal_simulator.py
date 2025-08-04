#!/usr/bin/env python3
"""
Minimal Modbus TCP Server for Testing
Uses the built-in pymodbus simulator
"""

import asyncio
import random
import threading
import time

async def run_simulator():
    """Run the simple simulator using pymodbus built-in simulator"""
    from pymodbus.server import StartTcpServer
    
    # Create a simple context with some data
    from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext
    
    # Create input registers with initial data
    registers = ModbusSequentialDataBlock(0, [0] * 100)
    
    # Set some initial realistic BMS data at registers 10-45
    initial_data = [
        3700, 3710, 3720, 3705, 3715, 3725, 3700, 3710,  # Cell voltages 1-8 (regs 10-17)
        29640,  # Pack voltage (reg 18)
        25,     # Cell delta (reg 19)
        250, 260,  # Temperatures (regs 20-21)
        -2500,  # Current (reg 22)
        1000, 100,  # ADC gain/offset (regs 23-24)
        4200, 2800,  # OV/UV limits (regs 25-26)
        75,     # SOC (reg 27)
        29650,  # FG voltage (reg 28)
        -2450,  # FG current (reg 29)
        255,    # FG temp (reg 30)
        33750,  # Remaining capacity (reg 31)
        45000,  # Full charge capacity (reg 32)
        45000,  # Design capacity (reg 33)
        -2500,  # Avg current (reg 34)
        480, 0, # Time to empty/full (regs 35-36)
        260,    # Internal temp (reg 37)
        156,    # Cycle count (reg 38)
        96,     # SOH (reg 39)
        29640, 0,  # Charging V/I (regs 40-41)
        450, -50, 15000, 25000  # Lifetime stats (regs 42-45)
    ]
    
    # Set the data at the correct addresses
    for i, value in enumerate(initial_data):
        registers.setValues(10 + i, [value])
    
    # Create context
    context = ModbusServerContext(slaves={1: {'ir': registers}}, single=False)
    
    print("Starting minimal TCP Modbus server on port 5020")
    print("Registers 10-45 contain BMS simulation data")
    print("Connect with: python3 tcp_logger_test.py")
    
    # Start the server
    await StartTcpServer(context=context, address=("0.0.0.0", 5020))

def update_data_continuously():
    """Update register data in background"""
    # This will be a simple version that doesn't update
    # Just to show the concept works
    pass

if __name__ == "__main__":
    try:
        asyncio.run(run_simulator())
    except KeyboardInterrupt:
        print("\nServer stopped")