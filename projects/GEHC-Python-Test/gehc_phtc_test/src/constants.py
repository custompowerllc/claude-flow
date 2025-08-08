#!/usr/bin/env python3
"""
Constants and protocol specifications for GEHC PHTC Test Application.

This module defines all protocol constants, command mappings, error codes,
and configuration defaults used throughout the application.
"""

from typing import Dict, List, Tuple, Any
from enum import IntEnum

# GEHC Protocol Constants

class GEHCProtocol:
    """GEHC RS422 Protocol constants and specifications."""
    
    # Message Structure Constants
    PREAMBLE = 0xAA                    # GE Healthcare Protocol identifier
    SYNC_HOST_TO_BATTERY = 0x23        # Host to Battery direction
    SYNC_BATTERY_TO_HOST = 0x40        # Battery to Host direction
    
    # CRC Constants
    CRC8_POLYNOMIAL = 0x07             # SMBus PEC polynomial
    CRC8_INITIAL_VALUE = 0x00          # Initial CRC value
    
    # Message Length Constants
    MIN_MESSAGE_LENGTH = 5             # Preamble + Sync + CMD + LEN + CRC
    MAX_MESSAGE_LENGTH = 37            # Max with 32 data bytes
    MAX_DATA_LENGTH = 32               # Maximum data payload
    HEADER_LENGTH = 4                  # Preamble + Sync + CMD + LEN
    CRC_LENGTH = 1                     # CRC8 checksum
    
    # Command Ranges
    MIN_COMMAND_CODE = 0x00
    MAX_COMMAND_CODE = 0xFF
    
    # Communication Timing
    DEFAULT_TIMEOUT_MS = 1000          # Default response timeout
    MIN_INTER_COMMAND_DELAY = 0.1      # Minimum delay between commands (seconds)
    MAX_INTER_COMMAND_DELAY = 10.0     # Maximum delay between commands (seconds)
    
    # Serial Communication
    DEFAULT_BAUD_RATE = 115200         # Standard baud rate
    DATA_BITS = 8                      # 8 data bits
    STOP_BITS = 1                      # 1 stop bit
    PARITY = None                      # No parity (8N1)


class ErrorCodes(IntEnum):
    """Standard error codes for GEHC protocol."""
    
    # Success
    SUCCESS = 0x00
    
    # Communication Errors (0x10-0x1F)
    COMM_TIMEOUT = 0x10
    COMM_CRC_ERROR = 0x11
    COMM_INVALID_LENGTH = 0x12
    COMM_INVALID_FORMAT = 0x13
    COMM_BUFFER_OVERFLOW = 0x14
    COMM_UNDERRUN = 0x15
    
    # Protocol Errors (0x20-0x2F)
    PROTO_INVALID_PREAMBLE = 0x20
    PROTO_INVALID_SYNC = 0x21
    PROTO_INVALID_COMMAND = 0x22
    PROTO_COMMAND_NOT_SUPPORTED = 0x23
    PROTO_INVALID_DATA_LENGTH = 0x24
    PROTO_DATA_OUT_OF_RANGE = 0x25
    
    # Device Errors (0x30-0x3F)
    DEVICE_NOT_READY = 0x30
    DEVICE_BUSY = 0x31
    DEVICE_FAULT = 0x32
    DEVICE_CALIBRATION_ERROR = 0x33
    DEVICE_TEMPERATURE_ERROR = 0x34
    DEVICE_VOLTAGE_ERROR = 0x35
    
    # Application Errors (0x40-0x4F)
    APP_CONFIGURATION_ERROR = 0x40
    APP_INITIALIZATION_ERROR = 0x41
    APP_RESOURCE_ERROR = 0x42
    APP_PERMISSION_ERROR = 0x43
    APP_INVALID_STATE = 0x44


# Data Type Specifications

DATA_TYPE_SPECS = {
    "unsigned int": {
        "size": 2,
        "struct_format": "H",  # unsigned short (2 bytes)
        "byte_order": "little",
        "signed": False,
        "min_value": 0,
        "max_value": 65535
    },
    "signed int": {
        "size": 2,
        "struct_format": "h",  # signed short (2 bytes)
        "byte_order": "little", 
        "signed": True,
        "min_value": -32768,
        "max_value": 32767
    },
    "word": {
        "size": 2,
        "struct_format": "H",  # unsigned short (2 bytes)
        "byte_order": "little",
        "signed": False,
        "min_value": 0,
        "max_value": 65535
    },
    "Boolean": {
        "size": 2,
        "struct_format": "H",  # treated as unsigned short
        "byte_order": "little",
        "signed": False,
        "converter": lambda x: bool(x),
        "min_value": 0,
        "max_value": 1
    },
    "string": {
        "size": "variable",
        "struct_format": "s",  # string format
        "byte_order": None,
        "signed": None,
        "encoding": "ascii"
    },
    "block data": {
        "size": "variable",
        "struct_format": "raw",  # raw bytes
        "byte_order": None,
        "signed": None
    }
}


# Command Categories and Groups

COMMAND_CATEGORIES = {
    "basic_monitoring": {
        "description": "Basic battery monitoring commands",
        "commands": ["0x08", "0x09", "0x0A", "0x0D", "0x0F", "0x10"],
        "priority": "high",
        "implementation_status": "100%"
    },
    "cell_voltages": {
        "description": "Individual cell voltage monitoring", 
        "commands": ["0x3C", "0x3D", "0x3E", "0x3F", "0x40", "0x41", "0x42", "0x43", "0x44", "0x45", "0x46", "0x47", "0x48"],
        "priority": "high",
        "implementation_status": "100%"
    },
    "temperature_sensors": {
        "description": "Temperature monitoring sensors",
        "commands": ["0x08", "0x49", "0x4A", "0x4B", "0x4C", "0x4D", "0x4E", "0x4F"],
        "priority": "medium",
        "implementation_status": "87.5%"
    },
    "safety_protection": {
        "description": "Safety and protection status",
        "commands": ["0x4A", "0x4B", "0x4C"],
        "priority": "high", 
        "implementation_status": "100%"
    },
    "device_info": {
        "description": "Device identification and information",
        "commands": ["0x1C", "0x20", "0x21", "0x17", "0x18", "0x19", "0x1A"],
        "priority": "low",
        "implementation_status": "75%"
    },
    "extended_smbus": {
        "description": "Extended SMBus protocol commands",
        "commands": ["0x0B", "0x0C", "0x14", "0x15", "0x16"],
        "priority": "medium",
        "implementation_status": "60%"
    },
    "predictive_algorithms": {
        "description": "Predictive time and capacity algorithms",
        "commands": ["0x04", "0x05", "0x06", "0x07", "0x11", "0x12", "0x13"],
        "priority": "low",
        "implementation_status": "0%"
    }
}


# Unit Conversion and Scaling

UNIT_CONVERSIONS = {
    "mV": {"base_unit": "V", "multiplier": 0.001, "precision": 0},
    "mA": {"base_unit": "A", "multiplier": 0.001, "precision": 0},
    "mAh": {"base_unit": "Ah", "multiplier": 0.001, "precision": 0},
    "mWh": {"base_unit": "Wh", "multiplier": 0.001, "precision": 1},
    "°C": {"base_unit": "°C", "multiplier": 1.0, "precision": 1},
    "K": {"base_unit": "K", "multiplier": 1.0, "precision": 1},
    "%": {"base_unit": "%", "multiplier": 1.0, "precision": 1},
    "minutes": {"base_unit": "min", "multiplier": 1.0, "precision": 0},
    "seconds": {"base_unit": "s", "multiplier": 1.0, "precision": 0},
    "10mW": {"base_unit": "mW", "multiplier": 10.0, "precision": 0}
}


# Common Command Specifications
# Note: This is a subset - full command table loaded from JSON

CORE_COMMANDS = {
    "0x08": {
        "name": "Temperature_1",
        "description": "Returns the cell-pack's internal temperature (°C)",
        "datatype": "unsigned int",
        "unit": "°C", 
        "granularity": 1.0,
        "range": "-40 to 120",
        "byte_count": 2,
        "category": "basic_monitoring"
    },
    "0x09": {
        "name": "Voltage", 
        "description": "Returns the cell-pack voltage (mV)",
        "datatype": "unsigned int",
        "unit": "mV",
        "granularity": 10.0,
        "range": "0 to 65535", 
        "byte_count": 2,
        "category": "basic_monitoring"
    },
    "0x0A": {
        "name": "Current",
        "description": "Returns the cell-pack current (mA)", 
        "datatype": "signed int",
        "unit": "mA",
        "granularity": 100.0,
        "range": "-32768 to 32767",
        "byte_count": 2,
        "category": "basic_monitoring"
    },
    "0x0D": {
        "name": "RelativeStateOfCharge",
        "description": "Returns the predicted remaining battery capacity (%)",
        "datatype": "unsigned int", 
        "unit": "%",
        "granularity": 1.0,
        "range": "0 to 100",
        "byte_count": 2,
        "category": "basic_monitoring"
    }
}


# Test Profile Defaults

DEFAULT_TEST_PROFILES = {
    "quick_test": {
        "description": "Fast test of core implemented commands only",
        "enabled_groups": ["basic_monitoring"],
        "max_commands": 10,
        "timeout_multiplier": 1.0,
        "expect_failures": False
    },
    "full_implemented": {
        "description": "Test all currently implemented commands",
        "enabled_groups": ["basic_monitoring", "cell_voltages", "safety_protection", "device_info"],
        "max_commands": 50,
        "timeout_multiplier": 1.2,
        "expect_failures": False
    },
    "development_test": {
        "description": "Include not-yet-implemented commands for development testing",
        "enabled_groups": ["basic_monitoring", "predictive_algorithms", "extended_smbus"],
        "max_commands": 20,
        "timeout_multiplier": 2.0,
        "expect_failures": True
    },
    "comprehensive": {
        "description": "Complete protocol test including all commands",
        "enabled_groups": list(COMMAND_CATEGORIES.keys()),
        "max_commands": 100,
        "timeout_multiplier": 1.5,
        "expect_failures": True
    }
}


# Serial Port Configurations

SERIAL_PORT_CONFIGS = {
    "windows": {
        "default_ports": ["COM1", "COM2", "COM3", "COM4", "COM5"],
        "port_pattern": r"COM\d+",
        "description_keywords": ["USB", "RS422", "Serial"]
    },
    "linux": {
        "default_ports": ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyS0"],
        "port_pattern": r"/dev/tty(USB|ACM|S)\d+",
        "description_keywords": ["USB", "RS422", "Serial", "FTDI"]
    },
    "macos": {
        "default_ports": ["/dev/tty.usbserial", "/dev/cu.usbserial", "/dev/tty.SLAB_USBtoUART"],
        "port_pattern": r"/dev/(tty|cu)\.(usb|SLAB)",
        "description_keywords": ["USB", "RS422", "Serial", "FTDI", "Silicon Labs"]
    }
}


# Performance Benchmarks and Targets

PERFORMANCE_TARGETS = {
    "command_processing_latency_ms": 100,      # Max processing time per command
    "memory_usage_mb": 50,                     # Max memory usage
    "cpu_usage_percent": 25,                   # Max CPU usage
    "commands_per_minute": 10,                 # Throughput target
    "error_recovery_time_ms": 2000,            # Max error recovery time
    "connection_establishment_ms": 5000,       # Max connection time
    "test_session_duration_minutes": 30       # Max single test session
}


# Error Message Templates

ERROR_MESSAGES = {
    ErrorCodes.COMM_TIMEOUT: "Communication timeout - device did not respond within {timeout}ms",
    ErrorCodes.COMM_CRC_ERROR: "CRC validation failed - expected {expected:02X}, got {actual:02X}",
    ErrorCodes.COMM_INVALID_LENGTH: "Invalid message length - expected {expected}, got {actual}",
    ErrorCodes.COMM_INVALID_FORMAT: "Invalid message format - {details}",
    ErrorCodes.PROTO_INVALID_PREAMBLE: "Invalid preamble - expected 0xAA, got 0x{actual:02X}",
    ErrorCodes.PROTO_INVALID_SYNC: "Invalid sync header - expected 0x40, got 0x{actual:02X}",
    ErrorCodes.PROTO_INVALID_COMMAND: "Invalid command code - 0x{command:02X} not recognized",
    ErrorCodes.PROTO_COMMAND_NOT_SUPPORTED: "Command 0x{command:02X} not supported by device",
    ErrorCodes.DEVICE_NOT_READY: "Device not ready - check connection and power",
    ErrorCodes.DEVICE_BUSY: "Device busy - retry after delay",
    ErrorCodes.APP_CONFIGURATION_ERROR: "Configuration error - {details}"
}


# Logging Configuration

LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20, 
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}

LOG_FORMATTERS = {
    "console": {
        "format": "%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S"
    },
    "file": {
        "format": "%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S.%f"
    },
    "json": {
        "format": "json",
        "fields": ["timestamp", "level", "logger", "message", "module", "function", "line"]
    }
}


# Rich Display Configuration

RICH_THEMES = {
    "default": {
        "success": "bold green",
        "warning": "bold yellow", 
        "error": "bold red",
        "info": "bold blue",
        "highlight": "bold cyan",
        "data": "white",
        "header": "bold magenta"
    },
    "dark": {
        "success": "bright_green",
        "warning": "bright_yellow",
        "error": "bright_red", 
        "info": "bright_blue",
        "highlight": "bright_cyan",
        "data": "bright_white",
        "header": "bright_magenta"
    }
}

PROGRESS_STYLES = {
    "spinner": ["dots", "dots2", "dots3", "line", "pipe", "simpleDots", "arc"],
    "bar": ["bar", "bar.complete", "bar.finished", "bar.pulse"],
    "columns": ["description", "bar", "percentage", "time_remaining"]
}


# File and Directory Defaults

DEFAULT_PATHS = {
    "config_dir": "config",
    "logs_dir": "logs", 
    "data_dir": "data",
    "temp_dir": "temp",
    "config_files": {
        "main": "config.json",
        "commands": "commands.json", 
        "profiles": "command_profiles.json"
    },
    "log_files": {
        "main": "gehc_phtc_test.log",
        "communication": "communication.log",
        "errors": "errors.log"
    }
}


# Export all constants and specifications

__all__ = [
    # Protocol Constants
    'GEHCProtocol', 'ErrorCodes',
    
    # Data Specifications
    'DATA_TYPE_SPECS', 'UNIT_CONVERSIONS',
    
    # Command Organization
    'COMMAND_CATEGORIES', 'CORE_COMMANDS', 'DEFAULT_TEST_PROFILES',
    
    # System Configuration
    'SERIAL_PORT_CONFIGS', 'PERFORMANCE_TARGETS',
    
    # Error Handling
    'ERROR_MESSAGES',
    
    # Logging and Display
    'LOG_LEVELS', 'LOG_FORMATTERS', 'RICH_THEMES', 'PROGRESS_STYLES',
    
    # File System
    'DEFAULT_PATHS'
]