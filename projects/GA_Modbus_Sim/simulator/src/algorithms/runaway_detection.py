#!/usr/bin/env python3
"""
Runaway Detection Algorithms - P3E Analysis Implementation

This module implements comprehensive thermal runaway detection and simulation
algorithms based on actual P3E battery pack analysis data. The algorithms
detect voltage threshold violations, temperature gradients, current anomalies,
and progressive cell failure patterns.

Based on P3E analysis findings:
- Early Warning: 100mV delta threshold
- High Risk: 300mV delta threshold (30-second response window)
- Critical: 500mV delta threshold (<10-second response window)
- Emergency: >700mV delta threshold (immediate shutdown)

Key findings from P3E data:
- Pack 0535: 1048mV peak delta, 4411mV overvoltage, 65°C thermal
- Pack 0533: 702mV peak delta during -5.3A discharge, 57-second escalation
- Cell #6 shows highest failure correlation across multiple packs
- BMS bypass creates catastrophic runaway conditions (1.49x more severe)
"""

import sys
import os
import logging
import time
import math
import threading
import json
from typing import Dict, List, Optional, Any, Tuple, NamedTuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import queue

# Import logging system
try:
    from ..utils.log_manager import get_logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False


class RunawayRiskLevel(Enum):
    """Risk levels for thermal runaway detection"""
    NORMAL = "normal"           # 8-15mV deltas
    EARLY_WARNING = "warning"   # 100mV threshold
    HIGH_RISK = "high"         # 300mV threshold
    CRITICAL = "critical"      # 500mV threshold
    EMERGENCY = "emergency"    # >700mV threshold
    CATASTROPHIC = "catastrophic"  # >1000mV (Pack 0535 level)


class RunawayEventType(Enum):
    """Types of runaway events detected"""
    VOLTAGE_DELTA = "voltage_delta"
    TEMPERATURE_GRADIENT = "temperature_gradient"
    CURRENT_ANOMALY = "current_anomaly"
    PROGRESSIVE_FAILURE = "progressive_failure"
    THERMAL_PROPAGATION = "thermal_propagation"
    BMS_PROTECTION_FAILURE = "bms_protection_failure"


@dataclass
class CellData:
    """Individual cell monitoring data"""
    cell_id: int
    voltage_mv: int
    temperature_dc: int  # 0.1°C units
    last_updated: datetime
    delta_history: List[int] = field(default_factory=list)
    temp_history: List[int] = field(default_factory=list)
    anomaly_count: int = 0
    risk_score: float = 0.0


@dataclass
class RunawayEvent:
    """Runaway detection event data"""
    event_id: str
    timestamp: datetime
    event_type: RunawayEventType
    risk_level: RunawayRiskLevel
    affected_cells: List[int]
    delta_mv: int
    max_cell_voltage: int
    min_cell_voltage: int
    temperature_c: float
    current_ma: int
    soc_percent: int
    escalation_time_seconds: float
    p3e_correlation: str
    recommended_action: str
    raw_data: Dict[str, Any]


@dataclass
class RunawayThresholds:
    """Configurable thresholds based on P3E analysis"""
    # Voltage delta thresholds (mV)
    early_warning_mv: int = 100    # 5-8x normal operation
    high_risk_mv: int = 300        # Pack 0533 escalation point
    critical_mv: int = 500         # All confirmed runaways exceed this
    emergency_mv: int = 700        # Pack 0533 peak before shutdown
    catastrophic_mv: int = 1000    # Pack 0535 level (1048mV)
    
    # Temperature thresholds (°C)
    temp_warning_c: float = 35.0   # Enhanced monitoring
    temp_high_c: float = 40.0      # Reduce current
    temp_critical_c: float = 45.0  # Emergency shutdown
    temp_emergency_c: float = 60.0 # Personnel evacuation
    
    # Current anomaly thresholds
    current_spike_threshold: float = 2.0  # 2x normal variation
    discharge_runaway_current: float = -5.3  # Pack 0533 runaway current
    
    # Time windows for response (seconds)
    warning_response_time: int = 60
    high_risk_response_time: int = 30    # Pack 0533: 30-second window
    critical_response_time: int = 10     # <10-second window
    emergency_response_time: int = 1     # BMS automatic shutdown
    
    # Historical analysis windows
    delta_history_window: int = 60       # 1 minute
    temp_gradient_window: int = 30       # 30 seconds
    escalation_detection_window: int = 300  # 5 minutes


class RunawayDetector:
    """
    Advanced thermal runaway detection system based on P3E analysis
    
    Implements multi-layer detection algorithms:
    1. Voltage threshold monitoring with P3E-validated thresholds
    2. Temperature gradient detection with thermal correlation
    3. Current anomaly detection for discharge runaway patterns
    4. Progressive cell failure simulation with Cell #6 priority monitoring
    5. Thermal runaway propagation modeling
    6. Real-time alert generation with escalation timelines
    """
    
    def __init__(self, cell_count: int = 8, thresholds: Optional[RunawayThresholds] = None):
        """Initialize the runaway detection system"""
        # Setup logging
        if LOGGING_AVAILABLE:
            self.logger = get_logger(__name__, 'runaway_detection')
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
        
        self.cell_count = cell_count
        self.thresholds = thresholds or RunawayThresholds()
        
        # Cell monitoring data
        self.cells: Dict[int, CellData] = {}
        for cell_id in range(1, cell_count + 1):
            self.cells[cell_id] = CellData(
                cell_id=cell_id,
                voltage_mv=3700,
                temperature_dc=250,  # 25.0°C
                last_updated=datetime.now()
            )
        
        # Detection state
        self.current_risk_level = RunawayRiskLevel.NORMAL
        self.active_events: List[RunawayEvent] = []
        self.event_history: List[RunawayEvent] = []
        self.monitoring_active = False
        self.shutdown_requested = False
        
        # Enhanced monitoring for Cell #6 (P3E correlation)
        self.high_risk_cells = [6]  # Based on P3E analysis
        
        # Event queue for real-time alerts
        self.alert_queue = queue.Queue()
        
        # Statistics
        self.stats = {
            'total_events': 0,
            'warning_events': 0,
            'critical_events': 0,
            'emergency_events': 0,
            'false_positives': 0,
            'detection_accuracy': 0.0,
            'average_response_time': 0.0,
            'p3e_correlations': 0
        }
        
        self.logger.info(f"RunawayDetector initialized for {cell_count} cells with P3E thresholds")
        self.logger.info(f"High-risk cell monitoring: {self.high_risk_cells}")
    
    def update_cell_data(self, cell_id: int, voltage_mv: int, temperature_dc: int, 
                        current_ma: int = 0, soc_percent: int = 50) -> None:
        """Update cell data and trigger detection analysis"""
        if cell_id not in self.cells:
            self.logger.warning(f"Unknown cell ID: {cell_id}")
            return
        
        cell = self.cells[cell_id]
        now = datetime.now()
        
        # Update cell data
        cell.voltage_mv = voltage_mv
        cell.temperature_dc = temperature_dc
        cell.last_updated = now
        
        # Update history with size limits
        if len(cell.delta_history) >= 100:
            cell.delta_history.pop(0)
        if len(cell.temp_history) >= 100:
            cell.temp_history.pop(0)
        
        # Calculate current pack delta
        voltages = [c.voltage_mv for c in self.cells.values()]
        pack_delta = max(voltages) - min(voltages)
        cell.delta_history.append(pack_delta)
        cell.temp_history.append(temperature_dc)
        
        # Store current operational data for event correlation
        self._current_data = {
            'current_ma': current_ma,
            'soc_percent': soc_percent,
            'pack_delta': pack_delta,
            'timestamp': now
        }
        
        # Trigger detection algorithms
        if self.monitoring_active:
            self._analyze_runaway_risk(cell_id)
    
    def start_monitoring(self) -> None:
        """Start continuous runaway monitoring"""
        self.monitoring_active = True
        self.shutdown_requested = False
        self.logger.info("Runaway monitoring started with P3E-validated thresholds")
        
        # Start background monitoring thread
        self._monitor_thread = threading.Thread(target=self._continuous_monitoring)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop runaway monitoring"""
        self.monitoring_active = False
        self.shutdown_requested = True
        self.logger.info("Runaway monitoring stopped")
    
    def _continuous_monitoring(self) -> None:
        """Background thread for continuous monitoring"""
        while self.monitoring_active and not self.shutdown_requested:
            try:
                # Perform periodic checks
                self._check_temperature_gradients()
                self._check_progressive_failure_patterns()
                self._update_risk_scores()
                self._cleanup_old_events()
                
                # Sleep for monitoring interval
                time.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {e}")
                time.sleep(5.0)  # Longer sleep on error
    
    def _analyze_runaway_risk(self, triggered_cell_id: int) -> None:
        """Comprehensive runaway risk analysis"""
        try:
            # Get current pack state
            voltages = [cell.voltage_mv for cell in self.cells.values()]
            temperatures = [cell.temperature_dc / 10.0 for cell in self.cells.values()]
            
            pack_delta = max(voltages) - min(voltages)
            max_voltage = max(voltages)
            min_voltage = min(voltages)
            max_temp = max(temperatures)
            avg_temp = sum(temperatures) / len(temperatures)
            
            current_ma = self._current_data.get('current_ma', 0)
            soc_percent = self._current_data.get('soc_percent', 50)
            
            # Determine risk level based on P3E thresholds
            previous_risk = self.current_risk_level
            new_risk_level = self._calculate_risk_level(pack_delta, max_temp, current_ma)
            
            # Check for risk escalation
            if new_risk_level.value != previous_risk.value:
                self.current_risk_level = new_risk_level
                self._handle_risk_escalation(previous_risk, new_risk_level, pack_delta, 
                                           max_voltage, min_voltage, max_temp, current_ma, soc_percent)
            
            # Specific detection algorithms
            self._detect_voltage_threshold_violation(pack_delta, max_voltage, min_voltage, current_ma, soc_percent)
            self._detect_current_anomalies(current_ma, soc_percent)
            
            # Enhanced monitoring for high-risk cells (Cell #6)
            for cell_id in self.high_risk_cells:
                if cell_id in self.cells:
                    self._enhanced_cell_monitoring(cell_id)
            
        except Exception as e:
            self.logger.error(f"Error in runaway risk analysis: {e}")
    
    def _calculate_risk_level(self, pack_delta: int, max_temp: float, current_ma: int) -> RunawayRiskLevel:
        """Calculate overall risk level based on P3E analysis thresholds"""
        # Voltage-based risk assessment
        if pack_delta >= self.thresholds.catastrophic_mv:
            return RunawayRiskLevel.CATASTROPHIC
        elif pack_delta >= self.thresholds.emergency_mv:
            return RunawayRiskLevel.EMERGENCY
        elif pack_delta >= self.thresholds.critical_mv:
            return RunawayRiskLevel.CRITICAL
        elif pack_delta >= self.thresholds.high_risk_mv:
            return RunawayRiskLevel.HIGH_RISK
        elif pack_delta >= self.thresholds.early_warning_mv:
            return RunawayRiskLevel.EARLY_WARNING
        
        # Temperature-based escalation
        if max_temp >= self.thresholds.temp_emergency_c:
            return RunawayRiskLevel.EMERGENCY
        elif max_temp >= self.thresholds.temp_critical_c:
            return RunawayRiskLevel.CRITICAL
        elif max_temp >= self.thresholds.temp_high_c:
            return RunawayRiskLevel.HIGH_RISK
        
        # Current-based risk (Pack 0533 pattern: -5.3A discharge)
        if abs(current_ma) > 5000 and current_ma < 0:  # High discharge current
            if pack_delta >= 50:  # Any elevated delta during high discharge
                return RunawayRiskLevel.HIGH_RISK
        
        return RunawayRiskLevel.NORMAL
    
    def _detect_voltage_threshold_violation(self, pack_delta: int, max_voltage: int, 
                                          min_voltage: int, current_ma: int, soc_percent: int) -> None:
        """Detect voltage threshold violations based on P3E analysis"""
        if pack_delta < self.thresholds.early_warning_mv:
            return  # No threshold violation
        
        # Determine affected cells
        affected_cells = []
        for cell_id, cell in self.cells.items():
            if (cell.voltage_mv == max_voltage and max_voltage > 4000) or \
               (cell.voltage_mv == min_voltage and min_voltage < 3000):
                affected_cells.append(cell_id)
        
        # Calculate escalation time
        escalation_time = self._calculate_escalation_time(pack_delta)
        
        # Determine P3E correlation
        p3e_correlation = self._get_p3e_correlation(pack_delta, affected_cells, current_ma)
        
        # Create runaway event
        event = RunawayEvent(
            event_id=f"VTV_{int(time.time())}_{pack_delta}",
            timestamp=datetime.now(),
            event_type=RunawayEventType.VOLTAGE_DELTA,
            risk_level=self.current_risk_level,
            affected_cells=affected_cells,
            delta_mv=pack_delta,
            max_cell_voltage=max_voltage,
            min_cell_voltage=min_voltage,
            temperature_c=max([cell.temperature_dc / 10.0 for cell in self.cells.values()]),
            current_ma=current_ma,
            soc_percent=soc_percent,
            escalation_time_seconds=escalation_time,
            p3e_correlation=p3e_correlation,
            recommended_action=self._get_recommended_action(self.current_risk_level),
            raw_data=self._current_data.copy()
        )
        
        self._process_runaway_event(event)
    
    def _detect_temperature_gradients(self) -> None:
        """Detect dangerous temperature gradients"""
        temperatures = [cell.temperature_dc / 10.0 for cell in self.cells.values()]
        temp_gradient = max(temperatures) - min(temperatures)
        max_temp = max(temperatures)
        
        # Check for rapid temperature rise (thermal runaway indicator)
        for cell_id, cell in self.cells.items():
            if len(cell.temp_history) >= 10:
                recent_temps = cell.temp_history[-10:]
                temp_rise_rate = (recent_temps[-1] - recent_temps[0]) / 10.0  # °C per second
                
                if temp_rise_rate > 1.0:  # >1°C/second rise
                    event = RunawayEvent(
                        event_id=f"TGD_{int(time.time())}_{cell_id}",
                        timestamp=datetime.now(),
                        event_type=RunawayEventType.TEMPERATURE_GRADIENT,
                        risk_level=RunawayRiskLevel.HIGH_RISK if temp_rise_rate > 2.0 else RunawayRiskLevel.EARLY_WARNING,
                        affected_cells=[cell_id],
                        delta_mv=max([c.voltage_mv for c in self.cells.values()]) - min([c.voltage_mv for c in self.cells.values()]),
                        max_cell_voltage=max([c.voltage_mv for c in self.cells.values()]),
                        min_cell_voltage=min([c.voltage_mv for c in self.cells.values()]),
                        temperature_c=max_temp,
                        current_ma=self._current_data.get('current_ma', 0),
                        soc_percent=self._current_data.get('soc_percent', 50),
                        escalation_time_seconds=10.0 / temp_rise_rate,  # Estimated time to critical
                        p3e_correlation=f"Thermal gradient {temp_rise_rate:.2f}°C/s detected on Cell #{cell_id}",
                        recommended_action="Activate cooling systems, reduce current",
                        raw_data={'temp_rise_rate': temp_rise_rate, 'temp_gradient': temp_gradient}
                    )
                    
                    self._process_runaway_event(event)
    
    def _detect_current_anomalies(self, current_ma: int, soc_percent: int) -> None:
        """Detect current anomalies that indicate runaway conditions"""
        # Pack 0533 pattern: -5.3A sustained discharge creates runaway
        if current_ma <= -5000:  # High discharge current
            pack_delta = max([c.voltage_mv for c in self.cells.values()]) - min([c.voltage_mv for c in self.cells.values()])
            
            if pack_delta >= 50:  # Any elevated delta during high discharge
                event = RunawayEvent(
                    event_id=f"CAD_{int(time.time())}_{abs(current_ma)}",
                    timestamp=datetime.now(),
                    event_type=RunawayEventType.CURRENT_ANOMALY,
                    risk_level=RunawayRiskLevel.HIGH_RISK,
                    affected_cells=list(range(1, self.cell_count + 1)),
                    delta_mv=pack_delta,
                    max_cell_voltage=max([c.voltage_mv for c in self.cells.values()]),
                    min_cell_voltage=min([c.voltage_mv for c in self.cells.values()]),
                    temperature_c=max([c.temperature_dc / 10.0 for c in self.cells.values()]),
                    current_ma=current_ma,
                    soc_percent=soc_percent,
                    escalation_time_seconds=60.0,  # Pack 0533: ~60 seconds to critical
                    p3e_correlation="Pack 0533 pattern: Sustained high discharge creates runaway conditions",
                    recommended_action="Reduce discharge current to <2A immediately",
                    raw_data={'discharge_pattern': 'pack_0533_correlation'}
                )
                
                self._process_runaway_event(event)
    
    def _check_progressive_failure_patterns(self) -> None:
        """Check for progressive cell failure patterns"""
        # Analyze cells for degradation patterns
        for cell_id, cell in self.cells.items():
            if len(cell.delta_history) >= 30:  # Need sufficient history
                recent_deltas = cell.delta_history[-30:]
                trend = self._calculate_trend(recent_deltas)
                
                # Escalating delta trend indicates progressive failure
                if trend > 2.0:  # >2mV increase per reading
                    risk_level = RunawayRiskLevel.HIGH_RISK if trend > 5.0 else RunawayRiskLevel.EARLY_WARNING
                    
                    event = RunawayEvent(
                        event_id=f"PFP_{int(time.time())}_{cell_id}",
                        timestamp=datetime.now(),
                        event_type=RunawayEventType.PROGRESSIVE_FAILURE,
                        risk_level=risk_level,
                        affected_cells=[cell_id],
                        delta_mv=recent_deltas[-1],
                        max_cell_voltage=max([c.voltage_mv for c in self.cells.values()]),
                        min_cell_voltage=min([c.voltage_mv for c in self.cells.values()]),
                        temperature_c=cell.temperature_dc / 10.0,
                        current_ma=self._current_data.get('current_ma', 0),
                        soc_percent=self._current_data.get('soc_percent', 50),
                        escalation_time_seconds=300.0 / trend,  # Estimated time to critical
                        p3e_correlation=f"Progressive failure pattern detected: {trend:.2f}mV/reading trend",
                        recommended_action="Enhanced monitoring, prepare for cell isolation",
                        raw_data={'failure_trend': trend, 'delta_history': recent_deltas[-10:]}
                    )
                    
                    self._process_runaway_event(event)
    
    def _enhanced_cell_monitoring(self, cell_id: int) -> None:
        """Enhanced monitoring for high-risk cells (Cell #6 based on P3E analysis)"""
        cell = self.cells[cell_id]
        
        # Cell #6 specific monitoring based on P3E correlation
        if cell_id == 6:
            # Check for P3E Pack 0535 pattern (4411mV overvoltage)
            if cell.voltage_mv > 4200:
                event = RunawayEvent(
                    event_id=f"ECM_CELL6_{int(time.time())}",
                    timestamp=datetime.now(),
                    event_type=RunawayEventType.BMS_PROTECTION_FAILURE,
                    risk_level=RunawayRiskLevel.EMERGENCY,
                    affected_cells=[6],
                    delta_mv=max([c.voltage_mv for c in self.cells.values()]) - min([c.voltage_mv for c in self.cells.values()]),
                    max_cell_voltage=cell.voltage_mv,
                    min_cell_voltage=min([c.voltage_mv for c in self.cells.values()]),
                    temperature_c=cell.temperature_dc / 10.0,
                    current_ma=self._current_data.get('current_ma', 0),
                    soc_percent=self._current_data.get('soc_percent', 50),
                    escalation_time_seconds=1.0,  # Immediate response required
                    p3e_correlation="Pack 0535 Cell #6 pattern: Overvoltage indicates BMS protection failure",
                    recommended_action="EMERGENCY SHUTDOWN - BMS protection failure",
                    raw_data={'p3e_pack_correlation': '0535', 'bms_failure_indicator': True}
                )
                
                self._process_runaway_event(event)
            
            # Check for P3E Pack 0533 pattern (UV during discharge)
            elif cell.voltage_mv < 2500:
                event = RunawayEvent(
                    event_id=f"ECM_CELL6_UV_{int(time.time())}",
                    timestamp=datetime.now(),
                    event_type=RunawayEventType.PROGRESSIVE_FAILURE,
                    risk_level=RunawayRiskLevel.CRITICAL,
                    affected_cells=[6],
                    delta_mv=max([c.voltage_mv for c in self.cells.values()]) - min([c.voltage_mv for c in self.cells.values()]),
                    max_cell_voltage=max([c.voltage_mv for c in self.cells.values()]),
                    min_cell_voltage=cell.voltage_mv,
                    temperature_c=cell.temperature_dc / 10.0,
                    current_ma=self._current_data.get('current_ma', 0),
                    soc_percent=self._current_data.get('soc_percent', 50),
                    escalation_time_seconds=30.0,
                    p3e_correlation="Pack 0533 Cell #6 pattern: Undervoltage during discharge",
                    recommended_action="Stop discharge immediately, cell isolation required",
                    raw_data={'p3e_pack_correlation': '0533', 'uv_failure_indicator': True}
                )
                
                self._process_runaway_event(event)
    
    def _calculate_escalation_time(self, current_delta_mv: int) -> float:
        """Calculate estimated time to next risk threshold based on P3E data"""
        if current_delta_mv >= self.thresholds.emergency_mv:
            return 1.0  # Already at emergency level
        elif current_delta_mv >= self.thresholds.critical_mv:
            return 10.0  # Critical to emergency: <10 seconds
        elif current_delta_mv >= self.thresholds.high_risk_mv:
            return 30.0  # High risk to critical: 30 seconds (Pack 0533 data)
        elif current_delta_mv >= self.thresholds.early_warning_mv:
            return 60.0  # Warning to high risk: 1 minute
        else:
            return 300.0  # Normal to warning: 5 minutes
    
    def _get_p3e_correlation(self, pack_delta: int, affected_cells: List[int], current_ma: int) -> str:
        """Get P3E pack correlation information"""
        correlations = []
        
        if pack_delta >= 1000:
            correlations.append("Pack 0535: 1048mV catastrophic runaway with 4411mV overvoltage")
        elif pack_delta >= 700:
            correlations.append("Pack 0533: 702mV runaway during -5.3A discharge")
        elif pack_delta >= 500:
            correlations.append("Pack 0520/0561: 502-533mV concerning runaway levels")
        elif pack_delta >= 300:
            correlations.append("Pack 0533: 300mV escalation threshold during discharge")
        elif pack_delta >= 100:
            correlations.append("P3E early warning threshold: 5-8x normal operation")
        
        if 6 in affected_cells:
            correlations.append("Cell #6 high-risk correlation (Packs 0533, 0535)")
        
        if current_ma <= -5000:
            correlations.append("Pack 0533 discharge pattern: -5.3A creates runaway conditions")
        
        return "; ".join(correlations) if correlations else "Normal operation range"
    
    def _get_recommended_action(self, risk_level: RunawayRiskLevel) -> str:
        """Get recommended action based on risk level"""
        actions = {
            RunawayRiskLevel.NORMAL: "Continue normal operation",
            RunawayRiskLevel.EARLY_WARNING: "Enhanced monitoring, generate alerts",
            RunawayRiskLevel.HIGH_RISK: "Reduce current to 50%, activate thermal monitoring",
            RunawayRiskLevel.CRITICAL: "Immediate shutdown preparation, <10-second response",
            RunawayRiskLevel.EMERGENCY: "Emergency shutdown, safety protocols, 1-second response",
            RunawayRiskLevel.CATASTROPHIC: "Immediate evacuation, emergency services, system isolation"
        }
        return actions.get(risk_level, "Unknown risk level")
    
    def _handle_risk_escalation(self, previous_risk: RunawayRiskLevel, new_risk: RunawayRiskLevel,
                               pack_delta: int, max_voltage: int, min_voltage: int, 
                               max_temp: float, current_ma: int, soc_percent: int) -> None:
        """Handle risk level escalation with appropriate responses"""
        self.logger.warning(f"Risk escalation: {previous_risk.value} -> {new_risk.value} "
                           f"(Delta: {pack_delta}mV, Temp: {max_temp:.1f}°C)")
        
        escalation_event = RunawayEvent(
            event_id=f"ESC_{int(time.time())}_{new_risk.value}",
            timestamp=datetime.now(),
            event_type=RunawayEventType.PROGRESSIVE_FAILURE,
            risk_level=new_risk,
            affected_cells=[],  # Will be determined by specific detection
            delta_mv=pack_delta,
            max_cell_voltage=max_voltage,
            min_cell_voltage=min_voltage,
            temperature_c=max_temp,
            current_ma=current_ma,
            soc_percent=soc_percent,
            escalation_time_seconds=self._calculate_escalation_time(pack_delta),
            p3e_correlation=f"Risk escalation from {previous_risk.value} to {new_risk.value}",
            recommended_action=self._get_recommended_action(new_risk),
            raw_data={'previous_risk': previous_risk.value, 'escalation_detected': True}
        )
        
        self._process_runaway_event(escalation_event)
        
        # Trigger automatic responses based on risk level
        if new_risk in [RunawayRiskLevel.EMERGENCY, RunawayRiskLevel.CATASTROPHIC]:
            self.request_emergency_shutdown()
    
    def _process_runaway_event(self, event: RunawayEvent) -> None:
        """Process a detected runaway event"""
        self.active_events.append(event)
        self.event_history.append(event)
        
        # Update statistics
        self.stats['total_events'] += 1
        if event.risk_level == RunawayRiskLevel.EARLY_WARNING:
            self.stats['warning_events'] += 1
        elif event.risk_level in [RunawayRiskLevel.CRITICAL, RunawayRiskLevel.HIGH_RISK]:
            self.stats['critical_events'] += 1
        elif event.risk_level in [RunawayRiskLevel.EMERGENCY, RunawayRiskLevel.CATASTROPHIC]:
            self.stats['emergency_events'] += 1
        
        if "Pack 0" in event.p3e_correlation:
            self.stats['p3e_correlations'] += 1
        
        # Add to alert queue
        self.alert_queue.put(event)
        
        # Log event
        self.logger.warning(f"RUNAWAY EVENT: {event.event_type.value} - {event.risk_level.value}")
        self.logger.warning(f"  Delta: {event.delta_mv}mV, Cells: {event.affected_cells}")
        self.logger.warning(f"  P3E Correlation: {event.p3e_correlation}")
        self.logger.warning(f"  Action: {event.recommended_action}")
        
        # Automatic responses for critical events
        if event.risk_level in [RunawayRiskLevel.EMERGENCY, RunawayRiskLevel.CATASTROPHIC]:
            self.request_emergency_shutdown()
    
    def request_emergency_shutdown(self) -> None:
        """Request emergency system shutdown"""
        self.shutdown_requested = True
        self.logger.critical("EMERGENCY SHUTDOWN REQUESTED - Thermal runaway detected")
        
        # Create shutdown event
        shutdown_event = RunawayEvent(
            event_id=f"SHUTDOWN_{int(time.time())}",
            timestamp=datetime.now(),
            event_type=RunawayEventType.BMS_PROTECTION_FAILURE,
            risk_level=RunawayRiskLevel.CATASTROPHIC,
            affected_cells=list(range(1, self.cell_count + 1)),
            delta_mv=max([c.voltage_mv for c in self.cells.values()]) - min([c.voltage_mv for c in self.cells.values()]),
            max_cell_voltage=max([c.voltage_mv for c in self.cells.values()]),
            min_cell_voltage=min([c.voltage_mv for c in self.cells.values()]),
            temperature_c=max([c.temperature_dc / 10.0 for c in self.cells.values()]),
            current_ma=self._current_data.get('current_ma', 0),
            soc_percent=self._current_data.get('soc_percent', 50),
            escalation_time_seconds=0.0,
            p3e_correlation="Emergency shutdown triggered",
            recommended_action="IMMEDIATE SYSTEM ISOLATION AND EVACUATION",
            raw_data={'emergency_shutdown': True}
        )
        
        self.alert_queue.put(shutdown_event)
    
    def get_next_alert(self, timeout: float = 1.0) -> Optional[RunawayEvent]:
        """Get next alert from the queue"""
        try:
            return self.alert_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current detector status"""
        voltages = [cell.voltage_mv for cell in self.cells.values()]
        temperatures = [cell.temperature_dc / 10.0 for cell in self.cells.values()]
        
        return {
            'monitoring_active': self.monitoring_active,
            'current_risk_level': self.current_risk_level.value,
            'shutdown_requested': self.shutdown_requested,
            'active_events': len(self.active_events),
            'total_events': len(self.event_history),
            'pack_delta_mv': max(voltages) - min(voltages) if voltages else 0,
            'max_voltage_mv': max(voltages) if voltages else 0,
            'min_voltage_mv': min(voltages) if voltages else 0,
            'max_temperature_c': max(temperatures) if temperatures else 0,
            'high_risk_cells': self.high_risk_cells,
            'thresholds': {
                'early_warning_mv': self.thresholds.early_warning_mv,
                'high_risk_mv': self.thresholds.high_risk_mv,
                'critical_mv': self.thresholds.critical_mv,
                'emergency_mv': self.thresholds.emergency_mv,
                'catastrophic_mv': self.thresholds.catastrophic_mv
            },
            'statistics': self.stats.copy(),
            'p3e_analysis_status': 'Active - Based on Packs 0520, 0533, 0535, 0561 data'
        }
    
    def get_detection_report(self) -> Dict[str, Any]:
        """Generate comprehensive detection report"""
        status = self.get_current_status()
        
        # Recent events summary
        recent_events = [event for event in self.event_history 
                        if (datetime.now() - event.timestamp).total_seconds() < 3600]
        
        # Risk distribution
        risk_distribution = {}
        for event in self.event_history:
            risk = event.risk_level.value
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
        
        # P3E correlation analysis
        p3e_matches = [event for event in self.event_history if "Pack 0" in event.p3e_correlation]
        
        return {
            'status': status,
            'recent_events': len(recent_events),
            'recent_events_detail': [
                {
                    'timestamp': event.timestamp.isoformat(),
                    'type': event.event_type.value,
                    'risk_level': event.risk_level.value,
                    'delta_mv': event.delta_mv,
                    'affected_cells': event.affected_cells,
                    'p3e_correlation': event.p3e_correlation
                }
                for event in recent_events[-10:]  # Latest 10 events
            ],
            'risk_distribution': risk_distribution,
            'p3e_correlations': {
                'total': len(p3e_matches),
                'accuracy': len(p3e_matches) / max(len(self.event_history), 1) * 100,
                'patterns_detected': list(set([event.p3e_correlation for event in p3e_matches]))
            },
            'cell_analysis': {
                cell_id: {
                    'voltage_mv': cell.voltage_mv,
                    'temperature_c': cell.temperature_dc / 10.0,
                    'anomaly_count': cell.anomaly_count,
                    'risk_score': cell.risk_score,
                    'high_risk_cell': cell_id in self.high_risk_cells
                }
                for cell_id, cell in self.cells.items()
            },
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate operational recommendations based on current state"""
        recommendations = []
        
        current_delta = max([c.voltage_mv for c in self.cells.values()]) - min([c.voltage_mv for c in self.cells.values()])
        
        if current_delta >= self.thresholds.critical_mv:
            recommendations.append("CRITICAL: Immediate shutdown preparation required")
            recommendations.append("Activate all cooling systems to maximum")
            recommendations.append("Prepare emergency evacuation procedures")
        elif current_delta >= self.thresholds.high_risk_mv:
            recommendations.append("HIGH RISK: Reduce current to 50% immediately")
            recommendations.append("Activate enhanced thermal monitoring")
            recommendations.append("Prepare for potential shutdown within 30 seconds")
        elif current_delta >= self.thresholds.early_warning_mv:
            recommendations.append("EARLY WARNING: Increase monitoring frequency")
            recommendations.append("Log all operational parameters")
            recommendations.append("Monitor Cell #6 with enhanced priority")
        
        # Enhanced monitoring for high-risk cells
        for cell_id in self.high_risk_cells:
            if cell_id in self.cells:
                cell = self.cells[cell_id]
                if cell.voltage_mv > 4000 or cell.voltage_mv < 3000:
                    recommendations.append(f"Enhanced monitoring required for Cell #{cell_id} (P3E correlation)")
        
        if not recommendations:
            recommendations.append("Continue normal operation with standard monitoring")
        
        return recommendations
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend in a series of values"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope
    
    def _check_temperature_gradients(self) -> None:
        """Check for dangerous temperature gradients across cells"""
        temperatures = [cell.temperature_dc / 10.0 for cell in self.cells.values()]
        if not temperatures:
            return
            
        temp_gradient = max(temperatures) - min(temperatures)
        
        # Significant gradient indicates thermal imbalance
        if temp_gradient > 10.0:  # >10°C difference
            self._detect_temperature_gradients()
    
    def _update_risk_scores(self) -> None:
        """Update risk scores for all cells"""
        for cell_id, cell in self.cells.items():
            score = 0.0
            
            # Voltage contribution
            if cell.voltage_mv > 4200:
                score += 10.0  # Overvoltage
            elif cell.voltage_mv < 3000:
                score += 8.0   # Undervoltage
            
            # Temperature contribution
            temp_c = cell.temperature_dc / 10.0
            if temp_c > 45:
                score += 10.0
            elif temp_c > 35:
                score += 5.0
            
            # High-risk cell penalty
            if cell_id in self.high_risk_cells:
                score += 2.0
            
            # Historical anomaly contribution
            score += cell.anomaly_count * 0.5
            
            cell.risk_score = min(score, 20.0)  # Cap at 20
    
    def _cleanup_old_events(self) -> None:
        """Clean up old events to prevent memory issues"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Remove old events from active list
        self.active_events = [event for event in self.active_events 
                             if (datetime.now() - event.timestamp).total_seconds() < 3600]
        
        # Keep only recent history
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-1000:]


def main():
    """Test function for runaway detection system"""
    # Setup logging
    if LOGGING_AVAILABLE:
        from ..utils.log_manager import setup_logging
        setup_logging(level='INFO')
        logger = get_logger(__name__, 'runaway_detection')
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
    
    print("=== P3E Runaway Detection System Test ===")
    
    # Create detector with P3E thresholds
    detector = RunawayDetector(cell_count=8)
    detector.start_monitoring()
    
    print(f"Monitoring started with P3E-validated thresholds:")
    print(f"  Early Warning: {detector.thresholds.early_warning_mv}mV")
    print(f"  High Risk: {detector.thresholds.high_risk_mv}mV")
    print(f"  Critical: {detector.thresholds.critical_mv}mV")
    print(f"  Emergency: {detector.thresholds.emergency_mv}mV")
    print(f"  Catastrophic: {detector.thresholds.catastrophic_mv}mV")
    
    # Test scenarios based on P3E analysis
    test_scenarios = [
        {
            'name': 'Normal Operation',
            'cell_voltages': [3700, 3705, 3698, 3702, 3701, 3699, 3703, 3697],
            'temperatures': [250, 252, 251, 249, 253, 250, 251, 252],
            'current': 0,
            'soc': 50
        },
        {
            'name': 'Pack 0533 Early Pattern (59mV delta)',
            'cell_voltages': [3147, 3192, 3206, 3195, 3198, 3147, 3201, 3189],  # Cell #6 low
            'temperatures': [305, 305, 305, 305, 305, 305, 305, 305],
            'current': -5300,  # -5.3A discharge
            'soc': 64
        },
        {
            'name': 'Pack 0533 Escalation (326mV delta)',
            'cell_voltages': [3179, 3192, 3206, 3195, 3198, 2853, 3201, 3189],  # Cell #6 dropping
            'temperatures': [305, 305, 305, 305, 305, 305, 305, 305],
            'current': -5300,
            'soc': 44
        },
        {
            'name': 'Pack 0533 Critical (702mV delta)',
            'cell_voltages': [3176, 3192, 3206, 3195, 3198, 2474, 3201, 3189],  # Critical failure
            'temperatures': [305, 305, 305, 305, 305, 305, 305, 305],
            'current': -5300,
            'soc': 42
        },
        {
            'name': 'Pack 0535 Catastrophic (1048mV delta)',
            'cell_voltages': [3363, 3368, 3370, 3365, 3369, 4411, 3367, 3364],  # Cell #6 runaway
            'temperatures': [650, 650, 650, 650, 650, 650, 650, 650],  # 65°C thermal
            'current': 0,
            'soc': 85
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n--- Test {i+1}: {scenario['name']} ---")
        
        # Update all cells with scenario data
        for cell_id in range(1, 9):
            detector.update_cell_data(
                cell_id=cell_id,
                voltage_mv=scenario['cell_voltages'][cell_id-1],
                temperature_dc=scenario['temperatures'][cell_id-1],
                current_ma=scenario['current'],
                soc_percent=scenario['soc']
            )
        
        # Wait for detection
        time.sleep(0.5)
        
        # Check for alerts
        alert = detector.get_next_alert(timeout=0.1)
        if alert:
            print(f"  ALERT: {alert.event_type.value} - {alert.risk_level.value}")
            print(f"  Delta: {alert.delta_mv}mV, Affected: {alert.affected_cells}")
            print(f"  P3E Correlation: {alert.p3e_correlation}")
            print(f"  Action: {alert.recommended_action}")
        else:
            print(f"  Status: Normal operation")
        
        # Show current status
        status = detector.get_current_status()
        print(f"  Pack Delta: {status['pack_delta_mv']}mV")
        print(f"  Risk Level: {status['current_risk_level']}")
        
        time.sleep(1.0)
    
    # Generate final report
    print("\n=== Detection Report ===")
    report = detector.get_detection_report()
    print(f"Total Events: {report['status']['total_events']}")
    print(f"P3E Correlations: {report['p3e_correlations']['total']}")
    print(f"Current Risk: {report['status']['current_risk_level']}")
    
    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  - {rec}")
    
    # Stop monitoring
    detector.stop_monitoring()
    print("\nMonitoring stopped.")


if __name__ == "__main__":
    main()