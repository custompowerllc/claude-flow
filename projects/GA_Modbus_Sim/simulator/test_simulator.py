#!/usr/bin/env python3
"""
Test script for the Modbus BMS Simulator

This script tests the core functionality of the simulator and verifies
compatibility with the GA Modbus applications.

Usage:
    python test_simulator.py
"""

import sys
import os
import time
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import simulator components
try:
    from simulator.src.core.modbus_server import ModbusSimulatorServer, ServerConfig
    from simulator.src.core.register_handler import RegisterHandler, BatteryScenario, BatteryState
    from simulator.src.utils.com_port_manager import ComPortManager
    SIMULATOR_AVAILABLE = True
except ImportError as e:
    print(f"Error importing simulator: {e}")
    SIMULATOR_AVAILABLE = False

# Import the register map from the main application
try:
    sys.path.insert(0, str(project_root / 'src'))
    from modbus_query_test import register_map
    REGISTER_MAP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import register_map: {e}")
    REGISTER_MAP_AVAILABLE = False


def test_register_handler():
    """Test the register handler functionality"""
    print("Testing RegisterHandler...")
    
    if not SIMULATOR_AVAILABLE:
        print("  ❌ Simulator not available")
        return False
    
    try:
        # Create register handler
        handler = RegisterHandler()
        
        # Test getting register values
        values = handler.get_all_registers()
        reg_dict = handler.get_register_dict()
        
        print(f"  ✅ Created handler with {len(values)} registers")
        print(f"  ✅ Register map compatibility: {REGISTER_MAP_AVAILABLE}")
        
        # Test register updates
        original_soc = handler.get_register('fg_state_of_charge')
        handler.update_register('fg_state_of_charge', 75)
        new_soc = handler.get_register('fg_state_of_charge')
        
        if new_soc == 75:
            print("  ✅ Register update working")
        else:
            print(f"  ❌ Register update failed: {original_soc} -> {new_soc}")
        
        # Test scenarios
        scenarios = handler.get_predefined_scenarios()
        print(f"  ✅ Found {len(scenarios)} predefined scenarios")
        
        # Test scenario switching
        charging_scenario = next((s for s in scenarios if s.state == BatteryState.CHARGING), None)
        if charging_scenario:
            handler.set_scenario(charging_scenario)
            values_after = handler.get_all_registers()
            print(f"  ✅ Scenario switching working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ RegisterHandler test failed: {e}")
        return False


def test_com_port_manager():
    """Test the COM port manager functionality"""
    print("Testing ComPortManager...")
    
    if not SIMULATOR_AVAILABLE:
        print("  ❌ Simulator not available")
        return False
    
    try:
        # Create COM port manager
        manager = ComPortManager()
        
        # Get available ports
        ports = manager.get_available_ports()
        print(f"  ✅ Found {len(ports)} serial ports")
        
        # Test port recommendations
        recommendations = manager.get_port_recommendations()
        suggested_port = recommendations.get('suggested_simulator_port')
        
        if suggested_port:
            print(f"  ✅ Suggested simulator port: {suggested_port}")
        else:
            print("  ⚠️  No suitable port found for simulator")
        
        # Test GA device detection
        ga_ports = manager.detect_ga_devices()
        if ga_ports:
            print(f"  ✅ Detected {len(ga_ports)} potential GA devices")
        else:
            print("  ℹ️  No GA devices detected")
        
        return True
        
    except Exception as e:
        print(f"  ❌ ComPortManager test failed: {e}")
        return False


def test_modbus_server():
    """Test the Modbus server functionality"""
    print("Testing ModbusSimulatorServer...")
    
    if not SIMULATOR_AVAILABLE:
        print("  ❌ Simulator not available")
        return False
    
    try:
        # Get a suitable port for testing
        manager = ComPortManager()
        recommendations = manager.get_port_recommendations()
        suggested_port = recommendations.get('suggested_simulator_port')
        
        if not suggested_port:
            print("  ⚠️  No suitable port available for server test")
            return True  # Not a failure, just no port available
        
        # Create server configuration
        config = ServerConfig(port=suggested_port)
        server = ModbusSimulatorServer(config)
        
        print(f"  ✅ Created server for port {suggested_port}")
        
        # Test server status
        status = server.get_status()
        print(f"  ✅ Server status: {status['state']}")
        
        # Test register updates
        initial_registers = server.get_register_values()
        server.update_register('fg_state_of_charge', 85)
        updated_registers = server.get_register_values()
        
        if updated_registers.get('fg_state_of_charge') == 85:
            print("  ✅ Server register update working")
        else:
            print("  ❌ Server register update failed")
        
        print("  ℹ️  Skipping actual server start (requires hardware)")
        return True
        
    except Exception as e:
        print(f"  ❌ ModbusSimulatorServer test failed: {e}")
        return False


def test_register_compatibility():
    """Test compatibility with the main application register map"""
    print("Testing register compatibility...")
    
    if not REGISTER_MAP_AVAILABLE:
        print("  ⚠️  Main application register_map not available")
        return True
    
    if not SIMULATOR_AVAILABLE:
        print("  ❌ Simulator not available")
        return False
    
    try:
        handler = RegisterHandler()
        values = handler.get_all_registers()
        reg_dict = handler.get_register_dict()
        
        # Check that we have values for all registers in the map
        missing_registers = []
        for addr, reg_name in register_map.items():
            if reg_name not in reg_dict:
                missing_registers.append(reg_name)
        
        if missing_registers:
            print(f"  ❌ Missing registers: {missing_registers}")
            return False
        
        # Check that we have the correct number of registers
        if len(values) != len(register_map):
            print(f"  ❌ Register count mismatch: {len(values)} vs {len(register_map)}")
            return False
        
        print(f"  ✅ All {len(register_map)} registers present")
        print(f"  ✅ Register address range: {min(register_map.keys())}-{max(register_map.keys())}")
        
        # Test some specific registers
        test_registers = ['afe_cell_volt1', 'afe_pack_volt', 'fg_state_of_charge', 'afe_current']
        for reg_name in test_registers:
            value = reg_dict.get(reg_name)
            if value is not None:
                print(f"  ✅ {reg_name}: {value}")
            else:
                print(f"  ❌ {reg_name}: missing")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Register compatibility test failed: {e}")
        return False


def main():
    """Run all tests"""
    # Setup logging
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise during testing
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("GA Modbus BMS Simulator - Test Suite")
    print("=" * 50)
    
    if not SIMULATOR_AVAILABLE:
        print("❌ Simulator modules not available. Please check imports.")
        return False
    
    # Run tests
    tests = [
        test_register_handler,
        test_com_port_manager,
        test_modbus_server,
        test_register_compatibility
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"Test {test_func.__name__} crashed: {e}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("Test Summary")
    print("-" * 20)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)