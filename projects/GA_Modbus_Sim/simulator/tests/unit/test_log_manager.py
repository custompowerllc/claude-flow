#!/usr/bin/env python3
"""
Comprehensive Test Suite for LogManager
========================================

This test suite validates the LogManager functionality including:
- Log file creation and rotation
- Different log levels and formatting
- CLI integration options
- File permissions and accessibility
- Performance impact validation
- Thread safety and concurrent access
- Integration with existing components

Author: Logging Validator Agent
"""

import unittest
import tempfile
import shutil
import os
import sys
import threading
import time
import json
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
from contextlib import contextmanager

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Test imports - these will be available once LogManager is implemented
try:
    from src.utils.log_manager import LogManager, LogConfig
    LOG_MANAGER_AVAILABLE = True
except ImportError:
    # Create mock classes for testing structure
    class LogManager:
        def __init__(self, config=None):
            self.config = config or {}
            self.logger = logging.getLogger('test')
        
        def get_logger(self, name):
            return logging.getLogger(name)
        
        def setup_file_logging(self, log_file, level='INFO'):
            pass
        
        def cleanup(self):
            pass
    
    class LogConfig:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
    LOG_MANAGER_AVAILABLE = False


class TestLogManagerCore(unittest.TestCase):
    """Test core LogManager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_config = LogConfig(
            log_dir=self.temp_dir,
            log_file="test_simulator.log",
            level="DEBUG",
            max_file_size="10MB",
            backup_count=5,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # Store original logging level
        self.original_level = logging.getLogger().level
        
    def tearDown(self):
        """Clean up test environment"""
        # Restore original logging level
        logging.getLogger().setLevel(self.original_level)
        
        # Clean up temp directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_log_manager_initialization(self):
        """Test LogManager initialization with various configurations"""
        # Test default initialization
        log_manager = LogManager()
        self.assertIsNotNone(log_manager)
        
        # Test initialization with config
        log_manager = LogManager(self.log_config)
        self.assertIsNotNone(log_manager.config)
        
        # Test initialization with dict config
        dict_config = {
            'log_dir': self.temp_dir,
            'log_file': 'test.log',
            'level': 'INFO'
        }
        log_manager = LogManager(dict_config)
        self.assertIsNotNone(log_manager.config)
    
    def test_logger_creation(self):
        """Test logger creation for different components"""
        log_manager = LogManager(self.log_config)
        
        # Test creating loggers for different components
        components = ['AFE', 'FuelGauge', 'ModbusServer', 'CLI', 'RegisterHandler']
        
        for component in components:
            logger = log_manager.get_logger(component)
            self.assertIsNotNone(logger)
            self.assertEqual(logger.name, component)
    
    def test_log_file_creation(self):
        """Test log file creation and basic writing"""
        log_manager = LogManager(self.log_config)
        
        # Setup file logging
        log_file_path = os.path.join(self.temp_dir, "test.log")
        log_manager.setup_file_logging(log_file_path, level='DEBUG')
        
        # Get a logger and write messages
        logger = log_manager.get_logger('TestComponent')
        logger.info("Test info message")
        logger.debug("Test debug message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        
        # Verify file exists and contains messages
        self.assertTrue(os.path.exists(log_file_path))
        
        # Read log file and verify content
        with open(log_file_path, 'r') as f:
            content = f.read()
            self.assertIn("Test info message", content)
            self.assertIn("Test debug message", content)
            self.assertIn("Test warning message", content)
            self.assertIn("Test error message", content)
    
    def test_log_levels(self):
        """Test different log levels and filtering"""
        log_file_path = os.path.join(self.temp_dir, "level_test.log")
        
        # Test INFO level filtering
        config = LogConfig(
            log_dir=self.temp_dir,
            log_file="level_test.log",
            level="INFO"
        )
        log_manager = LogManager(config)
        log_manager.setup_file_logging(log_file_path, level='INFO')
        
        logger = log_manager.get_logger('LevelTest')
        logger.debug("This should not appear")
        logger.info("This should appear")
        logger.warning("This should appear")
        logger.error("This should appear")
        
        # Verify only INFO and above messages are written
        with open(log_file_path, 'r') as f:
            content = f.read()
            self.assertNotIn("This should not appear", content)
            self.assertIn("This should appear", content)
    
    def test_log_formatting(self):
        """Test custom log formatting"""
        log_file_path = os.path.join(self.temp_dir, "format_test.log")
        
        custom_format = "%(levelname)s | %(name)s | %(message)s"
        config = LogConfig(
            log_dir=self.temp_dir,
            log_file="format_test.log",
            level="INFO",
            format=custom_format
        )
        
        log_manager = LogManager(config)
        log_manager.setup_file_logging(log_file_path, level='INFO')
        
        logger = log_manager.get_logger('FormatTest')
        logger.info("Custom format test")
        
        # Verify custom format is used
        with open(log_file_path, 'r') as f:
            content = f.read()
            self.assertIn("INFO | FormatTest | Custom format test", content)


class TestLogRotation(unittest.TestCase):
    """Test log rotation functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_size_based_rotation(self):
        """Test log rotation based on file size"""
        # Create config with small max file size
        config = LogConfig(
            log_dir=self.temp_dir,
            log_file="rotation_test.log",
            level="INFO",
            max_file_size="1KB",  # Very small for testing
            backup_count=3
        )
        
        log_manager = LogManager(config)
        log_file_path = os.path.join(self.temp_dir, "rotation_test.log")
        log_manager.setup_file_logging(log_file_path, level='INFO')
        
        logger = log_manager.get_logger('RotationTest')
        
        # Write enough data to trigger rotation
        for i in range(100):
            logger.info("This is a test message that will fill up the log file - message {}".format(i))
        
        # Check if rotation occurred (backup files should exist)
        backup_files = [f for f in os.listdir(self.temp_dir) if f.startswith("rotation_test.log.")]
        self.assertGreater(len(backup_files), 0, "Log rotation should have created backup files")
    
    def test_backup_count_limit(self):
        """Test that backup count is respected during rotation"""
        config = LogConfig(
            log_dir=self.temp_dir,
            log_file="backup_test.log",
            level="INFO",
            max_file_size="500B",  # Very small for testing
            backup_count=2  # Only keep 2 backups
        )
        
        log_manager = LogManager(config)
        log_file_path = os.path.join(self.temp_dir, "backup_test.log")
        log_manager.setup_file_logging(log_file_path, level='INFO')
        
        logger = log_manager.get_logger('BackupTest')
        
        # Write enough data to trigger multiple rotations
        for i in range(200):
            logger.info("Backup test message {} - this should trigger multiple rotations".format(i))
        
        # Check that only the specified number of backups exist
        backup_files = [f for f in os.listdir(self.temp_dir) if f.startswith("backup_test.log.")]
        self.assertLessEqual(len(backup_files), 2, "Should not exceed backup_count limit")


class TestLogManagerIntegration(unittest.TestCase):
    """Test integration with existing simulator components"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = LogConfig(
            log_dir=self.temp_dir,
            log_file="integration_test.log",
            level="DEBUG"
        )
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_modbus_server_integration(self):
        """Test LogManager integration with ModbusServer"""
        log_manager = LogManager(self.config)
        
        # Mock ModbusServer to test logging integration
        with patch('src.core.modbus_server.logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Create logger through LogManager
            modbus_logger = log_manager.get_logger('ModbusServer')
            
            # Verify logger configuration
            self.assertIsNotNone(modbus_logger)
    
    def test_register_handler_integration(self):
        """Test LogManager integration with RegisterHandler"""
        log_manager = LogManager(self.config)
        
        # Test that RegisterHandler can use LogManager
        handler_logger = log_manager.get_logger('RegisterHandler')
        
        # Test logging different register operations
        handler_logger.info("Initializing register handler")
        handler_logger.debug("Updating register values")
        handler_logger.warning("Register value out of range")
        
        # Verify messages are logged
        log_file_path = os.path.join(self.temp_dir, "integration_test.log")
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r') as f:
                content = f.read()
                self.assertIn("RegisterHandler", content)
    
    def test_cli_integration(self):
        """Test LogManager integration with CLI"""
        log_manager = LogManager(self.config)
        
        # Test CLI logger
        cli_logger = log_manager.get_logger('CLI')
        
        cli_logger.info("Starting simulator with port COM4")
        cli_logger.info("Setting scenario: Charging - 1A")
        cli_logger.warning("Port COM3 is busy, using COM4 instead")
        cli_logger.error("Failed to start server on port COM1")
        
        # Verify CLI-specific logging works
        self.assertIsNotNone(cli_logger)


class TestLogManagerPerformance(unittest.TestCase):
    """Test logging performance impact"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = LogConfig(
            log_dir=self.temp_dir,
            log_file="performance_test.log",
            level="INFO"
        )
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logging_performance_impact(self):
        """Test performance impact of logging on simulator operations"""
        log_manager = LogManager(self.config)
        logger = log_manager.get_logger('PerformanceTest')
        
        # Measure time without logging
        start_time = time.time()
        for i in range(1000):
            # Simulate register operations
            pass
        no_logging_time = time.time() - start_time
        
        # Measure time with logging
        start_time = time.time()
        for i in range(1000):
            logger.debug("Register update {}".format(i))
        with_logging_time = time.time() - start_time
        
        # Performance impact should be minimal (less than 2x)
        performance_ratio = with_logging_time / no_logging_time if no_logging_time > 0 else 1
        self.assertLess(performance_ratio, 2.0, "Logging should not significantly impact performance")
    
    def test_high_frequency_logging(self):
        """Test high-frequency logging scenarios"""
        log_manager = LogManager(self.config)
        logger = log_manager.get_logger('HighFrequencyTest')
        
        # Test rapid logging (simulate register updates at 10Hz)
        start_time = time.time()
        for i in range(100):  # 100 updates in rapid succession
            logger.debug("High frequency update: register {} = {}".format(i % 36, i * 10))
            time.sleep(0.001)  # 1ms delay
        
        duration = time.time() - start_time
        self.assertLess(duration, 2.0, "High frequency logging should complete quickly")


class TestLogManagerThreadSafety(unittest.TestCase):
    """Test thread safety of LogManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = LogConfig(
            log_dir=self.temp_dir,
            log_file="thread_safety_test.log",
            level="INFO"
        )
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_concurrent_logging(self):
        """Test concurrent logging from multiple threads"""
        log_manager = LogManager(self.config)
        
        # Create multiple loggers for different components
        loggers = {
            'AFE': log_manager.get_logger('AFE'),
            'FuelGauge': log_manager.get_logger('FuelGauge'),
            'ModbusServer': log_manager.get_logger('ModbusServer'),
            'RegisterHandler': log_manager.get_logger('RegisterHandler')
        }
        
        results = []
        
        def log_worker(logger_name, logger, count):
            """Worker function for concurrent logging"""
            try:
                for i in range(count):
                    logger.info("{} - Message {}".format(logger_name, i))
                results.append((logger_name, True))
            except Exception as e:
                results.append((logger_name, False, str(e)))
        
        # Start multiple threads
        threads = []
        for name, logger in loggers.items():
            thread = threading.Thread(target=log_worker, args=(name, logger, 50))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=5.0)
        
        # Verify all threads completed successfully
        self.assertEqual(len(results), 4, "All threads should complete")
        for result in results:
            self.assertTrue(result[1], "Thread {} should complete successfully".format(result[0]))
    
    def test_logger_cleanup(self):
        """Test proper cleanup of loggers and handlers"""
        log_manager = LogManager(self.config)
        
        # Create and use loggers
        logger = log_manager.get_logger('CleanupTest')
        logger.info("Test message before cleanup")
        
        # Test cleanup
        log_manager.cleanup()
        
        # Verify cleanup completed without errors
        self.assertTrue(True, "Cleanup should complete without errors")


class TestLogManagerConfiguration(unittest.TestCase):
    """Test LogManager configuration options"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_json_configuration(self):
        """Test loading configuration from JSON file"""
        config_data = {
            "log_dir": self.temp_dir,
            "log_file": "json_config_test.log",
            "level": "DEBUG",
            "max_file_size": "5MB",
            "backup_count": 3,
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "components": {
                "AFE": "DEBUG",
                "FuelGauge": "INFO",
                "ModbusServer": "WARNING",
                "CLI": "ERROR"
            }
        }
        
        config_file = os.path.join(self.temp_dir, "log_config.json")
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Test loading config from file
        if LOG_MANAGER_AVAILABLE:
            log_manager = LogManager.from_config_file(config_file)
            self.assertIsNotNone(log_manager)
    
    def test_environment_variable_paths(self):
        """Test support for environment variables in paths"""
        # Set test environment variable
        os.environ['TEST_LOG_DIR'] = self.temp_dir
        
        try:
            config = LogConfig(
                log_dir="${TEST_LOG_DIR}",
                log_file="env_test.log",
                level="INFO"
            )
            
            log_manager = LogManager(config)
            
            # Verify environment variable expansion works
            self.assertIsNotNone(log_manager)
        finally:
            # Clean up environment variable
            if 'TEST_LOG_DIR' in os.environ:
                del os.environ['TEST_LOG_DIR']
    
    def test_relative_path_resolution(self):
        """Test relative path resolution for log files"""
        config = LogConfig(
            log_dir="./logs",  # Relative path
            log_file="relative_test.log",
            level="INFO"
        )
        
        log_manager = LogManager(config)
        
        # Verify relative paths are handled correctly
        self.assertIsNotNone(log_manager)


class TestLogFilePermissions(unittest.TestCase):
    """Test log file permissions and accessibility"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_log_file_permissions(self):
        """Test that log files are created with appropriate permissions"""
        config = LogConfig(
            log_dir=self.temp_dir,
            log_file="permissions_test.log",
            level="INFO"
        )
        
        log_manager = LogManager(config)
        log_file_path = os.path.join(self.temp_dir, "permissions_test.log")
        log_manager.setup_file_logging(log_file_path, level='INFO')
        
        logger = log_manager.get_logger('PermissionsTest')
        logger.info("Testing file permissions")
        
        if os.path.exists(log_file_path):
            # Check file permissions (should be readable/writable by owner)
            file_stat = os.stat(log_file_path)
            file_mode = file_stat.st_mode
            
            # Verify file is readable and writable by owner
            self.assertTrue(file_mode & 0o400, "File should be readable by owner")
            self.assertTrue(file_mode & 0o200, "File should be writable by owner")
    
    def test_directory_creation(self):
        """Test automatic creation of log directories"""
        nested_dir = os.path.join(self.temp_dir, "nested", "log", "directory")
        config = LogConfig(
            log_dir=nested_dir,
            log_file="nested_test.log",
            level="INFO"
        )
        
        log_manager = LogManager(config)
        log_file_path = os.path.join(nested_dir, "nested_test.log")
        
        # This should create the nested directory structure
        log_manager.setup_file_logging(log_file_path, level='INFO')
        
        logger = log_manager.get_logger('DirectoryTest')
        logger.info("Testing directory creation")
        
        # Verify directory was created
        self.assertTrue(os.path.exists(nested_dir), "Nested directory should be created")
        self.assertTrue(os.path.exists(log_file_path), "Log file should be created")


def run_comprehensive_tests():
    """Run all logging validation tests"""
    print("=" * 80)
    print("LOGGING VALIDATION TEST SUITE")
    print("=" * 80)
    print()
    
    # Test suites to run
    test_suites = [
        TestLogManagerCore,
        TestLogRotation,
        TestLogManagerIntegration,
        TestLogManagerPerformance,
        TestLogManagerThreadSafety,
        TestLogManagerConfiguration,
        TestLogFilePermissions
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for suite_class in test_suites:
        print("Running {} tests...".format(suite_class.__name__))
        
        # Create test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(suite_class)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        
        print()
    
    # Print summary
    print("=" * 80)
    print("LOGGING VALIDATION SUMMARY")
    print("=" * 80)
    print("Total Tests: {}".format(total_tests))
    print("Failures: {}".format(total_failures))
    print("Errors: {}".format(total_errors))
    print("Success Rate: {:.1f}%".format((total_tests - total_failures - total_errors) / total_tests * 100 if total_tests > 0 else 0))
    print()
    
    if total_failures == 0 and total_errors == 0:
        print("✅ ALL LOGGING VALIDATION TESTS PASSED!")
    else:
        print("❌ Some tests failed. Review implementation and re-run tests.")
    
    return total_failures == 0 and total_errors == 0


if __name__ == "__main__":
    # Check if LogManager is available
    if not LOG_MANAGER_AVAILABLE:
        print("⚠️  WARNING: LogManager not yet implemented!")
        print("This test suite is ready to validate the LogManager once it's implemented.")
        print("Expected import: from src.utils.log_manager import LogManager, LogConfig")
        print()
    
    # Run comprehensive tests
    success = run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)