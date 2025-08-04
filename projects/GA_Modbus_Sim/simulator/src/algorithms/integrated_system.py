#!/usr/bin/env python3
"""
Integrated P3E Runaway Detection System

This module provides a unified interface to all P3E runaway detection algorithms,
integrating runaway detection, thermal propagation, alert management, and data
logging into a cohesive system that can be easily integrated with the existing
Modbus BMS simulator.

Key Features:
1. Unified system management and coordination
2. Real-time data processing and analysis
3. Automated response protocols based on P3E analysis
4. Comprehensive logging and validation
5. Integration with existing simulator infrastructure
6. P3E-validated thresholds and response protocols

Integration Points:
- Modbus server data feeds
- Register handler cell data
- Log manager integration
- Event notification system
- External monitoring APIs
"""

import sys
import os
import logging
import time
import json
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# Import logging system
try:
    from ..utils.log_manager import get_logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

# Import algorithm components
from .runaway_detection import RunawayDetector, RunawayThresholds, RunawayRiskLevel
from .thermal_propagation import ThermalPropagationSimulator, CoolingEffectiveness
from .alert_system import AlertManager, AlertConfiguration, AlertSeverity, AlertType
from .data_logger import DataLogger, LogLevel, DataFormat

# Import P3E constants
from . import P3E_THRESHOLDS, P3E_PATTERNS


@dataclass
class SystemConfiguration:
    """Configuration for the integrated P3E system"""
    # Detection settings
    runaway_thresholds: RunawayThresholds = field(default_factory=RunawayThresholds)
    thermal_cooling_effectiveness: CoolingEffectiveness = CoolingEffectiveness.MODERATE
    
    # Alert settings
    alert_config: AlertConfiguration = field(default_factory=AlertConfiguration)
    
    # Logging settings
    log_directory: str = "p3e_logs"
    log_level: LogLevel = LogLevel.STANDARD
    log_formats: List[DataFormat] = field(default_factory=lambda: [DataFormat.CSV, DataFormat.JSON])
    sample_rate_hz: float = 1.0
    
    # System settings
    auto_start_on_init: bool = True
    enable_emergency_shutdown: bool = True
    enable_p3e_simulations: bool = True
    integration_mode: str = "standalone"  # "standalone" or "modbus_integrated"
    
    # P3E specific settings
    enhanced_cell6_monitoring: bool = True
    pack_0533_simulation_enabled: bool = True
    pack_0535_simulation_enabled: bool = True


@dataclass
class SystemStatus:
    """Current system status"""
    system_active: bool = False
    detection_active: bool = False
    thermal_simulation_active: bool = False
    alert_processing_active: bool = False
    data_logging_active: bool = False
    current_risk_level: str = "normal"
    current_thermal_state: str = "normal"
    active_alerts: int = 0
    emergency_shutdown_requested: bool = False
    session_id: str = ""
    uptime_seconds: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)


class P3EIntegratedSystem:
    """
    Integrated P3E Runaway Detection System
    
    Provides a unified interface to all P3E detection algorithms with
    coordinated operation, automated responses, and comprehensive logging.
    """
    
    def __init__(self, config: Optional[SystemConfiguration] = None):
        """Initialize the integrated P3E system"""
        # Setup logging
        if LOGGING_AVAILABLE:
            self.logger = get_logger(__name__, 'p3e_integrated_system')
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
        
        self.config = config or SystemConfiguration()
        
        # System state
        self.system_active = False
        self.start_time = datetime.now()
        self.session_id = f"p3e_session_{int(time.time())}"
        
        # Initialize algorithm components
        self._initialize_components()
        
        # Integration callbacks
        self.cell_data_callback: Optional[Callable] = None
        self.emergency_shutdown_callback: Optional[Callable] = None
        self.status_update_callback: Optional[Callable] = None
        
        # System monitoring
        self._monitoring_thread = None
        self._system_status = SystemStatus(session_id=self.session_id)
        
        # Statistics
        self.stats = {
            'system_starts': 0,
            'emergency_shutdowns': 0,
            'total_detection_events': 0,
            'total_thermal_events': 0,
            'total_alerts_generated': 0,
            'p3e_correlations_detected': 0,
            'data_points_processed': 0,
            'average_processing_time_ms': 0.0
        }
        
        self.logger.info(f"P3E Integrated System initialized - Session: {self.session_id}")
        
        # Auto-start if configured
        if self.config.auto_start_on_init:
            self.start_system()
    
    def _initialize_components(self) -> None:
        """Initialize all algorithm components"""
        try:
            # Initialize runaway detector
            self.runaway_detector = RunawayDetector(
                cell_count=8,
                thresholds=self.config.runaway_thresholds
            )
            
            # Initialize thermal propagation simulator
            self.thermal_simulator = ThermalPropagationSimulator(
                cell_count=8,
                pack_layout="linear"
            )
            self.thermal_simulator.set_cooling_effectiveness(self.config.thermal_cooling_effectiveness)
            
            # Initialize alert manager
            self.alert_manager = AlertManager(self.config.alert_config)
            
            # Initialize data logger
            self.data_logger = DataLogger(
                log_directory=self.config.log_directory,
                log_level=self.config.log_level
            )
            
            # Set up cross-component integration
            self.data_logger.set_algorithm_references(
                runaway_detector=self.runaway_detector,
                thermal_simulator=self.thermal_simulator,
                alert_manager=self.alert_manager
            )
            
            self.logger.info("All algorithm components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
    
    def start_system(self) -> None:
        """Start the integrated P3E system"""
        if self.system_active:
            self.logger.warning("System is already active")
            return
        
        try:
            self.logger.info("Starting P3E Integrated System...")
            
            # Start individual components
            self.runaway_detector.start_monitoring()
            self.thermal_simulator.start_simulation(time_step=1.0)
            self.alert_manager.start_processing()
            self.data_logger.start_logging(
                sample_rate_hz=self.config.sample_rate_hz,
                formats=self.config.log_formats
            )
            
            # Start system monitoring
            self._start_system_monitoring()
            
            self.system_active = True
            self.stats['system_starts'] += 1
            
            # Update system status
            self._update_system_status()
            
            self.logger.info("P3E Integrated System started successfully")
            
            # Enable P3E simulations if configured
            if self.config.enable_p3e_simulations:
                self._enable_p3e_simulations()
            
        except Exception as e:
            self.logger.error(f"Failed to start system: {e}")
            self.stop_system()
            raise
    
    def stop_system(self) -> str:
        """Stop the integrated P3E system and return summary"""
        if not self.system_active:
            self.logger.warning("System is not active")
            return ""
        
        try:
            self.logger.info("Stopping P3E Integrated System...")
            
            # Stop individual components
            self.runaway_detector.stop_monitoring()
            self.thermal_simulator.stop_simulation()
            self.alert_manager.stop_processing()
            summary_file = self.data_logger.stop_logging()
            
            # Stop system monitoring
            self.system_active = False
            
            # Update final system status
            self._update_system_status()
            
            # Generate system summary
            system_summary = self._generate_system_summary()
            
            self.logger.info("P3E Integrated System stopped successfully")
            self.logger.info(f"Session summary: {summary_file}")
            
            return system_summary
            
        except Exception as e:
            self.logger.error(f"Error stopping system: {e}")
            return ""
    
    def process_cell_data(self, cell_voltages_mv: List[int], temperatures_dc: List[int],
                         current_ma: int, soc_percent: int, metadata: Dict[str, Any] = None) -> None:
        """Process new cell data through all detection algorithms"""
        if not self.system_active:
            return
        
        processing_start = time.time()
        
        try:
            # Update runaway detector
            for cell_id, voltage in enumerate(cell_voltages_mv, 1):
                if cell_id <= len(temperatures_dc):
                    temp = temperatures_dc[cell_id - 1]
                else:
                    temp = 250  # Default 25.0°C
                
                self.runaway_detector.update_cell_data(
                    cell_id=cell_id,
                    voltage_mv=voltage,
                    temperature_dc=temp,
                    current_ma=current_ma,
                    soc_percent=soc_percent
                )
            
            # Update thermal simulator
            for cell_id, voltage in enumerate(cell_voltages_mv, 1):
                if cell_id <= len(temperatures_dc):
                    temp_c = temperatures_dc[cell_id - 1] / 10.0
                    
                    # Calculate heat generation based on cell conditions
                    heat_generation = self._calculate_heat_generation(voltage, current_ma, temp_c)
                    
                    self.thermal_simulator.set_cell_temperature(cell_id, temp_c, heat_generation)
            
            # Log data point
            self.data_logger.log_data_point(
                cell_voltages_mv=cell_voltages_mv,
                temperatures_dc=temperatures_dc,
                current_ma=current_ma,
                soc_percent=soc_percent,
                metadata=metadata
            )
            
            # Check for alerts
            self._process_alerts()
            
            # Update statistics
            processing_time = (time.time() - processing_start) * 1000  # ms
            self.stats['data_points_processed'] += 1
            self.stats['average_processing_time_ms'] = (
                (self.stats['average_processing_time_ms'] * (self.stats['data_points_processed'] - 1) + 
                 processing_time) / self.stats['data_points_processed']
            )
            
            # Update system status
            self._update_system_status()
            
            # Enhanced Cell #6 monitoring (P3E correlation)
            if self.config.enhanced_cell6_monitoring and len(cell_voltages_mv) >= 6:
                self._enhanced_cell6_monitoring(cell_voltages_mv[5], temperatures_dc[5] if len(temperatures_dc) >= 6 else 250)
            
            # Call integration callback if set
            if self.cell_data_callback:
                self.cell_data_callback(cell_voltages_mv, temperatures_dc, current_ma, soc_percent)
            
        except Exception as e:
            self.logger.error(f"Error processing cell data: {e}")
    
    def _calculate_heat_generation(self, voltage_mv: int, current_ma: int, temperature_c: float) -> float:
        """Calculate heat generation for thermal simulation"""
        # Simple heat generation model based on I²R losses and temperature
        base_resistance = 0.001  # 1mΩ base resistance
        
        # Resistance increases with temperature
        temp_coefficient = 0.004  # 0.4%/°C
        resistance = base_resistance * (1 + temp_coefficient * (temperature_c - 25.0))
        
        # I²R losses
        current_a = current_ma / 1000.0
        heat_watts = (current_a ** 2) * resistance
        
        # Additional heat from voltage stress
        if voltage_mv > 4000:  # Overvoltage stress
            overvoltage_factor = (voltage_mv - 4000) / 1000.0
            heat_watts += overvoltage_factor * 0.5
        
        return max(0.0, heat_watts)
    
    def _process_alerts(self) -> None:
        """Process alerts from all detection algorithms"""
        try:
            # Check runaway detector alerts
            runaway_alert = self.runaway_detector.get_next_alert(timeout=0.1)
            if runaway_alert:
                self._handle_runaway_alert(runaway_alert)
            
            # Check thermal simulator alerts (if available)
            # Note: ThermalPropagationSimulator doesn't have get_next_alert method
            # We check status instead
            
            # Check for emergency shutdown requests
            if (self.runaway_detector.shutdown_requested and 
                self.config.enable_emergency_shutdown):
                self._trigger_emergency_shutdown("Runaway detector requested shutdown")
            
        except Exception as e:
            self.logger.error(f"Error processing alerts: {e}")
    
    def _handle_runaway_alert(self, runaway_event) -> None:
        """Handle runaway detection alert"""
        try:
            # Map runaway risk to alert severity
            severity_mapping = {
                RunawayRiskLevel.NORMAL: AlertSeverity.INFO,
                RunawayRiskLevel.EARLY_WARNING: AlertSeverity.WARNING,
                RunawayRiskLevel.HIGH_RISK: AlertSeverity.HIGH,
                RunawayRiskLevel.CRITICAL: AlertSeverity.CRITICAL,
                RunawayRiskLevel.EMERGENCY: AlertSeverity.EMERGENCY,
                RunawayRiskLevel.CATASTROPHIC: AlertSeverity.CATASTROPHIC
            }
            
            severity = severity_mapping.get(runaway_event.risk_level, AlertSeverity.WARNING)
            
            # Generate alert
            alert_id = self.alert_manager.generate_alert(
                alert_type=AlertType.VOLTAGE_THRESHOLD,
                title=f"P3E Runaway Detection: {runaway_event.risk_level.value.upper()}",
                message=f"Delta: {runaway_event.delta_mv}mV, Cells: {runaway_event.affected_cells}, "
                       f"Action: {runaway_event.recommended_action}",
                severity=severity,
                source_data={
                    'pack_delta_mv': runaway_event.delta_mv,
                    'max_voltage_mv': runaway_event.max_cell_voltage,
                    'min_voltage_mv': runaway_event.min_cell_voltage,
                    'current_ma': runaway_event.current_ma,
                    'soc_percent': runaway_event.soc_percent,
                    'affected_cells': runaway_event.affected_cells,
                    'escalation_time_s': runaway_event.escalation_time_seconds
                },
                p3e_correlation=runaway_event.p3e_correlation,
                metadata={'event_id': runaway_event.event_id, 'event_type': runaway_event.event_type.value}
            )
            
            self.stats['total_detection_events'] += 1
            self.stats['total_alerts_generated'] += 1
            
            if runaway_event.p3e_correlation:
                self.stats['p3e_correlations_detected'] += 1
            
            self.logger.info(f"Runaway alert generated: {alert_id}")
            
        except Exception as e:
            self.logger.error(f"Error handling runaway alert: {e}")
    
    def _enhanced_cell6_monitoring(self, cell6_voltage_mv: int, cell6_temp_dc: int) -> None:
        """Enhanced monitoring for Cell #6 based on P3E correlation"""
        cell6_temp_c = cell6_temp_dc / 10.0
        
        # Check for P3E Pack 0535 pattern (overvoltage)
        if cell6_voltage_mv > 4200:
            self.alert_manager.generate_alert(
                alert_type=AlertType.P3E_CORRELATION,
                title="Cell #6 Overvoltage - Pack 0535 Pattern",
                message=f"Cell #6 voltage {cell6_voltage_mv}mV exceeds 4200mV - matches Pack 0535 runaway pattern",
                severity=AlertSeverity.EMERGENCY,
                source_data={
                    'cell_6_voltage_mv': cell6_voltage_mv,
                    'cell_6_temperature_c': cell6_temp_c,
                    'p3e_pack_correlation': '0535'
                },
                p3e_correlation="Pack 0535: Cell #6 overvoltage with thermal runaway correlation"
            )
        
        # Check for P3E Pack 0533 pattern (undervoltage)
        elif cell6_voltage_mv < 2500:
            self.alert_manager.generate_alert(
                alert_type=AlertType.P3E_CORRELATION,
                title="Cell #6 Undervoltage - Pack 0533 Pattern",
                message=f"Cell #6 voltage {cell6_voltage_mv}mV below 2500mV - matches Pack 0533 failure pattern",
                severity=AlertSeverity.CRITICAL,
                source_data={
                    'cell_6_voltage_mv': cell6_voltage_mv,
                    'cell_6_temperature_c': cell6_temp_c,
                    'p3e_pack_correlation': '0533'
                },
                p3e_correlation="Pack 0533: Cell #6 undervoltage during discharge runaway"
            )
        
        # Enhanced thermal monitoring
        if cell6_temp_c > 45.0:
            self.alert_manager.generate_alert(
                alert_type=AlertType.THERMAL_PROPAGATION,
                title="Cell #6 Thermal Alert - P3E High-Risk Cell",
                message=f"Cell #6 temperature {cell6_temp_c:.1f}°C - enhanced monitoring due to P3E correlation",
                severity=AlertSeverity.HIGH,
                source_data={
                    'cell_6_voltage_mv': cell6_voltage_mv,
                    'cell_6_temperature_c': cell6_temp_c,
                    'p3e_enhanced_monitoring': True
                },
                p3e_correlation="Cell #6 thermal monitoring - high correlation with P3E failures"
            )
    
    def _trigger_emergency_shutdown(self, reason: str) -> None:
        """Trigger emergency shutdown"""
        if not self.config.enable_emergency_shutdown:
            self.logger.warning(f"Emergency shutdown disabled - would shutdown for: {reason}")
            return
        
        try:
            self.logger.critical(f"EMERGENCY SHUTDOWN TRIGGERED: {reason}")
            
            # Generate emergency alert
            self.alert_manager.generate_alert(
                alert_type=AlertType.EMERGENCY_SHUTDOWN,
                title="EMERGENCY SHUTDOWN ACTIVATED",
                message=f"Emergency shutdown triggered: {reason}",
                severity=AlertSeverity.CATASTROPHIC,
                source_data={'shutdown_reason': reason, 'timestamp': datetime.now().isoformat()},
                p3e_correlation="P3E Protocol: Emergency shutdown for catastrophic conditions"
            )
            
            self.stats['emergency_shutdowns'] += 1
            self._system_status.emergency_shutdown_requested = True
            
            # Call emergency shutdown callback if set
            if self.emergency_shutdown_callback:
                self.emergency_shutdown_callback(reason)
            
            # Stop system
            self.stop_system()
            
        except Exception as e:
            self.logger.error(f"Error in emergency shutdown: {e}")
    
    def _enable_p3e_simulations(self) -> None:
        """Enable P3E simulation patterns"""
        try:
            if self.config.pack_0535_simulation_enabled:
                # Schedule Pack 0535 simulation after 30 seconds
                def trigger_pack_0535():
                    time.sleep(30)
                    if self.system_active:
                        self.thermal_simulator.simulate_p3e_pack_0535_event()
                        self.logger.info("Pack 0535 simulation triggered")
                
                pack_0535_thread = threading.Thread(target=trigger_pack_0535)
                pack_0535_thread.daemon = True
                pack_0535_thread.start()
            
            if self.config.pack_0533_simulation_enabled:
                # Schedule Pack 0533 simulation after 60 seconds
                def trigger_pack_0533():
                    time.sleep(60)
                    if self.system_active:
                        self.thermal_simulator.simulate_p3e_pack_0533_thermal_correlation()
                        self.logger.info("Pack 0533 simulation triggered")
                
                pack_0533_thread = threading.Thread(target=trigger_pack_0533)
                pack_0533_thread.daemon = True
                pack_0533_thread.start()
            
            self.logger.info("P3E simulation patterns enabled")
            
        except Exception as e:
            self.logger.error(f"Error enabling P3E simulations: {e}")
    
    def _start_system_monitoring(self) -> None:
        """Start system monitoring thread"""
        def monitor_system():
            while self.system_active:
                try:
                    self._update_system_status()
                    
                    # Call status update callback if set
                    if self.status_update_callback:
                        self.status_update_callback(self._system_status)
                    
                    time.sleep(5.0)  # Update every 5 seconds
                    
                except Exception as e:
                    self.logger.error(f"Error in system monitoring: {e}")
                    time.sleep(10.0)
        
        self._monitoring_thread = threading.Thread(target=monitor_system)
        self._monitoring_thread.daemon = True
        self._monitoring_thread.start()
    
    def _update_system_status(self) -> None:
        """Update current system status"""
        try:
            self._system_status.system_active = self.system_active
            self._system_status.detection_active = self.runaway_detector.monitoring_active if self.runaway_detector else False
            self._system_status.thermal_simulation_active = self.thermal_simulator.simulation_active if self.thermal_simulator else False
            self._system_status.alert_processing_active = self.alert_manager.processing_active if self.alert_manager else False
            self._system_status.data_logging_active = self.data_logger.logging_active if self.data_logger else False
            
            # Get current risk levels
            if self.runaway_detector:
                detector_status = self.runaway_detector.get_current_status()
                self._system_status.current_risk_level = detector_status.get('current_risk_level', 'normal')
            
            if self.thermal_simulator:
                thermal_status = self.thermal_simulator.get_propagation_status()
                max_temp = thermal_status['current_status']['max_temperature_c']
                if max_temp >= 60.0:
                    self._system_status.current_thermal_state = 'runaway'
                elif max_temp >= 45.0:
                    self._system_status.current_thermal_state = 'critical'
                elif max_temp >= 35.0:
                    self._system_status.current_thermal_state = 'elevated'
                else:
                    self._system_status.current_thermal_state = 'normal'
            
            # Get active alerts count
            if self.alert_manager:
                alert_stats = self.alert_manager.get_alert_statistics()
                self._system_status.active_alerts = alert_stats.get('active_alerts', 0)
            
            # Calculate uptime
            self._system_status.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            self._system_status.last_update = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error updating system status: {e}")
    
    def _generate_system_summary(self) -> str:
        """Generate comprehensive system summary"""
        try:
            summary_file = os.path.join(self.config.log_directory, f"{self.session_id}_system_summary.json")
            
            # Collect all component statistics
            component_stats = {}
            
            if self.runaway_detector:
                component_stats['runaway_detector'] = self.runaway_detector.get_current_status()
            
            if self.thermal_simulator:
                component_stats['thermal_simulator'] = self.thermal_simulator.get_propagation_status()
            
            if self.alert_manager:
                component_stats['alert_manager'] = self.alert_manager.get_alert_statistics()
            
            if self.data_logger:
                component_stats['data_logger'] = self.data_logger.get_session_statistics()
            
            # Generate comprehensive summary
            summary = {
                'session_info': {
                    'session_id': self.session_id,
                    'start_time': self.start_time.isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'duration_seconds': (datetime.now() - self.start_time).total_seconds(),
                    'configuration': {
                        'sample_rate_hz': self.config.sample_rate_hz,
                        'log_level': self.config.log_level.name,
                        'integration_mode': self.config.integration_mode,
                        'emergency_shutdown_enabled': self.config.enable_emergency_shutdown,
                        'p3e_simulations_enabled': self.config.enable_p3e_simulations
                    }
                },
                'system_statistics': self.stats.copy(),
                'component_statistics': component_stats,
                'final_status': {
                    'current_risk_level': self._system_status.current_risk_level,
                    'current_thermal_state': self._system_status.current_thermal_state,
                    'active_alerts': self._system_status.active_alerts,
                    'emergency_shutdown_requested': self._system_status.emergency_shutdown_requested
                },
                'p3e_analysis': {
                    'correlations_detected': self.stats['p3e_correlations_detected'],
                    'patterns_available': list(P3E_PATTERNS.keys()),
                    'thresholds_used': P3E_THRESHOLDS.copy()
                }
            }
            
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            self.logger.info(f"System summary generated: {summary_file}")
            return summary_file
            
        except Exception as e:
            self.logger.error(f"Error generating system summary: {e}")
            return ""
    
    # Public interface methods
    
    def get_system_status(self) -> SystemStatus:
        """Get current system status"""
        self._update_system_status()
        return self._system_status
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        return self.stats.copy()
    
    def set_cell_data_callback(self, callback: Callable) -> None:
        """Set callback for cell data processing"""
        self.cell_data_callback = callback
    
    def set_emergency_shutdown_callback(self, callback: Callable) -> None:
        """Set callback for emergency shutdown"""
        self.emergency_shutdown_callback = callback
    
    def set_status_update_callback(self, callback: Callable) -> None:
        """Set callback for status updates"""
        self.status_update_callback = callback
    
    def simulate_p3e_scenario(self, scenario: str) -> bool:
        """Manually trigger P3E scenario simulation"""
        try:
            if scenario == "pack_0535" and self.thermal_simulator:
                self.thermal_simulator.simulate_p3e_pack_0535_event()
                self.logger.info("Pack 0535 scenario simulation triggered")
                return True
            elif scenario == "pack_0533" and self.thermal_simulator:
                self.thermal_simulator.simulate_p3e_pack_0533_thermal_correlation()
                self.logger.info("Pack 0533 scenario simulation triggered")
                return True
            else:
                self.logger.warning(f"Unknown or unavailable scenario: {scenario}")
                return False
        except Exception as e:
            self.logger.error(f"Error simulating P3E scenario {scenario}: {e}")
            return False
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        if self.alert_manager:
            return self.alert_manager.acknowledge_alert(alert_id, "integrated_system")
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        if self.alert_manager:
            return self.alert_manager.resolve_alert(alert_id, "integrated_system")
        return False
    
    def get_active_alerts(self) -> List[Any]:
        """Get all active alerts"""
        if self.alert_manager:
            return self.alert_manager.get_active_alerts()
        return []
    
    def export_session_data(self, format_type: str = "p3e_csv") -> Optional[str]:
        """Export session data in specified format"""
        if self.data_logger:
            if format_type == "p3e_csv":
                return self.data_logger.export_p3e_compatible_data()
        return None


def main():
    """Test function for integrated P3E system"""
    # Setup logging
    if LOGGING_AVAILABLE:
        from ..utils.log_manager import setup_logging
        setup_logging(level='INFO')
        logger = get_logger(__name__, 'integrated_system')
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
    
    print("=== P3E Integrated System Test ===")
    
    # Create system configuration
    config = SystemConfiguration(
        sample_rate_hz=2.0,
        log_level=LogLevel.DETAILED,
        enable_p3e_simulations=True,
        integration_mode="standalone"
    )
    
    # Create integrated system
    p3e_system = P3EIntegratedSystem(config)
    
    print(f"System initialized - Session: {p3e_system.session_id}")
    
    # Test scenarios based on P3E analysis
    test_scenarios = [
        {
            'name': 'Normal Operation',
            'duration': 5.0,
            'cell_voltages': [3700, 3705, 3698, 3702, 3701, 3699, 3703, 3697],
            'temperatures': [250, 252, 251, 249, 253, 250, 251, 252],
            'current': 0,
            'soc': 50
        },
        {
            'name': 'P3E Early Warning Pattern',
            'duration': 3.0,
            'cell_voltages': [3700, 3705, 3698, 3702, 3701, 3580, 3703, 3697],  # 125mV delta
            'temperatures': [280, 285, 283, 281, 287, 280, 284, 282],
            'current': -1000,
            'soc': 65
        },
        {
            'name': 'P3E Pack 0533 Pattern',
            'duration': 4.0,
            'cell_voltages': [3179, 3192, 3206, 3195, 3198, 2853, 3201, 3189],  # 353mV delta
            'temperatures': [305, 305, 305, 305, 305, 305, 305, 305],
            'current': -5300,
            'soc': 44
        },
        {
            'name': 'P3E Critical Level',
            'duration': 2.0,
            'cell_voltages': [3176, 3192, 3206, 3195, 3198, 2674, 3201, 3189],  # 532mV delta
            'temperatures': [350, 355, 353, 351, 357, 350, 354, 352],
            'current': -5300,
            'soc': 43
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n--- Test {i+1}: {scenario['name']} ---")
        
        start_time = time.time()
        while (time.time() - start_time) < scenario['duration']:
            # Process cell data
            p3e_system.process_cell_data(
                cell_voltages_mv=scenario['cell_voltages'],
                temperatures_dc=scenario['temperatures'],
                current_ma=scenario['current'],
                soc_percent=scenario['soc'],
                metadata={'scenario': scenario['name'], 'test_phase': i+1}
            )
            
            time.sleep(0.4)  # ~2.5Hz data rate
        
        # Show current status
        status = p3e_system.get_system_status()
        print(f"Risk Level: {status.current_risk_level}")
        print(f"Thermal State: {status.current_thermal_state}")
        print(f"Active Alerts: {status.active_alerts}")
        
        time.sleep(1.0)
    
    # Test P3E scenario simulation
    print("\n--- Testing P3E Scenario Simulation ---")
    p3e_system.simulate_p3e_scenario("pack_0535")
    time.sleep(2.0)
    
    # Show final statistics
    print("\n=== Final System Statistics ===")
    stats = p3e_system.get_system_statistics()
    
    print(f"Data Points Processed: {stats['data_points_processed']}")
    print(f"Detection Events: {stats['total_detection_events']}")
    print(f"Thermal Events: {stats['total_thermal_events']}")
    print(f"Alerts Generated: {stats['total_alerts_generated']}")
    print(f"P3E Correlations: {stats['p3e_correlations_detected']}")
    print(f"Average Processing Time: {stats['average_processing_time_ms']:.2f}ms")
    
    # Stop system and get summary
    print("\n=== Stopping System ===")
    summary_file = p3e_system.stop_system()
    print(f"System summary: {summary_file}")
    
    # Export P3E data
    p3e_export = p3e_system.export_session_data("p3e_csv")
    if p3e_export:
        print(f"P3E export: {p3e_export}")


if __name__ == "__main__":
    main()