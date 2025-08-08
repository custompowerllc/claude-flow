"""Message parser for GEHC PHTC RS422 protocol responses."""

import struct
from enum import Enum
from typing import Union, Any
from dataclasses import dataclass


class DataType(Enum):
    """Enumeration of supported data types."""
    UNSIGNED_INT_8 = "UNSIGNED_INT_8"
    UNSIGNED_INT_16 = "UNSIGNED_INT_16"
    UNSIGNED_INT_32 = "UNSIGNED_INT_32"
    SIGNED_INT_8 = "SIGNED_INT_8"
    SIGNED_INT_16 = "SIGNED_INT_16"
    SIGNED_INT_32 = "SIGNED_INT_32"
    BOOLEAN = "BOOLEAN"
    STRING = "STRING"
    BLOCK_DATA = "BLOCK_DATA"


@dataclass
class ScalingInfo:
    """Configuration for data scaling and units."""
    granularity: float
    unit: str
    offset: float = 0.0


@dataclass
class ParseResult:
    """Result of parsing response data."""
    raw_value: Any
    scaled_value: Any
    formatted_value: str
    unit: str
    data_type: DataType


class MessageParser:
    """Parser for RS422 protocol response messages."""

    def __init__(self):
        """Initialize the message parser."""
        self._data_type_parsers = {
            DataType.UNSIGNED_INT_8: self._parse_uint8,
            DataType.UNSIGNED_INT_16: self._parse_uint16,
            DataType.UNSIGNED_INT_32: self._parse_uint32,
            DataType.SIGNED_INT_8: self._parse_int8,
            DataType.SIGNED_INT_16: self._parse_int16,
            DataType.SIGNED_INT_32: self._parse_int32,
            DataType.BOOLEAN: self._parse_boolean,
            DataType.STRING: self._parse_string,
            DataType.BLOCK_DATA: self._parse_block_data,
        }

    def parse_response(
        self, 
        response_data: bytes, 
        data_type: Union[DataType, str], 
        scaling: ScalingInfo
    ) -> ParseResult:
        """
        Parse response data according to specified data type and scaling.
        
        Args:
            response_data: Raw bytes from device response
            data_type: Type of data to parse
            scaling: Scaling configuration for the data
            
        Returns:
            ParseResult containing raw, scaled, and formatted values
            
        Raises:
            ValueError: If data type is unsupported or data is insufficient
        """
        # Convert string data type to enum if needed
        if isinstance(data_type, str):
            try:
                data_type = DataType(data_type)
            except ValueError:
                raise ValueError(f"Unsupported data type: {data_type}")
        
        # Get the appropriate parser
        parser = self._data_type_parsers.get(data_type)
        if not parser:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        # Parse the raw value
        raw_value = parser(response_data)
        
        # Apply scaling
        scaled_value = self._apply_scaling(raw_value, scaling, data_type)
        
        # Format the value
        formatted_value = self._format_value(scaled_value, scaling.unit, data_type)
        
        return ParseResult(
            raw_value=raw_value,
            scaled_value=scaled_value,
            formatted_value=formatted_value,
            unit=scaling.unit,
            data_type=data_type
        )

    def _parse_uint8(self, data: bytes) -> int:
        """Parse unsigned 8-bit integer."""
        if len(data) < 1:
            raise ValueError("Insufficient data for UNSIGNED_INT_8")
        return struct.unpack("<B", data[0:1])[0]

    def _parse_uint16(self, data: bytes) -> int:
        """Parse unsigned 16-bit integer (little endian)."""
        if len(data) < 2:
            raise ValueError("Insufficient data for UNSIGNED_INT_16")
        return struct.unpack("<H", data[0:2])[0]

    def _parse_uint32(self, data: bytes) -> int:
        """Parse unsigned 32-bit integer (little endian)."""
        if len(data) < 4:
            raise ValueError("Insufficient data for UNSIGNED_INT_32")
        return struct.unpack("<I", data[0:4])[0]

    def _parse_int8(self, data: bytes) -> int:
        """Parse signed 8-bit integer."""
        if len(data) < 1:
            raise ValueError("Insufficient data for SIGNED_INT_8")
        return struct.unpack("<b", data[0:1])[0]

    def _parse_int16(self, data: bytes) -> int:
        """Parse signed 16-bit integer (little endian)."""
        if len(data) < 2:
            raise ValueError("Insufficient data for SIGNED_INT_16")
        return struct.unpack("<h", data[0:2])[0]

    def _parse_int32(self, data: bytes) -> int:
        """Parse signed 32-bit integer (little endian)."""
        if len(data) < 4:
            raise ValueError("Insufficient data for SIGNED_INT_32")
        return struct.unpack("<i", data[0:4])[0]

    def _parse_boolean(self, data: bytes) -> int:
        """Parse boolean value (returns int, converted to bool in scaling)."""
        if len(data) < 1:
            raise ValueError("Insufficient data for BOOLEAN")
        return struct.unpack("<B", data[0:1])[0]

    def _parse_string(self, data: bytes) -> bytes:
        """Parse string data (returns bytes, converted to string in scaling)."""
        return data

    def _parse_block_data(self, data: bytes) -> bytes:
        """Parse block data (raw bytes)."""
        return data

    def _apply_scaling(
        self, 
        raw_value: Any, 
        scaling: ScalingInfo, 
        data_type: DataType
    ) -> Any:
        """
        Apply scaling transformation to raw value.
        
        Args:
            raw_value: Raw parsed value
            scaling: Scaling configuration
            data_type: Type of data being scaled
            
        Returns:
            Scaled value with appropriate type
        """
        if data_type == DataType.BOOLEAN:
            return bool(raw_value)
        elif data_type == DataType.STRING:
            # Convert bytes to string, removing null terminator
            if isinstance(raw_value, bytes):
                return raw_value.decode('ascii', errors='ignore').rstrip('\x00')
            return str(raw_value)
        elif data_type == DataType.BLOCK_DATA:
            # Convert to list of integers for easier handling
            if isinstance(raw_value, bytes):
                return list(raw_value)
            return raw_value
        else:
            # Numeric types: apply granularity and offset
            return (raw_value * scaling.granularity) + scaling.offset

    def _format_value(self, scaled_value: Any, unit: str, data_type: DataType) -> str:
        """
        Format scaled value as display string.
        
        Args:
            scaled_value: Value after scaling applied
            unit: Unit string
            data_type: Type of data
            
        Returns:
            Formatted string for display
        """
        if data_type == DataType.BOOLEAN:
            return str(scaled_value)
        elif data_type == DataType.STRING:
            return str(scaled_value)
        elif data_type == DataType.BLOCK_DATA:
            if isinstance(scaled_value, list):
                # Format as hex bytes
                return ' '.join(f'{b:02X}' for b in scaled_value)
            return str(scaled_value)
        else:
            # Numeric types - format with appropriate precision
            if isinstance(scaled_value, float):
                # Round to reasonable precision to avoid floating point artifacts
                formatted_num = f"{scaled_value:.1f}"
                # Remove trailing zeros and decimal point if not needed
                formatted_num = formatted_num.rstrip('0').rstrip('.')
            else:
                formatted_num = str(scaled_value)
            
            if unit:
                if unit == "%":
                    return f"{formatted_num}{unit}"
                else:
                    return f"{formatted_num} {unit}"
            else:
                return formatted_num

    def validate_range(
        self, 
        value: float, 
        min_val: float = None, 
        max_val: float = None
    ) -> bool:
        """
        Validate if value is within specified range.
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            True if value is within range, False otherwise
        """
        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False
        return True