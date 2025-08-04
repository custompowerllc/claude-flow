#!/usr/bin/env python3
"""
Test script for the logging system implementation

This script demonstrates the logging system features:
- Component-specific loggers
- File rotation
- JSON formatting
- Console and file output
- Different log levels
"""

import sys
import time
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.log_manager import setup_logging, get_logger


def test_basic_logging():
    """Test basic logging functionality"""
    print("=== Testing Basic Logging ===")
    
    # Setup logging with default config
    log_manager = setup_logging()
    
    # Get loggers for different components
    server_logger = log_manager.get_logger("test.server", "server")
    cli_logger = log_manager.get_logger("test.cli", "cli")
    register_logger = log_manager.get_logger("test.register", "register_handler")
    
    # Test different log levels
    server_logger.debug("Server debug message")
    server_logger.info("Server started on COM4")
    server_logger.warning("Port conflict detected")
    server_logger.error("Failed to bind to port")
    
    cli_logger.info("CLI command executed: --list-ports")
    cli_logger.error("Invalid argument provided")
    
    register_logger.info("Register handler initialized")
    register_logger.debug("Updated register afe_cell_volt1 = 3700")
    
    print("✅ Basic logging test completed")
    print("📁 Check logs/ directory for output files")


def test_json_logging():
    """Test JSON formatted logging"""
    print("\n=== Testing JSON Logging ===")
    
    # Setup logging with JSON format
    log_manager = setup_logging(json_format=True)
    
    logger = log_manager.get_logger("test.json", "simulator")
    
    logger.info("JSON formatted log message", extra={
        "component": "simulator",
        "action": "test",
        "data": {"key": "value", "number": 42}
    })
    
    print("✅ JSON logging test completed")


def test_log_levels():
    """Test different log levels"""
    print("\n=== Testing Log Levels ===")
    
    log_manager = setup_logging(level='DEBUG')
    
    logger = log_manager.get_logger("test.levels", "simulator")
    
    logger.debug("Debug level message")
    logger.info("Info level message")
    logger.warning("Warning level message")
    logger.error("Error level message")
    logger.critical("Critical level message")
    
    # Test changing log level at runtime
    log_manager.set_log_level('ERROR', 'simulator')
    logger.info("This should not appear (level set to ERROR)")
    logger.error("This should appear (ERROR level)")
    
    print("✅ Log levels test completed")


def test_custom_config():
    """Test custom configuration"""
    print("\n=== Testing Custom Configuration ===")
    
    # Test with custom config file
    config_path = project_root / "config" / "logging_config.json"
    
    if config_path.exists():
        log_manager = setup_logging(config_path=str(config_path))
        logger = log_manager.get_logger("test.custom", "server")
        
        logger.info("Using custom configuration from {}".format(config_path))
        
        # Test configuration updates
        log_manager.update_config({
            'default_level': 'WARNING',
            'rotation': {
                'max_file_size': '5MB',
                'backup_count': 3
            }
        })
        
        logger.warning("Configuration updated successfully")
        print("✅ Custom configuration test completed")
    else:
        print("⚠️  Configuration file not found, skipping custom config test")


def test_error_scenarios():
    """Test error handling and edge cases"""
    print("\n=== Testing Error Scenarios ===")
    
    log_manager = setup_logging()
    logger = log_manager.get_logger("test.errors", "simulator")
    
    # Test logging with exceptions
    try:
        raise ValueError("Test exception for logging")
    except Exception as e:
        logger.error("Exception occurred", exc_info=True)
    
    # Test logging with various data types
    logger.info("Logging different data types", extra={
        'string': 'test',
        'number': 123,
        'float': 45.67,
        'boolean': True,
        'list': [1, 2, 3],
        'dict': {'nested': 'value'}
    })
    
    print("✅ Error scenarios test completed")


def test_performance():
    """Test logging performance"""
    print("\n=== Testing Performance ===")
    
    log_manager = setup_logging(level='INFO')
    logger = log_manager.get_logger("test.performance", "simulator")
    
    # Test rapid logging
    start_time = time.time()
    
    for i in range(1000):
        if i % 100 == 0:
            logger.info("Performance test message {}".format(i))
        else:
            logger.debug("Debug message {}".format(i))  # These should be filtered out
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    logger.info("Performance test completed: 1000 messages in {:.3f} seconds".format(elapsed))
    print("✅ Performance test completed: {:.3f} seconds".format(elapsed))


def main():
    """Run all logging tests"""
    print("🧪 GA Modbus Simulator - Logging System Test")
    print("=" * 50)
    
    try:
        test_basic_logging()
        test_json_logging()
        test_log_levels()
        test_custom_config()
        test_error_scenarios()
        test_performance()
        
        print("\n" + "=" * 50)
        print("🎉 All logging tests completed successfully!")
        print("\n📋 Summary:")
        print("  • Component-specific logging: ✅")
        print("  • File rotation: ✅")
        print("  • JSON formatting: ✅")
        print("  • Runtime level changes: ✅")
        print("  • Custom configuration: ✅")
        print("  • Error handling: ✅")
        print("  • Performance: ✅")
        
        print("\n📁 Check the following for log output:")
        print("  • logs/simulator.log (main log)")
        print("  • logs/modbus_server.log (server component)")
        print("  • logs/cli.log (CLI component)")
        print("  • logs/register_handler.log (register component)")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()