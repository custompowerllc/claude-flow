#!/usr/bin/env python3
"""
Core application modules for GEHC PHTC Test Application.

This package contains all the core implementation modules organized by responsibility:
- communication: RS422 serial communication and protocol handling
- parsing: Message parsing and data processing  
- config: Configuration management and validation
- display: Console output and user interface
- orchestration: Test coordination and workflow management
"""

# Import core interfaces and types for easy access
from .interfaces import *
from .config.types import *
from .constants import *
from .exceptions import *

__all__ = [
    # Re-export from interfaces
    'ISerialHandler', 'IProtocolHandler', 'ICRC8Calculator',
    'IMessageParser', 'IDataProcessor', 'IResponseValidator',
    'IConfigManager', 'IConsoleDisplay', 'IProgressDisplay',
    'ITestOrchestrator', 'IMainController',
    
    # Re-export from types
    'SerialConfig', 'CommandSpec', 'TestProfile', 'CommandTable',
    'GEHCMessage', 'ParsedResponse', 'ProcessedResponse',
    'CommandResult', 'TestResults', 'ApplicationStatus',
    'DataType', 'Priority', 'ConnectionState', 'ValidationError', 'TestStatus',
    
    # Re-export from constants
    'GEHCProtocol', 'ErrorCodes', 'DATA_TYPE_SPECS', 'COMMAND_CATEGORIES',
    'PERFORMANCE_TARGETS', 'ERROR_MESSAGES',
    
    # Re-export from exceptions
    'GEHCError', 'CommunicationError', 'ProtocolError', 'ConfigurationError',
    'DataProcessingError', 'DeviceError', 'TestExecutionError'
]