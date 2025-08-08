#!/usr/bin/env python3
"""
Exception classes for GEHC PHTC Test Application.

This module defines all custom exception types used throughout the application,
providing structured error handling and clear error categorization.
"""

from typing import Dict, Any, Optional, List
from .constants import ErrorCodes


class GEHCError(Exception):
    """
    Base exception class for all GEHC application errors.
    
    All application-specific exceptions inherit from this base class,
    allowing for comprehensive error handling and logging.
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[ErrorCodes] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize GEHC error.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for categorization
            context: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        
    def __str__(self) -> str:
        """Return formatted error message."""
        if self.error_code:
            return f"[{self.error_code.name}] {self.message}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code.value if self.error_code else None,
            "error_code_name": self.error_code.name if self.error_code else None,
            "context": self.context
        }


class CommunicationError(GEHCError):
    """
    Exception raised for RS422 serial communication errors.
    
    This includes connection failures, timeouts, data transmission errors,
    and other low-level communication issues.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[ErrorCodes] = None,
        port: Optional[str] = None,
        baud_rate: Optional[int] = None,
        timeout_ms: Optional[int] = None
    ):
        """
        Initialize communication error.
        
        Args:
            message: Error description
            error_code: Specific communication error code
            port: Serial port identifier
            baud_rate: Communication baud rate
            timeout_ms: Timeout value if applicable
        """
        context = {}
        if port:
            context["port"] = port
        if baud_rate:
            context["baud_rate"] = baud_rate
        if timeout_ms:
            context["timeout_ms"] = timeout_ms
            
        super().__init__(message, error_code, context)


class ConnectionTimeoutError(CommunicationError):
    """Exception raised when device connection times out."""
    
    def __init__(self, timeout_ms: int, port: str):
        super().__init__(
            f"Device connection timeout after {timeout_ms}ms",
            ErrorCodes.COMM_TIMEOUT,
            port=port,
            timeout_ms=timeout_ms
        )


class ResponseTimeoutError(CommunicationError):
    """Exception raised when device response times out."""
    
    def __init__(self, command_code: int, timeout_ms: int):
        super().__init__(
            f"No response received for command 0x{command_code:02X} within {timeout_ms}ms",
            ErrorCodes.COMM_TIMEOUT,
            timeout_ms=timeout_ms
        )
        self.context["command_code"] = command_code


class SerialPortError(CommunicationError):
    """Exception raised for serial port access issues."""
    
    def __init__(self, port: str, reason: str):
        super().__init__(
            f"Serial port '{port}' error: {reason}",
            port=port
        )


class ProtocolError(GEHCError):
    """
    Exception raised for GEHC protocol-related errors.
    
    This includes message format errors, invalid checksums,
    unsupported commands, and protocol violations.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[ErrorCodes] = None,
        command_code: Optional[int] = None,
        raw_message: Optional[bytes] = None
    ):
        """
        Initialize protocol error.
        
        Args:
            message: Error description
            error_code: Specific protocol error code
            command_code: Command code if applicable
            raw_message: Raw message data for debugging
        """
        context = {}
        if command_code is not None:
            context["command_code"] = f"0x{command_code:02X}"
        if raw_message is not None:
            context["raw_message"] = raw_message.hex().upper()
            context["message_length"] = len(raw_message)
            
        super().__init__(message, error_code, context)


class InvalidPreambleError(ProtocolError):
    """Exception raised when message preamble is invalid."""
    
    def __init__(self, expected: int, actual: int):
        super().__init__(
            f"Invalid preamble - expected 0x{expected:02X}, got 0x{actual:02X}",
            ErrorCodes.PROTO_INVALID_PREAMBLE
        )
        self.context.update({"expected": expected, "actual": actual})


class InvalidSyncHeaderError(ProtocolError):
    """Exception raised when sync header is invalid."""
    
    def __init__(self, expected: int, actual: int):
        super().__init__(
            f"Invalid sync header - expected 0x{expected:02X}, got 0x{actual:02X}",
            ErrorCodes.PROTO_INVALID_SYNC
        )
        self.context.update({"expected": expected, "actual": actual})


class CRCValidationError(ProtocolError):
    """Exception raised when CRC validation fails."""
    
    def __init__(self, expected: int, actual: int, data: bytes):
        super().__init__(
            f"CRC validation failed - expected 0x{expected:02X}, got 0x{actual:02X}",
            ErrorCodes.COMM_CRC_ERROR,
            raw_message=data
        )
        self.context.update({"expected_crc": expected, "actual_crc": actual})


class InvalidMessageLengthError(ProtocolError):
    """Exception raised when message length is invalid."""
    
    def __init__(self, expected: int, actual: int):
        super().__init__(
            f"Invalid message length - expected {expected}, got {actual}",
            ErrorCodes.COMM_INVALID_LENGTH
        )
        self.context.update({"expected_length": expected, "actual_length": actual})


class UnsupportedCommandError(ProtocolError):
    """Exception raised for unsupported command codes."""
    
    def __init__(self, command_code: int):
        super().__init__(
            f"Command 0x{command_code:02X} not supported by device",
            ErrorCodes.PROTO_COMMAND_NOT_SUPPORTED,
            command_code=command_code
        )


class ConfigurationError(GEHCError):
    """
    Exception raised for configuration-related errors.
    
    This includes missing configuration files, invalid JSON,
    missing required settings, and validation failures.
    """
    
    def __init__(
        self,
        message: str,
        config_file: Optional[str] = None,
        validation_errors: Optional[List[str]] = None
    ):
        """
        Initialize configuration error.
        
        Args:
            message: Error description
            config_file: Configuration file path if applicable
            validation_errors: List of validation error messages
        """
        context = {}
        if config_file:
            context["config_file"] = config_file
        if validation_errors:
            context["validation_errors"] = validation_errors
            
        super().__init__(message, ErrorCodes.APP_CONFIGURATION_ERROR, context)


class MissingConfigFileError(ConfigurationError):
    """Exception raised when required configuration file is missing."""
    
    def __init__(self, file_path: str):
        super().__init__(
            f"Required configuration file not found: {file_path}",
            config_file=file_path
        )


class InvalidConfigFormatError(ConfigurationError):
    """Exception raised when configuration file format is invalid."""
    
    def __init__(self, file_path: str, reason: str):
        super().__init__(
            f"Invalid configuration format in {file_path}: {reason}",
            config_file=file_path
        )


class MissingRequiredSettingError(ConfigurationError):
    """Exception raised when required configuration setting is missing."""
    
    def __init__(self, setting_name: str, config_file: str):
        super().__init__(
            f"Required setting '{setting_name}' missing from {config_file}",
            config_file=config_file
        )
        self.context["setting_name"] = setting_name


class DataProcessingError(GEHCError):
    """
    Exception raised for data processing and parsing errors.
    
    This includes data type conversion failures, scaling errors,
    and value validation issues.
    """
    
    def __init__(
        self,
        message: str,
        command_code: Optional[int] = None,
        data_type: Optional[str] = None,
        raw_data: Optional[bytes] = None
    ):
        """
        Initialize data processing error.
        
        Args:
            message: Error description
            command_code: Command code being processed
            data_type: Expected data type
            raw_data: Raw data that caused the error
        """
        context = {}
        if command_code is not None:
            context["command_code"] = f"0x{command_code:02X}"
        if data_type:
            context["data_type"] = data_type
        if raw_data is not None:
            context["raw_data"] = raw_data.hex().upper()
            context["data_length"] = len(raw_data)
            
        super().__init__(message, context=context)


class InvalidDataTypeError(DataProcessingError):
    """Exception raised when data type conversion fails."""
    
    def __init__(self, data_type: str, raw_data: bytes, reason: str):
        super().__init__(
            f"Cannot convert data to {data_type}: {reason}",
            data_type=data_type,
            raw_data=raw_data
        )


class DataOutOfRangeError(DataProcessingError):
    """Exception raised when data value is outside expected range."""
    
    def __init__(self, value: float, range_spec: str, command_code: int):
        super().__init__(
            f"Value {value} is outside expected range {range_spec}",
            ErrorCodes.PROTO_DATA_OUT_OF_RANGE,
            command_code=command_code
        )
        self.context["value"] = value
        self.context["range_spec"] = range_spec


class ScalingError(DataProcessingError):
    """Exception raised when data scaling fails."""
    
    def __init__(self, value: Any, granularity: float, reason: str):
        super().__init__(f"Cannot scale value {value} with granularity {granularity}: {reason}")
        self.context.update({"value": value, "granularity": granularity})


class DeviceError(GEHCError):
    """
    Exception raised for device-related errors.
    
    This includes device not ready, device faults,
    and hardware-specific error conditions.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[ErrorCodes] = None,
        device_status: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize device error.
        
        Args:
            message: Error description
            error_code: Specific device error code
            device_status: Device status information
        """
        context = device_status or {}
        super().__init__(message, error_code, context)


class DeviceNotReadyError(DeviceError):
    """Exception raised when device is not ready for communication."""
    
    def __init__(self, reason: str = "Device not responding"):
        super().__init__(
            f"Device not ready: {reason}",
            ErrorCodes.DEVICE_NOT_READY
        )


class DeviceBusyError(DeviceError):
    """Exception raised when device is busy processing previous command."""
    
    def __init__(self, retry_after_ms: Optional[int] = None):
        message = "Device is busy"
        if retry_after_ms:
            message += f", retry after {retry_after_ms}ms"
            
        super().__init__(message, ErrorCodes.DEVICE_BUSY)
        
        if retry_after_ms:
            self.context["retry_after_ms"] = retry_after_ms


class DeviceFaultError(DeviceError):
    """Exception raised when device reports a fault condition."""
    
    def __init__(self, fault_code: int, description: str):
        super().__init__(
            f"Device fault 0x{fault_code:04X}: {description}",
            ErrorCodes.DEVICE_FAULT
        )
        self.context.update({"fault_code": fault_code, "description": description})


class TestExecutionError(GEHCError):
    """
    Exception raised for test execution errors.
    
    This includes test profile errors, orchestration failures,
    and test workflow issues.
    """
    
    def __init__(
        self,
        message: str,
        profile_name: Optional[str] = None,
        failed_commands: Optional[List[str]] = None
    ):
        """
        Initialize test execution error.
        
        Args:
            message: Error description
            profile_name: Test profile name if applicable
            failed_commands: List of failed command codes
        """
        context = {}
        if profile_name:
            context["profile_name"] = profile_name
        if failed_commands:
            context["failed_commands"] = failed_commands
            
        super().__init__(message, context=context)


class InvalidTestProfileError(TestExecutionError):
    """Exception raised when test profile is invalid or not found."""
    
    def __init__(self, profile_name: str, reason: str = "Profile not found"):
        super().__init__(
            f"Invalid test profile '{profile_name}': {reason}",
            profile_name=profile_name
        )


class TestTimeoutError(TestExecutionError):
    """Exception raised when test execution times out."""
    
    def __init__(self, profile_name: str, timeout_seconds: int):
        super().__init__(
            f"Test profile '{profile_name}' timed out after {timeout_seconds} seconds",
            profile_name=profile_name
        )
        self.context["timeout_seconds"] = timeout_seconds


class ComponentInitializationError(GEHCError):
    """
    Exception raised when component initialization fails.
    
    This includes dependency injection failures, resource allocation
    errors, and component configuration issues.
    """
    
    def __init__(
        self,
        component_name: str,
        reason: str,
        dependencies: Optional[List[str]] = None
    ):
        """
        Initialize component initialization error.
        
        Args:
            component_name: Name of component that failed to initialize
            reason: Reason for initialization failure
            dependencies: List of required dependencies
        """
        message = f"Failed to initialize component '{component_name}': {reason}"
        
        context = {"component_name": component_name}
        if dependencies:
            context["required_dependencies"] = dependencies
            
        super().__init__(
            message,
            ErrorCodes.APP_INITIALIZATION_ERROR,
            context
        )


class ResourceError(GEHCError):
    """
    Exception raised for system resource errors.
    
    This includes memory allocation failures, file system errors,
    and other system resource issues.
    """
    
    def __init__(
        self,
        resource_type: str,
        operation: str,
        reason: str
    ):
        """
        Initialize resource error.
        
        Args:
            resource_type: Type of resource (memory, file, etc.)
            operation: Operation that failed
            reason: Reason for failure
        """
        message = f"Resource error - {operation} {resource_type}: {reason}"
        
        context = {
            "resource_type": resource_type,
            "operation": operation
        }
        
        super().__init__(
            message,
            ErrorCodes.APP_RESOURCE_ERROR,
            context
        )


# Exception mapping for error code to exception class
ERROR_CODE_MAPPING = {
    ErrorCodes.COMM_TIMEOUT: ResponseTimeoutError,
    ErrorCodes.COMM_CRC_ERROR: CRCValidationError,
    ErrorCodes.COMM_INVALID_LENGTH: InvalidMessageLengthError,
    ErrorCodes.PROTO_INVALID_PREAMBLE: InvalidPreambleError,
    ErrorCodes.PROTO_INVALID_SYNC: InvalidSyncHeaderError,
    ErrorCodes.PROTO_COMMAND_NOT_SUPPORTED: UnsupportedCommandError,
    ErrorCodes.PROTO_DATA_OUT_OF_RANGE: DataOutOfRangeError,
    ErrorCodes.DEVICE_NOT_READY: DeviceNotReadyError,
    ErrorCodes.DEVICE_BUSY: DeviceBusyError,
    ErrorCodes.DEVICE_FAULT: DeviceFaultError,
    ErrorCodes.APP_CONFIGURATION_ERROR: ConfigurationError,
    ErrorCodes.APP_INITIALIZATION_ERROR: ComponentInitializationError,
    ErrorCodes.APP_RESOURCE_ERROR: ResourceError,
}


def create_exception_from_error_code(
    error_code: ErrorCodes,
    message: str,
    **kwargs
) -> GEHCError:
    """
    Create appropriate exception instance from error code.
    
    Args:
        error_code: Error code to map to exception
        message: Error message
        **kwargs: Additional arguments for exception constructor
        
    Returns:
        GEHCError: Appropriate exception instance
    """
    exception_class = ERROR_CODE_MAPPING.get(error_code, GEHCError)
    
    try:
        return exception_class(message, error_code=error_code, **kwargs)
    except TypeError:
        # Fallback to base exception if constructor doesn't match
        return GEHCError(message, error_code=error_code, context=kwargs)


# Export all exception classes
__all__ = [
    # Base exception
    'GEHCError',
    
    # Communication exceptions
    'CommunicationError', 'ConnectionTimeoutError', 'ResponseTimeoutError',
    'SerialPortError',
    
    # Protocol exceptions
    'ProtocolError', 'InvalidPreambleError', 'InvalidSyncHeaderError',
    'CRCValidationError', 'InvalidMessageLengthError', 'UnsupportedCommandError',
    
    # Configuration exceptions
    'ConfigurationError', 'MissingConfigFileError', 'InvalidConfigFormatError',
    'MissingRequiredSettingError',
    
    # Data processing exceptions
    'DataProcessingError', 'InvalidDataTypeError', 'DataOutOfRangeError',
    'ScalingError',
    
    # Device exceptions
    'DeviceError', 'DeviceNotReadyError', 'DeviceBusyError', 'DeviceFaultError',
    
    # Test execution exceptions
    'TestExecutionError', 'InvalidTestProfileError', 'TestTimeoutError',
    
    # System exceptions
    'ComponentInitializationError', 'ResourceError',
    
    # Utility functions
    'create_exception_from_error_code', 'ERROR_CODE_MAPPING'
]