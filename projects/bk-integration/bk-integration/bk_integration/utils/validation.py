"""Input validation utilities for BK-Integration."""

import logging
from typing import Union, Any

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Validation-related error."""
    pass


def validate_range(value: Union[int, float], min_val: Union[int, float], 
                  max_val: Union[int, float], name: str) -> None:
    """Validate that a numeric value is within specified range.
    
    Args:
        value: Value to validate
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        name: Name of the parameter being validated
        
    Raises:
        ValidationError: If value is outside the valid range
    """
    if not isinstance(value, (int, float)):
        raise ValidationError(f"{name} must be numeric, got {type(value).__name__}")
    
    if value < min_val:
        raise ValidationError(f"{name} {value} is below minimum {min_val}")
    
    if value > max_val:
        raise ValidationError(f"{name} {value} exceeds maximum {max_val}")
    
    logger.debug(f"Validation passed: {name}={value} (range: {min_val}-{max_val})")


def validate_positive(value: Union[int, float], name: str) -> None:
    """Validate that a numeric value is positive.
    
    Args:
        value: Value to validate
        name: Name of the parameter being validated
        
    Raises:
        ValidationError: If value is not positive
    """
    if not isinstance(value, (int, float)):
        raise ValidationError(f"{name} must be numeric, got {type(value).__name__}")
    
    if value <= 0:
        raise ValidationError(f"{name} must be positive, got {value}")
    
    logger.debug(f"Positive validation passed: {name}={value}")


def validate_non_negative(value: Union[int, float], name: str) -> None:
    """Validate that a numeric value is non-negative.
    
    Args:
        value: Value to validate
        name: Name of the parameter being validated
        
    Raises:
        ValidationError: If value is negative
    """
    if not isinstance(value, (int, float)):
        raise ValidationError(f"{name} must be numeric, got {type(value).__name__}")
    
    if value < 0:
        raise ValidationError(f"{name} cannot be negative, got {value}")
    
    logger.debug(f"Non-negative validation passed: {name}={value}")


def validate_string_not_empty(value: str, name: str) -> None:
    """Validate that a string value is not empty.
    
    Args:
        value: String to validate
        name: Name of the parameter being validated
        
    Raises:
        ValidationError: If string is empty or not a string
    """
    if not isinstance(value, str):
        raise ValidationError(f"{name} must be a string, got {type(value).__name__}")
    
    if not value.strip():
        raise ValidationError(f"{name} cannot be empty")
    
    logger.debug(f"String validation passed: {name}='{value}'")


def validate_choice(value: Any, choices: list, name: str) -> None:
    """Validate that a value is one of the allowed choices.
    
    Args:
        value: Value to validate
        choices: List of allowed values
        name: Name of the parameter being validated
        
    Raises:
        ValidationError: If value is not in choices
    """
    if value not in choices:
        raise ValidationError(f"{name} must be one of {choices}, got {value}")
    
    logger.debug(f"Choice validation passed: {name}={value}")


def validate_voltage(voltage: float, device_type: str = "generic") -> None:
    """Validate voltage based on device type.
    
    Args:
        voltage: Voltage value to validate
        device_type: Type of device ('bk8520', 'bk9206b', 'generic')
        
    Raises:
        ValidationError: If voltage is invalid for device type
    """
    device_limits = {
        'bk8520': (0.0, 120.0),    # BK8520 Electronic Load
        'bk9206b': (0.0, 60.0),    # BK9206b Power Supply
        'generic': (0.0, 120.0)    # Conservative default
    }
    
    if device_type not in device_limits:
        device_type = 'generic'
    
    min_v, max_v = device_limits[device_type]
    validate_range(voltage, min_v, max_v, f"{device_type} voltage")


def validate_current(current: float, device_type: str = "generic") -> None:
    """Validate current based on device type.
    
    Args:
        current: Current value to validate
        device_type: Type of device ('bk8520', 'bk9206b', 'generic')
        
    Raises:
        ValidationError: If current is invalid for device type
    """
    device_limits = {
        'bk8520': (0.0, 60.0),     # BK8520 Electronic Load
        'bk9206b': (0.0, 5.0),     # BK9206b Power Supply
        'generic': (0.0, 60.0)     # Conservative default
    }
    
    if device_type not in device_limits:
        device_type = 'generic'
    
    min_i, max_i = device_limits[device_type]
    validate_range(current, min_i, max_i, f"{device_type} current")


def validate_power(power: float, device_type: str = "generic") -> None:
    """Validate power based on device type.
    
    Args:
        power: Power value to validate
        device_type: Type of device ('bk8520', 'bk9206b', 'generic')
        
    Raises:
        ValidationError: If power is invalid for device type
    """
    device_limits = {
        'bk8520': (0.0, 999.0),    # BK8520 Electronic Load
        'bk9206b': (0.0, 300.0),   # BK9206b Power Supply
        'generic': (0.0, 999.0)    # Conservative default
    }
    
    if device_type not in device_limits:
        device_type = 'generic'
    
    min_p, max_p = device_limits[device_type]
    validate_range(power, min_p, max_p, f"{device_type} power")


def validate_test_profile(profile: dict) -> None:
    """Validate battery test profile parameters.
    
    Args:
        profile: Test profile dictionary
        
    Raises:
        ValidationError: If profile parameters are invalid
    """
    required_fields = [
        'charge_voltage', 'charge_current', 'discharge_current',
        'cutoff_voltage', 'rest_time'
    ]
    
    # Check required fields
    for field in required_fields:
        if field not in profile:
            raise ValidationError(f"Missing required field: {field}")
    
    # Validate individual parameters
    validate_voltage(profile['charge_voltage'], 'bk9206b')
    validate_current(profile['charge_current'], 'bk9206b')
    validate_current(profile['discharge_current'], 'bk8520')
    validate_voltage(profile['cutoff_voltage'], 'bk8520')
    validate_range(profile['rest_time'], 0, 3600, "rest time")
    
    # Validate optional parameters if present
    if 'taper_threshold' in profile:
        validate_current(profile['taper_threshold'], 'bk9206b')
    
    if 'taper_duration' in profile:
        validate_range(profile['taper_duration'], 1, 3600, "taper duration")
    
    if 'max_charge_time_hours' in profile:
        validate_range(profile['max_charge_time_hours'], 0.1, 48, "max charge time")
    
    if 'max_discharge_time_hours' in profile:
        validate_range(profile['max_discharge_time_hours'], 0.1, 72, "max discharge time")
    
    # Logical validations
    if profile['cutoff_voltage'] >= profile['charge_voltage']:
        raise ValidationError("Cutoff voltage must be less than charge voltage")
    
    logger.debug(f"Test profile validation passed: {profile.get('name', 'unnamed')}")


def validate_api_response(response: dict, required_fields: list = None) -> None:
    """Validate API response structure.
    
    Args:
        response: API response dictionary
        required_fields: List of required fields to check
        
    Raises:
        ValidationError: If response is invalid
    """
    if not isinstance(response, dict):
        raise ValidationError(f"Response must be dict, got {type(response).__name__}")
    
    # Check for common API response fields
    if 'success' in response and not isinstance(response['success'], bool):
        raise ValidationError("'success' field must be boolean")
    
    if 'message' in response and not isinstance(response['message'], str):
        raise ValidationError("'message' field must be string")
    
    # Check required fields if specified
    if required_fields:
        for field in required_fields:
            if field not in response:
                raise ValidationError(f"Missing required response field: {field}")
    
    logger.debug("API response validation passed")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for file system
    """
    import re
    
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    # Ensure not empty
    if not filename:
        filename = "unnamed"
    
    return filename


def validate_file_path(path: str, must_exist: bool = False) -> None:
    """Validate file path.
    
    Args:
        path: File path to validate
        must_exist: Whether file must already exist
        
    Raises:
        ValidationError: If path is invalid
    """
    from pathlib import Path
    
    validate_string_not_empty(path, "file path")
    
    try:
        path_obj = Path(path)
        
        if must_exist and not path_obj.exists():
            raise ValidationError(f"File does not exist: {path}")
        
        # Check if parent directory exists (for new files)
        if not must_exist and not path_obj.parent.exists():
            raise ValidationError(f"Parent directory does not exist: {path_obj.parent}")
        
    except (OSError, ValueError) as e:
        raise ValidationError(f"Invalid file path: {e}")
    
    logger.debug(f"File path validation passed: {path}")