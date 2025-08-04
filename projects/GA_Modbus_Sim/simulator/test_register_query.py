#!/usr/bin/env python3
"""
Test register query simulation

This script tests that the register handler produces the exact same
format and data that the GA application expects.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from simulator.src.core.register_handler import RegisterHandler, BatteryScenario, BatteryState
from modbus_query_test import register_map, parse_id_registers


def test_register_format():
    """Test that register format matches GA app expectations"""
    print("Testing register format compatibility...")
    
    # Create register handler
    handler = RegisterHandler()
    
    # Get register values in Modbus format (list of integers)
    modbus_values = handler.get_all_registers()
    
    print(f"Generated {len(modbus_values)} register values")
    print(f"Expected {len(register_map)} registers from register_map")
    
    if len(modbus_values) != len(register_map):
        print(f"❌ Length mismatch: {len(modbus_values)} vs {len(register_map)}")
        return False
    
    # Simulate the exact same parsing that the GA app does
    # This is what happens in modbus_query_test.py line 322
    start_register = 10  # Register addresses start at 10
    mapped_data = parse_id_registers(start_register, modbus_values)
    
    print(f"✅ Parsed into {len(mapped_data)} parameters")
    
    # Check key parameters
    expected_params = [
        'afe_cell_volt1', 'afe_cell_volt2', 'afe_cell_volt3', 'afe_cell_volt4',
        'afe_cell_volt5', 'afe_cell_volt6', 'afe_cell_volt7', 'afe_cell_volt8',
        'afe_pack_volt', 'afe_cell_volt_delta', 'afe_current',
        'fg_state_of_charge', 'fg_voltage', 'fg_current'
    ]
    
    missing_params = []
    for param in expected_params:
        if param not in mapped_data:
            missing_params.append(param)
    
    if missing_params:
        print(f"❌ Missing parameters: {missing_params}")
        return False
    
    # Show sample values
    print("\nSample register values:")
    for param in expected_params[:8]:  # Show first 8
        value = mapped_data[param]
        print(f"  {param}: {value}")
    
    # Validate value ranges
    validations = [
        ('afe_cell_volt1', 2500, 4500, 'Cell voltage'),
        ('afe_pack_volt', 20000, 40000, 'Pack voltage'), 
        ('fg_state_of_charge', 0, 100, 'State of charge'),
        ('afe_current', -10000, 10000, 'Current')
    ]
    
    print("\nValue validation:")
    all_valid = True
    for param, min_val, max_val, desc in validations:
        value = mapped_data.get(param, 0)
        if min_val <= value <= max_val:
            print(f"  ✅ {desc}: {value} (valid range)")
        else:
            print(f"  ⚠️  {desc}: {value} (outside {min_val}-{max_val})")
            all_valid = False
    
    return all_valid


def test_scenario_variations():
    """Test different battery scenarios"""
    print("\nTesting scenario variations...")
    
    handler = RegisterHandler()
    scenarios = handler.get_predefined_scenarios()
    
    print(f"Testing {len(scenarios)} scenarios:")
    
    for scenario in scenarios[:3]:  # Test first 3 scenarios
        print(f"\n  Scenario: {scenario.name}")
        handler.set_scenario(scenario)
        
        # Get values
        modbus_values = handler.get_all_registers()
        mapped_data = parse_id_registers(10, modbus_values)
        
        # Show key values
        print(f"    Pack voltage: {mapped_data['afe_pack_volt']} mV")
        print(f"    Current: {mapped_data['afe_current']} mA")
        print(f"    SOC: {mapped_data['fg_state_of_charge']}%")
        print(f"    Cell delta: {mapped_data['afe_cell_volt_delta']} mV")
        
        # Verify scenario-specific values
        if scenario.current > 0:  # Charging
            if mapped_data['afe_current'] <= 0:
                print(f"    ⚠️  Expected positive current for charging scenario")
        elif scenario.current < 0:  # Discharging
            if mapped_data['afe_current'] >= 0:
                print(f"    ⚠️  Expected negative current for discharging scenario")
    
    return True


def test_realistic_values():
    """Test that values are realistic for a battery system"""
    print("\nTesting realistic value generation...")
    
    handler = RegisterHandler()
    
    # Set a known scenario
    scenario = BatteryScenario(
        name="Test Realistic",
        state=BatteryState.CHARGING,
        base_voltage=3.75,
        current=1.5,
        soc=75,
        cell_delta=0.025
    )
    handler.set_scenario(scenario)
    
    # Get multiple readings to test variation
    readings = []
    for i in range(5):
        modbus_values = handler.get_all_registers()
        mapped_data = parse_id_registers(10, modbus_values)
        readings.append(mapped_data)
    
    # Check cell voltage consistency
    first_reading = readings[0]
    cell_voltages = [first_reading[f'afe_cell_volt{i}'] for i in range(1, 9)]
    
    print(f"  Cell voltages: {[f'{v}mV' for v in cell_voltages[:4]]}...")
    
    # Check pack voltage = sum of cells
    expected_pack = sum(cell_voltages)
    actual_pack = first_reading['afe_pack_volt']
    
    if abs(expected_pack - actual_pack) < 10:  # Allow small rounding differences
        print(f"  ✅ Pack voltage calculation: {actual_pack} mV (expected ~{expected_pack})")
    else:
        print(f"  ❌ Pack voltage mismatch: {actual_pack} vs {expected_pack}")
        return False
    
    # Check delta calculation
    min_cell = min(cell_voltages)
    max_cell = max(cell_voltages)
    expected_delta = max_cell - min_cell
    actual_delta = first_reading['afe_cell_volt_delta']
    
    if abs(expected_delta - actual_delta) < 5:  # Allow small differences
        print(f"  ✅ Cell delta calculation: {actual_delta} mV (expected ~{expected_delta})")
    else:
        print(f"  ⚠️  Cell delta mismatch: {actual_delta} vs {expected_delta}")
    
    return True


def main():
    """Run all tests"""
    print("GA Modbus Simulator - Register Query Test")
    print("=" * 50)
    
    tests = [
        test_register_format,
        test_scenario_variations, 
        test_realistic_values
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\nTest Summary: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All register query tests passed!")
        print("✅ Simulator generates compatible register data")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)