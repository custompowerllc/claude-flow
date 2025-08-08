"""Tests for data processing utilities."""

import pytest
import struct
from gehc_phtc_test.src.parsing.data_utils import DataUtils, ValidationError


class TestDataUtils:
    """Test cases for DataUtils class."""

    def test_calculate_scaling_basic(self):
        """Test basic scaling calculation."""
        utils = DataUtils()
        
        result = utils.calculate_scaling(1000, granularity=0.1, offset=0)
        assert result == 100.0

    def test_calculate_scaling_with_offset(self):
        """Test scaling calculation with offset."""
        utils = DataUtils()
        
        result = utils.calculate_scaling(500, granularity=0.1, offset=-40.0)
        assert result == 10.0  # (500 * 0.1) - 40

    def test_convert_millivolts_to_volts(self):
        """Test conversion from millivolts to volts."""
        utils = DataUtils()
        
        result = utils.convert_units(5000, from_unit="mV", to_unit="V")
        assert result == 5.0

    def test_convert_celsius_to_fahrenheit(self):
        """Test temperature conversion."""
        utils = DataUtils()
        
        result = utils.convert_units(25.0, from_unit="°C", to_unit="°F")
        assert result == 77.0

    def test_convert_milliamps_to_amps(self):
        """Test current conversion."""
        utils = DataUtils()
        
        result = utils.convert_units(1500, from_unit="mA", to_unit="A")
        assert result == 1.5

    def test_format_value_with_precision(self):
        """Test value formatting with specified precision."""
        utils = DataUtils()
        
        result = utils.format_value(123.456789, precision=2)
        assert result == "123.46"

    def test_format_value_as_integer(self):
        """Test formatting whole numbers as integers."""
        utils = DataUtils()
        
        result = utils.format_value(123.0, precision=1)
        assert result == "123"

    def test_format_percentage_value(self):
        """Test formatting percentage values."""
        utils = DataUtils()
        
        result = utils.format_percentage(0.75)
        assert result == "75.0%"

    def test_validate_range_success(self):
        """Test successful range validation."""
        utils = DataUtils()
        
        # Should not raise exception
        utils.validate_range(50.0, min_val=0.0, max_val=100.0, name="test_value")

    def test_validate_range_below_minimum(self):
        """Test range validation below minimum."""
        utils = DataUtils()
        
        with pytest.raises(ValidationError, match="test_value.*below minimum"):
            utils.validate_range(-10.0, min_val=0.0, max_val=100.0, name="test_value")

    def test_validate_range_above_maximum(self):
        """Test range validation above maximum."""
        utils = DataUtils()
        
        with pytest.raises(ValidationError, match="test_value.*above maximum"):
            utils.validate_range(150.0, min_val=0.0, max_val=100.0, name="test_value")

    def test_clamp_value_within_range(self):
        """Test clamping value already within range."""
        utils = DataUtils()
        
        result = utils.clamp_value(50.0, min_val=0.0, max_val=100.0)
        assert result == 50.0

    def test_clamp_value_below_minimum(self):
        """Test clamping value below minimum."""
        utils = DataUtils()
        
        result = utils.clamp_value(-10.0, min_val=0.0, max_val=100.0)
        assert result == 0.0

    def test_clamp_value_above_maximum(self):
        """Test clamping value above maximum."""
        utils = DataUtils()
        
        result = utils.clamp_value(150.0, min_val=0.0, max_val=100.0)
        assert result == 100.0

    def test_bytes_to_hex_string(self):
        """Test converting bytes to hex string."""
        utils = DataUtils()
        
        data = bytes([0x01, 0x23, 0xAB, 0xFF])
        result = utils.bytes_to_hex_string(data)
        assert result == "01 23 AB FF"

    def test_hex_string_to_bytes(self):
        """Test converting hex string to bytes."""
        utils = DataUtils()
        
        hex_str = "01 23 AB FF"
        result = utils.hex_string_to_bytes(hex_str)
        assert result == bytes([0x01, 0x23, 0xAB, 0xFF])

    def test_parse_little_endian_uint16(self):
        """Test parsing little endian unsigned 16-bit integer."""
        utils = DataUtils()
        
        data = bytes([0x34, 0x12])  # 0x1234 in little endian
        result = utils.parse_little_endian_uint16(data)
        assert result == 0x1234

    def test_parse_little_endian_uint32(self):
        """Test parsing little endian unsigned 32-bit integer."""
        utils = DataUtils()
        
        data = bytes([0x78, 0x56, 0x34, 0x12])  # 0x12345678 in little endian
        result = utils.parse_little_endian_uint32(data)
        assert result == 0x12345678

    def test_calculate_checksum(self):
        """Test checksum calculation."""
        utils = DataUtils()
        
        data = bytes([0x01, 0x02, 0x03, 0x04])
        checksum = utils.calculate_checksum(data)
        assert checksum == 0x0A  # Sum of bytes

    def test_is_valid_ascii_string(self):
        """Test ASCII string validation."""
        utils = DataUtils()
        
        assert utils.is_valid_ascii_string(b"Hello World") == True
        assert utils.is_valid_ascii_string(b"Hello\x80World") == False

    def test_safe_decode_string(self):
        """Test safe string decoding with error handling."""
        utils = DataUtils()
        
        # Valid ASCII
        result = utils.safe_decode_string(b"Hello World\x00")
        assert result == "Hello World"
        
        # Invalid bytes replaced
        result = utils.safe_decode_string(b"Hello\x80\xFFWorld")
        assert "Hello" in result
        assert "World" in result

    def test_round_to_precision(self):
        """Test rounding to specified precision."""
        utils = DataUtils()
        
        result = utils.round_to_precision(123.456789, precision=3)
        assert result == 123.457

    def test_format_engineering_notation(self):
        """Test formatting in engineering notation."""
        utils = DataUtils()
        
        result = utils.format_engineering_notation(0.001234)
        assert result == "1.23e-03"

    def test_detect_data_anomalies(self):
        """Test detection of data anomalies."""
        utils = DataUtils()
        
        # Normal data
        normal_data = [1.0, 1.1, 0.9, 1.05, 0.95]
        anomalies = utils.detect_anomalies(normal_data, threshold=2.0)
        assert len(anomalies) == 0
        
        # Data with outlier
        outlier_data = [1.0, 1.1, 0.9, 10.0, 0.95]  # 10.0 is an outlier
        anomalies = utils.detect_anomalies(outlier_data, threshold=1.0)
        assert len(anomalies) >= 1
        assert 10.0 in anomalies

    def test_calculate_statistics(self):
        """Test statistical calculations."""
        utils = DataUtils()
        
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        stats = utils.calculate_statistics(data)
        
        assert stats['mean'] == 3.0
        assert stats['median'] == 3.0
        assert stats['min'] == 1.0
        assert stats['max'] == 5.0
        assert abs(stats['std'] - 1.58113883) < 0.0001  # Standard deviation

    def test_interpolate_missing_values(self):
        """Test interpolation of missing values."""
        utils = DataUtils()
        
        # Data with None values to interpolate
        data = [1.0, None, 3.0, None, 5.0]
        result = utils.interpolate_missing_values(data)
        
        expected = [1.0, 2.0, 3.0, 4.0, 5.0]  # Linear interpolation
        assert result == expected

    def test_apply_moving_average(self):
        """Test moving average calculation."""
        utils = DataUtils()
        
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = utils.apply_moving_average(data, window_size=3)
        
        # Expected: [1.0, 1.5, 2.0, 3.0, 4.0] (moving average with window=3)
        assert len(result) == len(data)
        assert abs(result[2] - 2.0) < 0.001  # (1+2+3)/3 = 2