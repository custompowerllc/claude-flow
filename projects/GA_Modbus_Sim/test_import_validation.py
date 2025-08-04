#!/usr/bin/env python3
"""
Import validation script for GA Modbus Python App
Tests that all import paths work correctly
"""

import sys
import os

def test_register_map_import():
    """Test that register_map can be imported correctly"""
    print("Testing register_map import...")
    
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(script_dir, "src")
    
    # Add src to path
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    try:
        # Import the module
        from modbus_query_test import register_map
        
        print(f"✅ Successfully imported register_map")
        print(f"   - Contains {len(register_map)} registers")
        print(f"   - Address range: {min(register_map.keys())} to {max(register_map.keys())}")
        
        # Validate expected registers
        expected_registers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]
        
        missing_registers = []
        for reg in expected_registers:
            if reg not in register_map:
                missing_registers.append(reg)
        
        if missing_registers:
            print(f"❌ Missing registers: {missing_registers}")
            return False
        else:
            print("✅ All expected registers (10-45) are present")
            return True
            
    except ImportError as e:
        print(f"❌ Failed to import register_map: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_dependencies():
    """Test that required dependencies are available"""
    print("\nTesting dependencies...")
    
    deps = [
        ("pymodbus", "pymodbus"),
        ("pyserial", "serial")  # Package name vs import name
    ]
    
    for dep_name, import_name in deps:
        try:
            module = __import__(import_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {dep_name}: version {version}")
        except ImportError:
            print(f"❌ {dep_name}: not installed")
            return False
    
    return True

def main():
    """Main validation function"""
    print("=" * 50)
    print("GA Modbus Python App - Import Validation")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    # Test dependencies
    if test_dependencies():
        tests_passed += 1
    
    # Test register map import
    if test_register_map_import():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All import tests PASSED!")
        return True
    else:
        print("❌ Some tests FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)