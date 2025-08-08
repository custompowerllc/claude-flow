#!/usr/bin/env python3
"""
Serial communication handler for RS422 interface.

This module provides the SerialHandler class for managing RS422 serial
communication with GEHC PHTC devices using pyserial library.
"""

import logging
import time
from typing import Optional, Union
import serial
import serial.tools.list_ports
from threading import Lock


class SerialConnectionError(Exception):
    """Exception raised for serial connection related errors."""
    pass


class SerialHandler:
    """
    Handles RS422 serial communication for GEHC PHTC devices.
    
    This class provides a robust interface for serial communication with
    proper error handling, connection management, and non-blocking operations.
    """
    
    def __init__(self, port: str, baud_rate: int = 115200, timeout: float = 1.0):
        """
        Initialize the serial handler.
        
        Args:
            port: Serial port name (e.g., 'COM3', '/dev/ttyUSB0')
            baud_rate: Communication baud rate (default: 115200)
            timeout: Read timeout in seconds (default: 1.0)
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial_connection: Optional[serial.Serial] = None
        self._lock = Lock()  # Thread safety for serial operations
        self.logger = logging.getLogger(__name__)
        
        # RS422 specific configuration (8N1)
        self.data_bits = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stop_bits = serial.STOPBITS_ONE
        self.flow_control = False  # No hardware flow control for RS422
        
        self.logger.info(f"SerialHandler initialized for port {port} at {baud_rate} baud")
    
    def connect(self) -> bool:
        """
        Establish serial connection to the device.
        
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            SerialConnectionError: If connection fails
        """
        with self._lock:
            try:
                if self.is_connected():
                    self.logger.warning("Serial connection already established")
                    return True
                
                # Verify port exists
                if not self._port_exists(self.port):
                    raise SerialConnectionError(f"Serial port {self.port} not found")
                
                self.serial_connection = serial.Serial(
                    port=self.port,
                    baudrate=self.baud_rate,
                    bytesize=self.data_bits,
                    parity=self.parity,
                    stopbits=self.stop_bits,
                    timeout=self.timeout,
                    write_timeout=self.timeout,
                    xonxoff=False,  # No software flow control
                    rtscts=False,   # No RTS/CTS flow control
                    dsrdtr=False    # No DSR/DTR flow control
                )
                
                # Wait for port to stabilize
                time.sleep(0.1)
                
                # Clear any existing data in buffers
                self.serial_connection.reset_input_buffer()
                self.serial_connection.reset_output_buffer()
                
                self.logger.info(f"Serial connection established on {self.port}")
                return True
                
            except (serial.SerialException, OSError) as e:
                self.logger.error(f"Failed to connect to {self.port}: {e}")
                self.serial_connection = None
                raise SerialConnectionError(f"Connection failed: {e}")
    
    def disconnect(self) -> None:
        """Close the serial connection."""
        with self._lock:
            if self.serial_connection and self.serial_connection.is_open:
                try:
                    self.serial_connection.close()
                    self.logger.info(f"Serial connection closed on {self.port}")
                except Exception as e:
                    self.logger.error(f"Error closing connection: {e}")
                finally:
                    self.serial_connection = None
    
    def is_connected(self) -> bool:
        """
        Check if serial connection is active.
        
        Returns:
            bool: True if connected and port is open, False otherwise
        """
        return (self.serial_connection is not None and 
                self.serial_connection.is_open)
    
    def send_command(self, command: bytes) -> bool:
        """
        Send a command through the serial port.
        
        Args:
            command: Raw bytes to send
            
        Returns:
            bool: True if sent successfully, False otherwise
            
        Raises:
            SerialConnectionError: If not connected or send fails
        """
        if not self.is_connected():
            raise SerialConnectionError("Not connected to serial port")
        
        with self._lock:
            try:
                bytes_written = self.serial_connection.write(command)
                self.serial_connection.flush()  # Ensure data is sent immediately
                
                success = bytes_written == len(command)
                if success:
                    self.logger.debug(f"Sent {bytes_written} bytes: {command.hex()}")
                else:
                    self.logger.warning(f"Partial write: {bytes_written}/{len(command)} bytes")
                
                return success
                
            except (serial.SerialException, OSError) as e:
                self.logger.error(f"Failed to send command: {e}")
                raise SerialConnectionError(f"Send failed: {e}")
    
    def receive_response(self, max_bytes: int = 256) -> Optional[bytes]:
        """
        Receive response from the serial port.
        
        Args:
            max_bytes: Maximum number of bytes to read
            
        Returns:
            bytes: Received data, or None if no data/timeout
            
        Raises:
            SerialConnectionError: If not connected or receive fails
        """
        if not self.is_connected():
            raise SerialConnectionError("Not connected to serial port")
        
        with self._lock:
            try:
                # Check if data is available
                if self.serial_connection.in_waiting == 0:
                    return None
                
                # Read available data up to max_bytes
                data = self.serial_connection.read(
                    min(max_bytes, self.serial_connection.in_waiting)
                )
                
                if data:
                    self.logger.debug(f"Received {len(data)} bytes: {data.hex()}")
                    return data
                else:
                    self.logger.debug("No data received (timeout)")
                    return None
                    
            except (serial.SerialException, OSError) as e:
                self.logger.error(f"Failed to receive response: {e}")
                raise SerialConnectionError(f"Receive failed: {e}")
    
    def receive_response_blocking(self, expected_length: int = 0, timeout: float = None) -> Optional[bytes]:
        """
        Receive response with blocking behavior until expected length or timeout.
        
        Args:
            expected_length: Expected number of bytes (0 = read what's available)
            timeout: Override default timeout for this operation
            
        Returns:
            bytes: Received data, or None if timeout
            
        Raises:
            SerialConnectionError: If not connected or receive fails
        """
        if not self.is_connected():
            raise SerialConnectionError("Not connected to serial port")
        
        original_timeout = self.serial_connection.timeout
        if timeout is not None:
            self.serial_connection.timeout = timeout
        
        try:
            with self._lock:
                if expected_length > 0:
                    data = self.serial_connection.read(expected_length)
                else:
                    # Read until timeout with buffer management
                    data = b""
                    start_time = time.time()
                    current_timeout = timeout or self.timeout
                    
                    while time.time() - start_time < current_timeout:
                        chunk = self.serial_connection.read(1)
                        if not chunk:
                            break
                        data += chunk
                        
                        # Small delay to allow more data to arrive
                        time.sleep(0.001)
                
                if data:
                    self.logger.debug(f"Received blocking {len(data)} bytes: {data.hex()}")
                    return data
                else:
                    self.logger.debug("No data received (blocking timeout)")
                    return None
                    
        except (serial.SerialException, OSError) as e:
            self.logger.error(f"Failed to receive blocking response: {e}")
            raise SerialConnectionError(f"Receive failed: {e}")
        finally:
            if timeout is not None:
                self.serial_connection.timeout = original_timeout
    
    def clear_buffers(self) -> None:
        """Clear input and output buffers."""
        if not self.is_connected():
            return
        
        with self._lock:
            try:
                self.serial_connection.reset_input_buffer()
                self.serial_connection.reset_output_buffer()
                self.logger.debug("Serial buffers cleared")
            except Exception as e:
                self.logger.warning(f"Error clearing buffers: {e}")
    
    def get_connection_info(self) -> dict:
        """
        Get current connection information.
        
        Returns:
            dict: Connection details including port, baud rate, etc.
        """
        info = {
            "port": self.port,
            "baud_rate": self.baud_rate,
            "timeout": self.timeout,
            "is_connected": self.is_connected(),
            "data_bits": self.data_bits,
            "parity": self.parity,
            "stop_bits": self.stop_bits
        }
        
        if self.is_connected():
            info.update({
                "bytes_waiting": self.serial_connection.in_waiting,
                "bytes_to_write": self.serial_connection.out_waiting
            })
        
        return info
    
    def _port_exists(self, port: str) -> bool:
        """
        Check if the specified serial port exists.
        
        Args:
            port: Port name to check
            
        Returns:
            bool: True if port exists, False otherwise
        """
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        return port in available_ports
    
    @staticmethod
    def list_available_ports() -> list:
        """
        Get list of available serial ports.
        
        Returns:
            list: List of available port names
        """
        return [port.device for port in serial.tools.list_ports.comports()]
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def __del__(self):
        """Destructor - ensure connection is closed."""
        if hasattr(self, 'serial_connection'):
            self.disconnect()