#!/usr/bin/env python3
"""
RegisterHandler - Manages BMS register values for Modbus simulation

This module handles the register map and values that correspond exactly to
the register_map defined in modbus_query_test.py. It provides both simulated
and realistic battery data based on different operating scenarios.

The register addresses and names are imported directly from the main application
to ensure 100% compatibility.
"""

import sys
import os
import logging
import random
import time
import math
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Import logging system
try:
    from ..utils.log_manager import get_logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

# Add the main src directory to path to import register_map
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

try:
    from modbus_query_test import register_map
    REGISTER_MAP_AVAILABLE = True
except ImportError:
    # Fallback register map if import fails
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
    REGISTER_MAP_AVAILABLE = False


class BatteryState(Enum):
    """Battery operating states for simulation"""
    IDLE = "idle"
    CHARGING = "charging"
    DISCHARGING = "discharging"
    BALANCING = "balancing"
    FAULT = "fault"


@dataclass
class BatteryScenario:
    """Configuration for different battery simulation scenarios"""
    name: str
    state: BatteryState
    base_voltage: float = 3.7  # Base cell voltage in volts
    current: float = 0.0  # Current in amps (positive = charging, negative = discharging)
    soc: int = 50  # State of charge percentage
    temperature: float = 25.0  # Temperature in Celsius
    cell_delta: float = 0.010  # Cell voltage delta in volts
    enable_noise: bool = True
    noise_level: float = 0.001  # Voltage noise level


class RegisterHandler:
    """
    Handles register values for BMS simulation
    
    This class manages the register values that correspond to the register_map
    from modbus_query_test.py, ensuring complete compatibility with the GA app.
    """
    
    def __init__(self):
        """Initialize the register handler"""
        if LOGGING_AVAILABLE:
            self.logger = get_logger(__name__, 'register_handler')
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
        
        # Register storage (name -> value mapping)
        self._registers: Dict[str, int] = {}
        
        # Simulation parameters
        self.current_scenario = BatteryScenario(
            name="Default",
            state=BatteryState.IDLE,
            base_voltage=3.7,
            current=0.0,
            soc=50
        )
        
        # Simulation state
        self._start_time = time.time()
        self._cycle_time = 0.0
        
        # Initialize registers with default values
        self._initialize_registers()
        
        self.logger.info("RegisterHandler initialized with {} registers".format(len(self._registers)))
        if not REGISTER_MAP_AVAILABLE:
            self.logger.warning("Using fallback register map - check import path")
    
    def _initialize_registers(self):
        """Initialize all registers with default values"""
        # Cell voltages (AFE registers) - in millivolts
        for i in range(1, 9):  # afe_cell_volt1 through afe_cell_volt8
            reg_name = "afe_cell_volt{}".format(i)
            self._registers[reg_name] = int(self.current_scenario.base_voltage * 1000)  # Convert to mV
        
        # Pack voltage - sum of cell voltages
        self._registers["afe_pack_volt"] = int(self.current_scenario.base_voltage * 8 * 1000)
        
        # Cell voltage delta - in millivolts
        self._registers["afe_cell_volt_delta"] = int(self.current_scenario.cell_delta * 1000)
        
        # Temperatures - in tenths of degree Celsius
        self._registers["afe_temp1"] = int(self.current_scenario.temperature * 10)
        self._registers["afe_temp2"] = int(self.current_scenario.temperature * 10)
        
        # Current - in milliamps
        self._registers["afe_current"] = int(self.current_scenario.current * 1000)
        
        # AFE configuration
        self._registers["afe_adc_gain"] = 1000  # ADC gain
        self._registers["afe_adc_offset"] = 0    # ADC offset
        self._registers["afe_ov_limit"] = 4200   # Overvoltage limit in mV
        self._registers["afe_uv_limit"] = 3000   # Undervoltage limit in mV
        
        # Fuel gauge registers
        self._registers["fg_state_of_charge"] = self.current_scenario.soc  # SOC in percentage
        self._registers["fg_voltage"] = int(self.current_scenario.base_voltage * 8 * 1000)  # Pack voltage in mV
        self._registers["fg_current"] = int(self.current_scenario.current * 1000)  # Current in mA
        self._registers["fg_temperature"] = int(self.current_scenario.temperature * 10)  # Temp in 0.1°C
        self._registers["fg_remaining_capacity"] = 2500  # Remaining capacity in mAh
        self._registers["fg_full_charge_cap"] = 5000     # Full charge capacity in mAh
        self._registers["fg_design_capacity"] = 5000     # Design capacity in mAh
        self._registers["fg_average_current"] = int(self.current_scenario.current * 1000)  # Average current in mA
        self._registers["fg_time_to_empty"] = 0 if self.current_scenario.current >= 0 else 300  # Minutes
        self._registers["fg_time_to_full"] = 0 if self.current_scenario.current <= 0 else 180   # Minutes
        self._registers["fg_internal_temp"] = int(self.current_scenario.temperature * 10)  # Internal temp
        self._registers["fg_cycle_count"] = 50          # Cycle count
        self._registers["fg_state_of_health"] = 98      # SOH in percentage
        self._registers["fg_charging_voltage"] = 4200   # Charging voltage in mV
        self._registers["fg_charging_current"] = 1000   # Charging current in mA
        self._registers["fg_lifetime_max_temp"] = 450   # Max temp in 0.1°C (45°C)
        self._registers["fg_lifetime_min_temp"] = -100  # Min temp in 0.1°C (-10°C)
        self._registers["fg_lifetime_max_chg"] = 2000   # Max charge current in mA
        self._registers["fg_lifetime_max_dsg"] = -3000  # Max discharge current in mA (negative)
        
        self.logger.info("Registers initialized with default values")
    
    def _add_noise(self, value: float, noise_level: float = 0.001) -> float:
        """Add realistic noise to a value"""
        if not self.current_scenario.enable_noise:
            return value
        
        noise = random.uniform(-noise_level, noise_level)
        return value + (value * noise)
    
    def _simulate_cell_voltages(self):
        """Simulate realistic cell voltage variations"""
        base_voltage_mv = self.current_scenario.base_voltage * 1000
        delta_mv = self.current_scenario.cell_delta * 1000
        
        # Add time-based variations
        self._cycle_time = (time.time() - self._start_time) % 60.0  # 60-second cycle
        time_factor = math.sin(self._cycle_time * 2 * math.pi / 60.0) * 0.1
        
        # Simulate individual cell voltages with variations
        cell_voltages = []
        for i in range(8):
            # Each cell has slightly different characteristics
            cell_offset = (i - 3.5) * 2.0  # Spread cells around center
            voltage_mv = base_voltage_mv + cell_offset + (time_factor * 10)
            
            # Add noise
            voltage_mv = self._add_noise(voltage_mv, self.current_scenario.noise_level)
            
            # Apply current effects
            if self.current_scenario.current > 0:  # Charging
                voltage_mv += abs(self.current_scenario.current) * 5  # Voltage rises during charging
            elif self.current_scenario.current < 0:  # Discharging
                voltage_mv -= abs(self.current_scenario.current) * 3  # Voltage drops during discharge
            
            cell_voltages.append(int(voltage_mv))
        
        # Update cell voltage registers
        for i, voltage in enumerate(cell_voltages, 1):
            self._registers["afe_cell_volt{}".format(i)] = voltage
        
        # Calculate pack voltage and delta
        pack_voltage = sum(cell_voltages)
        cell_delta = max(cell_voltages) - min(cell_voltages)
        
        self._registers["afe_pack_volt"] = pack_voltage
        self._registers["afe_cell_volt_delta"] = cell_delta
        self._registers["fg_voltage"] = pack_voltage
    
    def _simulate_current_and_soc(self):
        """Simulate current and state of charge based on battery state"""
        current_ma = int(self.current_scenario.current * 1000)
        
        # Add some variation to current
        if self.current_scenario.state != BatteryState.IDLE:
            current_variation = random.uniform(-0.1, 0.1) * abs(current_ma)
            current_ma += int(current_variation)
        
        # Update current registers
        self._registers["afe_current"] = current_ma
        self._registers["fg_current"] = current_ma
        self._registers["fg_average_current"] = current_ma
        
        # Simulate SOC changes based on current
        if abs(current_ma) > 100:  # Only change SOC if significant current
            # Very slow SOC change for demo purposes
            soc_change_rate = 0.001  # % per update
            if current_ma > 0:  # Charging
                self.current_scenario.soc = min(100, self.current_scenario.soc + soc_change_rate)
            else:  # Discharging
                self.current_scenario.soc = max(0, self.current_scenario.soc - soc_change_rate)
        
        self._registers["fg_state_of_charge"] = int(self.current_scenario.soc)
        
        # Update capacity estimates
        remaining_capacity = int(5000 * self.current_scenario.soc / 100)
        self._registers["fg_remaining_capacity"] = remaining_capacity
        
        # Update time estimates
        if current_ma > 100:  # Charging
            time_to_full = int((100 - self.current_scenario.soc) * 5000 / current_ma * 60 / 1000)
            self._registers["fg_time_to_full"] = min(time_to_full, 65535)
            self._registers["fg_time_to_empty"] = 65535
        elif current_ma < -100:  # Discharging
            time_to_empty = int(self.current_scenario.soc * 5000 / abs(current_ma) * 60 / 1000)
            self._registers["fg_time_to_empty"] = min(time_to_empty, 65535)
            self._registers["fg_time_to_full"] = 65535
        else:  # Idle
            self._registers["fg_time_to_empty"] = 65535
            self._registers["fg_time_to_full"] = 65535
    
    def _simulate_temperature(self):
        """Simulate temperature variations"""
        base_temp = self.current_scenario.temperature
        
        # Add thermal effects from current
        thermal_rise = abs(self.current_scenario.current) * 2.0  # 2°C per amp
        temp = base_temp + thermal_rise
        
        # Add time-based variation
        time_variation = math.sin(self._cycle_time * 2 * math.pi / 60.0) * 1.0
        temp += time_variation
        
        # Add noise
        temp = self._add_noise(temp, 0.01)
        
        temp_tenths = int(temp * 10)
        self._registers["afe_temp1"] = temp_tenths
        self._registers["afe_temp2"] = temp_tenths
        self._registers["fg_temperature"] = temp_tenths
        self._registers["fg_internal_temp"] = temp_tenths
    
    def update_simulation(self):
        """Update all simulated register values"""
        try:
            self._simulate_cell_voltages()
            self._simulate_current_and_soc()
            self._simulate_temperature()
            
            self.logger.debug("Updated simulation for scenario: {}".format(self.current_scenario.name))
            
        except Exception as e:
            self.logger.error("Error updating simulation: {}".format(e))
    
    def set_scenario(self, scenario: BatteryScenario):
        """Set the current battery simulation scenario"""
        self.current_scenario = scenario
        self._start_time = time.time()  # Reset timing
        self.logger.info("Set scenario to: {} ({})".format(scenario.name, scenario.state.value))
        
        # Update registers immediately
        self.update_simulation()
    
    def get_predefined_scenarios(self) -> List[BatteryScenario]:
        """Get list of predefined battery scenarios"""
        scenarios = [
            BatteryScenario(
                name="Idle - Balanced",
                state=BatteryState.IDLE,
                base_voltage=3.7,
                current=0.0,
                soc=50,
                cell_delta=0.005
            ),
            BatteryScenario(
                name="Charging - 1A",
                state=BatteryState.CHARGING,
                base_voltage=3.8,
                current=1.0,
                soc=60,
                cell_delta=0.015
            ),
            BatteryScenario(
                name="Discharging - 2A",
                state=BatteryState.DISCHARGING,
                base_voltage=3.6,
                current=-2.0,
                soc=40,
                cell_delta=0.020
            ),
            BatteryScenario(
                name="Balancing - High Delta",
                state=BatteryState.BALANCING,
                base_voltage=3.7,
                current=0.5,
                soc=80,
                cell_delta=0.050  # High delta for balance testing
            ),
            BatteryScenario(
                name="Low Battery",
                state=BatteryState.DISCHARGING,
                base_voltage=3.2,
                current=-0.5,
                soc=10,
                cell_delta=0.030
            ),
            BatteryScenario(
                name="Full Battery",
                state=BatteryState.IDLE,
                base_voltage=4.1,
                current=0.0,
                soc=95,
                cell_delta=0.008
            )
        ]
        return scenarios
    
    def get_all_registers(self) -> List[int]:
        """Get all register values in the correct order for Modbus response"""
        # Update simulation first
        self.update_simulation()
        
        # Return values in register address order (10-45)
        values = []
        for addr in sorted(register_map.keys()):
            reg_name = register_map[addr]
            value = self._registers.get(reg_name, 0)
            values.append(value)
        
        return values
    
    def get_register_dict(self) -> Dict[str, int]:
        """Get all registers as a name -> value dictionary"""
        self.update_simulation()
        return self._registers.copy()
    
    def update_register(self, register_name: str, value: int) -> bool:
        """Update a specific register value"""
        if register_name in self._registers:
            self._registers[register_name] = value
            self.logger.debug("Updated register {} = {}".format(register_name, value))
            return True
        else:
            self.logger.warning("Unknown register: {}".format(register_name))
            return False
    
    def get_register(self, register_name: str) -> Optional[int]:
        """Get a specific register value"""
        return self._registers.get(register_name)
    
    def get_register_info(self) -> Dict[str, Any]:
        """Get information about the register mapping"""
        return {
            'total_registers': len(register_map),
            'address_range': "{}-{}".format(min(register_map.keys()), max(register_map.keys())),
            'register_map_available': REGISTER_MAP_AVAILABLE,
            'current_scenario': self.current_scenario.name,
            'simulation_time': time.time() - self._start_time
        }


def main():
    """Test function for the register handler"""
    # Setup logging
    if LOGGING_AVAILABLE:
        from ..utils.log_manager import setup_logging
        setup_logging(level='INFO')
        logger = get_logger(__name__, 'register_handler')
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
    
    # Create register handler
    handler = RegisterHandler()
    
    # Test scenarios
    scenarios = handler.get_predefined_scenarios()
    
    print("Testing RegisterHandler with {} scenarios:".format(len(scenarios)))
    
    for scenario in scenarios:
        print("\nTesting scenario: {}".format(scenario.name))
        handler.set_scenario(scenario)
        
        # Get register values
        values = handler.get_all_registers()
        reg_dict = handler.get_register_dict()
        
        print("  Cell voltages: {}".format([reg_dict["afe_cell_volt{}".format(i)] for i in range(1, 9)]))
        print("  Pack voltage: {} mV".format(reg_dict['afe_pack_volt']))
        print("  Cell delta: {} mV".format(reg_dict['afe_cell_volt_delta']))
        print("  Current: {} mA".format(reg_dict['afe_current']))
        print("  SOC: {}%".format(reg_dict['fg_state_of_charge']))
        print("  Temperature: {}°C".format(reg_dict['afe_temp1'] / 10))
        
        time.sleep(1)
    
    print("\nRegister info: {}".format(handler.get_register_info()))


if __name__ == "__main__":
    main()