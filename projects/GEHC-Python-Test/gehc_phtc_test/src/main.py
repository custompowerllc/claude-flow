#!/usr/bin/env python3
"""
Main application entry point for GEHC PHTC RS422 Test Application.

This module implements the main controller that coordinates all components
and provides the primary application lifecycle management.
"""

import asyncio
import sys
import signal
import logging
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import traceback

from .interfaces import (
    IMainController, IConfigManager, ISerialHandler, IProtocolHandler,
    IMessageParser, IConsoleDisplay, IProgressDisplay, ITestOrchestrator,
    IComponentFactory, IGEHCErrorHandler, IGEHCLogger
)
from .config.types import (
    SerialConfig, TestResults, ApplicationStatus, ConnectionState
)
from .constants import GEHCProtocol, ErrorCodes, PERFORMANCE_TARGETS
from .exceptions import (
    GEHCError, CommunicationError, ProtocolError, ConfigurationError
)

# Import implementations (these would be created by other agents)
# from .communication.serial_handler import SerialHandler
# from .communication.protocol_handler import ProtocolHandler
# from .parsing.message_parser import MessageParser
# from .config.config_manager import ConfigManager
# from .display.console_display import ConsoleDisplay
# from .orchestration.test_orchestrator import TestOrchestrator


class MainController(IMainController):
    """
    Main application controller coordinating all system components.
    
    Responsibilities:
    - Component initialization and dependency injection
    - Application lifecycle management
    - Error handling and recovery
    - Resource cleanup and shutdown
    - Command-line interface handling
    """
    
    def __init__(self, config_dir: str = "config"):
        """Initialize main controller with configuration directory."""
        self.config_dir = Path(config_dir)
        self.started_time = datetime.now()
        self.shutdown_requested = False
        
        # Core components (initialized by initialize_components)
        self.config_manager: Optional[IConfigManager] = None
        self.serial_handler: Optional[ISerialHandler] = None
        self.protocol_handler: Optional[IProtocolHandler] = None
        self.message_parser: Optional[IMessageParser] = None
        self.console_display: Optional[IConsoleDisplay] = None
        self.progress_display: Optional[IProgressDisplay] = None
        self.test_orchestrator: Optional[ITestOrchestrator] = None
        self.error_handler: Optional[IGEHCErrorHandler] = None
        self.logger: Optional[IGEHCLogger] = None
        
        # Application state
        self._initialized = False
        self._running = False
        self._current_test: Optional[str] = None
        self._total_commands_processed = 0
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        # Setup basic logging
        self._setup_logging()
    
    async def initialize_components(self) -> bool:
        """
        Initialize and validate all application components.
        
        Returns:
            bool: True if all components initialized successfully
            
        Raises:
            ConfigurationError: If configuration is invalid
            ComponentError: If component initialization fails
        """
        try:
            self.logger.info("Initializing GEHC PHTC Test Application components...")
            
            # Initialize configuration manager first
            self.config_manager = self._create_config_manager()
            await self.config_manager.load_all_configs()
            
            # Validate configuration
            config_errors = self.config_manager.validate_configuration()
            if config_errors:
                raise ConfigurationError(f"Configuration validation failed: {config_errors}")
            
            # Get serial configuration
            serial_config = self.config_manager.load_serial_config()
            
            # Initialize component factory and create components
            factory = self._create_component_factory()
            
            # Create communication layer
            crc_calculator = factory.create_crc8_calculator()
            self.protocol_handler = factory.create_protocol_handler(crc_calculator)
            self.serial_handler = factory.create_serial_handler(serial_config)
            
            # Create data processing layer
            data_processor = factory.create_data_processor()
            response_validator = factory.create_response_validator(crc_calculator)
            self.message_parser = factory.create_message_parser(data_processor, response_validator)
            
            # Create display layer
            self.console_display = factory.create_console_display()
            self.progress_display = factory.create_progress_display(self.console_display.console)
            
            # Create orchestration layer
            self.test_orchestrator = factory.create_test_orchestrator(
                self.config_manager,
                self.serial_handler,
                self.protocol_handler,
                self.message_parser,
                self.console_display,
                self.progress_display
            )
            
            # Create support services
            self.error_handler = factory.create_error_handler()
            self.logger = factory.create_logger()
            
            self._initialized = True
            self.logger.info("All components initialized successfully")
            
            # Display startup banner
            self.console_display.show_startup_banner(serial_config)
            
            return True
            
        except Exception as e:
            error_msg = f"Component initialization failed: {str(e)}"
            logging.error(error_msg)
            if self.error_handler:
                await self.error_handler.handle_unexpected_error(e, {"phase": "initialization"})
            raise ConfigurationError(error_msg) from e
    
    async def run(self, profile: str = "full_implemented") -> TestResults:
        """
        Execute the complete test workflow.
        
        Args:
            profile: Test profile name to execute
            
        Returns:
            TestResults: Complete test execution results
            
        Raises:
            GEHCError: If test execution fails
        """
        if not self._initialized:
            raise GEHCError("Components not initialized. Call initialize_components() first.")
        
        try:
            self._running = True
            self._current_test = profile
            
            self.logger.info(f"Starting test execution with profile: {profile}")
            
            # Verify test profile exists
            test_profile = self.config_manager.get_test_profile(profile)
            if not test_profile:
                raise ConfigurationError(f"Test profile '{profile}' not found")
            
            # Connect to device
            self.console_display.show_real_time_status("Connecting to device...")
            connected = await self.serial_handler.connect()
            if not connected:
                raise CommunicationError("Failed to establish connection to PHTC device")
            
            self.console_display.show_real_time_status("Connection established")
            
            # Execute test profile
            results = await self.test_orchestrator.execute_test_profile(profile)
            
            # Update application statistics
            self._total_commands_processed += results.total_commands
            
            # Display final results
            self.console_display.display_final_summary(results)
            
            # Log performance metrics
            self._log_performance_metrics(results)
            
            self.logger.info(f"Test execution completed: {results.successful_commands}/{results.total_commands} successful")
            
            return results
            
        except Exception as e:
            error_msg = f"Test execution failed: {str(e)}"
            self.logger.error(error_msg)
            self.console_display.display_error("Test Execution Error", error_msg, traceback.format_exc())
            
            if self.error_handler:
                await self.error_handler.handle_unexpected_error(e, {"phase": "test_execution", "profile": profile})
            
            raise GEHCError(error_msg) from e
            
        finally:
            self._running = False
            self._current_test = None
            
            # Cleanup test session
            if self.test_orchestrator:
                await self.test_orchestrator.cleanup_test_session()
    
    async def cleanup_resources(self) -> None:
        """Clean shutdown of all resources and components."""
        try:
            self.logger.info("Starting application cleanup...")
            
            # Stop any running tests
            self._running = False
            self.shutdown_requested = True
            
            # Cleanup test orchestrator
            if self.test_orchestrator:
                await self.test_orchestrator.cleanup_test_session()
            
            # Disconnect serial connection
            if self.serial_handler:
                await self.serial_handler.disconnect()
            
            # Complete progress displays
            if self.progress_display:
                self.progress_display.complete_progress()
            
            # Final status message
            if self.console_display:
                self.console_display.show_real_time_status("Application shutdown complete")
            
            self.logger.info("Application cleanup completed successfully")
            
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")
            # Don't raise exceptions during cleanup
    
    def get_application_status(self) -> ApplicationStatus:
        """Get current application status and health information."""
        connection_info = None
        if self.serial_handler:
            connection_info = self.serial_handler.connection_info
        
        return ApplicationStatus(
            version="1.0.0",  # Should be loaded from package metadata
            started_time=self.started_time,
            connection_info=connection_info,
            current_test=self._current_test,
            total_commands_processed=self._total_commands_processed,
            memory_usage_mb=self._get_memory_usage(),
            cpu_usage_percent=self._get_cpu_usage()
        )
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            """Handle shutdown signals."""
            print(f"\nReceived signal {signum}, initiating graceful shutdown...")
            self.shutdown_requested = True
            
            # If we have an event loop, schedule cleanup
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.cleanup_resources())
            except RuntimeError:
                # No event loop running, direct cleanup
                pass
        
        signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
        
        if sys.platform != "win32":
            signal.signal(signal.SIGHUP, signal_handler)   # Hangup signal
    
    def _setup_logging(self) -> None:
        """Setup basic logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create application logger
        self.app_logger = logging.getLogger('gehc.phtc.main')
        self.app_logger.info("Basic logging initialized")
    
    def _create_config_manager(self) -> IConfigManager:
        """Create and configure the configuration manager."""
        # This would import the actual implementation
        # from .config.config_manager import ConfigManager
        # return ConfigManager(self.config_dir)
        raise NotImplementedError("ConfigManager implementation needed")
    
    def _create_component_factory(self) -> IComponentFactory:
        """Create component factory for dependency injection."""
        # This would import the actual implementation
        # from .factory import ComponentFactory
        # return ComponentFactory()
        raise NotImplementedError("ComponentFactory implementation needed")
    
    def _log_performance_metrics(self, results: TestResults) -> None:
        """Log performance metrics for monitoring."""
        metrics = {
            "test_duration_seconds": results.duration_seconds,
            "commands_per_second": results.total_commands / max(results.duration_seconds, 1),
            "success_rate_percent": results.success_rate,
            "average_command_time_ms": results.average_command_time_ms
        }
        
        for metric_name, value in metrics.items():
            self.logger.log_performance_metric(metric_name, value, "")
        
        # Check against performance targets
        if metrics["average_command_time_ms"] > PERFORMANCE_TARGETS["command_processing_latency_ms"]:
            self.app_logger.warning(f"Command processing latency exceeded target: {metrics['average_command_time_ms']:.1f}ms")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0


# Command Line Interface

def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="GEHC PHTC RS422 Communication Protocol Test Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m gehc_phtc_test                          # Run with default profile
  python -m gehc_phtc_test --profile quick_test     # Run quick test
  python -m gehc_phtc_test --config /path/to/config # Use custom config directory
  python -m gehc_phtc_test --list-profiles           # List available profiles
  python -m gehc_phtc_test --validate-config        # Validate configuration only
        """
    )
    
    parser.add_argument(
        '--profile', '-p',
        default='full_implemented',
        help='Test profile to execute (default: full_implemented)'
    )
    
    parser.add_argument(
        '--config-dir', '-c',
        default='config',
        help='Configuration directory path (default: config)'
    )
    
    parser.add_argument(
        '--list-profiles',
        action='store_true',
        help='List available test profiles and exit'
    )
    
    parser.add_argument(
        '--validate-config',
        action='store_true',
        help='Validate configuration files and exit'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging output'
    )
    
    parser.add_argument(
        '--log-file',
        help='Log file path (default: logs/gehc_phtc_test.log)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='GEHC PHTC Test Application v1.0.0'
    )
    
    return parser


async def main() -> int:
    """
    Main application entry point.
    
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create main controller
    controller = MainController(args.config_dir)
    
    try:
        # Initialize components
        await controller.initialize_components()
        
        # Handle special commands
        if args.list_profiles:
            profiles = controller.config_manager.load_test_profiles()
            print("\nAvailable Test Profiles:")
            print("=" * 50)
            for name, profile in profiles.items():
                print(f"{name:20s}: {profile.description}")
            return 0
        
        if args.validate_config:
            errors = controller.config_manager.validate_configuration()
            if errors:
                print("Configuration validation failed:")
                for error in errors:
                    print(f"  - {error}")
                return 1
            else:
                print("Configuration validation passed")
                return 0
        
        # Execute test profile
        results = await controller.run(args.profile)
        
        # Determine exit code based on results
        if results.failed_commands > 0:
            return 2  # Some commands failed
        elif results.successful_commands == 0:
            return 3  # No commands succeeded
        else:
            return 0  # Success
        
    except ConfigurationError as e:
        print(f"Configuration Error: {e}")
        return 4
    except CommunicationError as e:
        print(f"Communication Error: {e}")
        return 5
    except ProtocolError as e:
        print(f"Protocol Error: {e}")
        return 6
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        print(f"Unexpected Error: {e}")
        logging.exception("Unhandled exception in main")
        return 1
    
    finally:
        # Ensure cleanup always runs
        await controller.cleanup_resources()


# Entry point for python -m gehc_phtc_test
if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.exception("Fatal error in main entry point")
        sys.exit(1)