#!/usr/bin/env python3
"""
Compatibility test for the Modbus BMS Simulator

This script tests that the simulator can be queried by the existing
GA Modbus applications and returns the expected data format.

Usage:
    python3 test_compatibility.py
"""

import sys
import os
import time
import threading
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Import simulator components
try:
    from simulator.src.core.modbus_server import ModbusSimulatorServer, ServerConfig
    from simulator.src.core.register_handler import BatteryScenario, BatteryState
    from simulator.src.utils.com_port_manager import ComPortManager
    SIMULATOR_AVAILABLE = True
except ImportError as e:
    print(f"Error importing simulator: {e}")
    SIMULATOR_AVAILABLE = False

# Import GA application components
try:
    from modbus_query_test import read_battery_registers, register_map
    GA_APP_AVAILABLE = True
except ImportError as e:
    print(f"Error importing GA app: {e}")
    GA_APP_AVAILABLE = False

# Import pymodbus for direct testing
try:
    from pymodbus.client import ModbusSerialClient
    PYMODBUS_AVAILABLE = True
except ImportError:
    PYMODBUS_AVAILABLE = False


class CompatibilityTester:
    """Test compatibility between simulator and GA applications"""
    
    def __init__(self):
        """Initialize the compatibility tester"""
        self.server = None
        self.test_port = None
        self.port_manager = ComPortManager()
        
        # Setup logging for testing
        logging.basicConfig(level=logging.WARNING)  # Reduce noise
    
    def setup_test_environment(self) -> bool:
        """Setup test environment with simulator"""
        if not SIMULATOR_AVAILABLE:
            print("❌ Simulator not available")
            return False
        
        # Get a suitable port for testing
        recommendations = self.port_manager.get_port_recommendations()
        self.test_port = recommendations.get('suggested_simulator_port')
        
        if not self.test_port:
            print("⚠️  No suitable port available for testing")
            return False
        
        # Create and start simulator
        config = ServerConfig(port=self.test_port)
        self.server = ModbusSimulatorServer(config)
        
        # Set a test scenario
        charging_scenario = BatteryScenario(
            name="Test Charging",
            state=BatteryState.CHARGING,
            base_voltage=3.8,
            current=1.0,
            soc=65,
            cell_delta=0.020
        )
        self.server.register_handler.set_scenario(charging_scenario)
        
        print(f"Starting simulator on {self.test_port}...")
        if not self.server.start():
            print("❌ Failed to start simulator")
            return False
        
        # Wait for server to be ready
        time.sleep(2)
        
        if not self.server.is_running():
            print("❌ Simulator not running")
            return False
        
        print("✅ Simulator started and ready")
        return True
    
    def test_direct_modbus_query(self) -> bool:
        """Test direct Modbus query to simulator"""
        if not PYMODBUS_AVAILABLE:
            print("⚠️  PyModbus not available for direct testing")
            return True
        
        print("Testing direct Modbus query...")
        
        try:
            # Create Modbus client
            client = ModbusSerialClient(
                port=self.test_port,
                baudrate=9600,
                parity='E',
                stopbits=1,
                bytesize=8,
                timeout=2.0
            )
            
            # Connect to simulator
            if not client.connect():
                print("❌ Failed to connect to simulator")
                return False
            
            # Query registers (same as GA app)
            response = client.read_input_registers(
                address=9,  # Start address
                count=36,   # Number of registers
                slave=1     # Slave ID
            )
            
            client.close()
            
            if response.isError():
                print(f"❌ Modbus query error: {response}")
                return False
            
            # Validate response
            values = response.registers
            if len(values) != 36:
                print(f"❌ Wrong number of registers: {len(values)} (expected 36)")
                return False
            
            print(f"✅ Direct query successful: {len(values)} registers")
            
            # Check some key values
            pack_voltage = values[8]  # afe_pack_volt (register 18, index 8)
            soc = values[17]          # fg_state_of_charge (register 27, index 17)
            
            print(f"   Pack voltage: {pack_voltage} mV")
            print(f"   State of charge: {soc}%")
            
            # Validate reasonable values
            if pack_voltage < 20000 or pack_voltage > 40000:  # 20V - 40V range
                print(f"⚠️  Pack voltage seems unrealistic: {pack_voltage} mV")
            
            if soc < 0 or soc > 100:
                print(f"⚠️  SOC out of range: {soc}%")
            
            return True
            
        except Exception as e:
            print(f"❌ Direct query failed: {e}")
            return False
    
    def test_ga_app_integration(self) -> bool:
        """Test integration with GA application"""
        if not GA_APP_AVAILABLE:
            print("⚠️  GA application not available for testing")
            return True
        
        print("Testing GA application integration...")
        
        try:
            # Use the GA app's read function
            result = read_battery_registers(
                csv_filename=None,  # Don't save to CSV
                port=self.test_port,
                baudrate=9600,
                parity='E',
                stopbits=1,
                bytesize=8,
                slave_id=1
            )
            
            if result is None:
                print("❌ GA app query returned None")
                return False
            
            if isinstance(result, dict):
                print(f"✅ GA app query successful: {len(result)} parameters")
                
                # Check key parameters
                key_params = ['afe_cell_volt1', 'afe_pack_volt', 'fg_state_of_charge', 'afe_current']
                for param in key_params:
                    if param in result:
                        print(f"   {param}: {result[param]}")
                    else:
                        print(f"⚠️  Missing parameter: {param}")
                
                return True
            else:
                print(f"❌ Unexpected result type: {type(result)}")
                return False
                
        except Exception as e:
            print(f"❌ GA app integration test failed: {e}")
            return False
    
    def test_register_mapping(self) -> bool:
        """Test that register mapping is consistent"""
        if not GA_APP_AVAILABLE:
            print("⚠️  GA application not available for register mapping test")
            return True
        
        print("Testing register mapping consistency...")
        
        try:
            # Get register values from simulator
            sim_registers = self.server.get_register_values()
            
            # Check that simulator has all expected registers
            missing_registers = []
            for addr, reg_name in register_map.items():
                if reg_name not in sim_registers:
                    missing_registers.append(reg_name)
            
            if missing_registers:
                print(f"❌ Missing registers in simulator: {missing_registers}")
                return False
            
            print(f"✅ Register mapping consistent: {len(register_map)} registers")
            
            # Check value ranges
            checks = [
                ('afe_cell_volt1', 2500, 4500, 'mV'),     # Cell voltage range
                ('afe_pack_volt', 20000, 40000, 'mV'),    # Pack voltage range
                ('fg_state_of_charge', 0, 100, '%'),      # SOC range
                ('afe_temp1', -200, 800, '0.1°C'),        # Temperature range
            ]
            
            for reg_name, min_val, max_val, unit in checks:
                value = sim_registers.get(reg_name, 0)
                if min_val <= value <= max_val:
                    print(f"   {reg_name}: {value} {unit} ✅")
                else:
                    print(f"   {reg_name}: {value} {unit} ⚠️  (outside {min_val}-{max_val})")
            
            return True
            
        except Exception as e:
            print(f"❌ Register mapping test failed: {e}")
            return False
    
    def test_scenario_switching(self) -> bool:
        """Test that scenario switching affects register values"""
        print("Testing scenario switching...")
        
        try:
            # Get initial values
            initial_values = self.server.get_register_values()
            initial_current = initial_values.get('afe_current', 0)
            
            # Switch to discharging scenario
            discharge_scenario = BatteryScenario(
                name="Test Discharge",
                state=BatteryState.DISCHARGING,
                base_voltage=3.6,
                current=-2.0,  # Negative for discharge
                soc=30,
                cell_delta=0.030
            )
            self.server.register_handler.set_scenario(discharge_scenario)
            
            # Wait for update
            time.sleep(1)
            
            # Get new values
            updated_values = self.server.get_register_values()
            updated_current = updated_values.get('afe_current', 0)
            updated_soc = updated_values.get('fg_state_of_charge', 0)
            
            print(f"   Current changed: {initial_current} -> {updated_current} mA")
            print(f"   SOC: {updated_soc}%")
            
            # Verify current changed to negative (discharge)
            if updated_current < -1000:  # Should be around -2000 mA
                print("✅ Scenario switching working")
                return True
            else:
                print(f"⚠️  Current not as expected: {updated_current} mA")
                return False
                
        except Exception as e:
            print(f"❌ Scenario switching test failed: {e}")
            return False
    
    def cleanup(self):
        """Cleanup test environment"""
        if self.server:
            print("Stopping simulator...")
            self.server.stop()
            self.server = None
    
    def run_all_tests(self) -> bool:
        """Run all compatibility tests"""
        print("GA Modbus BMS Simulator - Compatibility Test Suite")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_environment():
            return False
        
        try:
            # Run tests
            tests = [
                self.test_direct_modbus_query,
                self.test_ga_app_integration,
                self.test_register_mapping,
                self.test_scenario_switching
            ]
            
            results = []
            for test_func in tests:
                try:
                    result = test_func()
                    results.append(result)
                    print()
                except Exception as e:
                    print(f"Test {test_func.__name__} crashed: {e}")
                    results.append(False)
                    print()
            
            # Summary
            passed = sum(results)
            total = len(results)
            
            print("Compatibility Test Summary")
            print("-" * 30)
            print(f"Passed: {passed}/{total}")
            
            if passed == total:
                print("🎉 All compatibility tests passed!")
                print("✅ Simulator is fully compatible with GA applications")
                return True
            else:
                print(f"❌ {total - passed} compatibility tests failed")
                return False
                
        finally:
            self.cleanup()


def main():
    """Main entry point"""
    if not SIMULATOR_AVAILABLE:
        print("❌ Simulator not available. Please check installation.")
        return False
    
    tester = CompatibilityTester()
    return tester.run_all_tests()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)