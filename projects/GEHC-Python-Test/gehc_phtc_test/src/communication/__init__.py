#!/usr/bin/env python3
"""
Communication layer for GEHC PHTC Test Application.

This module handles all aspects of RS422 serial communication including:
- Low-level serial port management and I/O operations
- GEHC protocol implementation with message formatting
- CRC8 checksum calculation and validation
- Connection management and error handling
"""

# Import interfaces for type checking
from ..interfaces import ISerialHandler, IProtocolHandler, ICRC8Calculator

# Note: Implementations will be created by communication agent
# from .serial_handler import SerialHandler
# from .protocol_handler import ProtocolHandler  
# from .crc8_calculator import CRC8Calculator

__all__ = [
    # Interfaces
    'ISerialHandler', 'IProtocolHandler', 'ICRC8Calculator',
    
    # Implementation classes (when created)
    # 'SerialHandler', 'ProtocolHandler', 'CRC8Calculator'
]