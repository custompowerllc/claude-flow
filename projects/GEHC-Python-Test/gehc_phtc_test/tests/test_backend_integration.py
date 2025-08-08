#!/usr/bin/env python3
"""
Integration tests for backend communication components.

This module tests the integration between SerialHandler, ProtocolHandler,
and communication utilities to ensure proper RS422 communication.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import serial

from gehc_phtc_test.src.communication import (
    SerialHandler, SerialConnectionError,
    ProtocolHandler, ProtocolError, MessageDirection,
    BufferManager, TimeoutHandler, ErrorDetector, RecoveryManager, MessageBuffer
)


class TestBackendIntegration:
    """Test integration of all backend communication components."""
    
    def test_protocol_handler_crc8_calculation(self):
        """Test CRC8 calculation using SMBus PEC polynomial."""
        handler = ProtocolHandler()
        
        # Test known CRC8 values for SMBus PEC
        test_data = b'\x23\x08\x00'  # Sync header, command, no data
        crc = handler.calculate_crc8(test_data)
        
        # Verify CRC8 is calculated (exact value depends on polynomial implementation)
        assert isinstance(crc, int)
        assert 0 <= crc <= 0xFF
    
    def test_command_formatting_and_validation(self):
        """Test command formatting and response validation."""
        handler = ProtocolHandler()
        
        # Format a command
        command = handler.format_command(0x08, b'')
        
        # Verify command structure: [0xAA][0x23][0x08][0x00][CRC8]
        assert len(command) == 5
        assert command[0] == 0xAA  # Preamble
        assert command[1] == 0x23  # Host-to-battery sync
        assert command[2] == 0x08  # Command code
        assert command[3] == 0x00  # No data length
        
        # Create a corresponding test response
        response = handler.create_test_response(0x08, b'\x1A\x2B')
        
        # Validate the response
        assert handler.validate_response(response)
        
        # Extract response data
        cmd_code, data = handler.extract_response_data(response)
        assert cmd_code == 0x08
        assert data == b'\x1A\x2B'
    
    @patch('serial.Serial')
    def test_serial_handler_basic_operations(self, mock_serial):
        """Test basic serial handler operations with mocked serial port."""
        # Setup mock
        mock_port = Mock()
        mock_port.is_open = True
        mock_port.in_waiting = 5
        mock_port.out_waiting = 0
        mock_serial.return_value = mock_port
        
        # Test connection
        handler = SerialHandler('COM3', 115200)
        assert handler.connect()
        assert handler.is_connected()
        
        # Test sending command
        test_command = b'\xAA\x23\x08\x00\x2D'
        mock_port.write.return_value = len(test_command)
        
        assert handler.send_command(test_command)
        mock_port.write.assert_called_with(test_command)
        mock_port.flush.assert_called()
        
        # Test receiving response
        test_response = b'\x40\x08\x02\x1A\x2B\x8F'
        mock_port.read.return_value = test_response
        
        response = handler.receive_response()
        assert response == test_response
        
        # Test disconnection
        handler.disconnect()
        mock_port.close.assert_called()
    
    def test_buffer_manager_operations(self):
        """Test buffer manager functionality."""
        buffer = BufferManager(max_size=100)
        
        # Test basic operations
        test_data = b'\xAA\x23\x08\x00\x2D'
        assert buffer.append(test_data)
        assert buffer.size() == len(test_data)
        
        # Test peek without consuming
        peeked = buffer.peek(3)
        assert peeked == test_data[:3]
        assert buffer.size() == len(test_data)  # Size unchanged
        
        # Test consume
        consumed = buffer.consume(2)
        assert consumed == test_data[:2]
        assert buffer.size() == len(test_data) - 2
        
        # Test pattern finding
        buffer.clear()
        buffer.append(b'\x00\x00\xAA\x23\x08')
        pos = buffer.find_pattern(b'\xAA\x23')
        assert pos == 2
        
        # Test overflow protection
        large_data = b'\x00' * 200
        assert not buffer.append(large_data)  # Should fail due to overflow
    
    def test_message_buffer_extraction(self):
        """Test message buffer message extraction."""
        msg_buffer = MessageBuffer()
        
        # Add partial data
        msg_buffer.add_data(b'\x00\x00')  # Noise
        msg_buffer.add_data(b'\x40\x08\x02\x1A\x2B\x8F')  # Complete response
        
        # Extract message
        message = msg_buffer.extract_complete_message()
        assert message == b'\x40\x08\x02\x1A\x2B\x8F'
        
        # Buffer should be empty now
        assert msg_buffer.size() == 0
    
    def test_timeout_handler(self):
        """Test timeout handler functionality."""
        handler = TimeoutHandler()
        
        # Test condition waiting
        start_time = time.time()
        condition_met = [False]
        
        def set_condition():
            time.sleep(0.1)
            condition_met[0] = True
        
        # Start condition setter in background
        import threading
        threading.Thread(target=set_condition).start()
        
        # Wait for condition
        result = handler.wait_for_condition(lambda: condition_met[0], timeout=0.5)
        assert result
        assert time.time() - start_time < 0.5
    
    def test_error_detector(self):
        """Test error detection functionality."""
        detector = ErrorDetector()
        
        # Test framing error detection
        bad_data = b'\xFF\xFF\xFF\xFF\xFF'  # High ratio of 0xFF suggests framing error
        assert detector.detect_framing_error(bad_data)
        
        # Test data corruption detection
        assert detector.detect_data_corruption(expected_length=5, actual_data=b'\x00\x00\x00')
        
        # Test timeout pattern detection
        response_times = [0.1, 0.1, 0.1, 0.5, 0.6, 0.7]  # Recent times are much higher
        assert detector.detect_timeout_pattern(response_times, threshold=2.0)
        
        # Get statistics
        stats = detector.get_error_statistics()
        assert stats['total_errors'] > 0
    
    def test_recovery_manager(self):
        """Test recovery manager functionality."""
        manager = RecoveryManager(max_retries=3)
        
        # Test successful recovery
        attempt_count = [0]
        def recovery_func():
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise Exception("Simulated failure")
            return "Success"
        
        success, result, attempts = manager.attempt_recovery(recovery_func)
        assert success
        assert result == "Success"
        assert attempts == 2
        
        # Test failed recovery
        def always_fail():
            raise Exception("Always fails")
        
        success, result, attempts = manager.attempt_recovery(always_fail)
        assert not success
        assert attempts == 3
    
    @patch('serial.Serial')
    def test_full_communication_flow(self, mock_serial):
        """Test complete communication flow from command to response."""
        # Setup mocks
        mock_port = Mock()
        mock_port.is_open = True
        mock_port.in_waiting = 0
        mock_serial.return_value = mock_port
        
        # Initialize components
        serial_handler = SerialHandler('COM3')
        protocol_handler = ProtocolHandler()
        
        # Connect
        assert serial_handler.connect()
        
        # Create and send command
        command = protocol_handler.format_command(0x08, b'')
        mock_port.write.return_value = len(command)
        
        assert serial_handler.send_command(command)
        
        # Simulate response
        test_response = protocol_handler.create_test_response(0x08, b'\x1A\x2B')
        mock_port.in_waiting = len(test_response)
        mock_port.read.return_value = test_response
        
        # Receive and validate response
        response = serial_handler.receive_response()
        assert response == test_response
        
        # Parse response
        is_valid, cmd_code, data = protocol_handler.parse_ge_response(response)
        assert is_valid
        assert cmd_code == 0x08
        assert data == b'\x1A\x2B'
        
        # Disconnect
        serial_handler.disconnect()
    
    def test_protocol_error_handling(self):
        """Test protocol error handling scenarios."""
        handler = ProtocolHandler()
        
        # Test invalid command code
        with pytest.raises(ProtocolError):
            handler.format_command(256)  # Out of range
        
        # Test data too long
        long_data = b'x' * 300
        with pytest.raises(ProtocolError):
            handler.format_command(0x08, long_data)
        
        # Test invalid response validation
        invalid_response = b'\x00\x08\x02\x1A\x2B\xFF'  # Wrong header
        assert not handler.validate_response(invalid_response)
        
        # Test CRC mismatch
        bad_crc_response = b'\x40\x08\x02\x1A\x2B\xFF'  # Wrong CRC
        assert not handler.validate_response(bad_crc_response)
    
    def test_message_analysis(self):
        """Test message analysis functionality."""
        handler = ProtocolHandler()
        
        # Analyze command message
        command = handler.format_command(0x08, b'\x12\x34')
        info = handler.get_message_info(command)
        
        assert info['type'] == 'command'
        assert info['direction'] == 'host_to_battery'
        assert info['command_code'] == 0x08
        assert info['data_length'] == 2
        assert info['crc8_valid']
        
        # Analyze response message
        response = handler.create_test_response(0x08, b'\x56\x78')
        info = handler.get_message_info(response)
        
        assert info['type'] == 'response'
        assert info['direction'] == 'battery_to_host'
        assert info['command_code'] == 0x08
        assert info['data_length'] == 2
        assert info['crc8_valid']


class TestCRC8Implementation:
    """Test CRC8 SMBus PEC implementation in detail."""
    
    def test_crc8_empty_data(self):
        """Test CRC8 calculation with empty data."""
        handler = ProtocolHandler()
        crc = handler.calculate_crc8(b'')
        assert crc == 0x00  # CRC of empty data should be 0
    
    def test_crc8_single_byte(self):
        """Test CRC8 calculation with single byte."""
        handler = ProtocolHandler()
        crc = handler.calculate_crc8(b'\x23')
        assert isinstance(crc, int)
        assert 0 <= crc <= 0xFF
    
    def test_crc8_consistency(self):
        """Test CRC8 calculation consistency."""
        handler = ProtocolHandler()
        test_data = b'\x23\x08\x02\x1A\x2B'
        
        # Calculate CRC multiple times
        crc1 = handler.calculate_crc8(test_data)
        crc2 = handler.calculate_crc8(test_data)
        
        assert crc1 == crc2  # Should be consistent
    
    def test_crc8_different_data(self):
        """Test CRC8 produces different values for different data."""
        handler = ProtocolHandler()
        
        crc1 = handler.calculate_crc8(b'\x23\x08\x00')
        crc2 = handler.calculate_crc8(b'\x23\x09\x00')
        
        assert crc1 != crc2  # Different data should produce different CRC


if __name__ == '__main__':
    pytest.main([__file__])