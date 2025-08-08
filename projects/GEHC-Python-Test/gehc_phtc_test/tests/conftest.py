"""Pytest configuration and fixtures for GEHC PHTC tests."""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import Mock, MagicMock
import pytest


# Test Data Fixtures
@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Sample configuration data for testing."""
    return {
        "communication": {
            "port": "/dev/ttyUSB0",
            "baudrate": 9600,
            "timeout": 1.0,
            "max_retries": 3,
            "retry_delay": 0.1
        },
        "protocol": {
            "slave_address": 0x01,
            "crc_polynomial": 0x07,
            "message_timeout": 2.0
        },
        "commands": {
            "enabled": ["read_temperature", "read_pressure", "read_status"],
            "intervals": {
                "read_temperature": 1.0,
                "read_pressure": 2.0,
                "read_status": 5.0
            }
        },
        "display": {
            "theme": "dark",
            "update_interval": 0.5,
            "show_raw_data": False,
            "log_level": "INFO"
        },
        "data_scaling": {
            "temperature": {
                "scale": 0.1,
                "offset": -40,
                "unit": "°C"
            },
            "pressure": {
                "scale": 0.01,
                "offset": 0,
                "unit": "bar"
            },
            "voltage": {
                "scale": 0.001,
                "offset": 0,
                "unit": "V"
            }
        }
    }


@pytest.fixture
def temp_config_file(sample_config: Dict[str, Any]) -> Generator[Path, None, None]:
    """Create a temporary configuration file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_config, f, indent=2)
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def invalid_config_file() -> Generator[Path, None, None]:
    """Create a temporary invalid configuration file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json content }")
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    temp_path.unlink(missing_ok=True)


# Mock Serial Port Fixture
@pytest.fixture
def mock_serial_port() -> Mock:
    """Mock serial port for testing serial communication."""
    mock_port = Mock()
    mock_port.is_open = True
    mock_port.in_waiting = 0
    mock_port.out_waiting = 0
    mock_port.baudrate = 9600
    mock_port.timeout = 1.0
    mock_port.write.return_value = 8  # Default bytes written
    mock_port.read.return_value = b''
    mock_port.readline.return_value = b''
    mock_port.reset_input_buffer.return_value = None
    mock_port.reset_output_buffer.return_value = None
    mock_port.close.return_value = None
    mock_port.open.return_value = None
    return mock_port


# PHTC Device Response Fixtures
@pytest.fixture
def phtc_temperature_response() -> bytes:
    """Sample PHTC temperature response message."""
    # Message format: [Address][Function][Data][CRC8]
    # Temperature reading: 25.6°C (raw value: 656 = 0x0290)
    return bytes([0x01, 0x03, 0x02, 0x90, 0x00, 0x4F])  # CRC calculated


@pytest.fixture
def phtc_pressure_response() -> bytes:
    """Sample PHTC pressure response message."""
    # Pressure reading: 1.23 bar (raw value: 123 = 0x007B)
    return bytes([0x01, 0x04, 0x00, 0x7B, 0x00, 0x8C])  # CRC calculated


@pytest.fixture
def phtc_status_response() -> bytes:
    """Sample PHTC status response message."""
    # Status: Normal operation (0x0001)
    return bytes([0x01, 0x05, 0x00, 0x01, 0x00, 0x55])  # CRC calculated


@pytest.fixture
def phtc_error_response() -> bytes:
    """Sample PHTC error response message."""
    # Error code: Invalid function (0x81)
    return bytes([0x01, 0x81, 0x02, 0x00, 0xC1])


@pytest.fixture
def corrupted_message() -> bytes:
    """Corrupted message with invalid CRC."""
    return bytes([0x01, 0x03, 0x02, 0x90, 0x00, 0xFF])  # Wrong CRC


# Test Command Fixtures
@pytest.fixture
def sample_test_commands() -> Dict[str, Dict[str, Any]]:
    """Sample test commands for various PHTC operations."""
    return {
        "read_temperature": {
            "command": bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x01]),
            "expected_response_length": 6,
            "data_type": "int16",
            "scaling": {"scale": 0.1, "offset": -40}
        },
        "read_pressure": {
            "command": bytes([0x01, 0x04, 0x00, 0x02, 0x00, 0x01]),
            "expected_response_length": 6,
            "data_type": "uint16",
            "scaling": {"scale": 0.01, "offset": 0}
        },
        "read_status": {
            "command": bytes([0x01, 0x05, 0x00, 0x03, 0x00, 0x01]),
            "expected_response_length": 6,
            "data_type": "uint16",
            "scaling": {"scale": 1, "offset": 0}
        },
        "read_voltage": {
            "command": bytes([0x01, 0x06, 0x00, 0x04, 0x00, 0x01]),
            "expected_response_length": 6,
            "data_type": "uint16",
            "scaling": {"scale": 0.001, "offset": 0}
        }
    }


# CRC8 Test Data Fixture
@pytest.fixture
def crc8_test_vectors() -> list[tuple[bytes, int]]:
    """Test vectors for CRC8 validation."""
    return [
        (b'', 0x00),
        (b'\x01', 0x07),
        (b'\x01\x02', 0x0D),
        (b'\x01\x02\x03', 0x0A),
        (b'\x01\x03\x00\x01\x00\x01', 0x8B),  # read_temperature command
        (b'\x01\x04\x00\x02\x00\x01', 0x9A),  # read_pressure command
        (b'\x01\x05\x00\x03\x00\x01', 0xEB),  # read_status command
    ]


# Performance Test Fixtures
@pytest.fixture
def performance_test_data() -> Dict[str, Any]:
    """Data for performance testing."""
    return {
        "message_count": 1000,
        "max_response_time_ms": 100,
        "max_processing_time_ms": 50,
        "expected_throughput_msgs_per_sec": 100
    }


# Error Scenario Fixtures
@pytest.fixture
def error_scenarios() -> Dict[str, Dict[str, Any]]:
    """Various error scenarios for testing."""
    return {
        "timeout": {
            "description": "Communication timeout",
            "mock_behavior": "timeout",
            "expected_exception": "TimeoutError"
        },
        "invalid_crc": {
            "description": "Invalid CRC in response",
            "mock_behavior": "invalid_crc",
            "expected_exception": "CRCError"
        },
        "device_error": {
            "description": "Device returns error code",
            "mock_behavior": "device_error",
            "expected_exception": "DeviceError"
        },
        "connection_lost": {
            "description": "Serial connection lost",
            "mock_behavior": "connection_lost",
            "expected_exception": "ConnectionError"
        },
        "invalid_response_length": {
            "description": "Response message too short/long",
            "mock_behavior": "invalid_length",
            "expected_exception": "MessageLengthError"
        }
    }


# Mock Rich Console for Display Testing
@pytest.fixture
def mock_rich_console() -> Mock:
    """Mock Rich console for display testing."""
    console = Mock()
    console.print = Mock()
    console.status = MagicMock()
    console.progress = MagicMock()
    console.rule = Mock()
    console.clear = Mock()
    return console


# Timing Test Fixture
@pytest.fixture
def timing_requirements() -> Dict[str, float]:
    """Timing requirements for performance testing."""
    return {
        "command_response_max_ms": 100,
        "message_processing_max_ms": 10,
        "display_update_max_ms": 50,
        "config_load_max_ms": 100
    }