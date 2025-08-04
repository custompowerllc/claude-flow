#!/usr/bin/env python3
"""
Simple Mock Modbus Server for Testing GA Logger
Creates a basic TCP Modbus server for testing the standalone logger
"""

import time
import threading
import random
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusServerContext, ModbusSequentialDataBlock

class MockBMSDataGenerator:
    """Generate realistic BMS data for testing"""
    
    def __init__(self):
        # Base cell voltages (in mV)
        self.base_cell_voltage = 3700
        self.cell_count = 8
        
        # Initialize registers (36 registers starting from address 10)
        self.registers = [0] * 36
        
        # Counter for realistic data variation
        self.counter = 0
        
    def generate_data(self):
        """Generate realistic BMS data"""
        self.counter += 1
        
        # Cell voltages (registers 10-17: addresses 0-7 in our array)
        cell_voltages = []
        for i in range(8):
            # Add some realistic variation
            voltage = self.base_cell_voltage + random.randint(-50, 50) + (i * 10)
            cell_voltages.append(voltage)
            self.registers[i] = voltage
        
        # Pack voltage (register 18: address 8)
        pack_voltage = sum(cell_voltages)
        self.registers[8] = pack_voltage
        
        # Cell voltage delta (register 19: address 9)
        cell_delta = max(cell_voltages) - min(cell_voltages)
        self.registers[9] = cell_delta
        
        # Temperature sensors (registers 20-21: addresses 10-11)
        temp1 = 250 + random.randint(-20, 30)  # 25°C ± variation
        temp2 = 260 + random.randint(-20, 30)  # 26°C ± variation
        self.registers[10] = temp1
        self.registers[11] = temp2
        
        # Current (register 22: address 12)
        current = random.randint(-5000, 5000)  # ±5A
        self.registers[12] = current
        
        # AFE ADC Gain & Offset (registers 23-24: addresses 13-14)
        self.registers[13] = 1000  # ADC gain
        self.registers[14] = 100   # ADC offset
        
        # Protection limits (registers 25-26: addresses 15-16)
        self.registers[15] = 4200  # OV limit
        self.registers[16] = 2800  # UV limit
        
        # Fuel Gauge data (registers 27-45: addresses 17-35)
        soc = 50 + random.randint(-10, 10)  # State of charge
        self.registers[17] = soc
        
        # FG voltage (register 28: address 18)
        self.registers[18] = pack_voltage + random.randint(-10, 10)
        
        # FG current (register 29: address 19)
        self.registers[19] = current + random.randint(-100, 100)
        
        # FG temperature (register 30: address 20)
        self.registers[20] = temp1 + random.randint(-5, 5)
        
        # Remaining capacity (register 31: address 21)
        self.registers[21] = int(45000 * (soc / 100))
        
        # Full charge capacity (register 32: address 22)
        self.registers[22] = 45000
        
        # Design capacity (register 33: address 23)
        self.registers[23] = 45000
        
        # Average current (register 34: address 24)
        self.registers[24] = current
        
        # Time to empty/full (registers 35-36: addresses 25-26)
        self.registers[25] = 480 if current < 0 else 0  # Time to empty
        self.registers[26] = 240 if current > 0 else 0  # Time to full
        
        # Internal temp (register 37: address 27)
        self.registers[27] = temp2
        
        # Cycle count (register 38: address 28)
        self.registers[28] = 150 + (self.counter // 100)
        
        # State of health (register 39: address 29)
        self.registers[29] = 95 + random.randint(-2, 2)
        
        # Charging voltage/current (registers 40-41: addresses 30-31)
        self.registers[30] = pack_voltage
        self.registers[31] = max(0, current) if current > 0 else 0
        
        # Lifetime stats (registers 42-45: addresses 32-35)
        self.registers[32] = 450  # Max temp
        self.registers[33] = -50  # Min temp
        self.registers[34] = 15000  # Max charge current
        self.registers[35] = 25000  # Max discharge current
        
        return self.registers

def update_register_data(datastore, data_generator):
    """Continuously update register data"""
    while True:
        try:
            # Generate new data
            data = data_generator.generate_data()
            
            # Update input registers starting at address 10
            for i, value in enumerate(data):
                datastore.setValues(4, 10 + i, [value])  # Function code 4 = input registers
                
            print(f"Updated registers - Cell1: {data[0]}mV, Cell8: {data[7]}mV, Pack: {data[8]}mV, SOC: {data[17]}%")
            
        except Exception as e:
            print(f"Error updating registers: {e}")
        
        time.sleep(0.5)  # Update every 500ms

def run_mock_server(port=5020):
    """Run the mock Modbus TCP server"""
    print(f"Starting Mock BMS Modbus Server on port {port}")
    
    # Create data generator
    data_generator = MockBMSDataGenerator()
    
    # Initialize datastore with input registers
    input_registers = ModbusSequentialDataBlock(0, [0] * 100)
    
    # Create server context with just input registers
    context = ModbusServerContext(slaves={
        1: {
            'di': None,  # Discrete inputs
            'co': None,  # Coils  
            'hr': None,  # Holding registers
            'ir': input_registers  # Input registers
        }
    })
    
    # Start data update thread
    update_thread = threading.Thread(target=update_register_data, args=(input_registers, data_generator))
    update_thread.daemon = True
    update_thread.start()
    
    print("Mock server ready - connect to 127.0.0.1:5020")
    print("Register mapping:")
    print("  Registers 10-17: Cell voltages 1-8")
    print("  Register 18: Pack voltage") 
    print("  Register 19: Cell delta")
    print("  Register 27: State of charge")
    print("  And more... (36 registers total)")
    print()
    print("To test with logger:")
    print("  python3 tcp_logger_test.py")
    
    try:
        # Start server
        StartTcpServer(context=context, address=("0.0.0.0", port))
    except KeyboardInterrupt:
        print("\nServer stopped by user")

if __name__ == "__main__":
    run_mock_server()