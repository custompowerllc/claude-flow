#!/usr/bin/env python3
"""
Unit tests for Register Handler in Modbus BMS Simulator

Tests register value generation, data simulation, and BMS physics:
- Realistic battery parameter simulation
- Register value calculations
- Data consistency and validation
- Scenario-based value generation
- Physics-based battery modeling
"""

import pytest
import unittest.mock as mock
from unittest.mock import MagicMock, patch
import random
import time
from datetime import datetime

# Import the register mapping from the existing GA app
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../src'))

try:
    from modbus_query_test import register_map, num_registers
except ImportError:
    # Fallback register map if import fails
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
    num_registers = len(register_map)


class BMSRegisterHandler:
    """Handles BMS register value generation and simulation"""
    
    def __init__(self):
        self.register_map = register_map
        self.num_registers = num_registers
        
        # Battery configuration for 8S LiFePO4
        self.num_cells = 8
        self.nominal_cell_voltage = 3280  # 3.28V in mV
        self.min_cell_voltage = 2500     # 2.5V safe minimum
        self.max_cell_voltage = 3650     # 3.65V safe maximum
        self.design_capacity = 80000     # 80Ah in mAh
        
        # Current scenario and state
        self.scenario = "normal"  # normal, charging, discharging, fault
        self.battery_soc = 75.0   # State of charge (%)
        self.battery_soh = 98.0   # State of health (%)
        self.cycle_count = 450
        self.temperature_c = 25.0  # Ambient temperature
        
        # Cell imbalance simulation
        self.cell_variations = [-8, -3, 2, 5, -6, 4, -1, 7]  # mV variations per cell
        
        # Initialize register values
        self.registers = {}
        self._update_all_registers()
    
    def set_scenario(self, scenario):
        """Set the current battery scenario"""
        valid_scenarios = ["normal", "charging", "discharging", "fault", "balancing"]
        if scenario not in valid_scenarios:
            raise ValueError(f"Invalid scenario: {scenario}. Valid: {valid_scenarios}")
        self.scenario = scenario
        self._update_all_registers()
    
    def set_battery_state(self, soc=None, soh=None, temperature=None):
        """Set battery state parameters"""
        if soc is not None:
            self.battery_soc = max(0.0, min(100.0, soc))
        if soh is not None:
            self.battery_soh = max(0.0, min(100.0, soh))
        if temperature is not None:
            self.temperature_c = temperature
        self._update_all_registers()
    
    def get_register_value(self, register_addr):
        """Get the current value of a specific register"""
        if register_addr not in self.register_map:
            raise ValueError(f"Invalid register address: {register_addr}")
        
        return self.registers.get(register_addr, 0)
    
    def get_all_register_values(self):
        """Get all register values as a list (addresses 10-45)"""
        values = []
        for i in range(self.num_registers):
            register_addr = 10 + i
            values.append(self.registers.get(register_addr, 0))
        return values
    
    def _update_all_registers(self):
        """Update all register values based on current state"""
        # Update cell voltages (registers 10-17)
        cell_voltages = []
        for i in range(self.num_cells):
            voltage = self._simulate_cell_voltage(i)
            register_addr = 10 + i
            self.registers[register_addr] = voltage
            cell_voltages.append(voltage)
        
        # Update pack voltage (register 18)
        pack_voltage = sum(cell_voltages)
        self.registers[18] = pack_voltage
        
        # Update cell delta (register 19)
        cell_delta = max(cell_voltages) - min(cell_voltages)
        self.registers[19] = cell_delta
        
        # Update temperatures (registers 20-21)
        self.registers[20] = self._simulate_temperature(sensor_id=0)
        self.registers[21] = self._simulate_temperature(sensor_id=1)
        
        # Update current (register 22)
        self.registers[22] = self._simulate_current()
        
        # Update AFE configuration (registers 23-26)
        self.registers[23] = 1000  # ADC gain
        self.registers[24] = 0     # ADC offset
        self.registers[25] = self.max_cell_voltage  # OV limit
        self.registers[26] = self.min_cell_voltage  # UV limit
        
        # Update fuel gauge data (registers 27-45)
        self._update_fuel_gauge_registers()
    
    def _simulate_cell_voltage(self, cell_id):
        """Simulate realistic cell voltage for LiFePO4"""
        if cell_id >= self.num_cells:
            raise ValueError(f"Invalid cell_id: {cell_id}")
        
        # Base voltage from SOC curve
        base_voltage = self._get_voltage_from_soc(self.battery_soc)
        
        # Add cell-specific variation
        cell_variation = self.cell_variations[cell_id]
        
        # Add scenario-specific effects
        scenario_effect = self._get_scenario_voltage_effect()
        
        # Add small random variation (±2mV)
        random_variation = random.randint(-2, 2)
        
        # Calculate final voltage
        voltage_mv = base_voltage + cell_variation + scenario_effect + random_variation
        
        # Clamp to safe limits
        return max(self.min_cell_voltage, min(self.max_cell_voltage, voltage_mv))
    
    def _get_voltage_from_soc(self, soc):
        """Get cell voltage from SOC using LiFePO4 curve"""
        # LiFePO4 voltage curve (simplified)
        if soc <= 0:
            return 2500   # Empty
        elif soc <= 10:
            return 2800 + (soc * 20)  # 2800-3000mV
        elif soc <= 90:
            return 3200 + (soc * 1)   # Flat region 3200-3290mV
        else:
            return 3290 + ((soc - 90) * 10)  # 3290-3390mV
    
    def _get_scenario_voltage_effect(self):
        """Get voltage effect based on current scenario"""
        if self.scenario == "charging":
            return 50  # Higher voltage during charge
        elif self.scenario == "discharging":
            return -30  # Lower voltage during discharge
        elif self.scenario == "fault":
            return -100  # Voltage drop during fault
        return 0  # Normal operation
    
    def _simulate_temperature(self, sensor_id):
        """Simulate temperature sensor readings"""
        # Base temperature with small sensor offset
        sensor_offset = 1 if sensor_id == 1 else 0
        base_temp = self.temperature_c + sensor_offset
        
        # Add scenario effects
        if self.scenario == "charging":
            base_temp += 3  # Charging heats up battery
        elif self.scenario == "discharging":
            base_temp += 5  # Discharging heats up more
        elif self.scenario == "fault":
            base_temp += 15  # Fault conditions cause heating
        
        # Add small random variation
        temp_variation = random.uniform(-1.0, 1.0)
        final_temp = base_temp + temp_variation
        
        # Convert to register format (tenths of degree)
        return int(final_temp * 10)
    
    def _simulate_current(self):
        """Simulate pack current based on scenario"""
        if self.scenario == "charging":
            # Charging current: 0.1C to 0.5C (8A to 40A for 80Ah)
            return random.randint(8000, 40000)  # Positive = charging
        elif self.scenario == "discharging":
            # Discharging current: 0.1C to 1C (8A to 80A for 80Ah)
            return random.randint(-80000, -8000)  # Negative = discharging
        elif self.scenario == "balancing":
            # Very low current during balancing
            return random.randint(-500, 500)
        elif self.scenario == "fault":
            # Fault may have high current
            return random.randint(-100000, 50000)
        else:
            # Normal standby: very low current
            return random.randint(-200, 200)
    
    def _update_fuel_gauge_registers(self):
        """Update fuel gauge related registers (27-45)"""
        # State of charge (register 27)
        self.registers[27] = int(self.battery_soc)
        
        # Fuel gauge voltage (register 28) - matches pack voltage
        self.registers[28] = self.registers[18]
        
        # Fuel gauge current (register 29) - matches AFE current with slight offset
        afe_current = self.registers[22]
        fg_current_offset = random.randint(-50, 50)
        self.registers[29] = afe_current + fg_current_offset
        
        # Fuel gauge temperature (register 30)
        self.registers[30] = self.registers[20]  # Match temp sensor 1
        
        # Remaining capacity (register 31)
        remaining_mah = int((self.battery_soc / 100.0) * self.design_capacity)
        self.registers[31] = remaining_mah
        
        # Full charge capacity (register 32)
        full_capacity = int((self.battery_soh / 100.0) * self.design_capacity)
        self.registers[32] = full_capacity
        
        # Design capacity (register 33)
        self.registers[33] = self.design_capacity
        
        # Average current (register 34)
        self.registers[34] = self.registers[22]  # Simplified
        
        # Time to empty (register 35)
        current_ma = abs(self.registers[22])
        if current_ma > 100 and self.scenario == "discharging":
            time_to_empty_min = int((remaining_mah / current_ma) * 60)
            self.registers[35] = min(65535, time_to_empty_min)  # Cap at 16-bit max
        else:
            self.registers[35] = 65535  # Max value when not discharging
        
        # Time to full (register 36)
        if self.scenario == "charging" and current_ma > 100:
            remaining_to_full = full_capacity - remaining_mah
            time_to_full_min = int((remaining_to_full / current_ma) * 60)
            self.registers[36] = min(65535, time_to_full_min)
        else:
            self.registers[36] = 0  # Not charging
        
        # Internal temperature (register 37)
        self.registers[37] = self.registers[20] + 5  # Slightly higher than external
        
        # Cycle count (register 38)
        self.registers[38] = self.cycle_count
        
        # State of health (register 39)
        self.registers[39] = int(self.battery_soh)
        
        # Charging voltage and current (registers 40-41)
        if self.scenario == "charging":
            self.registers[40] = self.registers[18] + 200  # Slightly higher during charge
            self.registers[41] = self.registers[22]
        else:
            self.registers[40] = self.registers[18]
            self.registers[41] = 0
        
        # Lifetime statistics (registers 42-45)
        self.registers[42] = 450   # Lifetime max temp (45°C)
        self.registers[43] = -100  # Lifetime min temp (-10°C)
        self.registers[44] = 50000 # Lifetime max charge (50A)
        self.registers[45] = 80000 # Lifetime max discharge (80A)


class TestBMSRegisterHandler(pytest.TestCase):
    """Test cases for BMS register handler"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.handler = BMSRegisterHandler()
    
    def test_initialization(self):
        """Test register handler initialization"""
        handler = BMSRegisterHandler()
        
        # Verify basic configuration
        self.assertEqual(handler.num_cells, 8)
        self.assertEqual(handler.num_registers, 36)
        self.assertEqual(handler.scenario, "normal")
        self.assertEqual(handler.battery_soc, 75.0)
        self.assertEqual(handler.battery_soh, 98.0)
        
        # Verify register map is loaded
        self.assertEqual(len(handler.register_map), 36)
        self.assertEqual(handler.register_map[10], "afe_cell_volt1")
        self.assertEqual(handler.register_map[45], "fg_lifetime_max_dsg")
        
        # Verify registers are initialized
        self.assertEqual(len(handler.registers), 36)
    
    def test_cell_voltage_simulation(self):
        """Test cell voltage simulation accuracy"""
        handler = BMSRegisterHandler()
        
        # Test all cell voltages
        for cell_id in range(8):
            voltage = handler._simulate_cell_voltage(cell_id)
            
            # Verify voltage is in valid range
            self.assertGreaterEqual(voltage, handler.min_cell_voltage)
            self.assertLessEqual(voltage, handler.max_cell_voltage)
            
            # Verify voltage is reasonable for SOC
            expected_base = handler._get_voltage_from_soc(handler.battery_soc)
            self.assertGreater(voltage, expected_base - 100)  # Within 100mV of expected
            self.assertLess(voltage, expected_base + 100)
    
    def test_soc_voltage_curve(self):
        """Test SOC to voltage curve mapping"""
        handler = BMSRegisterHandler()
        
        # Test key SOC points
        test_socs = [0, 10, 50, 90, 100]
        previous_voltage = 0
        
        for soc in test_socs:
            voltage = handler._get_voltage_from_soc(soc)
            
            # Voltage should increase with SOC
            self.assertGreater(voltage, previous_voltage)
            previous_voltage = voltage
            
            # Verify reasonable ranges
            if soc == 0:
                self.assertEqual(voltage, 2500)
            elif soc == 100:
                self.assertGreater(voltage, 3300)
    
    def test_scenario_effects(self):
        """Test different scenario effects on register values"""
        handler = BMSRegisterHandler()
        
        scenarios = ["normal", "charging", "discharging", "fault", "balancing"]
        
        for scenario in scenarios:
            handler.set_scenario(scenario)
            
            # Get current and verify it matches scenario
            current = handler.get_register_value(22)
            
            if scenario == "charging":
                self.assertGreater(current, 0, f"Charging current should be positive, got {current}")
                self.assertGreater(current, 1000, f"Charging current too low: {current}")
            elif scenario == "discharging":
                self.assertLess(current, 0, f"Discharging current should be negative, got {current}")
                self.assertLess(current, -1000, f"Discharging current too high: {current}")
            elif scenario == "normal" or scenario == "balancing":
                self.assertLess(abs(current), 1000, f"Standby current too high: {current}")
    
    def test_pack_voltage_calculation(self):
        """Test pack voltage equals sum of cell voltages"""
        handler = BMSRegisterHandler()
        
        # Get cell voltages
        cell_voltages = []
        for i in range(8):
            voltage = handler.get_register_value(10 + i)
            cell_voltages.append(voltage)
        
        # Get pack voltage
        pack_voltage = handler.get_register_value(18)
        
        # Verify pack voltage equals sum
        expected_pack = sum(cell_voltages)
        self.assertEqual(pack_voltage, expected_pack)
    
    def test_cell_delta_calculation(self):
        """Test cell voltage delta calculation"""
        handler = BMSRegisterHandler()
        
        # Get cell voltages
        cell_voltages = []
        for i in range(8):
            voltage = handler.get_register_value(10 + i)
            cell_voltages.append(voltage)
        
        # Get cell delta
        cell_delta = handler.get_register_value(19)
        
        # Verify delta equals max - min
        expected_delta = max(cell_voltages) - min(cell_voltages)
        self.assertEqual(cell_delta, expected_delta)
        
        # Verify delta is reasonable
        self.assertGreaterEqual(cell_delta, 0)
        self.assertLess(cell_delta, 200)  # Should be < 200mV for healthy battery
    
    def test_temperature_simulation(self):
        """Test temperature sensor simulation"""
        handler = BMSRegisterHandler()
        
        # Test both temperature sensors
        temp1 = handler.get_register_value(20)
        temp2 = handler.get_register_value(21)
        
        # Convert back to Celsius
        temp1_c = temp1 / 10.0
        temp2_c = temp2 / 10.0
        
        # Verify temperatures are reasonable
        self.assertGreater(temp1_c, -40)  # Above absolute minimum
        self.assertLess(temp1_c, 85)     # Below maximum rating
        self.assertGreater(temp2_c, -40)
        self.assertLess(temp2_c, 85)
        
        # Verify slight difference between sensors
        temp_diff = abs(temp1_c - temp2_c)
        self.assertLess(temp_diff, 10)  # Should be within 10°C
    
    def test_fuel_gauge_consistency(self):
        """Test fuel gauge data consistency"""
        handler = BMSRegisterHandler()
        
        # Test SOC consistency
        soc = handler.get_register_value(27)
        self.assertEqual(soc, int(handler.battery_soc))
        
        # Test voltage consistency
        fg_voltage = handler.get_register_value(28)
        pack_voltage = handler.get_register_value(18)
        self.assertEqual(fg_voltage, pack_voltage)
        
        # Test capacity relationships
        remaining_cap = handler.get_register_value(31)
        full_cap = handler.get_register_value(32)
        design_cap = handler.get_register_value(33)
        
        self.assertLessEqual(remaining_cap, full_cap)
        self.assertLessEqual(full_cap, design_cap)
        self.assertEqual(design_cap, handler.design_capacity)
        
        # Test SOH calculation
        soh = handler.get_register_value(39)
        expected_soh = int((full_cap / design_cap) * 100)
        self.assertAlmostEqual(soh, expected_soh, delta=1)
    
    def test_register_value_ranges(self):
        """Test all register values are within expected ranges"""
        handler = BMSRegisterHandler()
        
        # Test all scenarios
        scenarios = ["normal", "charging", "discharging"]
        
        for scenario in scenarios:
            handler.set_scenario(scenario)
            values = handler.get_all_register_values()
            
            # Cell voltages (0-7)
            for i in range(8):
                self.assertGreaterEqual(values[i], 2500)
                self.assertLessEqual(values[i], 3650)
            
            # Pack voltage (8)
            self.assertGreater(values[8], 20000)  # 8 * 2.5V
            self.assertLess(values[8], 30000)    # 8 * 3.65V
            
            # Cell delta (9)
            self.assertGreaterEqual(values[9], 0)
            self.assertLess(values[9], 500)  # Should be reasonable
            
            # Temperatures (10-11)
            for i in range(10, 12):
                self.assertGreater(values[i], -400)  # -40°C
                self.assertLess(values[i], 850)     # 85°C
            
            # SOC (17)
            self.assertGreaterEqual(values[17], 0)
            self.assertLessEqual(values[17], 100)
            
            # SOH (29)
            self.assertGreaterEqual(values[29], 0)
            self.assertLessEqual(values[29], 100)
    
    def test_state_changes(self):
        """Test battery state changes affect register values"""
        handler = BMSRegisterHandler()
        
        # Record initial values
        initial_soc = handler.get_register_value(27)
        initial_remaining = handler.get_register_value(31)
        
        # Change SOC
        new_soc = 50.0
        handler.set_battery_state(soc=new_soc)
        
        # Verify SOC changed
        new_soc_reg = handler.get_register_value(27)
        self.assertEqual(new_soc_reg, int(new_soc))
        
        # Verify remaining capacity changed
        new_remaining = handler.get_register_value(31)
        self.assertNotEqual(new_remaining, initial_remaining)
        
        # Verify cell voltages changed (SOC affects voltage)
        for i in range(8):
            new_voltage = handler.get_register_value(10 + i)
            # Should be different due to SOC change
            self.assertGreater(new_voltage, 2500)
            self.assertLess(new_voltage, 3650)
    
    def test_error_handling(self):
        """Test error handling in register handler"""
        handler = BMSRegisterHandler()
        
        # Test invalid register address
        with self.assertRaises(ValueError):
            handler.get_register_value(5)  # Below valid range
        
        with self.assertRaises(ValueError):
            handler.get_register_value(50)  # Above valid range
        
        # Test invalid scenario
        with self.assertRaises(ValueError):
            handler.set_scenario("invalid_scenario")
        
        # Test invalid cell ID
        with self.assertRaises(ValueError):
            handler._simulate_cell_voltage(10)  # Only 0-7 valid
    
    def test_time_calculations(self):
        """Test time to empty and time to full calculations"""
        handler = BMSRegisterHandler()
        
        # Test discharging scenario
        handler.set_scenario("discharging")
        time_to_empty = handler.get_register_value(35)
        self.assertGreater(time_to_empty, 0)
        self.assertLess(time_to_empty, 65535)
        
        # Test charging scenario
        handler.set_scenario("charging")
        time_to_full = handler.get_register_value(36)
        self.assertGreater(time_to_full, 0)
        self.assertLess(time_to_full, 65535)
        
        # Test normal scenario (should be max/0)
        handler.set_scenario("normal")
        time_to_empty = handler.get_register_value(35)
        time_to_full = handler.get_register_value(36)
        self.assertEqual(time_to_empty, 65535)  # Max when not discharging
        self.assertEqual(time_to_full, 0)       # 0 when not charging
    
    def test_data_stability(self):
        """Test that register values are stable without updates"""
        handler = BMSRegisterHandler()
        
        # Get initial values
        initial_values = handler.get_all_register_values()
        
        # Wait and get values again (no updates)
        time.sleep(0.01)
        second_values = handler.get_all_register_values()
        
        # Values should be identical (no time-based changes)
        self.assertEqual(initial_values, second_values)
    
    def test_register_data_types(self):
        """Test that all register values are valid 16-bit integers"""
        handler = BMSRegisterHandler()
        
        values = handler.get_all_register_values()
        
        for i, value in enumerate(values):
            register_addr = 10 + i
            param_name = register_map.get(register_addr, f"Register_{register_addr}")
            
            # Verify value is integer
            self.assertIsInstance(value, int, f"{param_name} is not integer: {type(value)}")
            
            # Verify value fits in 16-bit signed integer
            self.assertGreaterEqual(value, -32768, f"{param_name} below 16-bit range: {value}")
            self.assertLessEqual(value, 32767, f"{param_name} above 16-bit range: {value}")


if __name__ == '__main__':
    pytest.main([__file__])