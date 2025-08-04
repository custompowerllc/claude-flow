#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Modbus BMS Simulator tests

This module provides shared test fixtures, configuration, and utilities
for all test modules in the simulator test suite.
"""

import pytest
import tempfile
import os
import shutil
from unittest.mock import MagicMock
import sys
import time

# Add src path for imports
test_dir = os.path.dirname(__file__)
project_root = os.path.dirname(os.path.dirname(test_dir))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)


@pytest.fixture
def temp_directory():
    """Provide a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_register_map():
    """Provide the standard BMS register mapping"""
    return {
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


@pytest.fixture
def realistic_bms_data():
    """Provide realistic BMS data for testing"""
    return {
        # Cell voltages (8S LiFePO4)
        10: 3285, 11: 3287, 12: 3283, 13: 3289,
        14: 3281, 15: 3286, 16: 3284, 17: 3288,
        
        # Pack voltage (sum of cells)
        18: 26283,
        
        # Cell delta
        19: 8,
        
        # Temperatures
        20: 285,  # 28.5°C
        21: 287,  # 28.7°C
        
        # Current
        22: -2500,  # -2.5A discharge
        
        # AFE configuration
        23: 1000,  # ADC gain
        24: 0,     # ADC offset
        25: 3650,  # OV limit
        26: 2500,  # UV limit
        
        # Fuel gauge data
        27: 75,    # SOC 75%
        28: 26283, # FG voltage
        29: -2480, # FG current
        30: 285,   # FG temperature
        31: 60000, # Remaining capacity
        32: 80000, # Full capacity
        33: 80000, # Design capacity
        34: -2500, # Average current
        35: 1440,  # Time to empty
        36: 0,     # Time to full
        37: 285,   # Internal temp
        38: 450,   # Cycle count
        39: 98,    # SOH
        40: 26283, # Charging voltage
        41: 0,     # Charging current
        42: 350,   # Lifetime max temp
        43: 100,   # Lifetime min temp
        44: 5000,  # Lifetime max charge
        45: 12000  # Lifetime max discharge
    }


@pytest.fixture
def mock_serial_port():
    """Provide a mock serial port for testing"""
    mock_port = MagicMock()
    mock_port.device = "COM99"
    mock_port.description = "Mock Test Port"
    mock_port.hwid = "USB\\VID_TEST\\PID_TEST"
    return mock_port


@pytest.fixture
def available_test_port():
    """Find an available port number for testing"""
    import socket
    
    # Find an available TCP port for testing
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    
    return port


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Automatically cleanup after each test"""
    yield
    
    # Add any global cleanup here
    # For now, just a small delay to ensure proper cleanup
    time.sleep(0.01)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest settings"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "serial: marks tests that require serial port hardware"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Mark integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Mark unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Mark slow tests based on name patterns
        if any(keyword in item.name for keyword in ["stress", "performance", "concurrent"]):
            item.add_marker(pytest.mark.slow)
        
        # Mark serial tests
        if any(keyword in item.name for keyword in ["serial", "com_port", "port"]):
            item.add_marker(pytest.mark.serial)


# Custom test utilities
class TestUtils:
    """Utility functions for tests"""
    
    @staticmethod
    def validate_bms_register_value(register_addr, value):
        """Validate that a BMS register value is within expected range"""
        ranges = {
            # Cell voltages (10-17)
            **{addr: (2500, 3650) for addr in range(10, 18)},
            # Pack voltage (18)
            18: (20000, 29200),
            # Cell delta (19)
            19: (0, 500),
            # Temperatures (20-21)
            20: (-400, 850), 21: (-400, 850),
            # Current (22)
            22: (-50000, 50000),
            # SOC (27)
            27: (0, 100),
            # SOH (39)
            39: (0, 100),
        }
        
        if register_addr in ranges:
            min_val, max_val = ranges[register_addr]
            return min_val <= value <= max_val
        
        # Default range for 16-bit signed integer
        return -32768 <= value <= 32767
    
    @staticmethod
    def create_test_csv_data():
        """Create test CSV data in GA app format"""
        import csv
        import io
        from datetime import datetime
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        header = ['Timestamp'] + [
            "afe_cell_volt1", "afe_cell_volt2", "afe_cell_volt3", "afe_cell_volt4",
            "afe_cell_volt5", "afe_cell_volt6", "afe_cell_volt7", "afe_cell_volt8",
            "afe_pack_volt", "afe_cell_volt_delta", "afe_temp1", "afe_temp2",
            "afe_current", "afe_adc_gain", "afe_adc_offset", "afe_ov_limit",
            "afe_uv_limit", "fg_state_of_charge", "fg_voltage", "fg_current",
            "fg_temperature", "fg_remaining_capacity", "fg_full_charge_cap",
            "fg_design_capacity", "fg_average_current", "fg_time_to_empty",
            "fg_time_to_full", "fg_internal_temp", "fg_cycle_count",
            "fg_state_of_health", "fg_charging_voltage", "fg_charging_current",
            "fg_lifetime_max_temp", "fg_lifetime_min_temp", "fg_lifetime_max_chg",
            "fg_lifetime_max_dsg"
        ]
        writer.writerow(header)
        
        # Sample data row
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_row = [timestamp, 3285, 3287, 3283, 3289, 3281, 3286, 3284, 3288,
                   26283, 8, 285, 287, -2500, 1000, 0, 3650, 2500, 75, 26283,
                   -2480, 285, 60000, 80000, 80000, -2500, 1440, 0, 285, 450,
                   98, 26283, 0, 350, 100, 5000, 12000]
        writer.writerow(data_row)
        
        return output.getvalue()


# Make TestUtils available to all tests
@pytest.fixture
def test_utils():
    """Provide test utilities"""
    return TestUtils