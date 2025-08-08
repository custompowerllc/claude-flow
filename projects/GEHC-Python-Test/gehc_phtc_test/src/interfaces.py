#!/usr/bin/env python3
"""
Interface definitions for GEHC PHTC Test Application components.

This module defines abstract base classes and protocols that specify
the contracts for all major components in the system, ensuring
proper separation of concerns and testability.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, AsyncContextManager
from contextlib import asynccontextmanager

from .config.types import (
    SerialConfig, CommandSpec, TestProfile, CommandTable, TestResults,
    GEHCMessage, ParsedResponse, ProcessedResponse, CommandResult,
    ConnectionInfo, ApplicationStatus, ConnectionState, ValidationError
)


# Communication Layer Interfaces

class ISerialHandler(ABC):
    """Interface for RS422 serial communication."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to RS422 device."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close RS422 connection safely."""
        pass
    
    @abstractmethod
    async def send_data(self, data: bytes) -> bool:
        """Send raw data to RS422 port with error handling."""
        pass
    
    @abstractmethod
    async def receive_data(self, expected_length: Optional[int] = None) -> Optional[bytes]:
        """Receive data from RS422 port with timeout handling."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check current connection status."""
        pass
    
    @abstractmethod
    async def flush_buffers(self) -> None:
        """Clear input/output buffers."""
        pass
    
    @property
    @abstractmethod
    def connection_info(self) -> ConnectionInfo:
        """Get current connection information."""
        pass


class IProtocolHandler(ABC):
    """Interface for GEHC RS422 protocol implementation."""
    
    @abstractmethod
    def build_command_message(self, command_code: int, data: bytes = b'') -> bytes:
        """Build complete GEHC protocol message."""
        pass
    
    @abstractmethod
    def parse_response_message(self, response: bytes) -> Tuple[bool, Optional[GEHCMessage]]:
        """Parse and validate GEHC response message."""
        pass
    
    @abstractmethod
    def validate_message_structure(self, message: bytes) -> bool:
        """Validate message format and structure."""
        pass
    
    @abstractmethod
    def extract_payload(self, message: GEHCMessage) -> bytes:
        """Extract data payload from validated message."""
        pass
    
    @abstractmethod
    def calculate_message_crc(self, message_data: bytes) -> int:
        """Calculate CRC8 for message data."""
        pass
    
    @abstractmethod
    def format_hex_dump(self, data: bytes) -> str:
        """Format binary data as hex dump for debugging."""
        pass


class ICRC8Calculator(ABC):
    """Interface for CRC8 checksum calculations."""
    
    @abstractmethod
    def calculate(self, data: bytes) -> int:
        """Calculate CRC8 checksum for data."""
        pass
    
    @abstractmethod
    def verify(self, data: bytes, expected_crc: int) -> bool:
        """Verify data integrity against expected CRC."""
        pass


# Data Processing Layer Interfaces

class IMessageParser(ABC):
    """Interface for GEHC protocol message parsing."""
    
    @abstractmethod
    async def parse_response(
        self,
        command_code: int,
        response_data: bytes,
        command_info: CommandSpec
    ) -> ParsedResponse:
        """Parse complete response with validation and processing."""
        pass
    
    @abstractmethod
    def extract_raw_value(self, data: bytes, data_type: str) -> Any:
        """Extract raw value based on data type specification."""
        pass
    
    @abstractmethod
    async def process_command_response(
        self,
        command_code: int,
        response: GEHCMessage,
        command_spec: CommandSpec
    ) -> ProcessedResponse:
        """Process complete command response with all transformations."""
        pass


class IDataProcessor(ABC):
    """Interface for data type conversion and scaling."""
    
    @abstractmethod
    def convert_data_type(self, data: bytes, data_type: str) -> Any:
        """Convert raw bytes to specified data type."""
        pass
    
    @abstractmethod
    def apply_scaling(self, value: float, granularity: float) -> float:
        """Apply granularity scaling to raw value."""
        pass
    
    @abstractmethod
    def format_with_units(self, value: float, unit: str, precision: int = 2) -> str:
        """Format scaled value with appropriate units."""
        pass
    
    @abstractmethod
    def validate_range(self, value: float, range_spec: str) -> bool:
        """Validate value is within specified range."""
        pass
    
    @abstractmethod
    def get_type_info(self, data_type: str) -> Dict[str, Any]:
        """Get formatting information for data type."""
        pass


class IResponseValidator(ABC):
    """Interface for response validation and integrity checking."""
    
    @abstractmethod
    def validate_response(
        self,
        response: GEHCMessage,
        expected_command: int
    ) -> Tuple[bool, List[ValidationError]]:
        """Comprehensive response validation."""
        pass
    
    @abstractmethod
    def validate_crc(self, message: GEHCMessage) -> bool:
        """Validate message CRC8 checksum."""
        pass
    
    @abstractmethod
    def validate_length(self, message: GEHCMessage, expected_length: int) -> bool:
        """Validate response data length."""
        pass
    
    @abstractmethod
    def validate_command_match(self, response_cmd: int, expected_cmd: int) -> bool:
        """Validate response command matches request."""
        pass
    
    @abstractmethod
    def validate_data_integrity(self, data: bytes, data_type: str) -> bool:
        """Validate data integrity and format."""
        pass


# Configuration Layer Interfaces

class IConfigManager(ABC):
    """Interface for configuration management."""
    
    @abstractmethod
    async def load_all_configs(self) -> bool:
        """Load all configuration files."""
        pass
    
    @abstractmethod
    def load_serial_config(self) -> SerialConfig:
        """Load serial port configuration."""
        pass
    
    @abstractmethod
    def load_command_table(self) -> CommandTable:
        """Load command specifications."""
        pass
    
    @abstractmethod
    def get_enabled_commands(self, profile_name: Optional[str] = None) -> List[CommandSpec]:
        """Get list of enabled commands for profile."""
        pass
    
    @abstractmethod
    def is_command_implemented(self, command_code: str) -> bool:
        """Check if command is implemented."""
        pass
    
    @abstractmethod
    def get_command_spec(self, command_code: str) -> Optional[CommandSpec]:
        """Get command specification."""
        pass
    
    @abstractmethod
    def get_test_profile(self, profile_name: str) -> Optional[TestProfile]:
        """Get test profile configuration."""
        pass
    
    @abstractmethod
    def validate_configuration(self) -> List[str]:
        """Validate all configuration files."""
        pass


# Display Layer Interfaces  

class IConsoleDisplay(ABC):
    """Interface for Rich library console display."""
    
    @abstractmethod
    def show_startup_banner(self, config: SerialConfig) -> None:
        """Display application startup banner."""
        pass
    
    @abstractmethod
    def display_command_sending(self, command_spec: CommandSpec, message: bytes) -> None:
        """Show command transmission status."""
        pass
    
    @abstractmethod
    def display_response_received(self, parsed_response: ParsedResponse) -> None:
        """Display parsed response data."""
        pass
    
    @abstractmethod
    def display_error(self, error_type: str, message: str, details: Optional[str] = None) -> None:
        """Display error information with formatting."""
        pass
    
    @abstractmethod
    def display_final_summary(self, test_results: TestResults) -> None:
        """Show comprehensive test summary."""
        pass
    
    @abstractmethod
    def create_command_status_table(self, commands: List[CommandSpec]) -> Any:
        """Create formatted command status table."""
        pass
    
    @abstractmethod
    def create_results_table(self, results: List[ParsedResponse]) -> Any:
        """Create formatted results table."""
        pass


class IProgressDisplay(ABC):
    """Interface for progress tracking and status display."""
    
    @abstractmethod
    def start_test_progress(self, total_commands: int) -> None:
        """Initialize test execution progress tracking."""
        pass
    
    @abstractmethod
    def update_command_progress(self, completed: int, current_command: str) -> None:
        """Update progress for current command."""
        pass
    
    @abstractmethod
    def complete_progress(self) -> None:
        """Complete and cleanup progress display."""
        pass
    
    @abstractmethod
    def show_real_time_status(self, status: str) -> None:
        """Display real-time status updates."""
        pass


# Orchestration Layer Interfaces

class ITestOrchestrator(ABC):
    """Interface for test execution coordination."""
    
    @abstractmethod
    async def execute_test_profile(self, profile_name: str) -> TestResults:
        """Execute complete test profile."""
        pass
    
    @abstractmethod
    async def execute_single_command(
        self,
        command_spec: CommandSpec
    ) -> Tuple[bool, Optional[ParsedResponse]]:
        """Execute single command with full workflow."""
        pass
    
    @abstractmethod
    async def send_command_with_retry(
        self,
        command_spec: CommandSpec,
        retry_count: int = 3
    ) -> Tuple[bool, Optional[bytes]]:
        """Send command with retry logic."""
        pass
    
    @abstractmethod
    def calculate_performance_metrics(
        self,
        results: List[CommandResult],
        start_time: Any,
        end_time: Any
    ) -> Dict[str, float]:
        """Calculate test performance metrics."""
        pass
    
    @abstractmethod
    async def cleanup_test_session(self) -> None:
        """Clean up resources after test completion."""
        pass


class IMainController(ABC):
    """Interface for main application controller."""
    
    @abstractmethod
    async def initialize_components(self) -> bool:
        """Initialize and validate all components."""
        pass
    
    @abstractmethod
    async def run(self, profile: str = "full_implemented") -> TestResults:
        """Execute the complete test workflow."""
        pass
    
    @abstractmethod
    async def cleanup_resources(self) -> None:
        """Clean shutdown of all resources."""
        pass
    
    @abstractmethod
    def get_application_status(self) -> ApplicationStatus:
        """Get current application status."""
        pass


# Context Manager Interfaces

class IAsyncResourceManager(ABC):
    """Interface for async resource management."""
    
    @abstractmethod
    async def __aenter__(self):
        """Async context manager entry."""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass


# Factory Interfaces

class IComponentFactory(ABC):
    """Interface for component creation and dependency injection."""
    
    @abstractmethod
    def create_serial_handler(self, config: SerialConfig) -> ISerialHandler:
        """Create serial handler with configuration."""
        pass
    
    @abstractmethod
    def create_protocol_handler(self, crc_calculator: ICRC8Calculator) -> IProtocolHandler:
        """Create protocol handler with dependencies."""
        pass
    
    @abstractmethod
    def create_message_parser(
        self,
        data_processor: IDataProcessor,
        validator: IResponseValidator
    ) -> IMessageParser:
        """Create message parser with dependencies."""
        pass
    
    @abstractmethod
    def create_config_manager(self, config_dir: str) -> IConfigManager:
        """Create configuration manager."""
        pass
    
    @abstractmethod
    def create_console_display(self) -> IConsoleDisplay:
        """Create console display handler."""
        pass
    
    @abstractmethod
    def create_test_orchestrator(
        self,
        config_manager: IConfigManager,
        serial_handler: ISerialHandler,
        protocol_handler: IProtocolHandler,
        message_parser: IMessageParser,
        console_display: IConsoleDisplay,
        progress_display: IProgressDisplay
    ) -> ITestOrchestrator:
        """Create test orchestrator with all dependencies."""
        pass


# Service Provider Interface

class IServiceProvider(ABC):
    """Interface for dependency injection container."""
    
    @abstractmethod
    def register_singleton(self, interface: type, implementation: type) -> None:
        """Register singleton service implementation."""
        pass
    
    @abstractmethod
    def register_transient(self, interface: type, implementation: type) -> None:
        """Register transient service implementation."""
        pass
    
    @abstractmethod
    def register_instance(self, interface: type, instance: Any) -> None:
        """Register service instance."""
        pass
    
    @abstractmethod
    def resolve(self, interface: type) -> Any:
        """Resolve service implementation."""
        pass
    
    @abstractmethod
    def configure_services(self) -> None:
        """Configure all service registrations."""
        pass


# Error Handling Interfaces

class IGEHCErrorHandler(ABC):
    """Interface for application-wide error handling."""
    
    @abstractmethod
    async def handle_communication_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Handle communication-related errors."""
        pass
    
    @abstractmethod
    async def handle_protocol_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Handle protocol-related errors."""
        pass
    
    @abstractmethod
    async def handle_configuration_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Handle configuration-related errors."""
        pass
    
    @abstractmethod
    async def handle_unexpected_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Handle unexpected errors."""
        pass


# Logging Interface

class IGEHCLogger(ABC):
    """Interface for structured application logging."""
    
    @abstractmethod
    def log_command_sent(self, command_spec: CommandSpec, message: bytes) -> None:
        """Log command transmission."""
        pass
    
    @abstractmethod
    def log_response_received(self, response: ProcessedResponse) -> None:
        """Log response reception and processing."""
        pass
    
    @abstractmethod
    def log_error(self, error_type: str, message: str, context: Dict[str, Any]) -> None:
        """Log error with context."""
        pass
    
    @abstractmethod
    def log_performance_metric(self, metric_name: str, value: float, unit: str) -> None:
        """Log performance measurement."""
        pass
    
    @abstractmethod
    def log_test_summary(self, results: TestResults) -> None:
        """Log test execution summary."""
        pass


# Testing Support Interfaces

class IMockSerialDevice(ABC):
    """Interface for mock serial device for testing."""
    
    @abstractmethod
    async def simulate_command_response(self, command: bytes) -> bytes:
        """Simulate device response to command."""
        pass
    
    @abstractmethod
    def set_response_delay(self, delay_ms: int) -> None:
        """Set simulated response delay."""
        pass
    
    @abstractmethod
    def inject_error(self, error_type: str, probability: float) -> None:
        """Inject simulated errors for testing."""
        pass
    
    @abstractmethod
    def get_interaction_log(self) -> List[Dict[str, Any]]:
        """Get log of all interactions."""
        pass


# Type aliases for commonly used combinations

ComponentRegistry = Dict[type, Any]
ServiceConfiguration = Dict[str, Any]
ErrorContext = Dict[str, Any]
PerformanceMetrics = Dict[str, float]
InteractionLog = List[Dict[str, Any]]

# Export all interfaces
__all__ = [
    # Communication Layer
    'ISerialHandler', 'IProtocolHandler', 'ICRC8Calculator',
    
    # Data Processing Layer
    'IMessageParser', 'IDataProcessor', 'IResponseValidator',
    
    # Configuration Layer
    'IConfigManager',
    
    # Display Layer
    'IConsoleDisplay', 'IProgressDisplay',
    
    # Orchestration Layer
    'ITestOrchestrator', 'IMainController',
    
    # Context Management
    'IAsyncResourceManager',
    
    # Factory and DI
    'IComponentFactory', 'IServiceProvider',
    
    # Error Handling and Logging
    'IGEHCErrorHandler', 'IGEHCLogger',
    
    # Testing Support
    'IMockSerialDevice',
    
    # Type Aliases
    'ComponentRegistry', 'ServiceConfiguration', 'ErrorContext',
    'PerformanceMetrics', 'InteractionLog'
]