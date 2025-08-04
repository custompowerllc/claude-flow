# 🚨 CRITICAL: Modbus BMS Simulator Register Mapping Correction

## Issue Summary

**FOUND CRITICAL DISCREPANCY**: The original simulator implementation plan specified incorrect register addresses that don't match the actual GA Modbus Python App implementation.

## ❌ Original (Incorrect) Register Mapping

The implementation plan incorrectly specified:
```python
# WRONG - Don't use these addresses!
CELL_VOLTAGES = {
    0x1000: "cell_voltage_1",    # 4096 decimal
    0x1001: "cell_voltage_2",    # 4097 decimal
    # ... etc
}
PACK_DATA = {
    0x2000: "pack_voltage",      # 8192 decimal
    0x2001: "pack_current",      # 8193 decimal
}
```

## ✅ Corrected Register Mapping (Based on Actual GA App)

From analysis of the test files, the **actual register layout** is:

```python
# CORRECT - Use these sequential addresses starting from 0!
REGISTER_MAP = {
    # Cell Voltages (mV raw values)
    0:  "afe_cell_volt1",     # Cell 1 voltage (e.g., 3456 mV)
    1:  "afe_cell_volt2",     # Cell 2 voltage (e.g., 3457 mV)
    2:  "afe_cell_volt3",     # Cell 3 voltage (e.g., 3455 mV)
    3:  "afe_cell_volt4",     # Cell 4 voltage (e.g., 3458 mV)
    4:  "afe_cell_volt5",     # Cell 5 voltage (e.g., 3454 mV)
    5:  "afe_cell_volt6",     # Cell 6 voltage (e.g., 3459 mV)
    6:  "afe_cell_volt7",     # Cell 7 voltage (e.g., 3456 mV)
    7:  "afe_cell_volt8",     # Cell 8 voltage (e.g., 3457 mV)
    
    # Pack Data
    8:  "afe_pack_volt",      # Pack voltage (e.g., 27652 mV)
    9:  "reserved_1",         # Reserved/unused
    10: "afe_temperature",    # Temperature (e.g., 255 = 25.5°C)
    11: "reserved_2",         # Reserved/unused  
    12: "afe_current",        # Pack current (e.g., 2345 mA)
    
    # Additional registers (13-29) for extended data
    13: "afe_cell_volt_delta",  # Cell voltage delta (mV)
    14: "fg_state_of_charge",   # State of charge (%)
    15: "fg_voltage",           # Fuel gauge voltage (mV)
    16: "fg_current",           # Fuel gauge current (mA)
    17: "fg_temperature",       # Fuel gauge temperature
    18: "fg_remaining_capacity", # Remaining capacity (Ah)
    19: "fg_full_charge_cap",   # Full charge capacity (Ah)
    20: "fg_design_capacity",   # Design capacity (Ah)
    21: "fg_average_current",   # Average current (mA)
    22: "fg_time_to_empty",     # Time to empty (seconds)
    23: "fg_time_to_full",      # Time to full (seconds)
    24: "fg_internal_temp",     # Internal temperature
    25: "fg_cycle_count",       # Cycle count
    26: "fg_state_of_health",   # State of health (%)
    27: "fg_charging_voltage",  # Charging voltage (mV)
    28: "fg_charging_current",  # Charging current (mA)
    29: "balance_status",       # Balance status flags
}
```

## 🔧 Data Scaling and Formats

Based on the test data analysis:

| Parameter | Raw Format | Scaling | Example |
|-----------|------------|---------|---------|
| Cell Voltages | 16-bit unsigned | Raw mV | 3456 → 3.456V |
| Pack Voltage | 16-bit unsigned | Raw mV | 27652 → 27.652V |
| Current | 16-bit signed | Raw mA | 2345 → 2.345A |
| Temperature | 16-bit unsigned | × 10 | 255 → 25.5°C |
| SOC | 16-bit unsigned | × 10 | 855 → 85.5% |

## 📡 Modbus Communication Details

From the test code analysis:
```python
# The GA Modbus App reads registers using:
client.read_input_registers(
    address=0,        # Start at register 0 (NOT 0x1000!)
    count=30,         # Read 30 consecutive registers
    slave=slave_id    # Slave device ID (default: 2)
)
```

## 🛠️ Required Implementation Changes

### 1. Update ModbusSimulator Class
```python
class ModbusSimulator:
    def __init__(self):
        self.registers = [0] * 30  # 30 registers starting from address 0
        self.register_map = REGISTER_MAP  # Use corrected mapping
    
    def handle_read_input_registers(self, request):
        start_addr = request.address
        count = request.count
        
        # Validate address range (0-29)
        if start_addr < 0 or start_addr + count > 30:
            return ModbusExceptionResponse(request.function_code, 0x02)
        
        # Return the requested register values
        values = self.registers[start_addr:start_addr + count]
        return ReadInputRegistersResponse(values)
```

### 2. Update Battery Physics Engine
```python
class BatteryPhysicsEngine:
    def update_registers(self):
        # Cell voltages (mV) - realistic 8S LiFePO4 values
        for i in range(8):
            cell_voltage_mv = int(self.cells[i].voltage * 1000)  # Convert V to mV
            self.registers[i] = cell_voltage_mv
        
        # Pack voltage (mV)
        pack_voltage_mv = int(sum(cell.voltage for cell in self.cells) * 1000)
        self.registers[8] = pack_voltage_mv
        
        # Temperature (°C × 10)
        temp_scaled = int(self.temperature * 10)
        self.registers[10] = temp_scaled
        
        # Current (mA) - signed value
        current_ma = int(self.current * 1000)
        self.registers[12] = current_ma if current_ma >= 0 else (65536 + current_ma)  # Handle negative
```

### 3. Update Configuration Files
```yaml
# config/default.yaml
modbus:
  start_address: 0      # Start at register 0 (NOT 0x1000)
  register_count: 30    # Read 30 consecutive registers
  function_code: 4      # Read Input Registers (0x04)
  
battery:
  cell_count: 8
  voltage_range:
    min_mv: 2500        # 2.5V minimum per cell
    max_mv: 3650        # 3.65V maximum per cell
    nominal_mv: 3200    # 3.2V nominal per cell
```

## 🧪 Updated Test Scenarios

### Realistic 8S LiFePO4 Values
```python
# Normal operation scenario
NORMAL_OPERATION = {
    "registers": [
        3280, 3285, 3282, 3287, 3279, 3284, 3281, 3286,  # Cell voltages (mV)
        26264,  # Pack voltage (8 × 3.283V avg = 26.264V)
        0,      # Reserved
        275,    # Temperature (27.5°C)
        0,      # Reserved
        -5000,  # Current (-5.0A discharge)
        # ... additional registers
    ]
}

# Charging scenario
CHARGING_SCENARIO = {
    "registers": [
        3450, 3455, 3452, 3457, 3449, 3454, 3451, 3456,  # Higher cell voltages
        27624,  # Pack voltage (27.624V)
        0,      # Reserved
        285,    # Temperature (28.5°C - slightly higher during charge)
        0,      # Reserved
        3000,   # Current (+3.0A charge)
        # ... additional registers
    ]
}
```

## ⚠️ Critical Action Items

1. **IMMEDIATELY** update the implementation plan document
2. **REVISE** all register addressing from 0x1000+ to 0+
3. **VALIDATE** compatibility with actual GA Modbus App
4. **TEST** with real GA app before proceeding with development
5. **DOCUMENT** the exact communication protocol used

## 📞 Verification Required

**BEFORE implementing the simulator**, we must:

1. ✅ Confirm the exact register layout with the GA Modbus App team
2. ✅ Test actual Modbus communication with a real BMS device
3. ✅ Validate data scaling factors and formats
4. ✅ Verify slave ID, function codes, and timing requirements

---

**⚠️ WARNING**: Do not proceed with simulator development using the original 0x1000+ register addresses. The simulator MUST use sequential registers starting from address 0 to be compatible with the GA Modbus Python App.