#!/usr/bin/env python3
"""
Pydantic data models and type definitions for GEHC PHTC Test Application.

This module defines all data structures used throughout the application,
providing type safety, validation, and serialization capabilities.
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from datetime import datetime
from pathlib import Path


class DataType(str, Enum):
    """Supported data types for command responses."""
    UNSIGNED_INT = "unsigned int"
    SIGNED_INT = "signed int"
    WORD = "word"
    BOOLEAN = "Boolean"
    STRING = "string"
    BLOCK_DATA = "block data"


class Priority(str, Enum):
    """Test priority levels for command execution."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConnectionState(str, Enum):
    """Serial connection states."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class ValidationError(str, Enum):
    """Response validation error types."""
    INVALID_CRC = "invalid_crc"
    INVALID_LENGTH = "invalid_length"
    INVALID_FORMAT = "invalid_format"
    OUT_OF_RANGE = "out_of_range"
    TIMEOUT = "timeout"
    MALFORMED_DATA = "malformed_data"
    COMMAND_MISMATCH = "command_mismatch"


class TestStatus(str, Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


# Configuration Models

class SerialConfig(BaseModel):
    """Serial communication configuration."""
    serial_com_port: str = Field(..., description="Serial port identifier (e.g., COM3, /dev/ttyUSB0)")
    baud_rate: int = Field(115200, description="Communication baud rate")
    timeout_ms: int = Field(1000, description="Response timeout in milliseconds") 
    inter_command_delay: float = Field(0.5, description="Delay between commands in seconds")
    retry_count: int = Field(3, description="Number of retry attempts for failed commands")
    command_table_file: str = Field("commands.json", description="Command table filename")
    log_unsupported_commands: bool = Field(True, description="Log unsupported command attempts")
    skip_unsupported_commands: bool = Field(True, description="Skip unsupported commands in execution")
    
    @validator('baud_rate')
    def validate_baud_rate(cls, v):
        """Validate baud rate is a standard value."""
        valid_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800]
        if v not in valid_rates:
            raise ValueError(f"Baud rate must be one of: {valid_rates}")
        return v
    
    @validator('timeout_ms')
    def validate_timeout(cls, v):
        """Validate timeout is reasonable."""
        if v < 100 or v > 30000:
            raise ValueError("Timeout must be between 100ms and 30000ms")
        return v
    
    @validator('inter_command_delay')
    def validate_delay(cls, v):
        """Validate inter-command delay."""
        if v < 0.1 or v > 10.0:
            raise ValueError("Inter-command delay must be between 0.1 and 10.0 seconds")
        return v


class CommandSpec(BaseModel):
    """Individual command specification from command table."""
    name: str = Field(..., description="Human-readable command name")
    description: str = Field(..., description="Detailed command description")
    enabled: bool = Field(True, description="Command enabled for testing")
    implemented: bool = Field(False, description="Command implementation status in firmware")
    datatype: DataType = Field(..., description="Expected response data type")
    unit: str = Field("", description="Physical unit for the measurement")
    range: str = Field("", description="Valid value range specification")
    granularity: float = Field(1.0, description="Scaling granularity/resolution")
    byte_count: int = Field(2, description="Expected response data byte count")
    test_priority: Priority = Field(Priority.MEDIUM, description="Test execution priority level")
    notes: str = Field("", description="Implementation notes and comments")
    
    @validator('granularity')
    def validate_granularity(cls, v):
        """Validate granularity is positive."""
        if v <= 0:
            raise ValueError("Granularity must be positive")
        return v
    
    @validator('byte_count')
    def validate_byte_count(cls, v):
        """Validate byte count is reasonable."""
        if v < 1 or v > 32:
            raise ValueError("Byte count must be between 1 and 32")
        return v


class TestProfile(BaseModel):
    """Test execution profile configuration."""
    description: str = Field(..., description="Profile description and purpose")
    enabled_groups: List[str] = Field(default_factory=list, description="Enabled command groups")
    max_commands: int = Field(100, description="Maximum commands to execute in this profile")
    expect_failures: bool = Field(False, description="Whether to expect some command failures")
    timeout_multiplier: float = Field(1.0, description="Timeout adjustment factor for this profile")
    command_filter: Optional[List[str]] = Field(None, description="Specific commands to include/exclude")
    
    @validator('max_commands')
    def validate_max_commands(cls, v):
        """Validate maximum commands is reasonable."""
        if v < 1 or v > 1000:
            raise ValueError("Max commands must be between 1 and 1000")
        return v
    
    @validator('timeout_multiplier')
    def validate_timeout_multiplier(cls, v):
        """Validate timeout multiplier."""
        if v < 0.1 or v > 10.0:
            raise ValueError("Timeout multiplier must be between 0.1 and 10.0")
        return v


class CommandTable(BaseModel):
    """Complete command table configuration."""
    command_table: Dict[str, CommandSpec] = Field(..., description="Command specifications by hex code")
    command_groups: Dict[str, List[str]] = Field(default_factory=dict, description="Named command groups")
    test_profiles: Dict[str, TestProfile] = Field(default_factory=dict, description="Test execution profiles")
    
    @validator('command_table')
    def validate_command_codes(cls, v):
        """Validate command codes are valid hex strings."""
        for code in v.keys():
            if not code.startswith('0x') or len(code) != 4:
                raise ValueError(f"Command code '{code}' must be 4-character hex string (e.g., '0x08')")
            try:
                int(code, 16)
            except ValueError:
                raise ValueError(f"Command code '{code}' is not valid hexadecimal")
        return v


# Protocol Models

class GEHCMessage(BaseModel):
    """GEHC protocol message structure."""
    preamble: int = Field(0xAA, description="GE Healthcare protocol identifier")
    sync_header: int = Field(0x23, description="Synchronization header (0x23=H2B, 0x40=B2H)")
    command_code: int = Field(..., description="Command code byte")
    data_length: int = Field(0, description="Number of data bytes")
    data: bytes = Field(b'', description="Command/response data payload")
    crc8: int = Field(0, description="CRC8 checksum")
    
    class Config:
        arbitrary_types_allowed = True
    
    @validator('preamble')
    def validate_preamble(cls, v):
        """Validate preamble is correct."""
        if v != 0xAA:
            raise ValueError("Preamble must be 0xAA for GE Healthcare protocol")
        return v
    
    @validator('sync_header')
    def validate_sync_header(cls, v):
        """Validate sync header values."""
        if v not in [0x23, 0x40]:
            raise ValueError("Sync header must be 0x23 (Host to Battery) or 0x40 (Battery to Host)")
        return v
    
    @validator('command_code')
    def validate_command_code(cls, v):
        """Validate command code range."""
        if v < 0 or v > 255:
            raise ValueError("Command code must be between 0 and 255")
        return v
    
    @root_validator
    def validate_data_consistency(cls, values):
        """Validate data length matches actual data."""
        data_length = values.get('data_length', 0)
        data = values.get('data', b'')
        if data_length != len(data):
            raise ValueError(f"Data length ({data_length}) does not match actual data size ({len(data)})")
        return values


# Response Models

class ParsedResponse(BaseModel):
    """Structured response data after parsing and processing."""
    command_code: int = Field(..., description="Command code that generated this response")
    command_name: str = Field(..., description="Human-readable command name")
    raw_value: Any = Field(..., description="Raw extracted value before scaling")
    scaled_value: Optional[float] = Field(None, description="Value after scaling/granularity applied")
    formatted_value: str = Field(..., description="Human-readable formatted value with units")
    unit: str = Field("", description="Physical unit for the measurement")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    valid: bool = Field(..., description="Whether response passed all validation checks")
    errors: List[ValidationError] = Field(default_factory=list, description="Validation errors encountered")
    processing_time_ms: float = Field(0.0, description="Time taken to process response in milliseconds")
    
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True


class ProcessedResponse(BaseModel):
    """Extended response data with additional processing information."""
    parsed_response: ParsedResponse = Field(..., description="Basic parsed response data")
    command_spec: CommandSpec = Field(..., description="Command specification used for processing")
    raw_message: bytes = Field(..., description="Original raw response message")
    message_hex: str = Field(..., description="Hex representation of raw message")
    validation_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed validation results")
    
    class Config:
        arbitrary_types_allowed = True


# Test Results Models

class CommandResult(BaseModel):
    """Result of executing a single command."""
    command_code: str = Field(..., description="Command code in hex format")
    command_spec: CommandSpec = Field(..., description="Command specification")
    status: TestStatus = Field(..., description="Execution status")
    response: Optional[ProcessedResponse] = Field(None, description="Response data if successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    execution_time_ms: float = Field(0.0, description="Total execution time in milliseconds")
    retry_count: int = Field(0, description="Number of retries attempted")
    
    class Config:
        use_enum_values = True


class TestResults(BaseModel):
    """Complete test execution results."""
    profile_name: str = Field(..., description="Name of executed test profile")
    start_time: datetime = Field(..., description="Test execution start time")
    end_time: Optional[datetime] = Field(None, description="Test execution completion time")
    total_commands: int = Field(0, description="Total number of commands in test")
    successful_commands: int = Field(0, description="Number of successful commands")
    failed_commands: int = Field(0, description="Number of failed commands")
    skipped_commands: int = Field(0, description="Number of skipped commands")
    command_results: List[CommandResult] = Field(default_factory=list, description="Individual command results")
    errors: List[str] = Field(default_factory=list, description="General execution errors")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance measurements")
    configuration_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Configuration used for test")
    
    @property
    def duration_seconds(self) -> float:
        """Calculate test duration in seconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_commands == 0:
            return 0.0
        return (self.successful_commands / self.total_commands) * 100.0
    
    @property 
    def average_command_time_ms(self) -> float:
        """Calculate average command execution time."""
        successful_results = [r for r in self.command_results if r.status == TestStatus.SUCCESS]
        if not successful_results:
            return 0.0
        total_time = sum(r.execution_time_ms for r in successful_results)
        return total_time / len(successful_results)


# System Status Models

class ConnectionInfo(BaseModel):
    """Serial connection information and status."""
    port: str = Field(..., description="Serial port identifier")
    baud_rate: int = Field(..., description="Communication baud rate")
    state: ConnectionState = Field(..., description="Current connection state")
    connected_time: Optional[datetime] = Field(None, description="Connection establishment time")
    bytes_sent: int = Field(0, description="Total bytes transmitted")
    bytes_received: int = Field(0, description="Total bytes received")
    error_count: int = Field(0, description="Communication error count")
    last_error: Optional[str] = Field(None, description="Last error message")
    
    class Config:
        use_enum_values = True


class ApplicationStatus(BaseModel):
    """Overall application status and health."""
    version: str = Field(..., description="Application version")
    started_time: datetime = Field(default_factory=datetime.now, description="Application start time")
    connection_info: Optional[ConnectionInfo] = Field(None, description="Serial connection status")
    current_test: Optional[str] = Field(None, description="Currently executing test profile")
    total_commands_processed: int = Field(0, description="Total commands processed since start")
    memory_usage_mb: float = Field(0.0, description="Current memory usage in MB")
    cpu_usage_percent: float = Field(0.0, description="Current CPU usage percentage")
    
    @property
    def uptime_seconds(self) -> float:
        """Calculate application uptime in seconds."""
        return (datetime.now() - self.started_time).total_seconds()


# Type Mappings and Constants

DATA_TYPE_FORMATS = {
    DataType.UNSIGNED_INT: {"size": 2, "format": "H", "signed": False},
    DataType.SIGNED_INT: {"size": 2, "format": "h", "signed": True}, 
    DataType.WORD: {"size": 2, "format": "H", "signed": False},
    DataType.BOOLEAN: {"size": 2, "format": "H", "converter": bool},
    DataType.STRING: {"size": "variable", "format": "s"},
    DataType.BLOCK_DATA: {"size": "variable", "format": "raw"}
}

GEHC_PROTOCOL_CONSTANTS = {
    "PREAMBLE": 0xAA,
    "SYNC_HOST_TO_BATTERY": 0x23,
    "SYNC_BATTERY_TO_HOST": 0x40,
    "CRC_POLYNOMIAL": 0x07,  # SMBus PEC polynomial
    "MAX_DATA_LENGTH": 32,
    "MIN_MESSAGE_LENGTH": 5,  # Preamble + Sync + CMD + LEN + CRC
    "DEFAULT_TIMEOUT_MS": 1000,
    "MIN_INTER_COMMAND_DELAY": 0.1
}

# Export all types for easy importing
__all__ = [
    # Enums
    'DataType', 'Priority', 'ConnectionState', 'ValidationError', 'TestStatus',
    
    # Configuration Models
    'SerialConfig', 'CommandSpec', 'TestProfile', 'CommandTable',
    
    # Protocol Models  
    'GEHCMessage',
    
    # Response Models
    'ParsedResponse', 'ProcessedResponse',
    
    # Test Results Models
    'CommandResult', 'TestResults',
    
    # System Status Models
    'ConnectionInfo', 'ApplicationStatus',
    
    # Constants
    'DATA_TYPE_FORMATS', 'GEHC_PROTOCOL_CONSTANTS'
]