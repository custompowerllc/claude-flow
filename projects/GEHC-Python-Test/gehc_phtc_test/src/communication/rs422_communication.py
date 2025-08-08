"""
GEHC PHTC RS422 Test Application - RS422 Communication

This module provides the RS422Communication class for serial communication
with GEHC PHTC devices.
"""

import time
import serial
import serial.tools.list_ports
from typing import Optional, List, Dict, Any
from threading import Lock


class RS422Communication:
    """Handles RS422 serial communication with GEHC PHTC devices."""
    
    def __init__(
        self, 
        port: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        display=None
    ):
        """Initialize RS422 communication.
        
        Args:
            port: Serial port to use. If None, will auto-detect
            config: Serial configuration dictionary
            display: Display instance for status messages
        """
        self.port = port
        self.config = config or self._get_default_serial_config()
        self.display = display
        self.serial_connection: Optional[serial.Serial] = None
        self.lock = Lock()
        self._connected = False
    
    def _get_default_serial_config(self) -> Dict[str, Any]:
        """Get default serial configuration.
        
        Returns:
            Dictionary with default serial settings
        """
        return {
            "baudrate": 9600,
            "bytesize": 8,
            "parity": "N", 
            "stopbits": 1,
            "timeout": 1.0,
            "xonxoff": False,
            "rtscts": True,
            "dsrdtr": False
        }
    
    def get_available_ports(self) -> List[str]:
        """Get list of available serial ports.
        
        Returns:
            List of available serial port names
        """
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def auto_detect_port(self) -> Optional[str]:
        """Attempt to automatically detect the correct serial port.
        
        Returns:
            Port name if found, None otherwise
        """
        available_ports = self.get_available_ports()
        
        if not available_ports:
            return None
        
        # For now, return the first available port
        # In a real implementation, you might want to test each port
        # by sending a command and checking for expected response
        return available_ports[0]
    
    def connect(self) -> bool:
        """Establish serial connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        with self.lock:
            if self._connected:
                return True
            
            try:
                # Auto-detect port if not specified
                if not self.port:
                    self.port = self.auto_detect_port()
                    if not self.port:
                        if self.display:
                            self.display.show_message("No serial ports available", "error")
                        return False
                
                # Convert parity string to serial constants
                parity_map = {
                    "N": serial.PARITY_NONE,
                    "E": serial.PARITY_EVEN,
                    "O": serial.PARITY_ODD,
                    "M": serial.PARITY_MARK,
                    "S": serial.PARITY_SPACE
                }
                
                # Convert stopbits to serial constants
                stopbits_map = {
                    1: serial.STOPBITS_ONE,
                    1.5: serial.STOPBITS_ONE_POINT_FIVE,
                    2: serial.STOPBITS_TWO
                }
                
                # Create serial connection
                self.serial_connection = serial.Serial(
                    port=self.port,
                    baudrate=self.config["baudrate"],
                    bytesize=self.config["bytesize"],
                    parity=parity_map.get(self.config["parity"], serial.PARITY_NONE),
                    stopbits=stopbits_map.get(self.config["stopbits"], serial.STOPBITS_ONE),
                    timeout=self.config["timeout"],
                    xonxoff=self.config["xonxoff"],
                    rtscts=self.config["rtscts"],
                    dsrdtr=self.config["dsrdtr"]
                )
                
                # Wait a moment for connection to stabilize
                time.sleep(0.1)
                
                self._connected = True
                
                if self.display:
                    self.display.show_message(f"Connected to {self.port}", "success")
                    self.display.show_connection_status(True, self.port)
                
                return True
                
            except Exception as e:
                self._connected = False
                if self.display:
                    self.display.show_message(f"Failed to connect to {self.port}: {e}", "error")
                return False
    
    def disconnect(self) -> None:
        """Close serial connection."""
        with self.lock:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
            
            self._connected = False
            
            if self.display:
                self.display.show_message("Disconnected from serial port", "info")
                self.display.show_connection_status(False)
    
    def is_connected(self) -> bool:
        """Check if serial connection is active.
        
        Returns:
            True if connected, False otherwise
        """
        return self._connected and self.serial_connection and self.serial_connection.is_open
    
    def send_command(self, command: str, timeout: Optional[float] = None) -> str:
        """Send a command and wait for response.
        
        Args:
            command: Command string to send
            timeout: Optional timeout override
            
        Returns:
            Response string from device
            
        Raises:
            RuntimeError: If not connected
            TimeoutError: If response timeout
            Exception: For other communication errors
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to serial port")
        
        with self.lock:
            try:
                # Clear any pending data
                self.serial_connection.reset_input_buffer()
                
                # Send command (add line terminator if not present)
                cmd_bytes = command.encode('ascii')
                if not cmd_bytes.endswith(b'\r\n'):
                    cmd_bytes += b'\r\n'
                
                self.serial_connection.write(cmd_bytes)
                self.serial_connection.flush()
                
                # Use provided timeout or default
                read_timeout = timeout or self.config.get("timeout", 1.0)
                
                # Read response
                response_bytes = b''
                start_time = time.time()
                
                while True:
                    if time.time() - start_time > read_timeout:
                        raise TimeoutError(f"Response timeout ({read_timeout}s)")
                    
                    # Read available bytes
                    if self.serial_connection.in_waiting > 0:
                        chunk = self.serial_connection.read(self.serial_connection.in_waiting)
                        response_bytes += chunk
                        
                        # Check for common terminators
                        if response_bytes.endswith(b'\r\n') or response_bytes.endswith(b'\n'):
                            break
                    else:
                        time.sleep(0.01)  # Small delay to avoid busy waiting
                
                # Decode response
                response = response_bytes.decode('ascii', errors='replace').strip()
                return response
                
            except Exception as e:
                if self.display:
                    self.display.show_message(f"Communication error: {e}", "error")
                raise
    
    def send_raw_bytes(self, data: bytes) -> bytes:
        """Send raw bytes and return response.
        
        Args:
            data: Raw bytes to send
            
        Returns:
            Raw response bytes
            
        Raises:
            RuntimeError: If not connected
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to serial port")
        
        with self.lock:
            self.serial_connection.write(data)
            self.serial_connection.flush()
            
            # Wait for response
            time.sleep(0.1)
            
            # Read all available data
            response = b''
            while self.serial_connection.in_waiting > 0:
                response += self.serial_connection.read(self.serial_connection.in_waiting)
                time.sleep(0.01)
            
            return response
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about the current connection.
        
        Returns:
            Dictionary with connection information
        """
        info = {
            "port": self.port,
            "connected": self.is_connected(),
            "config": self.config.copy()
        }
        
        if self.serial_connection:
            info.update({
                "baudrate": self.serial_connection.baudrate,
                "bytesize": self.serial_connection.bytesize,
                "parity": self.serial_connection.parity,
                "stopbits": self.serial_connection.stopbits,
                "timeout": self.serial_connection.timeout,
                "bytes_to_read": self.serial_connection.in_waiting if self.is_connected() else 0,
                "bytes_to_write": self.serial_connection.out_waiting if self.is_connected() else 0
            })
        
        return info