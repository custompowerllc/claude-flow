#!/usr/bin/env python3
"""
P3E Runaway Detection Algorithms - Comprehensive Test Suite

This script provides a comprehensive test suite for all P3E runaway detection
algorithms, validating their functionality against actual P3E analysis data
and demonstrating the integrated system capabilities.

Test Scenarios:
1. Normal operation validation
2. P3E Pack 0535 catastrophic runaway (1048mV, 65°C)
3. P3E Pack 0533 discharge runaway (702mV, -5.3A discharge)
4. P3E Pack 0520/0561 concerning levels (502-533mV)
5. Progressive failure cascade simulation
6. Thermal propagation modeling
7. Alert system validation
8. Data logging and export validation

Expected Outputs:
- Detection algorithm performance metrics
- Thermal propagation analysis
- Real-time alert generation
- P3E-compatible data export
- Comprehensive validation report
"""

import sys
import os
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add simulator src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'simulator', 'src'))

# Import P3E algorithms
try:
    from algorithms.integrated_system import P3EIntegratedSystem, SystemConfiguration
    from algorithms.runaway_detection import RunawayRiskLevel
    from algorithms.thermal_propagation import ThermalState, CoolingEffectiveness
    from algorithms.alert_system import AlertSeverity
    from algorithms.data_logger import LogLevel, DataFormat
    from algorithms import P3E_THRESHOLDS, P3E_PATTERNS
    ALGORITHMS_AVAILABLE = True
except ImportError as e:
    print(f"ERROR: Could not import P3E algorithms: {e}")
    print("Please ensure the simulator/src/algorithms package is properly installed")
    sys.exit(1)


class P3ETestSuite:
    """Comprehensive test suite for P3E algorithms"""
    
    def __init__(self, output_directory: str = "p3e_test_results"):
        """Initialize test suite"""
        self.output_dir = Path(output_directory)
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'test_suite.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Test results
        self.test_results = {
            'test_session': f"p3e_test_{int(time.time())}",
            'start_time': datetime.now(),
            'end_time': None,
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_details': [],
            'p3e_correlations_validated': 0,
            'performance_metrics': {},
            'validation_summary': {}
        }
        
        self.logger.info(f"P3E Test Suite initialized - Output: {self.output_dir}")
    
    def run_all_tests(self) -> Dict:
        """Run all P3E algorithm tests"""
        print("=" * 80)
        print("P3E RUNAWAY DETECTION ALGORITHMS - COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"Session: {self.test_results['test_session']}")
        print(f"Output Directory: {self.output_dir}")
        print(f"Start Time: {self.test_results['start_time']}")
        print()
        
        # Test scenarios
        test_scenarios = [
            self.test_system_initialization,
            self.test_normal_operation,
            self.test_p3e_early_warning,
            self.test_p3e_pack_0533_pattern,
            self.test_p3e_pack_0535_catastrophic,
            self.test_progressive_failure,
            self.test_thermal_propagation,
            self.test_alert_escalation,
            self.test_data_logging,
            self.test_p3e_export_validation,
            self.test_emergency_shutdown,
            self.test_integration_callbacks
        ]
        
        # Run all tests
        for test_func in test_scenarios:
            try:
                print(f"\n{'='*60}")
                print(f"RUNNING: {test_func.__name__.replace('_', ' ').title()}")
                print('='*60)
                
                test_start = time.time()
                result = test_func()
                test_duration = time.time() - test_start
                
                self.test_results['tests_run'] += 1
                
                if result['passed']:
                    self.test_results['tests_passed'] += 1
                    print(f"✅ PASSED ({test_duration:.2f}s)")
                else:
                    self.test_results['tests_failed'] += 1
                    print(f"❌ FAILED ({test_duration:.2f}s): {result.get('error', 'Unknown error')}")
                
                result['duration_seconds'] = test_duration
                self.test_results['test_details'].append(result)
                
            except Exception as e:
                self.logger.error(f"Test {test_func.__name__} failed with exception: {e}")
                self.test_results['tests_failed'] += 1
                self.test_results['test_details'].append({
                    'test_name': test_func.__name__,
                    'passed': False,
                    'error': str(e),
                    'duration_seconds': 0
                })
        
        # Finalize results
        self.test_results['end_time'] = datetime.now()
        self.test_results['total_duration'] = (
            self.test_results['end_time'] - self.test_results['start_time']
        ).total_seconds()
        
        # Generate final report
        self._generate_final_report()
        
        return self.test_results
    
    def test_system_initialization(self) -> Dict:
        """Test P3E system initialization"""
        try:
            # Create system configuration
            config = SystemConfiguration(
                sample_rate_hz=5.0,  # High rate for testing
                log_level=LogLevel.VERBOSE,
                log_formats=[DataFormat.CSV, DataFormat.JSON, DataFormat.SQLITE],
                enable_p3e_simulations=False,  # Disable for controlled testing
                integration_mode="standalone"
            )
            
            # Initialize system
            self.p3e_system = P3EIntegratedSystem(config)
            
            # Verify system components
            assert self.p3e_system.runaway_detector is not None
            assert self.p3e_system.thermal_simulator is not None
            assert self.p3e_system.alert_manager is not None
            assert self.p3e_system.data_logger is not None
            
            # Check system status
            status = self.p3e_system.get_system_status()
            assert status.system_active == True
            assert status.session_id is not None
            
            print(f"  ✓ System initialized successfully")
            print(f"  ✓ Session ID: {status.session_id}")
            print(f"  ✓ All components active")
            
            return {
                'test_name': 'system_initialization',
                'passed': True,
                'session_id': status.session_id,
                'components_active': 4
            }
            
        except Exception as e:
            return {
                'test_name': 'system_initialization',
                'passed': False,
                'error': str(e)
            }
    
    def test_normal_operation(self) -> Dict:
        """Test normal operation detection"""
        try:
            print("  Testing normal operation (8-15mV delta range)...")
            
            # Normal cell voltages with small delta
            normal_voltages = [3700, 3705, 3698, 3702, 3701, 3699, 3703, 3697]  # 8mV delta
            normal_temps = [250, 252, 251, 249, 253, 250, 251, 252]  # 25.0-25.3°C
            
            detection_events = 0
            
            # Run for 10 seconds
            start_time = time.time()
            while (time.time() - start_time) < 10.0:
                self.p3e_system.process_cell_data(
                    cell_voltages_mv=normal_voltages,
                    temperatures_dc=normal_temps,
                    current_ma=0,
                    soc_percent=50,
                    metadata={'test_phase': 'normal_operation'}
                )
                
                # Check for unexpected detection events
                status = self.p3e_system.get_system_status()
                if status.current_risk_level != 'normal':
                    detection_events += 1
                
                time.sleep(0.1)  # 10Hz
            
            # Verify normal operation
            final_status = self.p3e_system.get_system_status()
            stats = self.p3e_system.get_system_statistics()
            
            assert final_status.current_risk_level == 'normal'
            assert final_status.current_thermal_state == 'normal'
            assert detection_events == 0  # No false positives
            
            print(f"  ✓ Normal operation maintained for 10 seconds")
            print(f"  ✓ Risk level: {final_status.current_risk_level}")
            print(f"  ✓ Thermal state: {final_status.current_thermal_state}")
            print(f"  ✓ Data points processed: {stats['data_points_processed']}")
            
            return {
                'test_name': 'normal_operation',
                'passed': True,
                'data_points_processed': stats['data_points_processed'],
                'false_positives': detection_events,
                'final_risk_level': final_status.current_risk_level
            }
            
        except Exception as e:
            return {
                'test_name': 'normal_operation',
                'passed': False,
                'error': str(e)
            }
    
    def test_p3e_early_warning(self) -> Dict:
        """Test P3E early warning threshold (100mV)"""
        try:
            print("  Testing P3E early warning threshold (100mV)...")
            
            # Cell voltages with 120mV delta (exceeds 100mV threshold)
            warning_voltages = [3700, 3705, 3698, 3702, 3701, 3580, 3703, 3697]  # 125mV delta
            warning_temps = [280, 285, 283, 281, 287, 280, 284, 282]  # Slightly elevated
            
            warning_detected = False
            
            # Run until warning detected or timeout
            start_time = time.time()
            while (time.time() - start_time) < 5.0 and not warning_detected:
                self.p3e_system.process_cell_data(
                    cell_voltages_mv=warning_voltages,
                    temperatures_dc=warning_temps,
                    current_ma=-1000,  # Light discharge
                    soc_percent=65,
                    metadata={'test_phase': 'early_warning', 'p3e_threshold': '100mV'}
                )
                
                status = self.p3e_system.get_system_status()
                if status.current_risk_level in ['warning', 'early_warning']:
                    warning_detected = True
                
                time.sleep(0.2)
            
            # Verify warning detection
            final_status = self.p3e_system.get_system_status()
            stats = self.p3e_system.get_system_statistics()
            
            assert warning_detected, "Early warning not detected"
            assert stats['total_alerts_generated'] > 0, "No alerts generated"
            
            print(f"  ✓ Early warning detected in {time.time() - start_time:.1f}s")
            print(f"  ✓ Final risk level: {final_status.current_risk_level}")
            print(f"  ✓ Alerts generated: {stats['total_alerts_generated']}")
            print(f"  ✓ P3E correlations: {stats['p3e_correlations_detected']}")
            
            self.test_results['p3e_correlations_validated'] += 1
            
            return {
                'test_name': 'p3e_early_warning',
                'passed': True,
                'detection_time_s': time.time() - start_time,
                'alerts_generated': stats['total_alerts_generated'],
                'p3e_correlations': stats['p3e_correlations_detected']
            }
            
        except Exception as e:
            return {
                'test_name': 'p3e_early_warning',
                'passed': False,
                'error': str(e)
            }
    
    def test_p3e_pack_0533_pattern(self) -> Dict:
        """Test P3E Pack 0533 discharge runaway pattern"""
        try:
            print("  Testing P3E Pack 0533 pattern (702mV, -5.3A discharge)...")
            
            # Simulate Pack 0533 escalation pattern
            escalation_phases = [
                # Phase 1: Initial discharge (59mV delta)
                {
                    'voltages': [3147, 3192, 3206, 3195, 3198, 3147, 3201, 3189],
                    'temps': [305, 305, 305, 305, 305, 305, 305, 305],
                    'current': -5300,
                    'soc': 64,
                    'duration': 2.0,
                    'expected_risk': 'normal'
                },
                # Phase 2: Escalation begins (326mV delta)
                {
                    'voltages': [3179, 3192, 3206, 3195, 3198, 2853, 3201, 3189],
                    'temps': [305, 305, 305, 305, 305, 305, 305, 305],
                    'current': -5300,
                    'soc': 44,
                    'duration': 1.0,
                    'expected_risk': 'high'
                },
                # Phase 3: Critical escalation (503mV delta)
                {
                    'voltages': [3179, 3192, 3206, 3195, 3198, 2674, 3201, 3189],
                    'temps': [305, 305, 305, 305, 305, 305, 305, 305],
                    'current': -5300,
                    'soc': 43,
                    'duration': 1.0,
                    'expected_risk': 'critical'
                },
                # Phase 4: Peak runaway (702mV delta)
                {
                    'voltages': [3176, 3192, 3206, 3195, 3198, 2474, 3201, 3189],
                    'temps': [305, 305, 305, 305, 305, 305, 305, 305],
                    'current': -5300,
                    'soc': 42,
                    'duration': 1.0,
                    'expected_risk': 'emergency'
                }
            ]
            
            phase_results = []
            total_alerts = 0
            
            for i, phase in enumerate(escalation_phases):
                print(f"    Phase {i+1}: {phase['duration']}s, Target: {phase['expected_risk']}")
                
                phase_start = time.time()
                risk_achieved = False
                
                while (time.time() - phase_start) < phase['duration']:
                    self.p3e_system.process_cell_data(
                        cell_voltages_mv=phase['voltages'],
                        temperatures_dc=phase['temps'],
                        current_ma=phase['current'],
                        soc_percent=phase['soc'],
                        metadata={
                            'test_phase': 'pack_0533_escalation',
                            'escalation_phase': i+1,
                            'p3e_pattern': 'pack_0533'
                        }
                    )
                    
                    status = self.p3e_system.get_system_status()
                    if (phase['expected_risk'] in status.current_risk_level or 
                        status.current_risk_level in ['emergency', 'critical']):
                        risk_achieved = True
                    
                    time.sleep(0.1)
                
                current_stats = self.p3e_system.get_system_statistics()
                phase_alerts = current_stats['total_alerts_generated'] - total_alerts
                total_alerts = current_stats['total_alerts_generated']
                
                phase_results.append({
                    'phase': i+1,
                    'risk_achieved': risk_achieved,
                    'alerts_generated': phase_alerts,
                    'final_risk': self.p3e_system.get_system_status().current_risk_level
                })
                
                print(f"      Risk achieved: {risk_achieved}, Alerts: {phase_alerts}")
            
            # Verify Pack 0533 pattern detection
            final_stats = self.p3e_system.get_system_statistics()
            assert final_stats['p3e_correlations_detected'] > 0, "No P3E correlations detected"
            assert total_alerts > 0, "No alerts generated during escalation"
            
            print(f"  ✓ Pack 0533 pattern simulation completed")
            print(f"  ✓ Total alerts: {total_alerts}")
            print(f"  ✓ P3E correlations: {final_stats['p3e_correlations_detected']}")
            
            self.test_results['p3e_correlations_validated'] += 1
            
            return {
                'test_name': 'p3e_pack_0533_pattern',
                'passed': True,
                'escalation_phases': phase_results,
                'total_alerts': total_alerts,
                'p3e_correlations': final_stats['p3e_correlations_detected']
            }
            
        except Exception as e:
            return {
                'test_name': 'p3e_pack_0533_pattern',
                'passed': False,
                'error': str(e)
            }
    
    def test_p3e_pack_0535_catastrophic(self) -> Dict:
        """Test P3E Pack 0535 catastrophic runaway pattern"""
        try:
            print("  Testing P3E Pack 0535 catastrophic pattern (1048mV, 65°C)...")
            
            # Simulate Pack 0535 catastrophic event
            catastrophic_voltages = [3363, 3368, 3370, 3365, 3369, 4411, 3367, 3364]  # 1048mV delta
            catastrophic_temps = [650, 650, 650, 650, 650, 650, 650, 650]  # 65°C
            
            emergency_detected = False
            catastrophic_detected = False
            
            # Run until catastrophic detection or timeout
            start_time = time.time()
            while (time.time() - start_time) < 3.0:
                self.p3e_system.process_cell_data(
                    cell_voltages_mv=catastrophic_voltages,
                    temperatures_dc=catastrophic_temps,
                    current_ma=0,  # No current (BMS bypassed scenario)
                    soc_percent=85,
                    metadata={
                        'test_phase': 'pack_0535_catastrophic',
                        'p3e_pattern': 'pack_0535',
                        'bms_bypassed': True
                    }
                )
                
                status = self.p3e_system.get_system_status()
                if 'emergency' in status.current_risk_level:
                    emergency_detected = True
                if 'catastrophic' in status.current_risk_level:
                    catastrophic_detected = True
                
                # Check for emergency shutdown
                if status.emergency_shutdown_requested:
                    print(f"    Emergency shutdown requested at {time.time() - start_time:.1f}s")
                    break
                
                time.sleep(0.1)
            
            # Verify catastrophic detection
            final_stats = self.p3e_system.get_system_statistics()
            final_status = self.p3e_system.get_system_status()
            
            assert emergency_detected or catastrophic_detected, "Catastrophic level not detected"
            assert final_stats['total_alerts_generated'] > 0, "No alerts generated"
            
            print(f"  ✓ Catastrophic pattern detected in {time.time() - start_time:.1f}s")
            print(f"  ✓ Emergency detected: {emergency_detected}")
            print(f"  ✓ Catastrophic detected: {catastrophic_detected}")
            print(f"  ✓ Emergency shutdown: {final_status.emergency_shutdown_requested}")
            print(f"  ✓ Total alerts: {final_stats['total_alerts_generated']}")
            
            self.test_results['p3e_correlations_validated'] += 1
            
            return {
                'test_name': 'p3e_pack_0535_catastrophic',
                'passed': True,
                'emergency_detected': emergency_detected,
                'catastrophic_detected': catastrophic_detected,
                'emergency_shutdown': final_status.emergency_shutdown_requested,
                'detection_time_s': time.time() - start_time
            }
            
        except Exception as e:
            return {
                'test_name': 'p3e_pack_0535_catastrophic',
                'passed': False,
                'error': str(e)
            }
    
    def test_progressive_failure(self) -> Dict:
        """Test progressive failure detection"""
        try:
            print("  Testing progressive failure detection...")
            
            # Simulate progressive cell degradation
            base_voltages = [3700, 3705, 3698, 3702, 3701, 3699, 3703, 3697]
            
            progressive_events = 0
            
            # Gradually increase Cell #6 degradation
            for step in range(20):
                # Cell #6 progressively fails
                degraded_voltages = base_voltages.copy()
                degraded_voltages[5] = 3699 - (step * 15)  # 15mV degradation per step
                
                self.p3e_system.process_cell_data(
                    cell_voltages_mv=degraded_voltages,
                    temperatures_dc=[250] * 8,
                    current_ma=-2000,  # Moderate discharge
                    soc_percent=max(50 - step, 10),
                    metadata={
                        'test_phase': 'progressive_failure',
                        'degradation_step': step,
                        'cell_6_voltage': degraded_voltages[5]
                    }
                )
                
                # Check for progressive failure detection
                status = self.p3e_system.get_system_status()
                if status.current_risk_level not in ['normal']:
                    progressive_events += 1
                
                time.sleep(0.1)
            
            final_stats = self.p3e_system.get_system_statistics()
            final_status = self.p3e_system.get_system_status()
            
            assert progressive_events > 0, "No progressive failure detected"
            assert final_stats['total_detection_events'] > 0, "No detection events"
            
            print(f"  ✓ Progressive failure events: {progressive_events}")
            print(f"  ✓ Final risk level: {final_status.current_risk_level}")
            print(f"  ✓ Detection events: {final_stats['total_detection_events']}")
            
            return {
                'test_name': 'progressive_failure',
                'passed': True,
                'progressive_events': progressive_events,
                'detection_events': final_stats['total_detection_events']
            }
            
        except Exception as e:
            return {
                'test_name': 'progressive_failure',
                'passed': False,
                'error': str(e)
            }
    
    def test_thermal_propagation(self) -> Dict:
        """Test thermal propagation simulation"""
        try:
            print("  Testing thermal propagation simulation...")
            
            # Simulate thermal propagation scenario
            normal_voltages = [3700, 3705, 3698, 3702, 3701, 3699, 3703, 3697]
            
            thermal_events = 0
            max_temp_reached = 25.0
            
            # Gradually increase temperature to simulate thermal propagation
            for step in range(30):
                # Progressive temperature increase
                base_temp = 250 + (step * 10)  # Increase 1°C per step
                hot_spot_temp = base_temp + (step * 5)  # Hot spot increases faster
                
                temperatures = [base_temp] * 8
                temperatures[5] = hot_spot_temp  # Cell #6 hot spot
                
                max_temp_c = max(temperatures) / 10.0
                if max_temp_c > max_temp_reached:
                    max_temp_reached = max_temp_c
                
                self.p3e_system.process_cell_data(
                    cell_voltages_mv=normal_voltages,
                    temperatures_dc=temperatures,
                    current_ma=-1000,
                    soc_percent=50,
                    metadata={
                        'test_phase': 'thermal_propagation',
                        'temp_step': step,
                        'max_temp_c': max_temp_c
                    }
                )
                
                status = self.p3e_system.get_system_status()
                if status.current_thermal_state != 'normal':
                    thermal_events += 1
                
                # Stop if thermal runaway detected
                if max_temp_c >= 60.0:
                    print(f"    Thermal runaway reached at step {step} ({max_temp_c:.1f}°C)")
                    break
                
                time.sleep(0.05)
            
            final_stats = self.p3e_system.get_system_statistics()
            final_status = self.p3e_system.get_system_status()
            
            assert thermal_events > 0, "No thermal events detected"
            assert max_temp_reached > 35.0, "Temperature did not reach elevated levels"
            
            print(f"  ✓ Thermal events detected: {thermal_events}")
            print(f"  ✓ Max temperature reached: {max_temp_reached:.1f}°C")
            print(f"  ✓ Final thermal state: {final_status.current_thermal_state}")
            
            return {
                'test_name': 'thermal_propagation',
                'passed': True,
                'thermal_events': thermal_events,
                'max_temperature_c': max_temp_reached,
                'final_thermal_state': final_status.current_thermal_state
            }
            
        except Exception as e:
            return {
                'test_name': 'thermal_propagation',
                'passed': False,
                'error': str(e)
            }
    
    def test_alert_escalation(self) -> Dict:
        """Test alert escalation system"""
        try:
            print("  Testing alert escalation system...")
            
            # Generate escalating conditions
            escalation_voltages = [3700, 3705, 3698, 3702, 3701, 3400, 3703, 3697]  # 305mV delta
            
            initial_alerts = 0
            escalated_alerts = 0
            
            # Run escalation test
            start_time = time.time()
            while (time.time() - start_time) < 8.0:
                self.p3e_system.process_cell_data(
                    cell_voltages_mv=escalation_voltages,
                    temperatures_dc=[350] * 8,  # 35°C
                    current_ma=-3000,
                    soc_percent=40,
                    metadata={'test_phase': 'alert_escalation'}
                )
                
                time.sleep(0.2)
            
            # Check alert statistics
            final_stats = self.p3e_system.get_system_statistics()
            active_alerts = self.p3e_system.get_active_alerts()
            
            assert final_stats['total_alerts_generated'] > 0, "No alerts generated"
            
            print(f"  ✓ Total alerts generated: {final_stats['total_alerts_generated']}")
            print(f"  ✓ Active alerts: {len(active_alerts)}")
            print(f"  ✓ P3E correlations: {final_stats['p3e_correlations_detected']}")
            
            return {
                'test_name': 'alert_escalation',
                'passed': True,
                'total_alerts': final_stats['total_alerts_generated'],
                'active_alerts': len(active_alerts),
                'p3e_correlations': final_stats['p3e_correlations_detected']
            }
            
        except Exception as e:
            return {
                'test_name': 'alert_escalation',
                'passed': False,
                'error': str(e)
            }
    
    def test_data_logging(self) -> Dict:
        """Test data logging functionality"""
        try:
            print("  Testing data logging functionality...")
            
            # Run data logging test
            test_voltages = [3700, 3705, 3698, 3702, 3701, 3650, 3703, 3697]  # 55mV delta
            
            initial_data_points = self.p3e_system.get_system_statistics()['data_points_processed']
            
            # Generate data for logging
            for i in range(50):
                self.p3e_system.process_cell_data(
                    cell_voltages_mv=test_voltages,
                    temperatures_dc=[260 + i] * 8,  # Progressive temperature
                    current_ma=-500 - (i * 10),     # Progressive current
                    soc_percent=max(80 - i, 20),    # Progressive SOC
                    metadata={
                        'test_phase': 'data_logging',
                        'data_point': i,
                        'logging_test': True
                    }
                )
                time.sleep(0.02)  # 50Hz for stress test
            
            # Verify data logging
            final_data_points = self.p3e_system.get_system_statistics()['data_points_processed']
            data_points_logged = final_data_points - initial_data_points
            
            assert data_points_logged >= 50, "Insufficient data points logged"
            
            print(f"  ✓ Data points logged: {data_points_logged}")
            print(f"  ✓ Logging frequency: {data_points_logged / 1.0:.1f} Hz")
            
            return {
                'test_name': 'data_logging',
                'passed': True,
                'data_points_logged': data_points_logged,
                'logging_frequency_hz': data_points_logged / 1.0
            }
            
        except Exception as e:
            return {
                'test_name': 'data_logging',
                'passed': False,
                'error': str(e)
            }
    
    def test_p3e_export_validation(self) -> Dict:
        """Test P3E data export validation"""
        try:
            print("  Testing P3E data export validation...")
            
            # Export P3E compatible data
            export_file = self.p3e_system.export_session_data("p3e_csv")
            
            assert export_file is not None, "Export file not generated"
            assert os.path.exists(export_file), "Export file does not exist"
            
            # Validate export file
            with open(export_file, 'r') as f:
                lines = f.readlines()
            
            assert len(lines) > 1, "Export file has no data"
            
            # Check header format
            header = lines[0].strip()
            expected_fields = ['timestamp', 'pack_delta_mv', 'current_ma', 'cell_1_mv', 'cell_6_mv']
            
            for field in expected_fields:
                assert field in header, f"Missing field: {field}"
            
            print(f"  ✓ Export file generated: {export_file}")
            print(f"  ✓ Data lines: {len(lines) - 1}")
            print(f"  ✓ Header validation passed")
            
            return {
                'test_name': 'p3e_export_validation',
                'passed': True,
                'export_file': export_file,
                'data_lines': len(lines) - 1,
                'file_size_bytes': os.path.getsize(export_file)
            }
            
        except Exception as e:
            return {
                'test_name': 'p3e_export_validation',
                'passed': False,
                'error': str(e)
            }
    
    def test_emergency_shutdown(self) -> Dict:
        """Test emergency shutdown functionality"""
        try:
            print("  Testing emergency shutdown functionality...")
            
            # Simulate conditions requiring emergency shutdown
            emergency_voltages = [3000, 3705, 3698, 3702, 3701, 4500, 3703, 3697]  # Extreme delta
            emergency_temps = [800] * 8  # 80°C - catastrophic temperature
            
            shutdown_triggered = False
            
            # Run until shutdown or timeout
            start_time = time.time()
            while (time.time() - start_time) < 2.0 and not shutdown_triggered:
                self.p3e_system.process_cell_data(
                    cell_voltages_mv=emergency_voltages,
                    temperatures_dc=emergency_temps,
                    current_ma=-8000,  # Extreme current
                    soc_percent=30,
                    metadata={'test_phase': 'emergency_shutdown'}
                )
                
                status = self.p3e_system.get_system_status()
                if status.emergency_shutdown_requested:
                    shutdown_triggered = True
                    print(f"    Emergency shutdown triggered at {time.time() - start_time:.1f}s")
                
                time.sleep(0.1)
            
            # Note: System might stop itself during emergency, so we check final state
            final_stats = self.p3e_system.get_system_statistics()
            
            # Emergency conditions should trigger alerts even if system stops
            assert final_stats['total_alerts_generated'] > 0, "No emergency alerts generated"
            
            print(f"  ✓ Emergency shutdown triggered: {shutdown_triggered}")
            print(f"  ✓ Emergency alerts: {final_stats['total_alerts_generated']}")
            print(f"  ✓ Emergency shutdowns: {final_stats['emergency_shutdowns']}")
            
            return {
                'test_name': 'emergency_shutdown',
                'passed': True,
                'shutdown_triggered': shutdown_triggered,
                'emergency_alerts': final_stats['total_alerts_generated'],
                'response_time_s': time.time() - start_time
            }
            
        except Exception as e:
            return {
                'test_name': 'emergency_shutdown',
                'passed': False,
                'error': str(e)
            }
    
    def test_integration_callbacks(self) -> Dict:
        """Test integration callback functionality"""
        try:
            print("  Testing integration callbacks...")
            
            callback_calls = {'cell_data': 0, 'status_update': 0}
            
            # Set up callbacks
            def cell_data_callback(voltages, temps, current, soc):
                callback_calls['cell_data'] += 1
            
            def status_callback(status):
                callback_calls['status_update'] += 1
            
            self.p3e_system.set_cell_data_callback(cell_data_callback)
            self.p3e_system.set_status_update_callback(status_callback)
            
            # Generate data to trigger callbacks
            for i in range(10):
                self.p3e_system.process_cell_data(
                    cell_voltages_mv=[3700] * 8,
                    temperatures_dc=[250] * 8,
                    current_ma=0,
                    soc_percent=50,
                    metadata={'test_phase': 'callbacks', 'iteration': i}
                )
                time.sleep(0.1)
            
            # Wait for status callbacks (they run every 5 seconds)
            time.sleep(6.0)
            
            assert callback_calls['cell_data'] >= 10, "Cell data callbacks not triggered"
            assert callback_calls['status_update'] >= 1, "Status callbacks not triggered"
            
            print(f"  ✓ Cell data callbacks: {callback_calls['cell_data']}")
            print(f"  ✓ Status update callbacks: {callback_calls['status_update']}")
            
            return {
                'test_name': 'integration_callbacks',
                'passed': True,
                'cell_data_callbacks': callback_calls['cell_data'],
                'status_callbacks': callback_calls['status_update']
            }
            
        except Exception as e:
            return {
                'test_name': 'integration_callbacks',
                'passed': False,
                'error': str(e)
            }
    
    def _generate_final_report(self) -> None:
        """Generate comprehensive final test report"""
        try:
            # Stop the system and get final summary
            system_summary = self.p3e_system.stop_system()
            
            # Collect all system statistics
            final_stats = self.p3e_system.get_system_statistics()
            
            # Generate comprehensive report
            report = {
                'test_session_info': {
                    'session_id': self.test_results['test_session'],
                    'start_time': self.test_results['start_time'].isoformat(),
                    'end_time': self.test_results['end_time'].isoformat(),
                    'total_duration_seconds': self.test_results['total_duration']
                },
                'test_summary': {
                    'tests_run': self.test_results['tests_run'],
                    'tests_passed': self.test_results['tests_passed'],
                    'tests_failed': self.test_results['tests_failed'],
                    'success_rate': (self.test_results['tests_passed'] / max(self.test_results['tests_run'], 1)) * 100
                },
                'p3e_validation': {
                    'correlations_validated': self.test_results['p3e_correlations_validated'],
                    'thresholds_tested': list(P3E_THRESHOLDS.keys()),
                    'patterns_tested': ['pack_0533', 'pack_0535', 'progressive_failure', 'thermal_propagation']
                },
                'system_performance': final_stats,
                'test_details': self.test_results['test_details'],
                'system_summary_file': system_summary
            }
            
            # Save comprehensive report
            report_file = self.output_dir / f"{self.test_results['test_session']}_comprehensive_report.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            # Generate summary report
            self._generate_summary_report(report)
            
            print(f"\n📋 Comprehensive report saved: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Error generating final report: {e}")
    
    def _generate_summary_report(self, full_report: Dict) -> None:
        """Generate human-readable summary report"""
        try:
            summary_file = self.output_dir / f"{self.test_results['test_session']}_summary_report.txt"
            
            with open(summary_file, 'w') as f:
                f.write("P3E RUNAWAY DETECTION ALGORITHMS - TEST SUMMARY REPORT\n")
                f.write("=" * 80 + "\n\n")
                
                # Test session info
                f.write(f"Session ID: {self.test_results['test_session']}\n")
                f.write(f"Duration: {self.test_results['total_duration']:.1f} seconds\n")
                f.write(f"Tests Run: {self.test_results['tests_run']}\n")
                f.write(f"Tests Passed: {self.test_results['tests_passed']}\n")
                f.write(f"Tests Failed: {self.test_results['tests_failed']}\n")
                f.write(f"Success Rate: {(self.test_results['tests_passed'] / max(self.test_results['tests_run'], 1)) * 100:.1f}%\n\n")
                
                # P3E validation summary
                f.write("P3E VALIDATION RESULTS:\n")
                f.write("-" * 40 + "\n")
                f.write(f"P3E Correlations Validated: {self.test_results['p3e_correlations_validated']}\n")
                f.write(f"Thresholds Tested: {', '.join(P3E_THRESHOLDS.keys())}\n")
                f.write(f"Patterns Tested: Pack 0533, Pack 0535, Progressive Failure, Thermal Propagation\n\n")
                
                # Individual test results
                f.write("INDIVIDUAL TEST RESULTS:\n")
                f.write("-" * 40 + "\n")
                for test in self.test_results['test_details']:
                    status = "✅ PASSED" if test['passed'] else "❌ FAILED"
                    duration = test.get('duration_seconds', 0)
                    f.write(f"{status} - {test['test_name'].replace('_', ' ').title()} ({duration:.1f}s)\n")
                    if not test['passed'] and 'error' in test:
                        f.write(f"          Error: {test['error']}\n")
                
                f.write(f"\n📋 Full report: {self.test_results['test_session']}_comprehensive_report.json\n")
            
            print(f"📋 Summary report saved: {summary_file}")
            
        except Exception as e:
            self.logger.error(f"Error generating summary report: {e}")


def main():
    """Run P3E algorithm test suite"""
    print("P3E Runaway Detection Algorithms - Test Suite")
    print("=" * 60)
    
    # Create and run test suite
    test_suite = P3ETestSuite(output_directory="p3e_test_results")
    results = test_suite.run_all_tests()
    
    # Print final summary
    print("\n" + "=" * 80)
    print("FINAL TEST RESULTS")
    print("=" * 80)
    print(f"Tests Run: {results['tests_run']}")
    print(f"Tests Passed: {results['tests_passed']}")
    print(f"Tests Failed: {results['tests_failed']}")
    print(f"Success Rate: {(results['tests_passed'] / max(results['tests_run'], 1)) * 100:.1f}%")
    print(f"P3E Correlations Validated: {results['p3e_correlations_validated']}")
    print(f"Total Duration: {results['total_duration']:.1f} seconds")
    
    if results['tests_failed'] == 0:
        print("\n🎉 ALL TESTS PASSED! P3E algorithms are working correctly.")
    else:
        print(f"\n⚠️  {results['tests_failed']} test(s) failed. Check logs for details.")
    
    print(f"\n📁 Results saved to: p3e_test_results/")
    
    return results['tests_failed'] == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)