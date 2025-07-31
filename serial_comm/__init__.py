"""
Python Serial Communication Module for RS422
============================================

A comprehensive async serial communication library supporting:
- RS422 communication protocol
- Automatic port detection and enumeration
- Connection persistence and recovery
- Custom protocol implementation
- Non-blocking async/await operations
- Robust error handling and logging

Usage:
    from serial_comm import SerialManager, RS422Protocol
    
    manager = SerialManager()
    protocol = RS422Protocol()
    
    async with manager.connect('/dev/ttyUSB0') as connection:
        response = await protocol.send_command(connection, 'GET_STATUS')
"""

from .manager import SerialManager
from .protocol import RS422Protocol, ProtocolError, Message
from .detector import PortDetector
from .config import SerialConfig
from .exceptions import (
    SerialCommError,
    ConnectionError,
    ProtocolError,
    TimeoutError,
    ConfigurationError
)

__version__ = "1.0.0"
__author__ = "Claude Code Assistant"

__all__ = [
    'SerialManager',
    'RS422Protocol', 
    'ProtocolError',
    'Message',
    'PortDetector',
    'SerialConfig',
    'SerialCommError',
    'ConnectionError',
    'TimeoutError',
    'ConfigurationError'
]