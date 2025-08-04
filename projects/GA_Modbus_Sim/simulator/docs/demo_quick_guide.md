# GA Modbus Simulator - Quick Demo Guide

## 🚀 Quick Start Commands

### 1. Check System Readiness
```bash
python3 demo_phase1.py
```
**Expected**: 5/5 checks passed, "Phase 1 implementation is ready!"

### 2. List Available Ports
```bash
python3 run_simulator.py --list-ports
```
**Expected**: Shows available serial ports with GA device detection

### 3. List Battery Scenarios
```bash
python3 run_simulator.py --list-scenarios
```
**Expected**: Shows 6 scenarios (Idle, Charging, Discharging, etc.)

### 4. Start Simulator
```bash
python3 run_simulator.py --port /dev/cu.debug-console --scenario "Charging - 1A"
```
**Expected**: "✅ Simulator started successfully!" message

## 🧪 Test Commands

### Basic Functionality Test
```bash
python3 test_simulator.py
```
**Expected**: "🎉 All tests passed!" with 4/4 components validated

### Register Compatibility Test
```bash
python3 test_register_query.py
```
**Expected**: All 36 registers validated with realistic values

### Integration Test
```bash
python3 test_compatibility.py
```
**Expected**: Register mapping and scenario switching validation

## 📊 Demo Scenarios

### Scenario 1: Idle Battery
```bash
python3 run_simulator.py --port /dev/cu.debug-console --scenario "Idle - Balanced"
```
- Voltage: 3.7V per cell
- Current: 0A
- SOC: 50%

### Scenario 2: Charging Battery
```bash
python3 run_simulator.py --port /dev/cu.debug-console --scenario "Charging - 1A"
```
- Voltage: 3.8V per cell
- Current: +1A
- SOC: 60%

### Scenario 3: Discharging Battery
```bash
python3 run_simulator.py --port /dev/cu.debug-console --scenario "Discharging - 2A"
```
- Voltage: 3.6V per cell
- Current: -2A
- SOC: 40%

## 🔧 Troubleshooting

### Port Issues
```bash
# If port conflicts occur
python3 run_simulator.py --list-ports
# Use suggested safe port
```

### Testing with GA App
```bash
# From main project directory
cd ../src
python3 modbus_standalone_logger.py --port /dev/cu.debug-console --sn SIM001 --rma 12345
```

### Verbose Debugging
```bash
python3 run_simulator.py --port /dev/cu.debug-console --scenario "Charging - 1A" --verbose
```

## 📈 Expected Demo Results

### ✅ Successful Outcomes
- Simulator starts without errors
- Registers update with realistic values
- Scenarios switch properly
- Port management works correctly
- GA app compatibility confirmed

### 📊 Sample Register Values
```
afe_cell_volt1: 3694 mV    (Cell 1 voltage)
afe_pack_volt: 29599 mV    (Total pack voltage)
fg_state_of_charge: 50%    (State of charge)
afe_current: 0 mA          (Pack current)
afe_temp1: 24.9°C          (Temperature)
```

## 🎯 Demo Validation Checklist

- [ ] All dependencies installed (pymodbus, pyserial)
- [ ] Phase 1 demonstration passes all checks
- [ ] 3 serial ports detected
- [ ] 6 battery scenarios available
- [ ] Simulator starts successfully
- [ ] Register values are realistic
- [ ] Scenario switching works
- [ ] Port conflict detection works
- [ ] Clean shutdown possible

## 📝 Notes

- Use `/dev/cu.debug-console` as safe port (avoids GA device conflicts)
- All 36 registers from addresses 10-45 are supported
- Compatible with existing GA Modbus applications
- Real-time value updates every second
- Graceful shutdown with Ctrl+C

---
**Quick Guide Version**: 1.0  
**Compatible With**: GA Modbus Python App v1.0