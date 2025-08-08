"""Mock serial port implementation for testing PHTC communication."""

import time
from typing import Optional, Dict, Any, List, Callable
from unittest.mock import Mock
import threading


class MockSerialPort:
    """
    Mock serial port that simulates PHTC device responses.
    
    Supports various test scenarios including:
    - Normal operation responses
    - Error conditions (timeouts, CRC errors, device errors)
    - Communication failures
    - Performance testing
    """
    
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.is_open = False
        self.in_waiting = 0
        self.out_waiting = 0
        
        # Test behavior configuration
        self.behavior_mode = "normal"  # normal, timeout, crc_error, device_error, etc.
        self.response_delay = 0.01  # Simulated device response delay
        self.fail_probability = 0.0  # Probability of random failures (0.0-1.0)
        
        # Response mappings for different commands
        self.command_responses: Dict[bytes, bytes] = {
            # Read temperature command -> response
            bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0x8B]): bytes([0x01, 0x03, 0x02, 0x90, 0x00, 0x4F]),
            # Read pressure command -> response
            bytes([0x01, 0x04, 0x00, 0x02, 0x00, 0x01, 0x9A]): bytes([0x01, 0x04, 0x00, 0x7B, 0x00, 0x8C]),
            # Read status command -> response
            bytes([0x01, 0x05, 0x00, 0x03, 0x00, 0x01, 0xEB]): bytes([0x01, 0x05, 0x00, 0x01, 0x00, 0x55]),
        }
        
        # Buffer for simulating serial communication
        self._input_buffer = bytearray()
        self._output_buffer = bytearray()
        self._lock = threading.Lock()
        
        # Statistics tracking
        self.bytes_written = 0
        self.bytes_read = 0
        self.commands_processed = 0
        self.errors_generated = 0
    
    def open(self):
        """Open the mock serial port."""
        if self.behavior_mode == "connection_failed":
            raise ConnectionError("Failed to open serial port")
        self.is_open = True
    
    def close(self):
        """Close the mock serial port."""
        self.is_open = False
        self._input_buffer.clear()
        self._output_buffer.clear()
    
    def write(self, data: bytes) -> int:
        """Write data to the mock serial port."""
        if not self.is_open:
            raise RuntimeError("Serial port not open")
        
        with self._lock:
            self._output_buffer.extend(data)
            self.bytes_written += len(data)
            
            # Simulate device processing and response generation
            self._process_command(data)
            
        return len(data)
    
    def read(self, size: int = 1) -> bytes:
        """Read data from the mock serial port."""
        if not self.is_open:
            raise RuntimeError("Serial port not open")
        
        # Simulate response delay
        if self.response_delay > 0:
            time.sleep(self.response_delay)
        
        with self._lock:
            if self.behavior_mode == "timeout":
                # Simulate timeout by not returning data
                time.sleep(self.timeout + 0.1)
                return b''
            
            # Read from input buffer
            data = bytes(self._input_buffer[:size])
            del self._input_buffer[:size]
            self.bytes_read += len(data)
            self.in_waiting = len(self._input_buffer)
            
            return data
    
    def readline(self, size: int = -1) -> bytes:
        """Read a line from the mock serial port."""
        return self.read(size if size > 0 else 1024)
    
    def reset_input_buffer(self):
        """Clear the input buffer."""
        with self._lock:
            self._input_buffer.clear()
            self.in_waiting = 0
    
    def reset_output_buffer(self):
        """Clear the output buffer."""
        with self._lock:
            self._output_buffer.clear()
            self.out_waiting = 0
    
    def _process_command(self, command: bytes):
        """Process received command and generate appropriate response."""
        self.commands_processed += 1
        
        # Check for specific test behaviors
        if self.behavior_mode == "device_error":
            # Generate device error response
            error_response = bytes([0x01, 0x81, 0x02, 0x00, 0xC1])
            self._input_buffer.extend(error_response)
            self.in_waiting = len(self._input_buffer)
            self.errors_generated += 1
            return
        
        if self.behavior_mode == "invalid_crc":
            # Generate response with invalid CRC
            if command in self.command_responses:
                valid_response = self.command_responses[command]
                invalid_response = valid_response[:-1] + b'\xFF'  # Wrong CRC
                self._input_buffer.extend(invalid_response)
                self.in_waiting = len(self._input_buffer)
                self.errors_generated += 1
                return
        
        if self.behavior_mode == "invalid_length":
            # Generate response with wrong length
            self._input_buffer.extend(b'\x01\x03')  # Too short
            self.in_waiting = len(self._input_buffer)
            self.errors_generated += 1
            return
        
        if self.behavior_mode == "connection_lost":
            # Simulate connection loss during communication
            self.is_open = False
            raise ConnectionError("Connection lost during communication")
        
        # Normal operation - find and return appropriate response
        for cmd, response in self.command_responses.items():
            if command.startswith(cmd[:-1]):  # Match command without CRC
                self._input_buffer.extend(response)
                self.in_waiting = len(self._input_buffer)
                return
        
        # Unknown command - generate error
        error_response = bytes([0x01, 0x81, 0x01, 0x00, 0xC0])  # Invalid function error
        self._input_buffer.extend(error_response)
        self.in_waiting = len(self._input_buffer)
    
    def set_behavior_mode(self, mode: str, **kwargs):
        """Set the behavior mode for testing different scenarios."""
        self.behavior_mode = mode
        
        if "response_delay" in kwargs:
            self.response_delay = kwargs["response_delay"]
        if "fail_probability" in kwargs:
            self.fail_probability = kwargs["fail_probability"]
    
    def add_custom_response(self, command: bytes, response: bytes):
        """Add a custom command/response mapping."""
        self.command_responses[command] = response
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get communication statistics for testing."""
        return {
            "bytes_written": self.bytes_written,
            "bytes_read": self.bytes_read,
            "commands_processed": self.commands_processed,
            "errors_generated": self.errors_generated,
            "buffer_sizes": {
                "input": len(self._input_buffer),
                "output": len(self._output_buffer)
            }
        }
    
    def reset_statistics(self):
        """Reset all statistics counters."""
        self.bytes_written = 0
        self.bytes_read = 0
        self.commands_processed = 0
        self.errors_generated = 0


class MockSerialFactory:
    """Factory for creating mock serial ports with predefined configurations."""
    
    @staticmethod
    def create_normal_port() -> MockSerialPort:
        """Create a mock port for normal operation testing."""
        port = MockSerialPort()
        port.set_behavior_mode("normal")
        return port
    
    @staticmethod
    def create_timeout_port() -> MockSerialPort:
        """Create a mock port that simulates timeouts."""
        port = MockSerialPort()
        port.set_behavior_mode("timeout")
        return port
    
    @staticmethod
    def create_error_port() -> MockSerialPort:
        """Create a mock port that generates device errors."""
        port = MockSerialPort()
        port.set_behavior_mode("device_error")
        return port
    
    @staticmethod
    def create_crc_error_port() -> MockSerialPort:
        """Create a mock port that generates CRC errors."""
        port = MockSerialPort()
        port.set_behavior_mode("invalid_crc")
        return port
    
    @staticmethod
    def create_unstable_port(fail_probability: float = 0.1) -> MockSerialPort:
        """Create a mock port with random failures for stress testing."""
        port = MockSerialPort()
        port.set_behavior_mode("normal", fail_probability=fail_probability)
        return port


class MockPHTCDevice:
    """
    High-level mock PHTC device that can simulate various device states
    and realistic sensor readings.
    """
    
    def __init__(self):
        self.temperature = 25.0  # °C
        self.pressure = 1.013  # bar
        self.voltage = 12.5  # V
        self.status = 0x0001  # Normal operation
        
        # Simulation parameters
        self.temperature_drift = 0.1  # °C per update
        self.pressure_drift = 0.01  # bar per update
        self.voltage_noise = 0.05  # V noise amplitude
        
        # Device state
        self.is_calibrated = True
        self.last_update = time.time()
        self.update_count = 0
    
    def update_sensors(self):
        """Update sensor readings to simulate realistic changes."""
        self.update_count += 1
        current_time = time.time()
        dt = current_time - self.last_update
        
        # Simulate temperature changes
        self.temperature += self.temperature_drift * dt
        
        # Simulate pressure changes
        self.pressure += self.pressure_drift * dt
        
        # Simulate voltage noise
        import random
        self.voltage += random.uniform(-self.voltage_noise, self.voltage_noise)
        
        self.last_update = current_time
    
    def get_temperature_raw(self) -> int:
        """Get temperature as raw 16-bit integer (scaled by 0.1)."""
        self.update_sensors()
        return int((self.temperature + 40) * 10)  # Offset and scale
    
    def get_pressure_raw(self) -> int:
        """Get pressure as raw 16-bit integer (scaled by 0.01)."""
        self.update_sensors()
        return int(self.pressure * 100)  # Scale by 100
    
    def get_voltage_raw(self) -> int:
        """Get voltage as raw 16-bit integer (scaled by 0.001)."""
        self.update_sensors()
        return int(self.voltage * 1000)  # Scale by 1000
    
    def get_status_raw(self) -> int:
        """Get device status as raw 16-bit integer."""
        return self.status
    
    def set_error_condition(self, error_code: int):
        """Set device to error state."""
        self.status = error_code | 0x8000  # Set error bit