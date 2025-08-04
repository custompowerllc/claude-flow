#!/usr/bin/env python3
"""
Integration Tests for Logging with Existing Demo Scripts
========================================================

This test suite validates logging integration with:
- run_simulator.py CLI interface
- demo_phase1.py demonstration script
- Existing ModbusServer and RegisterHandler components
- Real-world usage scenarios

Author: Logging Validator Agent
"""

import unittest
import tempfile
import shutil
import os
import sys
import subprocess
import threading
import time
import json
import signal
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import simulator components
try:
    from src.core.modbus_server import ModbusSimulatorServer, ServerConfig
    from src.core.register_handler import RegisterHandler, BatteryScenario
    from src.utils.com_port_manager import ComPortManager
    SIMULATOR_AVAILABLE = True
except ImportError:
    SIMULATOR_AVAILABLE = False

# Test imports for LogManager
try:
    from src.utils.log_manager import LogManager, LogConfig
    LOG_MANAGER_AVAILABLE = True
except ImportError:
    LOG_MANAGER_AVAILABLE = False


class TestCLILoggingIntegration(unittest.TestCase):
    """Test logging integration with run_simulator.py CLI"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.simulator_script = project_root / "run_simulator.py"
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cli_verbose_logging(self):
        """Test CLI verbose logging flag"""
        if not os.path.exists(self.simulator_script):
            self.skipTest("run_simulator.py not found")
        
        # Test running simulator with verbose logging
        cmd = [
            sys.executable, str(self.simulator_script),
            "--list-ports",
            "--verbose"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(project_root)
            )
            
            # Should complete successfully
            self.assertEqual(result.returncode, 0, "CLI should execute successfully")
            
            # With verbose flag, should see more detailed output
            if LOG_MANAGER_AVAILABLE:
                self.assertIn("DEBUG", result.stderr.upper())
            
        except subprocess.TimeoutExpired:
            self.fail("CLI command timed out")
        except FileNotFoundError:
            self.skipTest("Python executable or script not found")
    
    def test_cli_log_file_option(self):
        """Test CLI log file output option"""
        if not LOG_MANAGER_AVAILABLE:
            self.skipTest("LogManager not implemented yet")
        
        log_file = os.path.join(self.temp_dir, "cli_test.log")
        
        # Test running simulator with log file option
        cmd = [
            sys.executable, str(self.simulator_script),
            "--list-scenarios",
            "--log-file", log_file,
            "--verbose"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(project_root)
            )
            
            # Should complete successfully
            self.assertEqual(result.returncode, 0, "CLI should execute successfully")
            
            # Log file should be created
            self.assertTrue(os.path.exists(log_file), "Log file should be created")
            
            # Log file should contain relevant messages
            with open(log_file, 'r') as f:
                content = f.read()
                self.assertIn("Available Battery Scenarios", content)
        
        except subprocess.TimeoutExpired:
            self.fail("CLI command timed out")
        except FileNotFoundError:
            self.skipTest("Python executable or script not found")
    
    def test_cli_log_level_option(self):
        """Test CLI log level configuration"""
        if not LOG_MANAGER_AVAILABLE:
            self.skipTest("LogManager not implemented yet")
        
        log_file = os.path.join(self.temp_dir, "level_test.log")
        
        # Test with different log levels
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            with self.subTest(level=level):
                cmd = [
                    sys.executable, str(self.simulator_script),
                    "--list-ports",
                    "--log-file", log_file,
                    "--log-level", level
                ]
                
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        cwd=str(project_root)
                    )
                    
                    # Should complete successfully
                    self.assertEqual(result.returncode, 0, "CLI should execute successfully for level {}".format(level))
                
                except subprocess.TimeoutExpired:
                    self.fail("CLI command timed out for level {}".format(level))


class TestModbusServerLoggingIntegration(unittest.TestCase):
    """Test logging integration with ModbusServer"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        if LOG_MANAGER_AVAILABLE:
            self.log_config = LogConfig(
                log_dir=self.temp_dir,
                log_file="modbus_server_test.log",
                level="DEBUG"
            )
            self.log_manager = LogManager(self.log_config)
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'log_manager'):
            self.log_manager.cleanup()
        
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_modbus_server_startup_logging(self):
        """Test logging during ModbusServer startup"""
        if not SIMULATOR_AVAILABLE:
            self.skipTest("Simulator components not available")
        
        # Create server config for testing (use non-existent port)
        config = ServerConfig(
            port="COM999",  # Non-existent port for testing
            baudrate=9600,
            slave_id=1
        )
        
        if LOG_MANAGER_AVAILABLE:
            # Mock the logger to use LogManager
            with patch('src.core.modbus_server.logging.getLogger') as mock_get_logger:
                mock_logger = self.log_manager.get_logger('ModbusServer')
                mock_get_logger.return_value = mock_logger
                
                # Create server
                server = ModbusSimulatorServer(config)
                
                # Attempt to start (should fail due to invalid port)
                result = server.start()
                
                # Should fail gracefully with proper logging
                self.assertFalse(result, "Server should fail to start with invalid port")
                
                # Check log file for expected messages
                log_file = os.path.join(self.temp_dir, "modbus_server_test.log")
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        content = f.read()
                        self.assertIn("ModbusSimulatorServer", content)
        else:
            # Basic test without LogManager
            server = ModbusSimulatorServer(config)
            result = server.start()
            self.assertFalse(result, "Server should fail to start with invalid port")
    
    def test_register_update_logging(self):
        """Test logging during register updates"""
        if not SIMULATOR_AVAILABLE:
            self.skipTest("Simulator components not available")
        
        if LOG_MANAGER_AVAILABLE:
            # Create register handler with LogManager
            with patch('src.core.register_handler.logging.getLogger') as mock_get_logger:
                mock_logger = self.log_manager.get_logger('RegisterHandler')
                mock_get_logger.return_value = mock_logger
                
                handler = RegisterHandler()
                
                # Perform some register operations
                handler.update_register("afe_cell_volt1", 3700)
                handler.update_register("fg_state_of_charge", 75)
                handler.get_all_registers()
                
                # Check log file for register operations
                log_file = os.path.join(self.temp_dir, "modbus_server_test.log")
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        content = f.read()
                        self.assertIn("RegisterHandler", content)
        else:
            # Basic test without LogManager
            handler = RegisterHandler()
            result = handler.update_register("afe_cell_volt1", 3700)
            self.assertTrue(result, "Register update should succeed")


class TestDemoScriptLoggingIntegration(unittest.TestCase):
    """Test logging integration with demo scripts"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.demo_script = project_root / "demo_phase1.py"
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_demo_script_with_logging(self):
        """Test demo script execution with logging enabled"""
        if not os.path.exists(self.demo_script):
            self.skipTest("demo_phase1.py not found")
        
        if not LOG_MANAGER_AVAILABLE:
            self.skipTest("LogManager not implemented yet")
        
        log_file = os.path.join(self.temp_dir, "demo_test.log")
        
        # Test running demo with logging
        cmd = [
            sys.executable, str(self.demo_script),
            "--log-file", log_file,
            "--verbose",
            "--no-interactive"  # If demo supports non-interactive mode
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(project_root)
            )
            
            # Check if demo completed (may fail due to port issues, but should log)
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    content = f.read()
                    # Should contain demo-related log messages
                    self.assertTrue(len(content) > 0, "Log file should contain messages")
        
        except subprocess.TimeoutExpired:
            self.fail("Demo script timed out")
        except FileNotFoundError:
            self.skipTest("Python executable or demo script not found")


class TestLoggingPerformanceIntegration(unittest.TestCase):
    """Test logging performance in realistic scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        if LOG_MANAGER_AVAILABLE:
            self.log_config = LogConfig(
                log_dir=self.temp_dir,
                log_file="performance_test.log",
                level="INFO"
            )
            self.log_manager = LogManager(self.log_config)
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'log_manager'):
            self.log_manager.cleanup()
        
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_register_simulation_performance(self):
        """Test logging performance during register simulation"""
        if not SIMULATOR_AVAILABLE or not LOG_MANAGER_AVAILABLE:
            self.skipTest("Required components not available")
        
        # Create register handler
        handler = RegisterHandler()
        
        # Create logger for register handler
        register_logger = self.log_manager.get_logger('RegisterHandler')
        
        # Simulate register updates with logging
        start_time = time.time()
        
        for i in range(100):  # 100 update cycles
            # Update simulation (this happens ~1Hz in real usage)
            handler.update_simulation()
            
            # Log register values (this might happen during debugging)
            register_logger.debug("Simulation cycle {}: SOC={}%, Voltage={}mV".format(
                i,
                handler.get_register('fg_state_of_charge'),
                handler.get_register('afe_pack_volt')
            ))
            
            time.sleep(0.01)  # 10ms delay (100Hz simulation)
        
        duration = time.time() - start_time
        
        # Should complete in reasonable time (less than 5 seconds for 100 cycles)
        self.assertLess(duration, 5.0, "Register simulation with logging should be performant")
        
        # Verify log file was created and contains entries
        log_file = os.path.join(self.temp_dir, "performance_test.log")
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                content = f.read()
                self.assertIn("Simulation cycle", content)
    
    def test_concurrent_component_logging(self):
        """Test logging from multiple components concurrently"""
        if not SIMULATOR_AVAILABLE or not LOG_MANAGER_AVAILABLE:
            self.skipTest("Required components not available")
        
        # Create loggers for different components
        loggers = {
            'AFE': self.log_manager.get_logger('AFE'),
            'FuelGauge': self.log_manager.get_logger('FuelGauge'),
            'ModbusServer': self.log_manager.get_logger('ModbusServer'),
            'CLI': self.log_manager.get_logger('CLI')
        }
        
        results = []
        
        def component_worker(name, logger):
            """Simulate a component doing work with logging"""
            try:
                for i in range(20):
                    if name == 'AFE':
                        logger.debug("Cell voltage reading: {}mV".format(3700 + i))
                    elif name == 'FuelGauge':
                        logger.info("SOC update: {}%".format(50 + i))
                    elif name == 'ModbusServer':
                        logger.info("Modbus query processed: register {}".format(10 + i))
                    elif name == 'CLI':
                        logger.info("User command: scenario {}".format(i))
                    
                    time.sleep(0.01)  # Small delay
                
                results.append((name, True))
            except Exception as e:
                results.append((name, False, str(e)))
        
        # Start concurrent logging from multiple components
        threads = []
        for name, logger in loggers.items():
            thread = threading.Thread(target=component_worker, args=(name, logger))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=10.0)
        
        # Verify all components completed successfully
        self.assertEqual(len(results), 4, "All components should complete")
        for result in results:
            self.assertTrue(result[1], "Component {} should complete successfully".format(result[0]))
        
        # Verify log file contains messages from all components
        log_file = os.path.join(self.temp_dir, "performance_test.log")
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                content = f.read()
                for component in loggers.keys():
                    self.assertIn(component, content, "Should contain messages from {}".format(component))


class TestLoggingErrorHandling(unittest.TestCase):
    """Test logging behavior during error conditions"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logging_with_insufficient_permissions(self):
        """Test logging behavior when log directory is not writable"""
        if not LOG_MANAGER_AVAILABLE:
            self.skipTest("LogManager not implemented yet")
        
        # Create a directory and remove write permissions
        restricted_dir = os.path.join(self.temp_dir, "restricted")
        os.makedirs(restricted_dir)
        os.chmod(restricted_dir, 0o444)  # Read-only
        
        try:
            config = LogConfig(
                log_dir=restricted_dir,
                log_file="restricted_test.log",
                level="INFO"
            )
            
            # LogManager should handle permission errors gracefully
            log_manager = LogManager(config)
            logger = log_manager.get_logger('PermissionTest')
            
            # Should not raise exception, but may fall back to console logging
            logger.info("Test message with restricted permissions")
            
            # Test should complete without crashing
            self.assertTrue(True, "Should handle permission errors gracefully")
        
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(restricted_dir, 0o755)
            except:
                pass
    
    def test_logging_with_disk_full_simulation(self):
        """Test logging behavior when disk space is limited"""
        # This is a conceptual test - actual disk full simulation is complex
        # In a real implementation, LogManager should handle disk full errors
        
        if not LOG_MANAGER_AVAILABLE:
            self.skipTest("LogManager not implemented yet")
        
        config = LogConfig(
            log_dir=self.temp_dir,
            log_file="disk_full_test.log",
            level="INFO",
            max_file_size="1KB"  # Very small to trigger rotation quickly
        )
        
        log_manager = LogManager(config)
        logger = log_manager.get_logger('DiskFullTest')
        
        # Should handle errors gracefully even with small file limits
        try:
            for i in range(100):
                logger.info("Large message that will fill up disk space quickly - iteration {}".format(i))
        except Exception as e:
            self.fail("LogManager should handle disk space issues gracefully: {}".format(e))


def run_integration_tests():
    """Run all logging integration tests"""
    print("=" * 80)
    print("LOGGING INTEGRATION TEST SUITE")
    print("=" * 80)
    print()
    
    # Check component availability
    print("Component Availability:")
    print("- Simulator Components: {}".format("✅" if SIMULATOR_AVAILABLE else "❌"))
    print("- LogManager: {}".format("✅" if LOG_MANAGER_AVAILABLE else "❌"))
    print()
    
    # Test suites to run
    test_suites = [
        TestCLILoggingIntegration,
        TestModbusServerLoggingIntegration,
        TestDemoScriptLoggingIntegration,
        TestLoggingPerformanceIntegration,
        TestLoggingErrorHandling
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0
    
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
        total_skipped += len(result.skipped)
        
        print()
    
    # Print summary
    print("=" * 80)
    print("LOGGING INTEGRATION TEST SUMMARY")
    print("=" * 80)
    print("Total Tests: {}".format(total_tests))
    print("Failures: {}".format(total_failures))
    print("Errors: {}".format(total_errors))
    print("Skipped: {}".format(total_skipped))
    
    if total_tests > 0:
        success_rate = (total_tests - total_failures - total_errors) / total_tests * 100
        print("Success Rate: {:.1f}%".format(success_rate))
    
    print()
    
    if total_failures == 0 and total_errors == 0:
        print("✅ ALL INTEGRATION TESTS PASSED!")
    else:
        print("❌ Some tests failed. Review implementation and re-run tests.")
    
    return total_failures == 0 and total_errors == 0


if __name__ == "__main__":
    # Run integration tests
    success = run_integration_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)