#!/usr/bin/env python3
"""
GEHC Protocol handler for RS422 communication.

This module implements the GE Healthcare protocol for communication with
PHTC devices, including message formatting, CRC8 calculation, and response validation.
"""

import logging
import struct
from typing import Tuple, Optional, Dict, Any, Union
from enum import Enum


class MessageDirection(Enum):
    """Message direction indicators."""
    HOST_TO_BATTERY = 0x23  # Synchronization header for host-to-battery messages
    BATTERY_TO_HOST = 0x40  # Response header for battery-to-host messages


class ProtocolError(Exception):
    """Exception raised for protocol-related errors."""
    pass


class ProtocolHandler:
    """
    Handles GEHC protocol message formatting and parsing.
    
    This class implements the GE Healthcare RS422 protocol specification
    including CRC8 calculation using SMBus PEC polynomial.
    """
    
    # Protocol constants
    PREAMBLE = 0xAA  # GE Healthcare Protocol identifier
    MAX_DATA_LENGTH = 255
    MIN_MESSAGE_LENGTH = 5  # [PREAMBLE][SYNC][CMD][LEN][CRC8]
    
    # CRC8 SMBus PEC polynomial (x^8 + x^2 + x^1 + 1)
    CRC8_POLYNOMIAL = 0x07
    CRC8_INIT = 0x00
    
    def __init__(self):
        """Initialize the protocol handler."""
        self.logger = logging.getLogger(__name__)
        
        # Pre-compute CRC8 lookup table for performance
        self._crc8_table = self._build_crc8_table()
        self.logger.info("ProtocolHandler initialized with CRC8 SMBus PEC")
    
    def format_command(self, command_code: int, data: bytes = b'') -> bytes:
        """
        Format a command message according to GEHC protocol.
        
        Message format: [0xAA][0x23][CMD][LEN][DATA...][CRC8]
        
        Args:
            command_code: Command byte (0x00-0xFF)
            data: Optional data payload
            
        Returns:
            bytes: Formatted command message
            
        Raises:
            ProtocolError: If parameters are invalid
        """
        if not (0 <= command_code <= 0xFF):
            raise ProtocolError(f"Invalid command code: {command_code:#04x}")
        
        if len(data) > self.MAX_DATA_LENGTH:
            raise ProtocolError(f"Data too long: {len(data)} bytes (max {self.MAX_DATA_LENGTH})")
        
        # Build message without CRC8
        message = struct.pack('BBB', self.PREAMBLE, MessageDirection.HOST_TO_BATTERY.value, command_code)
        message += struct.pack('B', len(data))  # Data length
        message += data  # Data payload
        
        # Calculate and append CRC8
        crc8 = self.calculate_crc8(message[1:])  # CRC calculated from sync header onwards
        message += struct.pack('B', crc8)
        
        self.logger.debug(f"Formatted command {command_code:#04x}: {message.hex()}")
        return message
    
    def validate_response(self, response: bytes) -> bool:
        """
        Validate a response message structure and CRC8.
        
        Expected format: [0x40][CMD][LEN][DATA...][CRC8]
        
        Args:
            response: Raw response bytes
            
        Returns:
            bool: True if response is valid, False otherwise
        """
        if len(response) < 4:  # Minimum: [0x40][CMD][LEN][CRC8]
            self.logger.warning(f"Response too short: {len(response)} bytes")
            return False
        
        # Check response header
        if response[0] != MessageDirection.BATTERY_TO_HOST.value:
            self.logger.warning(f"Invalid response header: {response[0]:#04x}")
            return False
        
        # Extract data length
        if len(response) < 3:
            return False
        
        data_length = response[2]
        expected_length = 4 + data_length  # [0x40][CMD][LEN][DATA...][CRC8]
        
        if len(response) != expected_length:
            self.logger.warning(f"Response length mismatch: got {len(response)}, expected {expected_length}")
            return False
        
        # Validate CRC8
        message_without_crc = response[:-1]
        received_crc = response[-1]
        calculated_crc = self.calculate_crc8(message_without_crc)
        
        if received_crc != calculated_crc:
            self.logger.warning(f"CRC8 mismatch: got {received_crc:#04x}, calculated {calculated_crc:#04x}")
            return False
        
        self.logger.debug(f"Response validated: {response.hex()}")
        return True
    
    def calculate_crc8(self, data: bytes) -> int:
        """
        Calculate CRC8 checksum using SMBus PEC polynomial.
        
        Uses polynomial 0x07 (x^8 + x^2 + x^1 + 1) which is the standard
        SMBus Packet Error Check polynomial.
        
        Args:
            data: Data bytes to calculate CRC for
            
        Returns:
            int: CRC8 checksum (0x00-0xFF)
        """
        crc = self.CRC8_INIT
        
        for byte in data:
            crc = self._crc8_table[crc ^ byte]
        
        return crc
    
    def extract_response_data(self, response: bytes) -> Tuple[int, bytes]:
        """
        Extract command code and data from a validated response.
        
        Args:
            response: Validated response bytes
            
        Returns:
            tuple: (command_code, data_bytes)
            
        Raises:
            ProtocolError: If response format is invalid
        """
        if not self.validate_response(response):
            raise ProtocolError("Invalid response format")
        
        command_code = response[1]
        data_length = response[2]
        
        if data_length == 0:
            data = b''
        else:
            data = response[3:3+data_length]
        
        self.logger.debug(f"Extracted response - Command: {command_code:#04x}, Data: {data.hex()}")
        return command_code, data
    
    def build_ge_message(self, command_code: int, data: bytes = b'') -> bytes:
        """
        Build a complete GE Healthcare protocol message.
        
        This is an alias for format_command() for consistency with documentation.
        
        Args:
            command_code: Command byte
            data: Optional data payload
            
        Returns:
            bytes: Complete formatted message
        """
        return self.format_command(command_code, data)
    
    def parse_ge_response(self, response: bytes) -> Tuple[bool, int, bytes]:
        """
        Parse a GE Healthcare protocol response.
        
        Args:
            response: Raw response bytes
            
        Returns:
            tuple: (is_valid, command_code, data_bytes)
        """
        try:
            is_valid = self.validate_response(response)
            if is_valid:
                command_code, data = self.extract_response_data(response)
                return True, command_code, data
            else:
                return False, 0, b''
        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")
            return False, 0, b''
    
    def _build_crc8_table(self) -> list:
        """
        Build CRC8 lookup table for SMBus PEC polynomial.
        
        Returns:
            list: 256-element CRC8 lookup table
        """
        table = []
        
        for i in range(256):
            crc = i
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ self.CRC8_POLYNOMIAL
                else:
                    crc = crc << 1
                crc &= 0xFF
            table.append(crc)
        
        return table
    
    def get_message_info(self, message: bytes) -> Dict[str, Any]:
        """
        Get detailed information about a message.
        
        Args:
            message: Message bytes to analyze
            
        Returns:
            dict: Message analysis information
        """
        if len(message) < 1:
            return {"error": "Empty message"}
        
        info = {
            "raw_hex": message.hex(),
            "length": len(message),
            "preamble": message[0] if len(message) > 0 else None,
            "sync_header": message[1] if len(message) > 1 else None,
            "command_code": message[2] if len(message) > 2 else None,
            "data_length": message[3] if len(message) > 3 else None,
        }
        
        # Determine message type
        if len(message) > 1:
            if message[0] == self.PREAMBLE and message[1] == MessageDirection.HOST_TO_BATTERY.value:
                info["type"] = "command"
                info["direction"] = "host_to_battery"
            elif message[0] == MessageDirection.BATTERY_TO_HOST.value:
                info["type"] = "response"
                info["direction"] = "battery_to_host"
            else:
                info["type"] = "unknown"
                info["direction"] = "unknown"
        
        # Extract data if present
        if len(message) > 4 and info.get("data_length", 0) > 0:
            data_start = 4 if info["type"] == "command" else 3
            data_end = data_start + info["data_length"]
            if len(message) > data_end:
                info["data"] = message[data_start:data_end].hex()
        
        # Extract CRC8
        if len(message) > 4:
            info["crc8_received"] = message[-1]
            
            # Calculate expected CRC8
            if info["type"] == "command":
                crc_data = message[1:-1]  # From sync header to end, excluding CRC
            else:
                crc_data = message[:-1]   # All except CRC
            
            info["crc8_calculated"] = self.calculate_crc8(crc_data)
            info["crc8_valid"] = info["crc8_received"] == info["crc8_calculated"]
        
        return info
    
    @staticmethod
    def is_command_supported(command_code: int) -> bool:
        """
        Check if a command code is within valid range.
        
        Args:
            command_code: Command code to check
            
        Returns:
            bool: True if command code is valid (0x00-0xFF)
        """
        return 0 <= command_code <= 0xFF
    
    def create_test_message(self, command_code: int = 0x08) -> bytes:
        """
        Create a test message for protocol validation.
        
        Args:
            command_code: Command code for test message
            
        Returns:
            bytes: Test message
        """
        return self.format_command(command_code, b'')
    
    def create_test_response(self, command_code: int = 0x08, data: bytes = b'\x1A\x2B') -> bytes:
        """
        Create a test response message for protocol validation.
        
        Args:
            command_code: Command code for response
            data: Response data payload
            
        Returns:
            bytes: Test response message
        """
        # Build response: [0x40][CMD][LEN][DATA...][CRC8]
        message = struct.pack('BB', MessageDirection.BATTERY_TO_HOST.value, command_code)
        message += struct.pack('B', len(data))
        message += data
        
        # Calculate and append CRC8
        crc8 = self.calculate_crc8(message)
        message += struct.pack('B', crc8)
        
        return message