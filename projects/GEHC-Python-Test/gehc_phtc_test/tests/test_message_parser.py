"""Tests for MessageParser class."""

import pytest
from typing import Dict, Any, Union
from gehc_phtc_test.src.parsing.message_parser import MessageParser, DataType, ScalingInfo


class TestMessageParser:
    """Test cases for MessageParser class."""

    def test_parse_unsigned_int_16_basic(self):
        """Test parsing basic unsigned 16-bit integer."""
        parser = MessageParser()
        response_data = bytes([0x12, 0x34])  # Little endian: 0x3412
        
        result = parser.parse_response(
            response_data,
            data_type=DataType.UNSIGNED_INT_16,
            scaling=ScalingInfo(granularity=1.0, unit="", offset=0)
        )
        
        assert result.raw_value == 0x3412
        assert result.scaled_value == 0x3412
        assert result.formatted_value == "13330"
        assert result.unit == ""

    def test_parse_signed_int_16_negative(self):
        """Test parsing signed 16-bit integer with negative value."""
        parser = MessageParser()
        response_data = bytes([0xFF, 0xFF])  # -1 in two's complement
        
        result = parser.parse_response(
            response_data,
            data_type=DataType.SIGNED_INT_16,
            scaling=ScalingInfo(granularity=1.0, unit="", offset=0)
        )
        
        assert result.raw_value == -1
        assert result.scaled_value == -1
        assert result.formatted_value == "-1"

    def test_parse_with_scaling_millivolts(self):
        """Test parsing with scaling to millivolts."""
        parser = MessageParser()
        response_data = bytes([0x00, 0x10])  # 0x1000 = 4096
        
        result = parser.parse_response(
            response_data,
            data_type=DataType.UNSIGNED_INT_16,
            scaling=ScalingInfo(granularity=0.1, unit="mV", offset=0)
        )
        
        assert result.raw_value == 4096
        assert result.scaled_value == 409.6
        assert result.formatted_value == "409.6 mV"
        assert result.unit == "mV"

    def test_parse_with_offset_temperature(self):
        """Test parsing temperature with offset."""
        parser = MessageParser()
        response_data = bytes([0x00, 0x01])  # 256
        
        result = parser.parse_response(
            response_data,
            data_type=DataType.UNSIGNED_INT_16,
            scaling=ScalingInfo(granularity=0.1, unit="°C", offset=-40.0)
        )
        
        assert result.raw_value == 256
        assert abs(result.scaled_value - (-14.4)) < 0.001  # (256 * 0.1) - 40
        assert result.formatted_value.startswith("-14.4") and "°C" in result.formatted_value

    def test_parse_percentage(self):
        """Test parsing percentage values."""
        parser = MessageParser()
        response_data = bytes([0x32])  # 50 decimal
        
        result = parser.parse_response(
            response_data,
            data_type=DataType.UNSIGNED_INT_8,
            scaling=ScalingInfo(granularity=0.4, unit="%", offset=0)
        )
        
        assert result.raw_value == 50
        assert result.scaled_value == 20.0  # 50 * 0.4
        assert result.formatted_value == "20.0%"

    def test_parse_boolean_true(self):
        """Test parsing boolean true value."""
        parser = MessageParser()
        response_data = bytes([0x01])
        
        result = parser.parse_response(
            response_data,
            data_type=DataType.BOOLEAN,
            scaling=ScalingInfo(granularity=1.0, unit="", offset=0)
        )
        
        assert result.raw_value == 1
        assert result.scaled_value == True
        assert result.formatted_value == "True"

    def test_parse_boolean_false(self):
        """Test parsing boolean false value."""
        parser = MessageParser()
        response_data = bytes([0x00])
        
        result = parser.parse_response(
            response_data,
            data_type=DataType.BOOLEAN,
            scaling=ScalingInfo(granularity=1.0, unit="", offset=0)
        )
        
        assert result.raw_value == 0
        assert result.scaled_value == False
        assert result.formatted_value == "False"

    def test_parse_string_data(self):
        """Test parsing string data."""
        parser = MessageParser()
        response_data = b"GEHC TEST\x00"
        
        result = parser.parse_response(
            response_data,
            data_type=DataType.STRING,
            scaling=ScalingInfo(granularity=1.0, unit="", offset=0)
        )
        
        assert result.raw_value == b"GEHC TEST\x00"
        assert result.scaled_value == "GEHC TEST"
        assert result.formatted_value == "GEHC TEST"

    def test_parse_block_data(self):
        """Test parsing block data."""
        parser = MessageParser()
        response_data = bytes([0x01, 0x02, 0x03, 0x04])
        
        result = parser.parse_response(
            response_data,
            data_type=DataType.BLOCK_DATA,
            scaling=ScalingInfo(granularity=1.0, unit="", offset=0)
        )
        
        assert result.raw_value == bytes([0x01, 0x02, 0x03, 0x04])
        assert result.scaled_value == [1, 2, 3, 4]
        assert result.formatted_value == "01 02 03 04"

    def test_validate_range_within_bounds(self):
        """Test range validation within bounds."""
        parser = MessageParser()
        
        # Test within range
        assert parser.validate_range(50.0, min_val=0.0, max_val=100.0) == True

    def test_validate_range_outside_bounds(self):
        """Test range validation outside bounds."""
        parser = MessageParser()
        
        # Test outside range
        assert parser.validate_range(150.0, min_val=0.0, max_val=100.0) == False
        assert parser.validate_range(-10.0, min_val=0.0, max_val=100.0) == False

    def test_parse_invalid_data_type(self):
        """Test parsing with invalid data type."""
        parser = MessageParser()
        response_data = bytes([0x01, 0x02])
        
        with pytest.raises(ValueError, match="Unsupported data type"):
            parser.parse_response(
                response_data,
                data_type="INVALID_TYPE",
                scaling=ScalingInfo(granularity=1.0, unit="", offset=0)
            )

    def test_parse_insufficient_data(self):
        """Test parsing with insufficient data."""
        parser = MessageParser()
        response_data = bytes([0x01])  # Only 1 byte for 16-bit data
        
        with pytest.raises(ValueError, match="Insufficient data"):
            parser.parse_response(
                response_data,
                data_type=DataType.UNSIGNED_INT_16,
                scaling=ScalingInfo(granularity=1.0, unit="", offset=0)
            )

    def test_parse_current_milliamps(self):
        """Test parsing current in milliamps."""
        parser = MessageParser()
        response_data = bytes([0xE8, 0x03])  # 1000 in little endian
        
        result = parser.parse_response(
            response_data,
            data_type=DataType.UNSIGNED_INT_16,
            scaling=ScalingInfo(granularity=0.01, unit="mA", offset=0)
        )
        
        assert result.raw_value == 1000
        assert result.scaled_value == 10.0
        assert result.formatted_value == "10.0 mA"

    def test_parse_32_bit_unsigned(self):
        """Test parsing 32-bit unsigned integer."""
        parser = MessageParser()
        response_data = bytes([0x00, 0x10, 0x00, 0x00])  # 0x00001000 = 4096
        
        result = parser.parse_response(
            response_data,
            data_type=DataType.UNSIGNED_INT_32,
            scaling=ScalingInfo(granularity=1.0, unit="", offset=0)
        )
        
        assert result.raw_value == 4096
        assert result.scaled_value == 4096
        assert result.formatted_value == "4096"