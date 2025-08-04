"""
Test configuration and fixtures for the GA Battery Management System tests.
"""

import pytest
import tempfile
import os
from datetime import datetime
from unittest.mock import Mock


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for test log files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_battery_data():
    """Sample battery data for testing with raw integer values (legacy format)."""
    return {
        'afe_cell_volt1': 3456,  # Raw mV values
        'afe_cell_volt2': 3457,
        'afe_cell_volt3': 3455,
        'afe_cell_volt4': 3458,
        'afe_cell_volt5': 3454,
        'afe_cell_volt6': 3459,
        'afe_cell_volt7': 3456,
        'afe_cell_volt8': 3457,
        'afe_pack_volt': 27652,  # Raw mV
        'afe_cell_volt_delta': 5,  # Raw mV
        'afe_temp1': 25.5,
        'afe_temp2': 26.0,
        'afe_current': 2.345,
        'fg_state_of_charge': 85.5,
        'fg_voltage': 27650,  # Raw mV
        'fg_current': 2.340,
        'fg_temperature': 25.8,
        'fg_remaining_capacity': 68.4,
        'fg_full_charge_cap': 80.0,
        'fg_design_capacity': 80.0,
        'fg_average_current': 2.300,
        'fg_time_to_empty': 1800,
        'fg_time_to_full': 0,
        'fg_internal_temp': 25.5,
        'fg_cycle_count': 125,
        'fg_state_of_health': 98.5,
        'fg_charging_voltage': 29400,  # Raw mV
        'fg_charging_current': 0.0,
        'fg_lifetime_max_temp': 45.0,
        'fg_lifetime_min_temp': -10.0,
        'fg_lifetime_max_chg': 5.0,
        'fg_lifetime_max_dsg': 10.0,
        'timestamp': datetime(2025, 7, 12, 10, 30, 45, 123000)
    }


@pytest.fixture
def mock_modbus_client():
    """Mock Modbus client for testing."""
    mock = Mock()
    mock.connected = True
    mock.connect.return_value = True
    mock.close.return_value = None
    return mock


@pytest.fixture
def sample_csv_file(temp_log_dir, sample_battery_data):
    """Create a sample CSV file for testing."""
    csv_path = os.path.join(temp_log_dir, "test_battery_data.csv")
    
    # Import the CSV writer
    from src.ga_modbus_csv_writer import write_modbus_data_to_csv
    
    # Write sample data
    write_modbus_data_to_csv(sample_battery_data, csv_path)
    
    return csv_path