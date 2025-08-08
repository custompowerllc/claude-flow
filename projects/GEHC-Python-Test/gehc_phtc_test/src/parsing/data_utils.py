"""Data processing utilities for GEHC PHTC RS422 protocol."""

import struct
import statistics
from typing import List, Optional, Dict, Any, Union


class ValidationError(Exception):
    """Exception raised for data validation errors."""
    pass


class DataUtils:
    """Utility class for data processing, conversion, and validation."""

    def __init__(self):
        """Initialize data utilities."""
        self._conversion_factors = {
            # Voltage conversions
            ("mV", "V"): 0.001,
            ("V", "mV"): 1000.0,
            # Current conversions
            ("mA", "A"): 0.001,
            ("A", "mA"): 1000.0,
            ("µA", "mA"): 0.001,
            ("mA", "µA"): 1000.0,
            ("µA", "A"): 0.000001,
            ("A", "µA"): 1000000.0,
        }

    def calculate_scaling(
        self, 
        raw_value: Union[int, float], 
        granularity: float, 
        offset: float = 0.0
    ) -> float:
        """
        Calculate scaled value from raw data.
        
        Args:
            raw_value: Raw numeric value from device
            granularity: Scaling factor (resolution per LSB)
            offset: Offset to apply after scaling
            
        Returns:
            Scaled value as float
        """
        return (raw_value * granularity) + offset

    def convert_units(
        self, 
        value: Union[int, float], 
        from_unit: str, 
        to_unit: str
    ) -> float:
        """
        Convert value between different units.
        
        Args:
            value: Value to convert
            from_unit: Source unit
            to_unit: Target unit
            
        Returns:
            Converted value
            
        Raises:
            ValueError: If conversion not supported
        """
        if from_unit == to_unit:
            return float(value)

        # Handle temperature conversions specially
        if from_unit == "°C" and to_unit == "°F":
            return (value * 9.0 / 5.0) + 32.0
        elif from_unit == "°F" and to_unit == "°C":
            return (value - 32.0) * 5.0 / 9.0

        # Handle standard unit conversions
        conversion_key = (from_unit, to_unit)
        if conversion_key in self._conversion_factors:
            return value * self._conversion_factors[conversion_key]

        raise ValueError(f"Conversion from {from_unit} to {to_unit} not supported")

    def format_value(self, value: Union[int, float], precision: int = 2) -> str:
        """
        Format numeric value with specified precision.
        
        Args:
            value: Value to format
            precision: Number of decimal places
            
        Returns:
            Formatted string
        """
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        
        return f"{value:.{precision}f}".rstrip('0').rstrip('.')

    def format_percentage(self, value: Union[int, float], precision: int = 1) -> str:
        """
        Format value as percentage.
        
        Args:
            value: Value to format (0.0 to 1.0)
            precision: Number of decimal places
            
        Returns:
            Formatted percentage string
        """
        percentage = value * 100.0
        return f"{percentage:.{precision}f}%"

    def validate_range(
        self, 
        value: Union[int, float], 
        min_val: Optional[float] = None, 
        max_val: Optional[float] = None,
        name: str = "value"
    ) -> None:
        """
        Validate that value is within specified range.
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            name: Name of value for error messages
            
        Raises:
            ValidationError: If value is out of range
        """
        if min_val is not None and value < min_val:
            raise ValidationError(f"{name} ({value}) is below minimum ({min_val})")
        
        if max_val is not None and value > max_val:
            raise ValidationError(f"{name} ({value}) is above maximum ({max_val})")

    def clamp_value(
        self, 
        value: Union[int, float], 
        min_val: float, 
        max_val: float
    ) -> float:
        """
        Clamp value to specified range.
        
        Args:
            value: Value to clamp
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Clamped value
        """
        return max(min_val, min(value, max_val))

    def bytes_to_hex_string(self, data: bytes, separator: str = " ") -> str:
        """
        Convert bytes to hexadecimal string representation.
        
        Args:
            data: Bytes to convert
            separator: Separator between hex bytes
            
        Returns:
            Hex string representation
        """
        return separator.join(f"{b:02X}" for b in data)

    def hex_string_to_bytes(self, hex_str: str) -> bytes:
        """
        Convert hexadecimal string to bytes.
        
        Args:
            hex_str: Hex string (space or comma separated)
            
        Returns:
            Bytes object
            
        Raises:
            ValueError: If invalid hex string
        """
        # Remove separators and whitespace
        clean_hex = hex_str.replace(" ", "").replace(",", "").replace("\n", "")
        
        # Ensure even length
        if len(clean_hex) % 2 != 0:
            raise ValueError("Hex string must have even number of characters")
        
        try:
            return bytes.fromhex(clean_hex)
        except ValueError as e:
            raise ValueError(f"Invalid hex string: {e}")

    def parse_little_endian_uint16(self, data: bytes, offset: int = 0) -> int:
        """
        Parse little endian unsigned 16-bit integer.
        
        Args:
            data: Bytes to parse
            offset: Byte offset to start parsing
            
        Returns:
            Parsed integer value
            
        Raises:
            ValueError: If insufficient data
        """
        if len(data) < offset + 2:
            raise ValueError("Insufficient data for uint16")
        
        return struct.unpack("<H", data[offset:offset+2])[0]

    def parse_little_endian_uint32(self, data: bytes, offset: int = 0) -> int:
        """
        Parse little endian unsigned 32-bit integer.
        
        Args:
            data: Bytes to parse
            offset: Byte offset to start parsing
            
        Returns:
            Parsed integer value
            
        Raises:
            ValueError: If insufficient data
        """
        if len(data) < offset + 4:
            raise ValueError("Insufficient data for uint32")
        
        return struct.unpack("<I", data[offset:offset+4])[0]

    def calculate_checksum(self, data: bytes, algorithm: str = "sum") -> int:
        """
        Calculate checksum for data validation.
        
        Args:
            data: Data to calculate checksum for
            algorithm: Checksum algorithm ("sum", "xor")
            
        Returns:
            Calculated checksum
        """
        if algorithm == "sum":
            return sum(data) & 0xFF
        elif algorithm == "xor":
            checksum = 0
            for byte in data:
                checksum ^= byte
            return checksum
        else:
            raise ValueError(f"Unsupported checksum algorithm: {algorithm}")

    def is_valid_ascii_string(self, data: bytes) -> bool:
        """
        Check if bytes represent a valid ASCII string.
        
        Args:
            data: Bytes to check
            
        Returns:
            True if valid ASCII, False otherwise
        """
        try:
            # Check if all bytes are valid ASCII (0-127)
            for byte in data:
                if byte > 127:
                    return False
            return True
        except Exception:
            return False

    def safe_decode_string(
        self, 
        data: bytes, 
        encoding: str = "ascii", 
        errors: str = "replace"
    ) -> str:
        """
        Safely decode bytes to string with error handling.
        
        Args:
            data: Bytes to decode
            encoding: Character encoding
            errors: Error handling strategy
            
        Returns:
            Decoded string
        """
        # Remove null terminators
        clean_data = data.rstrip(b'\x00')
        return clean_data.decode(encoding, errors=errors)

    def round_to_precision(self, value: float, precision: int) -> float:
        """
        Round value to specified number of decimal places.
        
        Args:
            value: Value to round
            precision: Number of decimal places
            
        Returns:
            Rounded value
        """
        return round(value, precision)

    def format_engineering_notation(self, value: float, precision: int = 3) -> str:
        """
        Format value in engineering notation.
        
        Args:
            value: Value to format
            precision: Number of significant digits
            
        Returns:
            Engineering notation string
        """
        return f"{value:.{precision-1}e}"

    def detect_anomalies(
        self, 
        data: List[Union[int, float]], 
        threshold: float = 2.0
    ) -> List[Union[int, float]]:
        """
        Detect anomalous values using standard deviation method.
        
        Args:
            data: List of values to analyze
            threshold: Number of standard deviations for anomaly threshold
            
        Returns:
            List of anomalous values
        """
        if len(data) < 2:
            return []
        
        mean = statistics.mean(data)
        stdev = statistics.stdev(data)
        
        anomalies = []
        for value in data:
            if abs(value - mean) > threshold * stdev:
                anomalies.append(value)
        
        return anomalies

    def calculate_statistics(self, data: List[Union[int, float]]) -> Dict[str, float]:
        """
        Calculate basic statistics for a dataset.
        
        Args:
            data: List of numeric values
            
        Returns:
            Dictionary containing statistical measures
        """
        if not data:
            return {}
        
        return {
            'count': len(data),
            'mean': statistics.mean(data),
            'median': statistics.median(data),
            'min': min(data),
            'max': max(data),
            'std': statistics.stdev(data) if len(data) > 1 else 0.0,
            'variance': statistics.variance(data) if len(data) > 1 else 0.0
        }

    def interpolate_missing_values(
        self, 
        data: List[Optional[Union[int, float]]]
    ) -> List[Union[int, float]]:
        """
        Interpolate missing values using linear interpolation.
        
        Args:
            data: List with possible None values to interpolate
            
        Returns:
            List with interpolated values
        """
        result = data.copy()
        n = len(result)
        
        for i in range(n):
            if result[i] is None:
                # Find previous and next non-None values
                prev_idx = prev_val = next_idx = next_val = None
                
                # Look backward
                for j in range(i - 1, -1, -1):
                    if result[j] is not None:
                        prev_idx, prev_val = j, result[j]
                        break
                
                # Look forward
                for j in range(i + 1, n):
                    if result[j] is not None:
                        next_idx, next_val = j, result[j]
                        break
                
                # Interpolate
                if prev_idx is not None and next_idx is not None:
                    # Linear interpolation
                    ratio = (i - prev_idx) / (next_idx - prev_idx)
                    result[i] = prev_val + ratio * (next_val - prev_val)
                elif prev_idx is not None:
                    # Use previous value
                    result[i] = prev_val
                elif next_idx is not None:
                    # Use next value
                    result[i] = next_val
                else:
                    # No valid values found, use 0
                    result[i] = 0.0
        
        return result

    def apply_moving_average(
        self, 
        data: List[Union[int, float]], 
        window_size: int
    ) -> List[float]:
        """
        Apply moving average filter to data.
        
        Args:
            data: List of numeric values
            window_size: Size of moving average window
            
        Returns:
            List of averaged values
        """
        if window_size < 1:
            raise ValueError("Window size must be positive")
        
        if window_size > len(data):
            window_size = len(data)
        
        result = []
        for i in range(len(data)):
            start_idx = max(0, i - window_size + 1)
            end_idx = i + 1
            window_data = data[start_idx:end_idx]
            avg = sum(window_data) / len(window_data)
            result.append(avg)
        
        return result