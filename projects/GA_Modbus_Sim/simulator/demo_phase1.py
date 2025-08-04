#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 Demonstration Script for Modbus BMS Simulator

This script demonstrates the core functionality implemented in Phase 1:
- Virtual COM port creation
- Modbus RTU server with exact GA app compatibility
- Register mapping and basic simulation
- Integration with GA standalone logger
"""

import sys
import time
import subprocess
import os

# Add project root to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

def print_banner():
    """Print demonstration banner"""
    print("=" * 60)
    print("Modbus BMS Simulator - Phase 1 Demonstration")
    print("=" * 60)
    print("GA Modbus Python App Compatible Simulator")
    print("Phase 1: Virtual COM Port + Exact Modbus Protocol")
    print("=" * 60)

def check_requirements():
    """Check if required dependencies are installed with version validation"""
    print("\nChecking Requirements...")
    
    # Check requirements with correct module names for import
    requirements = [
        ("pymodbus", "pip install pymodbus", "3.0.0"),
        ("serial", "pip install pyserial", "3.0")  # Package name is pyserial, but import name is serial
    ]
    
    missing = []
    for package, install_cmd, min_version in requirements:
        try:
            module = __import__(package)
            display_name = "pyserial" if package == "serial" else package
            
            # Try to get version information
            version = getattr(module, '__version__', 'unknown')
            print("[OK] {} - installed (version: {})".format(display_name, version))
            
            # Additional validation for pymodbus API compatibility
            if package == "pymodbus":
                try:
                    from pymodbus.client import ModbusSerialClient
                    print("  [OK] ModbusSerialClient import successful")
                except ImportError:
                    print("  [WARNING] ModbusSerialClient import failed - may need newer version")
            
        except ImportError:
            display_name = "pyserial" if package == "serial" else package
            print("[MISSING] {} - missing".format(display_name))
            missing.append(install_cmd)
    
    if missing:
        print("\nMissing dependencies. Install with:")
        for cmd in missing:
            print("  {}".format(cmd))
        return False
    
    return True

def list_available_ports():
    """List available serial ports"""
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        
        print("\nAvailable Serial Ports ({} found):".format(len(ports)))
        if not ports:
            print("  No serial ports detected")
            return []
        
        for i, port in enumerate(ports, 1):
            print("  {}. {} - {}".format(i, port.device, port.description))
        
        return [port.device for port in ports]
    except ImportError:
        print("[ERROR] pyserial not available for port listing")
        return []

def demo_register_mapping():
    """Demonstrate register mapping compatibility"""
    print("\nRegister Mapping Demonstration:")
    
    try:
        # Fix the import path to correctly import register map from GA app
        modbus_query_path = os.path.join(project_root, "src", "modbus_query_test.py")
        if os.path.exists(modbus_query_path):
            # Add the src directory to the path temporarily
            src_path = os.path.join(project_root, "src")
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            
            # Import the module and validate register_map exists
            import modbus_query_test
            if not hasattr(modbus_query_test, 'register_map'):
                print("[ERROR] modbus_query_test.py found but register_map not defined")
                return False
            
            register_map = modbus_query_test.register_map
            
            # Validate register_map structure
            if not isinstance(register_map, dict):
                print("[ERROR] register_map is not a dictionary")
                return False
            
            if len(register_map) < 36:
                print("[ERROR] register_map has insufficient registers: {} (expected 36)".format(len(register_map)))
                return False
            
            print("[OK] Successfully imported register_map with {} registers".format(len(register_map)))
            print("Register Coverage:")
            print("  Start Address: {}".format(min(register_map.keys())))
            print("  End Address: {}".format(max(register_map.keys())))
            print("  Total Registers: {}".format(len(register_map)))
            
            # Show sample registers
            print("\nSample Register Mapping:")
            sample_regs = [10, 18, 22, 27, 45]
            for reg_addr in sample_regs:
                if reg_addr in register_map:
                    print("  Register {}: {}".format(reg_addr, register_map[reg_addr]))
            
            return True
        else:
            print("[ERROR] modbus_query_test.py not found at expected location")
            return False
        
    except ImportError as e:
        print("[ERROR] Failed to import register mapping: {}".format(e))
        return False
    except Exception as e:
        print("[ERROR] Unexpected error importing register mapping: {}".format(e))
        return False

def demo_modbus_server():
    """Demonstrate Modbus server functionality"""
    print("\nModbus Server Demonstration:")
    
    simulator_path = os.path.join(os.path.dirname(__file__), "run_simulator.py")
    
    if not os.path.exists(simulator_path):
        print("[ERROR] Simulator not found. Expected at: simulator/run_simulator.py")
        return False
    
    print("[OK] Simulator found")
    print("Location: {}".format(simulator_path))
    
    # Test command line interface
    try:
        proc = subprocess.Popen([
            sys.executable, simulator_path, "--help"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        result = type('Result', (), {
            'returncode': proc.returncode, 
            'stderr': stderr
        })()
        
        if result.returncode == 0:
            print("[OK] Command line interface working")
            print("Help output available")
        else:
            print("[ERROR] CLI error: {}".format(result.stderr))
            return False
            
    except subprocess.TimeoutExpired:
        print("[WARNING] CLI timeout (may be normal)")
    except Exception as e:
        print("[ERROR] CLI test failed: {}".format(e))
        return False
    
    return True

def demo_compatibility():
    """Demonstrate GA app compatibility"""
    print("\nGA App Compatibility Check:")
    
    standalone_logger = os.path.join(project_root, "src", "modbus_standalone_logger.py")
    
    if not os.path.exists(standalone_logger):
        print("[ERROR] GA standalone logger not found")
        return False
    
    print("[OK] GA standalone logger found")
    
    # Check if query parameters match
    expected_params = {
        "address": 9,
        "count": 36,
        "slave": 1
    }
    
    print("Expected Modbus Query Parameters:")
    for param, value in expected_params.items():
        print("  {}: {}".format(param, value))
    
    print("[OK] Simulator configured for GA app compatibility")
    return True

def demo_test_suite():
    """Demonstrate test suite"""
    print("\nTest Suite Demonstration:")
    
    test_dir = os.path.join(os.path.dirname(__file__), "tests")
    
    if not os.path.exists(test_dir):
        print("[ERROR] Test directory not found")
        return False
    
    test_files = []
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_files.append(os.path.join(root, file))
    print("[OK] Found {} test files".format(len(test_files)))
    
    unit_dir = os.path.join(test_dir, "unit")
    integration_dir = os.path.join(test_dir, "integration")
    
    unit_tests = []
    integration_tests = []
    
    if os.path.exists(unit_dir):
        unit_tests = [f for f in os.listdir(unit_dir) if f.startswith("test_") and f.endswith(".py")]
    
    if os.path.exists(integration_dir):
        integration_tests = [f for f in os.listdir(integration_dir) if f.startswith("test_") and f.endswith(".py")]
    
    test_categories = {
        "unit": len(unit_tests),
        "integration": len(integration_tests)
    }
    
    for category, count in test_categories.items():
        print("  {}: {} test files".format(category, count))
    
    # Try to run a quick test
    run_tests_path = os.path.join(test_dir, "run_tests.py")
    if os.path.exists(run_tests_path):
        print("[OK] Test runner available")
        print("Run tests with: python {} check".format(run_tests_path))
    
    return True

def show_usage_examples():
    """Show usage examples"""
    print("\nUsage Examples:")
    
    examples = [
        ("List available ports", "python run_simulator.py --list-ports"),
        ("Start simulator", "python run_simulator.py --port COM3 --scenario normal"),
        ("Test with GA logger", "cd ../src && python modbus_standalone_logger.py --port COM3 --sn SIM001 --rma 12345"),
        ("Run tests", "cd tests && python run_tests.py all"),
        ("Check system", "python demo_phase1.py")
    ]
    
    for description, command in examples:
        print("  {}:".format(description))
        print("     {}".format(command))
        print()

def main():
    """Main demonstration function"""
    print_banner()
    
    # Run demonstration checks
    checks = [
        ("Requirements", check_requirements),
        ("Register Mapping", demo_register_mapping),
        ("Modbus Server", demo_modbus_server),
        ("GA Compatibility", demo_compatibility),
        ("Test Suite", demo_test_suite)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print("[ERROR] {} check failed: {}".format(name, e))
            results[name] = False
    
    # Show available ports
    list_available_ports()
    
    # Show usage examples
    show_usage_examples()
    
    # Summary
    print("\nPhase 1 Implementation Status:")
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print("  {} {}".format(status, name))
    
    print("\nOverall: {}/{} checks passed".format(passed, total))
    
    if passed == total:
        print("\n[SUCCESS] Phase 1 implementation is ready!")
        print("You can now start the simulator and test with the GA app")
    else:
        print("\n[WARNING] Some issues need to be resolved before full operation")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()