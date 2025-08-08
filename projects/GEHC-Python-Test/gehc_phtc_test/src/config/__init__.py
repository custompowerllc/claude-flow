#!/usr/bin/env python3
"""
Configuration management module for GEHC PHTC Test Application.

This module handles all aspects of application configuration including:
- JSON configuration file loading and validation
- Type-safe configuration models with Pydantic
- Command table management and command specifications
- Test profile definitions and management
"""

from .types import (
    # Enums
    DataType, Priority, ConnectionState, ValidationError, TestStatus,
    
    # Configuration models
    SerialConfig, CommandSpec, TestProfile, CommandTable,
    
    # Protocol models
    GEHCMessage,
    
    # Response models
    ParsedResponse, ProcessedResponse,
    
    # Test results models
    CommandResult, TestResults,
    
    # Status models
    ConnectionInfo, ApplicationStatus,
    
    # Constants
    DATA_TYPE_FORMATS, GEHC_PROTOCOL_CONSTANTS
)

# Note: ConfigManager implementation will be created by configuration agent
# from .config_manager import ConfigManager

__all__ = [
    # Enums
    'DataType', 'Priority', 'ConnectionState', 'ValidationError', 'TestStatus',
    
    # Configuration Models
    'SerialConfig', 'CommandSpec', 'TestProfile', 'CommandTable',
    
    # Protocol Models
    'GEHCMessage',
    
    # Response Models
    'ParsedResponse', 'ProcessedResponse',
    
    # Test Results Models
    'CommandResult', 'TestResults',
    
    # Status Models  
    'ConnectionInfo', 'ApplicationStatus',
    
    # Constants
    'DATA_TYPE_FORMATS', 'GEHC_PROTOCOL_CONSTANTS',
    
    # Implementation classes (when created)
    # 'ConfigManager'
]