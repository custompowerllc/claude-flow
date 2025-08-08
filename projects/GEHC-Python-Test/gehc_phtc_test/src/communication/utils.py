#!/usr/bin/env python3
"""
Communication utilities for RS422 serial operations.

This module provides utility functions for buffer management, timeout handling,
and error detection/recovery for GEHC PHTC communication.
"""

import time
import logging
from typing import Optional, List, Dict, Any, Callable
from threading import Event, Thread
from queue import Queue, Empty
import struct


class BufferManager:
    """
    Manages circular buffer for serial communication data.
    
    Provides efficient buffer management with overflow protection
    and data integrity checks.
    """
    
    def __init__(self, max_size: int = 4096):
        """
        Initialize buffer manager.
        
        Args:
            max_size: Maximum buffer size in bytes
        """
        self.max_size = max_size
        self.buffer = bytearray()
        self.logger = logging.getLogger(__name__)
    
    def append(self, data: bytes) -> bool:
        """
        Append data to buffer with overflow protection.
        
        Args:
            data: Data to append
            
        Returns:
            bool: True if data appended, False if would overflow
        """
        if len(self.buffer) + len(data) > self.max_size:
            self.logger.warning(f"Buffer overflow prevented: {len(self.buffer)} + {len(data)} > {self.max_size}")
            return False
        
        self.buffer.extend(data)
        return True
    
    def peek(self, length: int = None) -> bytes:
        """
        Peek at data without removing from buffer.
        
        Args:
            length: Number of bytes to peek (None = all)
            
        Returns:
            bytes: Peeked data
        """
        if length is None:
            return bytes(self.buffer)
        return bytes(self.buffer[:length])
    
    def consume(self, length: int) -> bytes:
        """
        Consume data from beginning of buffer.
        
        Args:
            length: Number of bytes to consume
            
        Returns:
            bytes: Consumed data
        """
        if length <= 0:
            return b''
        
        consumed = bytes(self.buffer[:length])
        del self.buffer[:length]
        return consumed
    
    def find_pattern(self, pattern: bytes, start: int = 0) -> int:
        """
        Find pattern in buffer.
        
        Args:
            pattern: Pattern to search for
            start: Start position for search
            
        Returns:
            int: Position of pattern, or -1 if not found
        """
        try:
            return self.buffer.index(pattern, start)
        except ValueError:
            return -1
    
    def clear(self) -> None:
        """Clear all buffer data."""
        self.buffer.clear()
    
    def size(self) -> int:
        """Get current buffer size."""
        return len(self.buffer)
    
    def available_space(self) -> int:
        """Get available space in buffer."""
        return self.max_size - len(self.buffer)


class TimeoutHandler:
    """
    Handles various timeout scenarios for communication operations.
    """
    
    def __init__(self):
        """Initialize timeout handler."""
        self.logger = logging.getLogger(__name__)
    
    def wait_for_condition(self, condition_func: Callable[[], bool], 
                          timeout: float, check_interval: float = 0.01) -> bool:
        """
        Wait for a condition to become true with timeout.
        
        Args:
            condition_func: Function that returns bool
            timeout: Timeout in seconds
            check_interval: How often to check condition
            
        Returns:
            bool: True if condition met, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(check_interval)
        
        return False
    
    def execute_with_timeout(self, func: Callable, timeout: float, *args, **kwargs) -> tuple:
        """
        Execute function with timeout using thread.
        
        Args:
            func: Function to execute
            timeout: Timeout in seconds
            args: Function arguments
            kwargs: Function keyword arguments
            
        Returns:
            tuple: (success, result) where success is bool and result is return value or exception
        """
        result_queue = Queue()
        exception_queue = Queue()
        
        def target():
            try:
                result = func(*args, **kwargs)
                result_queue.put(result)
            except Exception as e:
                exception_queue.put(e)
        
        thread = Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            self.logger.warning(f"Function timed out after {timeout} seconds")
            return False, None
        
        try:
            result = result_queue.get_nowait()
            return True, result
        except Empty:
            try:
                exception = exception_queue.get_nowait()
                return False, exception
            except Empty:
                return False, None


class ErrorDetector:
    """
    Detects and analyzes communication errors.
    """
    
    def __init__(self):
        """Initialize error detector."""
        self.logger = logging.getLogger(__name__)
        self.error_counts = {}
        self.error_history = []
        self.max_history = 1000
    
    def detect_framing_error(self, data: bytes) -> bool:
        """
        Detect framing errors in received data.
        
        Args:
            data: Received data
            
        Returns:
            bool: True if framing error detected
        """
        if not data:
            return False
        
        # Check for invalid characters or patterns that suggest framing issues
        invalid_chars = 0
        for byte in data:
            if byte == 0xFF or byte == 0x00:  # Common framing error indicators
                invalid_chars += 1
        
        error_ratio = invalid_chars / len(data)
        is_error = error_ratio > 0.5  # More than 50% invalid suggests framing error
        
        if is_error:
            self._record_error("framing_error", f"High invalid char ratio: {error_ratio:.2f}")
        
        return is_error
    
    def detect_timeout_pattern(self, response_times: List[float], threshold: float = 2.0) -> bool:
        """
        Detect timeout patterns that might indicate communication issues.
        
        Args:
            response_times: List of recent response times
            threshold: Threshold multiplier for average response time
            
        Returns:
            bool: True if timeout pattern detected
        """
        if len(response_times) < 5:
            return False
        
        avg_time = sum(response_times) / len(response_times)
        recent_avg = sum(response_times[-3:]) / 3
        
        is_pattern = recent_avg > avg_time * threshold
        
        if is_pattern:
            self._record_error("timeout_pattern", f"Recent avg {recent_avg:.3f}s vs overall {avg_time:.3f}s")
        
        return is_pattern
    
    def detect_data_corruption(self, expected_length: int, actual_data: bytes) -> bool:
        """
        Detect data corruption based on expected vs actual data.
        
        Args:
            expected_length: Expected data length
            actual_data: Actual received data
            
        Returns:
            bool: True if corruption detected
        """
        if len(actual_data) != expected_length:
            self._record_error("length_mismatch", f"Expected {expected_length}, got {len(actual_data)}")
            return True
        
        # Check for obvious corruption patterns
        if len(set(actual_data)) == 1 and len(actual_data) > 1:  # All same byte
            self._record_error("repeated_byte", f"All bytes are {actual_data[0]:#04x}")
            return True
        
        return False
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics and analysis.
        
        Returns:
            dict: Error statistics
        """
        total_errors = sum(self.error_counts.values())
        stats = {
            "total_errors": total_errors,
            "error_types": dict(self.error_counts),
            "recent_errors": len([e for e in self.error_history if time.time() - e["timestamp"] < 300]),  # Last 5 minutes
            "error_rate": len(self.error_history) / max(1, len(self.error_history)) if self.error_history else 0
        }
        
        if self.error_history:
            stats["first_error"] = self.error_history[0]["timestamp"]
            stats["last_error"] = self.error_history[-1]["timestamp"]
        
        return stats
    
    def _record_error(self, error_type: str, description: str) -> None:
        """
        Record an error occurrence.
        
        Args:
            error_type: Type of error
            description: Error description
        """
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        error_record = {
            "timestamp": time.time(),
            "type": error_type,
            "description": description
        }
        
        self.error_history.append(error_record)
        
        # Limit history size
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
        
        self.logger.warning(f"Error detected - {error_type}: {description}")


class RecoveryManager:
    """
    Manages error recovery strategies for communication failures.
    """
    
    def __init__(self, max_retries: int = 3):
        """
        Initialize recovery manager.
        
        Args:
            max_retries: Maximum number of retry attempts
        """
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
        self.recovery_stats = {
            "attempts": 0,
            "successes": 0,
            "failures": 0
        }
    
    def attempt_recovery(self, recovery_func: Callable, *args, **kwargs) -> tuple:
        """
        Attempt recovery with exponential backoff.
        
        Args:
            recovery_func: Function to attempt for recovery
            args: Function arguments
            kwargs: Function keyword arguments
            
        Returns:
            tuple: (success, result, attempts_made)
        """
        for attempt in range(self.max_retries):
            self.recovery_stats["attempts"] += 1
            
            try:
                self.logger.info(f"Recovery attempt {attempt + 1}/{self.max_retries}")
                
                # Exponential backoff delay
                if attempt > 0:
                    delay = min(2 ** (attempt - 1) * 0.1, 2.0)  # Max 2 second delay
                    time.sleep(delay)
                
                result = recovery_func(*args, **kwargs)
                
                self.recovery_stats["successes"] += 1
                self.logger.info(f"Recovery successful on attempt {attempt + 1}")
                return True, result, attempt + 1
                
            except Exception as e:
                self.logger.warning(f"Recovery attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    self.recovery_stats["failures"] += 1
                continue
        
        self.logger.error(f"Recovery failed after {self.max_retries} attempts")
        return False, None, self.max_retries
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """
        Get recovery statistics.
        
        Returns:
            dict: Recovery statistics
        """
        attempts = self.recovery_stats["attempts"]
        if attempts > 0:
            success_rate = (self.recovery_stats["successes"] / attempts) * 100
        else:
            success_rate = 0
        
        return {
            **self.recovery_stats,
            "success_rate": success_rate
        }


class MessageBuffer:
    """
    Specialized buffer for managing protocol messages.
    """
    
    def __init__(self, preamble: int = 0xAA, response_header: int = 0x40):
        """
        Initialize message buffer.
        
        Args:
            preamble: Expected message preamble byte
            response_header: Expected response header byte
        """
        self.preamble = preamble
        self.response_header = response_header
        self.buffer_manager = BufferManager()
        self.logger = logging.getLogger(__name__)
    
    def add_data(self, data: bytes) -> None:
        """
        Add data to message buffer.
        
        Args:
            data: Data to add
        """
        if not self.buffer_manager.append(data):
            self.logger.warning("Message buffer overflow, clearing old data")
            self.buffer_manager.clear()
            self.buffer_manager.append(data)
    
    def extract_complete_message(self) -> Optional[bytes]:
        """
        Extract a complete message from buffer if available.
        
        Returns:
            bytes: Complete message, or None if no complete message available
        """
        # Look for message start patterns
        command_start = self.buffer_manager.find_pattern(struct.pack('BB', self.preamble, 0x23))
        response_start = self.buffer_manager.find_pattern(struct.pack('B', self.response_header))
        
        message_start = -1
        is_command = False
        
        if command_start >= 0 and (response_start < 0 or command_start < response_start):
            message_start = command_start
            is_command = True
        elif response_start >= 0:
            message_start = response_start
            is_command = False
        
        if message_start < 0:
            return None
        
        # Discard data before message start
        if message_start > 0:
            self.buffer_manager.consume(message_start)
        
        # Check if we have enough data for message length
        min_length = 5 if is_command else 4  # Minimum message lengths
        if self.buffer_manager.size() < min_length:
            return None
        
        # Get message length
        if is_command:
            if self.buffer_manager.size() < 4:
                return None
            data_length = self.buffer_manager.peek(4)[3]
            total_length = 5 + data_length  # [AA][23][CMD][LEN][DATA...][CRC8]
        else:
            if self.buffer_manager.size() < 3:
                return None
            data_length = self.buffer_manager.peek(3)[2]
            total_length = 4 + data_length  # [40][CMD][LEN][DATA...][CRC8]
        
        # Check if we have complete message
        if self.buffer_manager.size() < total_length:
            return None
        
        # Extract complete message
        message = self.buffer_manager.consume(total_length)
        self.logger.debug(f"Extracted {'command' if is_command else 'response'} message: {message.hex()}")
        return message
    
    def clear(self) -> None:
        """Clear message buffer."""
        self.buffer_manager.clear()
    
    def size(self) -> int:
        """Get buffer size."""
        return self.buffer_manager.size()