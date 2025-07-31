"""
Custom exceptions for serial communication module.
"""

class SerialCommError(Exception):
    """Base exception for all serial communication errors."""
    pass


class ConnectionError(SerialCommError):
    """Raised when connection to serial port fails or is lost."""
    pass


class ProtocolError(SerialCommError):
    """Raised when protocol-level errors occur."""
    pass


class TimeoutError(SerialCommError):
    """Raised when operations timeout."""
    pass


class ConfigurationError(SerialCommError):
    """Raised when invalid configuration is provided."""
    pass


class ChecksumError(ProtocolError):
    """Raised when message checksum validation fails."""
    pass


class FramingError(ProtocolError):
    """Raised when message framing is invalid."""
    pass


class DeviceNotFoundError(ConnectionError):
    """Raised when specified device is not found."""
    pass


class PermissionError(ConnectionError):
    """Raised when insufficient permissions to access device."""
    pass