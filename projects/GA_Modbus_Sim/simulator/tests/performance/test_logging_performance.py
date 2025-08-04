#!/usr/bin/env python3
"""
Logging Performance Impact Tests
===============================

This test suite specifically validates the performance impact of logging
on the simulator's real-time operations, ensuring that logging doesn't
interfere with the 1Hz register update cycle or Modbus response times.

Author: Logging Validator Agent
"""

import unittest
import tempfile
import shutil
import os
import sys
import threading
import time
import statistics
import psutil
from pathlib import Path
from contextlib import contextmanager

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import simulator components
try:
    from src.core.register_handler import RegisterHandler, BatteryScenario, BatteryState
    SIMULATOR_AVAILABLE = True
except ImportError:
    SIMULATOR_AVAILABLE = False

# Import LogManager for testing
try:
    from src.utils.log_manager import LogManager, LogConfig
    LOG_MANAGER_AVAILABLE = True
except ImportError:
    LOG_MANAGER_AVAILABLE = False


@contextmanager
def performance_monitor():
    """Context manager to monitor performance metrics"""
    process = psutil.Process()
    start_time = time.time()
    start_cpu = process.cpu_percent()
    start_memory = process.memory_info().rss
    
    yield
    
    end_time = time.time()
    end_cpu = process.cpu_percent()
    end_memory = process.memory_info().rss
    
    return {
        'duration': end_time - start_time,
        'cpu_usage': end_cpu - start_cpu,
        'memory_delta': end_memory - start_memory
    }


class TestRegisterUpdatePerformance(unittest.TestCase):
    """Test logging impact on register update performance"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        if LOG_MANAGER_AVAILABLE:
            self.log_config = LogConfig(
                log_dir=self.temp_dir,
                log_file="performance_test.log",
                level="DEBUG",
                max_file_size="10MB",
                backup_count=3
            )
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_register_update_baseline_performance(self):
        """Measure baseline performance without logging"""
        if not SIMULATOR_AVAILABLE:
            self.skipTest("RegisterHandler not available")
        
        handler = RegisterHandler()
        
        # Measure baseline performance
        update_times = []
        
        for i in range(100):
            start_time = time.perf_counter()
            handler.update_simulation()
            end_time = time.perf_counter()
            update_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = statistics.mean(update_times)
        max_time = max(update_times)
        min_time = min(update_times)
        
        print("Baseline Performance (no logging):")
        print("  Average: {:.4f}ms".format(avg_time * 1000))
        print("  Maximum: {:.4f}ms".format(max_time * 1000))
        print("  Minimum: {:.4f}ms".format(min_time * 1000))
        
        # Store baseline for comparison
        self.baseline_avg = avg_time
        self.baseline_max = max_time
        
        # Baseline should be very fast (< 1ms average)
        self.assertLess(avg_time, 0.001, "Baseline register update should be < 1ms")
    
    def test_register_update_with_logging_performance(self):
        """Measure performance impact with logging enabled"""
        if not SIMULATOR_AVAILABLE or not LOG_MANAGER_AVAILABLE:
            self.skipTest("Required components not available")
        
        # Setup logging
        log_manager = LogManager(self.log_config)
        logger = log_manager.get_logger('RegisterHandler')
        
        handler = RegisterHandler()
        
        # Measure performance with logging
        update_times = []
        
        for i in range(100):
            start_time = time.perf_counter()
            
            # Update simulation with logging
            handler.update_simulation()
            
            # Log register values (realistic logging scenario)
            register_dict = handler.get_register_dict()
            logger.debug("Cycle {}: SOC={}%, Voltage={}mV, Current={}mA".format(
                i,
                register_dict.get('fg_state_of_charge', 0),
                register_dict.get('afe_pack_volt', 0),
                register_dict.get('afe_current', 0)
            ))
            
            end_time = time.perf_counter()
            update_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = statistics.mean(update_times)
        max_time = max(update_times)
        min_time = min(update_times)
        
        print("With Logging Performance:")
        print("  Average: {:.4f}ms".format(avg_time * 1000))
        print("  Maximum: {:.4f}ms".format(max_time * 1000))
        print("  Minimum: {:.4f}ms".format(min_time * 1000))
        
        # Performance impact should be minimal
        if hasattr(self, 'baseline_avg'):
            impact_ratio = avg_time / self.baseline_avg
            print("  Impact ratio: {:.2f}x".format(impact_ratio))
            
            # Logging should not increase time by more than 2x
            self.assertLess(impact_ratio, 2.0, "Logging impact should be < 2x baseline")
        
        # Even with logging, should still be reasonably fast (< 5ms)
        self.assertLess(avg_time, 0.005, "Register update with logging should be < 5ms")
        
        log_manager.cleanup()
    
    def test_high_frequency_logging_impact(self):
        """Test impact of high-frequency logging (10Hz simulation)"""
        if not SIMULATOR_AVAILABLE or not LOG_MANAGER_AVAILABLE:
            self.skipTest("Required components not available")
        
        log_manager = LogManager(self.log_config)
        logger = log_manager.get_logger('HighFrequency')
        
        handler = RegisterHandler()
        
        # Simulate 10Hz logging for 10 seconds (100 cycles)
        total_start = time.time()
        cycle_times = []
        
        for i in range(100):
            cycle_start = time.perf_counter()
            
            # Update simulation
            handler.update_simulation()
            
            # High frequency logging (multiple log entries per cycle)
            register_dict = handler.get_register_dict()
            
            # Log individual cell voltages
            for j in range(1, 9):
                cell_volt = register_dict.get(f'afe_cell_volt{j}', 0)
                logger.debug("Cell {}: {}mV".format(j, cell_volt))
            
            # Log fuel gauge data
            logger.debug("SOC: {}%, Remaining: {}mAh".format(
                register_dict.get('fg_state_of_charge', 0),
                register_dict.get('fg_remaining_capacity', 0)
            ))
            
            cycle_end = time.perf_counter()
            cycle_times.append(cycle_end - cycle_start)
            
            # Sleep to maintain 10Hz rate
            time.sleep(0.1)
        
        total_time = time.time() - total_start
        
        # Analysis
        avg_cycle_time = statistics.mean(cycle_times)
        max_cycle_time = max(cycle_times)
        
        print("High Frequency Logging (10Hz):")
        print("  Total time: {:.2f}s".format(total_time))
        print("  Average cycle: {:.4f}ms".format(avg_cycle_time * 1000))
        print("  Maximum cycle: {:.4f}ms".format(max_cycle_time * 1000))
        print("  Expected time: ~10.0s")
        
        # Should maintain timing despite heavy logging
        self.assertLess(total_time, 12.0, "High frequency logging should not significantly delay timing")
        self.assertLess(avg_cycle_time, 0.01, "Average cycle time should be < 10ms")
        
        log_manager.cleanup()


class TestConcurrentLoggingPerformance(unittest.TestCase):
    """Test performance with concurrent logging from multiple components"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        if LOG_MANAGER_AVAILABLE:
            self.log_config = LogConfig(
                log_dir=self.temp_dir,
                log_file="concurrent_test.log",
                level="INFO",
                max_file_size="5MB",
                backup_count=2
            )
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_concurrent_component_logging(self):
        """Test concurrent logging from multiple simulated components"""
        if not LOG_MANAGER_AVAILABLE:
            self.skipTest("LogManager not available")
        
        log_manager = LogManager(self.log_config)
        
        # Create loggers for different components
        loggers = {
            'AFE': log_manager.get_logger('AFE'),
            'FuelGauge': log_manager.get_logger('FuelGauge'),
            'ModbusServer': log_manager.get_logger('ModbusServer'),
            'CLI': log_manager.get_logger('CLI')
        }
        
        results = []
        
        def component_worker(name, logger, duration=5.0):
            """Simulate a component doing work with logging"""
            start_time = time.time()
            cycle_count = 0
            
            try:
                while time.time() - start_time < duration:
                    cycle_start = time.perf_counter()
                    
                    # Simulate component-specific work
                    if name == 'AFE':
                        logger.info("Cell voltage scan complete - {} cells".format(8))
                        logger.debug("Cell balance check: OK")
                    elif name == 'FuelGauge':
                        logger.info("SOC calculation: {}%".format(50 + (cycle_count % 50)))
                        logger.debug("Capacity estimation updated")
                    elif name == 'ModbusServer':
                        logger.info("Query processed: register {} count {}".format(10, 36))
                        logger.debug("Response sent: {} bytes".format(72 + cycle_count % 10))
                    elif name == 'CLI':
                        logger.info("Status check: all systems operational")
                        if cycle_count % 10 == 0:
                            logger.warning("Routine maintenance reminder")
                    
                    cycle_end = time.perf_counter()
                    cycle_time = cycle_end - cycle_start
                    
                    cycle_count += 1
                    
                    # Maintain ~10Hz rate
                    time.sleep(max(0, 0.1 - cycle_time))
                
                total_time = time.time() - start_time
                avg_cycle_time = total_time / cycle_count if cycle_count > 0 else 0
                
                results.append({
                    'component': name,
                    'success': True,
                    'cycles': cycle_count,
                    'total_time': total_time,
                    'avg_cycle_time': avg_cycle_time
                })
                
            except Exception as e:
                results.append({
                    'component': name,
                    'success': False,
                    'error': str(e)
                })
        
        # Start concurrent workers
        threads = []
        test_duration = 5.0  # 5 seconds
        
        start_time = time.time()
        for name, logger in loggers.items():
            thread = threading.Thread(target=component_worker, args=(name, logger, test_duration))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=test_duration + 2.0)
        
        total_test_time = time.time() - start_time
        
        # Analyze results
        print("Concurrent Logging Performance:")
        print("  Test duration: {:.2f}s".format(total_test_time))
        
        successful_components = 0
        total_cycles = 0
        
        for result in results:
            if result['success']:
                successful_components += 1
                total_cycles += result['cycles']
                print("  {}: {} cycles, {:.4f}ms avg".format(
                    result['component'],
                    result['cycles'],
                    result['avg_cycle_time'] * 1000
                ))
            else:
                print("  {}: FAILED - {}".format(result['component'], result['error']))
        
        print("  Total cycles: {}".format(total_cycles))
        
        # Validation
        self.assertEqual(len(results), 4, "All components should complete")
        self.assertEqual(successful_components, 4, "All components should succeed")
        self.assertLess(total_test_time, test_duration + 1.0, "Test should complete within time limit")
        self.assertGreater(total_cycles, 150, "Should achieve reasonable cycle count")  # ~40 cycles per component
        
        log_manager.cleanup()


class TestLoggingMemoryUsage(unittest.TestCase):
    """Test memory usage impact of logging"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_memory_usage_over_time(self):
        """Test memory usage with extended logging"""
        if not LOG_MANAGER_AVAILABLE:
            self.skipTest("LogManager not available")
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        log_config = LogConfig(
            log_dir=self.temp_dir,
            log_file="memory_test.log",
            level="DEBUG",
            max_file_size="1MB",  # Small size to trigger rotation
            backup_count=3
        )
        
        log_manager = LogManager(log_config)
        logger = log_manager.get_logger('MemoryTest')
        
        # Log continuously for a period
        memory_samples = []
        
        for i in range(1000):
            # Generate varying log messages
            if i % 10 == 0:
                logger.info("Status update {}: All systems operational".format(i))
            
            logger.debug("Debug message {}: Register values updated - SOC={}%, Volt={}mV".format(
                i, 50 + (i % 50), 29600 + (i % 800)
            ))
            
            if i % 5 == 0:
                logger.warning("Periodic warning {}: Cell voltage delta = {}mV".format(i, 10 + (i % 30)))
            
            # Sample memory every 100 iterations
            if i % 100 == 0:
                current_memory = process.memory_info().rss
                memory_samples.append(current_memory)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        max_memory = max(memory_samples) if memory_samples else final_memory
        
        print("Memory Usage Analysis:")
        print("  Initial memory: {:.2f} MB".format(initial_memory / 1024 / 1024))
        print("  Final memory: {:.2f} MB".format(final_memory / 1024 / 1024))
        print("  Maximum memory: {:.2f} MB".format(max_memory / 1024 / 1024))
        print("  Memory increase: {:.2f} MB".format(memory_increase / 1024 / 1024))
        
        # Memory increase should be reasonable (< 50MB for extended logging)
        max_increase_mb = 50
        self.assertLess(memory_increase / 1024 / 1024, max_increase_mb,
                       "Memory increase should be < {}MB".format(max_increase_mb))
        
        log_manager.cleanup()
    
    def test_log_rotation_memory_impact(self):
        """Test memory usage during log rotation"""
        if not LOG_MANAGER_AVAILABLE:
            self.skipTest("LogManager not available")
        
        log_config = LogConfig(
            log_dir=self.temp_dir,
            log_file="rotation_memory_test.log",
            level="INFO",
            max_file_size="100KB",  # Very small to force frequent rotation
            backup_count=5
        )
        
        log_manager = LogManager(log_config)
        logger = log_manager.get_logger('RotationTest')
        
        process = psutil.Process()
        memory_before = process.memory_info().rss
        
        # Generate enough logs to trigger multiple rotations
        large_message = "Large log message with lots of data: " + "X" * 200
        
        for i in range(2000):  # Should trigger several rotations
            logger.info("Rotation test {}: {}".format(i, large_message))
            
            if i % 500 == 0:
                # Force garbage collection and check memory
                import gc
                gc.collect()
        
        memory_after = process.memory_info().rss
        memory_delta = memory_after - memory_before
        
        print("Log Rotation Memory Impact:")
        print("  Memory before: {:.2f} MB".format(memory_before / 1024 / 1024))
        print("  Memory after: {:.2f} MB".format(memory_after / 1024 / 1024))
        print("  Memory delta: {:.2f} MB".format(memory_delta / 1024 / 1024))
        
        # Check that rotation files were created
        log_files = [f for f in os.listdir(self.temp_dir) if f.startswith("rotation_memory_test.log")]
        print("  Log files created: {}".format(len(log_files)))
        
        # Memory delta should be reasonable even with rotation
        self.assertLess(memory_delta / 1024 / 1024, 30, "Memory delta during rotation should be < 30MB")
        self.assertGreater(len(log_files), 1, "Log rotation should create backup files")
        
        log_manager.cleanup()


def run_performance_tests():
    """Run all logging performance tests"""
    print("=" * 80)
    print("LOGGING PERFORMANCE TEST SUITE")
    print("=" * 80)
    print()
    
    # Check component availability
    print("Component Availability:")
    print("- Simulator Components: {}".format("✅" if SIMULATOR_AVAILABLE else "❌"))
    print("- LogManager: {}".format("✅" if LOG_MANAGER_AVAILABLE else "❌"))
    print("- psutil (for monitoring): {}".format("✅" if 'psutil' in sys.modules else "❌"))
    print()
    
    if not LOG_MANAGER_AVAILABLE:
        print("⚠️  LogManager not available - performance tests will be skipped")
        return False
    
    # Test suites to run
    test_suites = [
        TestRegisterUpdatePerformance,
        TestConcurrentLoggingPerformance,
        TestLoggingMemoryUsage
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
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        total_skipped += len(result.skipped)
        
        print()
    
    # Print summary
    print("=" * 80)
    print("LOGGING PERFORMANCE TEST SUMMARY")
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
        print("✅ ALL PERFORMANCE TESTS PASSED!")
        print("📊 Logging implementation meets performance requirements")
    else:
        print("❌ Some performance tests failed")
        print("🔧 Review logging implementation for performance optimization")
    
    return total_failures == 0 and total_errors == 0


if __name__ == "__main__":
    # Run performance tests
    success = run_performance_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)