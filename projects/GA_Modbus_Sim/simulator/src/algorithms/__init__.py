#!/usr/bin/env python3
"""
P3E Runaway Detection Algorithms Package

This package provides comprehensive thermal runaway detection and simulation
algorithms based on P3E battery pack analysis data from Custom Power LLC.

The algorithms implement multi-layered detection systems with validated 
thresholds derived from actual runaway events in P3E battery packs.

Key Components:
1. RunawayDetector - Voltage threshold and current anomaly detection
2. ThermalPropagationSimulator - Thermal runaway propagation modeling
3. AlertManager - Real-time alert generation and escalation
4. DataLogger - Comprehensive data logging for validation

P3E Analysis Foundation:
- Pack 0535: 1048mV catastrophic runaway with 4411mV overvoltage, 65°C thermal
- Pack 0533: 702mV runaway during -5.3A discharge with 57-second escalation
- Pack 0520/0561: 502-533mV concerning runaway levels
- Cell #6 shows highest failure correlation across multiple packs

Validated Thresholds:
- Early Warning: 100mV (5-8x normal operation)
- High Risk: 300mV (Pack 0533 escalation point, 30-second response)
- Critical: 500mV (All confirmed runaways exceed this, <10-second response)
- Emergency: 700mV (Pack 0533 peak level, 1-second BMS response)
- Catastrophic: 1000mV+ (Pack 0535 level, immediate evacuation)

Response Protocols:
- 100mV: Enhanced monitoring, alert generation
- 300mV: Reduce current to 50%, 30-second response window
- 500mV: Emergency shutdown preparation, <10-second response
- 700mV+: Immediate shutdown, safety protocols, evacuation
"""

from .runaway_detection import (
    RunawayDetector,
    RunawayEvent,
    RunawayRiskLevel,
    RunawayEventType,
    RunawayThresholds,
    CellData
)

from .thermal_propagation import (
    ThermalPropagationSimulator,
    ThermalPropagationEvent,
    ThermalState,
    CoolingEffectiveness,
    CellThermalData
)

from .alert_system import (
    AlertManager,
    Alert,
    AlertSeverity,
    AlertType,
    AlertChannel,
    AlertRule,
    AlertConfiguration
)

from .data_logger import (
    DataLogger,
    DataPoint,
    ValidationMetrics,
    LogLevel,
    DataFormat
)

__version__ = "1.0.0"
__author__ = "Custom Power LLC - P3E Analysis Team"
__description__ = "P3E Thermal Runaway Detection Algorithms"

# P3E validated thresholds for easy access
P3E_THRESHOLDS = {
    'early_warning_mv': 100,
    'high_risk_mv': 300,
    'critical_mv': 500,
    'emergency_mv': 700,
    'catastrophic_mv': 1000,
    'thermal_warning_c': 35.0,
    'thermal_critical_c': 45.0,
    'thermal_runaway_c': 60.0,
    'discharge_runaway_current_ma': -5300,
    'cell6_overvoltage_mv': 4200,
    'cell6_undervoltage_mv': 2500
}

# P3E correlation patterns for reference
P3E_PATTERNS = {
    'pack_0535': {
        'description': 'Catastrophic runaway with BMS bypass',
        'peak_delta_mv': 1048,
        'peak_voltage_mv': 4411,
        'thermal_peak_c': 65.0,
        'cell_correlation': 6,
        'duration_hours': 3.0,
        'severity': 'catastrophic'
    },
    'pack_0533': {
        'description': 'Discharge runaway with rapid escalation',
        'peak_delta_mv': 702,
        'min_voltage_mv': 2474,
        'discharge_current_ma': -5300,
        'escalation_time_s': 57,
        'cell_correlation': 6,
        'severity': 'emergency'
    },
    'pack_0520': {
        'description': 'Hidden runaway not initially reported',
        'peak_delta_mv': 502,
        'peak_voltage_mv': 3938,
        'cell_correlation': 7,
        'severity': 'critical'
    },
    'pack_0561': {
        'description': 'Active runaway during testing',
        'peak_delta_mv': 533,
        'peak_voltage_mv': 3940,
        'cell_correlation': 8,
        'severity': 'critical'
    }
}

# Export all components
__all__ = [
    # Core detection classes
    'RunawayDetector',
    'ThermalPropagationSimulator', 
    'AlertManager',
    'DataLogger',
    
    # Event and data classes
    'RunawayEvent',
    'ThermalPropagationEvent',
    'Alert',
    'DataPoint',
    'ValidationMetrics',
    
    # Enumerations
    'RunawayRiskLevel',
    'RunawayEventType',
    'ThermalState',
    'CoolingEffectiveness',
    'AlertSeverity',
    'AlertType',
    'AlertChannel',
    'LogLevel',
    'DataFormat',
    
    # Configuration classes
    'RunawayThresholds',
    'AlertRule',
    'AlertConfiguration',
    
    # Data classes
    'CellData',
    'CellThermalData',
    
    # Constants
    'P3E_THRESHOLDS',
    'P3E_PATTERNS'
]