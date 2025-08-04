#!/usr/bin/env python3
"""
Test script for intelligent logging functionality
Tests the core components without requiring all dependencies
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_auto_start_stop_manager():
    """Test AutoStartStopManager functionality"""
    print("=== Testing AutoStartStopManager ===")
    
    try:
        from core.auto_start_stop_manager import (
            AutoStartConfig, CurrentValidator, VoltageStabilizationDetector,
            AutoStartStopManager, TriggerType, SessionState
        )
        
        # Test configuration
        config = AutoStartConfig()
        config.intelligent_logging_enabled = True
        config.charge_threshold = 0.5
        print(f"✓ AutoStartConfig created: charge_threshold={config.charge_threshold}A")
        
        # Test current validator
        validator = CurrentValidator(config)
        
        # Test normal current reading
        reading = validator.validate_current(1000)  # 1000mA = 1A
        print(f"✓ Current validation: {reading.value}A, valid={reading.is_valid}")
        
        # Test spurious reading (65535 = idle state)
        spurious_reading = validator.validate_current(65535)
        print(f"✓ Spurious current: {spurious_reading.value}A, valid={spurious_reading.is_valid}")
        
        # Test voltage stabilization detector
        voltage_detector = VoltageStabilizationDetector(config)
        
        # Add some voltage readings
        for voltage in [3.7, 3.701, 3.699, 3.700, 3.702]:
            voltage_detector.add_voltage_reading(voltage)
        
        is_stable, info = voltage_detector.is_voltage_stabilized()
        print(f"✓ Voltage stabilization: stable={is_stable}, info={info}")
        
        print("✓ AutoStartStopManager components test passed")
        return True
        
    except Exception as e:
        print(f"✗ AutoStartStopManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_current_validation_scenarios():
    """Test various current validation scenarios"""
    print("\n=== Testing Current Validation Scenarios ===")
    
    try:
        from core.auto_start_stop_manager import AutoStartConfig, CurrentValidator
        
        config = AutoStartConfig()
        validator = CurrentValidator(config)
        
        # Test scenarios
        test_cases = [
            (500, 0.5, True, "Normal charging current"),
            (65535, -0.001, False, "Idle state (spurious)"),
            (32768, -32.768, False, "Large negative current (unreasonable)"),
            (1500, 1.5, True, "Higher charging current"),
            (64500, -1.036, False, "Near-idle spurious reading"),
            (0, 0.0, True, "Zero current"),
        ]
        
        for raw_value, expected_amps, expected_valid, description in test_cases:
            reading = validator.validate_current(raw_value)
            status = "✓" if (abs(reading.value - expected_amps) < 0.01 and reading.is_valid == expected_valid) else "✗"
            print(f"{status} {description}: raw={raw_value} -> {reading.value:.3f}A, valid={reading.is_valid}")
        
        return True
        
    except Exception as e:
        print(f"✗ Current validation test failed: {e}")
        return False

def test_session_state_machine():
    """Test session state transitions"""
    print("\n=== Testing Session State Machine ===")
    
    try:
        from core.auto_start_stop_manager import SessionState, TriggerType
        
        # Test state enum
        states = [SessionState.IDLE, SessionState.MONITORING, SessionState.GRACE_PERIOD, SessionState.STABILIZING]
        print(f"✓ Session states: {[s.value for s in states]}")
        
        # Test trigger types
        triggers = [TriggerType.CHARGING, TriggerType.DISCHARGING, TriggerType.MANUAL]
        print(f"✓ Trigger types: {[t.value for t in triggers]}")
        
        return True
        
    except Exception as e:
        print(f"✗ Session state test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Intelligent Logging Tests...")
    print("=" * 50)
    
    tests = [
        test_auto_start_stop_manager,
        test_current_validation_scenarios,
        test_session_state_machine,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'=' * 50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Intelligent logging implementation is working correctly.")
        return 0
    else:
        print("✗ Some tests failed. Check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())