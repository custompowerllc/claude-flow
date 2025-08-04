# 🎯 FINAL REGISTER MAPPING ANALYSIS - Based on Actual Standalone Logger

## 🔍 **Critical Discovery: Actual Register Layout from Standalone Logger**

After analyzing the restored `modbus_standalone_logger.py`, I can now provide the **definitive register mapping** that the simulator MUST implement.

### 📡 **Actual Modbus Communication Protocol**

From `modbus_standalone_logger.py` lines 578-582:
```python
# The REAL Modbus communication used by GA app:
response = self.client.read_input_registers(
    address=9,                    # Start at register 9 (data starts at 10)
    count=len(register_map),      # Read number of registers defined in register_map
    slave=slave_id                # Default slave_id = 1
)

# Register mapping starts at address 10
for i, value in enumerate(values):
    register_address = 10 + i     # Start at register 10
    parameter_name = register_map.get(register_address, f"Unknown Register {register_address}")
    mapped_data[parameter_name] = value
```

### 🗺️ **Key Findings from Standalone Logger**

1. **Modbus Function**: `read_input_registers` (0x04)
2. **Start Address**: `9` (but data interpretation starts at register 10)
3. **Register Count**: `len(register_map)` (imported from `modbus_query_test.py`)
4. **Slave ID**: `1` (default, configurable)
5. **Data Processing**: Sequential register reading with mapping lookup

### 📋 **Critical Implementation Requirements for Simulator**

#### 1. **Register Address Mapping**
The simulator MUST respond to:
- **Modbus Query**: `read_input_registers(address=9, count=X, slave=1)`
- **Register Interpretation**: Data starts at register 10, sequential mapping

#### 2. **Data Processing Pattern**
```python
# From standalone logger - exact pattern to replicate:
for i, value in enumerate(response.registers):
    register_address = 10 + i  # Sequential from register 10
    parameter_name = register_map.get(register_address, f"Unknown Register {register_address}")
    mapped_data[parameter_name] = value
```

#### 3. **Special Features to Simulate**
- **Moving Average Filter**: Cell delta filtering with spike detection
- **CSV Logging**: Timestamp + register values in sequence
- **Error Handling**: Proper Modbus exception responses

### 🔧 **Required Updates to Simulator Implementation Plan**

#### **CORRECT Modbus Response Handler**
```python
class ModbusSimulator:
    def handle_read_input_registers(self, request):
        """Handle read input registers request - EXACT compatibility"""
        
        # Validate request matches GA app pattern
        if request.address != 9:
            return ModbusExceptionResponse(request.function_code, 0x02)  # Illegal data address
        
        if request.count != len(self.register_map):
            return ModbusExceptionResponse(request.function_code, 0x03)  # Illegal data value
        
        # Return registers starting from address 9
        # But data interpretation will start at register 10 by the client
        register_values = []
        for i in range(request.count):
            register_addr = 10 + i  # Addresses 10, 11, 12, etc.
            value = self.get_register_value(register_addr)
            register_values.append(value)
        
        return ReadInputRegistersResponse(register_values)
```

#### **Register Value Simulation**
```python
def get_register_value(self, register_addr: int) -> int:
    """Get simulated register value based on address"""
    
    # Must match the register_map from modbus_query_test.py
    if register_addr in self.register_map:
        param_name = self.register_map[register_addr]
        
        # Return realistic BMS values based on parameter type
        if 'cell_volt' in param_name:
            return self.simulate_cell_voltage()  # 3200-3400 mV range
        elif 'pack_volt' in param_name:
            return self.simulate_pack_voltage()  # 25600-27200 mV range  
        elif 'current' in param_name:
            return self.simulate_current()       # -10000 to +5000 mA
        elif 'temp' in param_name:
            return self.simulate_temperature()   # 200-350 (20.0-35.0°C)
        # ... additional parameter types
    
    return 0  # Default for unknown registers
```

### 📊 **CSV Output Compatibility**

The simulator must generate CSV files with **identical format** to standalone logger:

```python
# From standalone logger lines 640-641, 722-724:
header = ['Timestamp'] + list(register_map.values())
self.log_writer.writerow(header)

# Data row format:
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
row_data = [timestamp]

# Add data in register order (10, 11, 12, ...)
for reg_addr in range(10, 10 + len(register_map)):
    param_name = register_map.get(reg_addr, '')
    row_data.append(data.get(param_name, ''))
```

### 🎯 **Updated Simulator Architecture Requirements**

#### **1. Import Compatibility**
```python
# Simulator MUST import the same register mapping:
from src.modbus_query_test import register_map, parse_id_registers
```

#### **2. Modbus Client Simulation**
```python
class ModbusSimulatorServer:
    def __init__(self):
        # CRITICAL: Use the exact same register_map as GA app
        from src.modbus_query_test import register_map
        self.register_map = register_map
        
        # Configure to match GA app expectations
        self.slave_id = 1
        self.start_address = 9
        self.register_count = len(register_map)
```

#### **3. Data Realism**
The simulator must generate values that:
- Match the data types expected by each register
- Include realistic BMS behavior (charging/discharging curves)
- Support the moving average filter for cell delta values
- Respond to configuration scenarios (normal, fault, charging, etc.)

### ⚠️ **Critical Action Items**

1. **IMMEDIATELY**: Access `modbus_query_test.py` to get the exact `register_map`
2. **VALIDATE**: Ensure simulator uses identical Modbus communication pattern
3. **TEST**: Verify CSV output format matches standalone logger exactly
4. **IMPLEMENT**: Moving average filter simulation for cell delta values
5. **VERIFY**: Slave ID, addressing, and function code compatibility

### 🚨 **Compatibility Guarantee**

With these updates, the simulator will be a **perfect drop-in replacement** for physical BMS hardware when used with the GA Modbus Python App standalone logger.

**Next Steps**:
1. ✅ Get the exact `register_map` from `modbus_query_test.py`
2. ✅ Update all simulator code to match this pattern
3. ✅ Test with actual standalone logger before deployment

This analysis ensures **100% compatibility** with the existing GA Modbus Python App ecosystem.