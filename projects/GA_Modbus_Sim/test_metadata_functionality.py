#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for metadata functionality in standalone logger and dashboard
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_metadata_structure():
    """Test the metadata structure creation"""
    print("\n=== Testing Metadata Structure ===")
    
    # Create a test metadata structure
    test_metadata = {
        "csv_file": {
            "name": "20250720_120000-0573-8765.csv",
            "full_path": "/test/path/20250720_120000-0573-8765.csv"
        },
        "session": {
            "rma_number": "8765",
            "serial_number": "0573",
            "com_port": "COM3",
            "start_timestamp": "2025-07-20T12:00:00",
            "end_timestamp": None,
            "baudrate": 9600,
            "slave_id": 1
        },
        "logging": {
            "interval": 0.5,
            "filter_enabled": True,
            "filter_settings": {
                "window_size": 5,
                "spike_threshold": 2.0
            }
        }
    }
    
    # Validate structure
    required_sections = ['csv_file', 'session', 'logging']
    for section in required_sections:
        if section not in test_metadata:
            print(f"[FAIL] Missing section: {section}")
            return False
    
    print("[PASS] Metadata structure valid")
    print(json.dumps(test_metadata, indent=2))
    return True


def test_dashboard_metadata_loading():
    """Test dashboard metadata loading with mock data"""
    print("\n=== Testing Dashboard Metadata Loading ===")
    
    try:
        from modbus_dashboard import ModbusDashboard
    except ImportError as e:
        print(f"[FAIL] Could not import ModbusDashboard: {e}")
        return False
    
    # Create temporary test files
    with tempfile.TemporaryDirectory() as temp_dir:
        csv_file = Path(temp_dir) / "test_20250720_120000-0573-8765.csv"
        metadata_file = csv_file.with_suffix('.json')
        
        # Create test CSV file
        with open(csv_file, 'w') as f:
            f.write("Timestamp,afe_cell_volt1,afe_cell_volt2\n")
            f.write("2025-07-20T12:00:00,3234,3235\n")
        
        # Create test metadata file
        test_metadata = {
            "csv_file": {
                "name": "test_20250720_120000-0573-8765.csv",
                "full_path": str(csv_file.absolute())
            },
            "session": {
                "rma_number": "8765",
                "serial_number": "0573",
                "com_port": "COM3",
                "start_timestamp": "2025-07-20T12:00:00",
                "end_timestamp": "2025-07-20T12:05:00",
                "baudrate": 9600,
                "slave_id": 1
            },
            "logging": {
                "interval": 0.5,
                "filter_enabled": True,
                "filter_settings": {
                    "window_size": 5,
                    "spike_threshold": 2.0
                }
            }
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(test_metadata, f, indent=2)
        
        # Test dashboard creation (mock matplotlib to avoid display issues)
        with patch('modbus_dashboard.MATPLOTLIB_AVAILABLE', False):
            try:
                dashboard = ModbusDashboard(str(csv_file))
                
                # Check if metadata was loaded
                if dashboard.metadata:
                    print("[PASS] Metadata loaded successfully")
                    
                    # Verify data from metadata
                    print(f"  COM Port: {dashboard.com_port}")
                    print(f"  Serial Number: {dashboard.serial_number}")
                    print(f"  RMA Number: {dashboard.rma_number}")
                    
                    # Verify specific values
                    if dashboard.com_port == "COM3":
                        print("[PASS] COM port from metadata")
                    else:
                        print(f"[FAIL] Wrong COM port: {dashboard.com_port}")
                        return False
                        
                    if dashboard.serial_number == "0573":
                        print("[PASS] Serial number from metadata")
                    else:
                        print(f"[FAIL] Wrong serial number: {dashboard.serial_number}")
                        return False
                        
                    if dashboard.rma_number == "8765":
                        print("[PASS] RMA number from metadata")
                    else:
                        print(f"[FAIL] Wrong RMA number: {dashboard.rma_number}")
                        return False
                    
                    return True
                else:
                    print("[FAIL] Metadata not loaded")
                    return False
                    
            except Exception as e:
                print(f"[FAIL] Error creating dashboard: {e}")
                return False


def test_imports():
    """Test that required modules can be imported"""
    print("\n=== Testing Module Imports ===")
    
    try:
        from modbus_standalone_logger import StandaloneModbusLogger
        print("[PASS] StandaloneModbusLogger imported")
    except ImportError as e:
        print(f"[FAIL] Could not import StandaloneModbusLogger: {e}")
        return False
    
    try:
        from modbus_dashboard import ModbusDashboard
        print("[PASS] ModbusDashboard imported")
    except ImportError as e:
        print(f"[FAIL] Could not import ModbusDashboard: {e}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("Testing Metadata Functionality - Phase 1 Implementation")
    print("=" * 60)
    
    # Test imports
    test1_passed = test_imports()
    
    # Test metadata structure
    test2_passed = test_metadata_structure()
    
    # Test dashboard loading (with mock)
    test3_passed = test_dashboard_metadata_loading()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"  Module Imports:    {'[PASS] PASSED' if test1_passed else '[FAIL] FAILED'}")
    print(f"  Metadata Structure: {'[PASS] PASSED' if test2_passed else '[FAIL] FAILED'}")
    print(f"  Dashboard Loading: {'[PASS] PASSED' if test3_passed else '[FAIL] FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n[PASS] All Phase 1 tests passed!")
        print("\nTo test with real data:")
        print("1. Run: python -m src.modbus_standalone_logger --port COM3 --serial-number 0573 --rma-number 8765")
        print("2. Stop logging after a few seconds")
        print("3. Check for .json metadata file alongside the .csv file")
        print("4. Run: python -m src.modbus_dashboard <csv_file> to see metadata in dashboard")
        return 0
    else:
        print("\n[FAIL] Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())