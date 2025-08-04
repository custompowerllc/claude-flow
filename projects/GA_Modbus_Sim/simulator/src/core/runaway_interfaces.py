"""
Thermal Runaway Simulation Interfaces

This module defines the abstract base classes and interfaces for the thermal runaway
simulation system. These interfaces provide contracts for thermal modeling, P3E detection,
and emergency response systems.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import threading


class RunawayStage(Enum):
    """Stages of thermal runaway progression"""
    NORMAL = "normal"           # T < 60°C
    ELEVATED = "elevated"       # 60°C ≤ T < 100°C
    CRITICAL = "critical"       # 100°C ≤ T < 130°C
    ONSET = "onset"            # 130°C ≤ T < 200°C
    PROPAGATING = "propagating" # 200°C ≤ T < 400°C
    PEAK = "peak"              # T ≥ 400°C
    COOLING = "cooling"        # Post-peak cooling phase


class RunawayTrigger(Enum):
    """Mechanisms that can trigger thermal runaway"""
    OVERCHARGE = "overcharge"         # V > 4.5V sustained
    INTERNAL_SHORT = "internal_short" # Sudden voltage drop + current spike
    EXTERNAL_HEAT = "external_heat"   # Neighboring cell propagation
    MECHANICAL_ABUSE = "mechanical"   # Physical damage simulation
    AGING_DEGRADATION = "aging"       # Long-term degradation effects
    NAIL_PENETRATION = "nail_penetration"  # Physical abuse testing
    CRUSH_TEST = "crush_test"         # Mechanical deformation


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class EmergencyAction(Enum):
    """Emergency actions that can be triggered"""
    DISCONNECT_LOAD = "disconnect_load"
    ISOLATE_PACK = "isolate_pack"
    ACTIVATE_SUPPRESSION = "activate_suppression"
    EVACUATE_AREA = "evacuate_area"
    NOTIFY_EMERGENCY = "notify_emergency"
    VENT_GASES = "vent_gases"
    COOL_PACK = "cool_pack"


@dataclass
class ThermalState:
    """Represents the thermal state of a single cell"""
    cell_id: int
    temperature: float          # Current cell temperature (°C)
    heat_generation: float      # Active heat generation rate (W)
    runaway_stage: RunawayStage # Current runaway stage
    time_to_peak: float        # Estimated time to peak temperature (s)
    propagation_risk: float    # Risk of triggering adjacent cells (0-1)
    internal_pressure: float   # Internal cell pressure (Pa)
    last_updated: datetime


@dataclass
class ThermalProperties:
    """Physical thermal properties of battery cells"""
    cell_mass: float = 0.045           # kg (typical 18650 cell)
    specific_heat: float = 1020        # J/kg·K
    thermal_conductivity: float = 2.5   # W/m·K
    surface_area: float = 0.0034       # m² (18650 surface area)
    emissivity: float = 0.8            # Surface emissivity
    convection_coefficient: float = 10.0 # W/m²·K


@dataclass
class RunawayParameters:
    """Parameters controlling thermal runaway behavior"""
    onset_temperature: float = 130.0    # °C - runaway onset
    peak_temperature: float = 600.0     # °C - maximum temperature
    heat_generation_rate: float = 200.0 # W/kg at peak
    cooling_rate: float = 50.0          # W/kg cooling rate
    gas_generation_rate: float = 0.1    # mol/s at peak
    pressure_threshold: float = 1e6     # Pa - rupture pressure


@dataclass
class P3EConfig:
    """Configuration for P3E detection framework"""
    # Prevention layer (P1)
    max_cell_voltage: float = 4.25      # V
    max_pack_voltage: float = 34.0      # V
    max_charge_current: float = 5.0     # A
    max_discharge_current: float = 10.0 # A
    max_temperature: float = 45.0       # °C
    max_cell_delta: float = 0.1         # V
    max_voltage_rate: float = 0.1       # V/s
    max_temp_rate: float = 5.0          # °C/s
    
    # Protection layer (P2)
    thermal_gradient_threshold: float = 10.0  # °C/min
    voltage_instability_threshold: float = 0.05  # V std dev
    current_anomaly_threshold: float = 0.5    # A unexpected current
    
    # Propagation layer (P3)
    runaway_onset_temp: float = 130.0   # °C
    propagation_temp: float = 200.0     # °C
    critical_temp: float = 400.0        # °C
    thermal_coupling: float = 0.15      # coupling coefficient
    
    # Emergency layer (P4)
    emergency_temp: float = 200.0       # °C
    evacuation_temp: float = 400.0      # °C
    suppression_temp: float = 300.0     # °C
    auto_actions_enabled: bool = True


@dataclass
class Alert:
    """Represents a detection alert"""
    alert_type: str
    message: str
    severity: AlertSeverity
    cell_id: Optional[int] = None
    timestamp: datetime = None
    value: Optional[float] = None
    threshold: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class PreventionStatus:
    """Status from prevention layer detection"""
    alerts: List[Alert]
    prevention_score: float  # 0-1, higher = more concerning
    voltage_violations: int
    temperature_violations: int
    current_violations: int
    rate_violations: int


@dataclass
class ProtectionStatus:
    """Status from protection layer detection"""
    risk_score: float           # 0-1, higher = more concerning
    gradient_alert: bool
    stability_alert: bool
    current_anomaly: bool
    thermal_gradients: List[float]
    voltage_stability: float
    anomaly_confidence: float


@dataclass
class PropagationStatus:
    """Status from propagation layer detection"""
    active_runaways: List[int]  # Cell IDs in runaway
    propagation_risks: List[Tuple[int, int, float]]  # (source, target, risk)
    max_temperature: float
    total_heat_generation: float
    estimated_propagation_time: float


@dataclass
class EmergencyStatus:
    """Status from emergency layer detection"""
    emergency_actions: List[EmergencyAction]
    max_temperature: float
    evacuation_required: bool
    suppression_active: bool
    estimated_damage: str  # "minor", "moderate", "severe", "catastrophic"


@dataclass
class RunawayScenario:
    """Defines a thermal runaway simulation scenario"""
    name: str
    description: str
    trigger_cell: Optional[int] = None
    trigger_type: RunawayTrigger = RunawayTrigger.OVERCHARGE
    duration: float = 300.0           # seconds
    severity: str = "medium"          # "low", "medium", "high"
    propagation_enabled: bool = True
    detection_config: Optional[P3EConfig] = None
    thermal_properties: Optional[ThermalProperties] = None
    runaway_parameters: Optional[RunawayParameters] = None


class ThermalModel(ABC):
    """
    Abstract base class for thermal runaway modeling
    
    This interface defines the contract for simulating thermal behavior
    of battery cells including heat generation, propagation, and cooling.
    """
    
    @abstractmethod
    def initialize_cells(self, cell_count: int, properties: ThermalProperties) -> None:
        """Initialize thermal model with specified number of cells"""
        pass
    
    @abstractmethod
    def update_thermal_state(self, dt: float) -> Dict[int, ThermalState]:
        """Update thermal state for all cells over time interval dt"""
        pass
    
    @abstractmethod
    def trigger_runaway(self, cell_id: int, trigger: RunawayTrigger, 
                       severity: float = 1.0) -> bool:
        """Initiate thermal runaway in specific cell"""
        pass
    
    @abstractmethod
    def set_ambient_conditions(self, temperature: float, 
                             convection_coefficient: float) -> None:
        """Set ambient thermal conditions"""
        pass
    
    @abstractmethod
    def calculate_heat_transfer(self, source_cell: int, target_cell: int) -> float:
        """Calculate heat transfer rate between two cells"""
        pass
    
    @abstractmethod
    def get_thermal_state(self, cell_id: int) -> ThermalState:
        """Get current thermal state of specific cell"""
        pass
    
    @abstractmethod
    def get_all_thermal_states(self) -> Dict[int, ThermalState]:
        """Get thermal states of all cells"""
        pass
    
    @abstractmethod
    def reset_model(self) -> None:
        """Reset model to initial conditions"""
        pass


class P3EDetector(ABC):
    """
    Abstract base class for P3E (Prevention, Protection, Propagation, Emergency) detection
    
    This interface defines the four-layer detection framework for thermal runaway
    prevention and response.
    """
    
    @abstractmethod
    def configure(self, config: P3EConfig) -> None:
        """Configure detection parameters"""
        pass
    
    @abstractmethod
    def evaluate_prevention(self, registers: Dict[str, int]) -> PreventionStatus:
        """Evaluate prevention layer (P1) - operational parameter monitoring"""
        pass
    
    @abstractmethod
    def evaluate_protection(self, registers: Dict[str, int], 
                          thermal_states: Dict[int, ThermalState]) -> ProtectionStatus:
        """Evaluate protection layer (P2) - advanced algorithm detection"""
        pass
    
    @abstractmethod
    def evaluate_propagation(self, thermal_states: Dict[int, ThermalState]) -> PropagationStatus:
        """Evaluate propagation layer (P3) - active runaway detection"""
        pass
    
    @abstractmethod
    def evaluate_emergency(self, thermal_states: Dict[int, ThermalState]) -> EmergencyStatus:
        """Evaluate emergency layer (P4) - emergency response actions"""
        pass
    
    @abstractmethod
    def evaluate_all_layers(self, registers: Dict[str, int], 
                          thermal_states: Dict[int, ThermalState]) -> 'P3EResults':
        """Evaluate all P3E layers and return combined results"""
        pass
    
    @abstractmethod
    def get_detection_status(self) -> Dict[str, Any]:
        """Get overall detection system status"""
        pass
    
    @abstractmethod
    def reset_detection_state(self) -> None:
        """Reset detection system to initial state"""
        pass


@dataclass
class P3EResults:
    """Combined results from all P3E detection layers"""
    prevention: PreventionStatus
    protection: ProtectionStatus
    propagation: PropagationStatus
    emergency: EmergencyStatus
    overall_risk_score: float
    recommended_actions: List[str]
    timestamp: datetime


class RunawayRegisterManager(ABC):
    """
    Abstract base class for managing runaway-specific registers
    
    This interface extends the base register management with thermal runaway
    specific data and simulation capabilities.
    """
    
    @abstractmethod
    def initialize_runaway_registers(self) -> None:
        """Initialize the 20 runaway-specific registers (46-65)"""
        pass
    
    @abstractmethod
    def update_thermal_registers(self, thermal_states: Dict[int, ThermalState]) -> None:
        """Update thermal model registers (46-55)"""
        pass
    
    @abstractmethod
    def update_detection_registers(self, detection_results: P3EResults) -> None:
        """Update detection status registers (56-60)"""
        pass
    
    @abstractmethod
    def update_emergency_registers(self, emergency_status: EmergencyStatus) -> None:
        """Update emergency action registers (61-65)"""
        pass
    
    @abstractmethod
    def get_extended_registers(self) -> List[int]:
        """Get all 56 registers (original 36 + runaway 20)"""
        pass
    
    @abstractmethod
    def set_runaway_enabled(self, enabled: bool) -> None:
        """Enable or disable runaway simulation"""
        pass
    
    @abstractmethod
    def trigger_scenario(self, scenario: RunawayScenario) -> bool:
        """Trigger a specific runaway scenario"""
        pass
    
    @abstractmethod
    def get_scenario_status(self) -> Dict[str, Any]:
        """Get status of active scenarios"""
        pass


class RunawayController(ABC):
    """
    Abstract base class for high-level runaway simulation control
    
    This interface provides the main control API for managing thermal runaway
    simulation scenarios and monitoring.
    """
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize controller with configuration"""
        pass
    
    @abstractmethod
    def start_scenario(self, scenario_name: str) -> bool:
        """Start a named runaway scenario"""
        pass
    
    @abstractmethod
    def stop_scenario(self, scenario_name: str) -> bool:
        """Stop a specific runaway scenario"""
        pass
    
    @abstractmethod
    def stop_all_scenarios(self) -> None:
        """Stop all active runaway scenarios"""
        pass
    
    @abstractmethod
    def get_available_scenarios(self) -> List[str]:
        """Get list of available scenario names"""
        pass
    
    @abstractmethod
    def get_scenario_details(self, scenario_name: str) -> Optional[RunawayScenario]:
        """Get details of a specific scenario"""
        pass
    
    @abstractmethod
    def get_controller_status(self) -> Dict[str, Any]:
        """Get comprehensive controller status"""
        pass
    
    @abstractmethod
    def set_monitoring_enabled(self, enabled: bool) -> None:
        """Enable or disable runaway monitoring"""
        pass
    
    @abstractmethod
    def export_scenario_data(self, scenario_name: str, 
                           format_type: str = "csv") -> str:
        """Export scenario data in specified format"""
        pass


class RunawayMonitor(ABC):
    """
    Abstract base class for runaway monitoring and alerting
    
    This interface defines monitoring capabilities for thermal runaway
    simulation including logging, alerting, and data export.
    """
    
    @abstractmethod
    def start_monitoring(self, scenario: RunawayScenario) -> None:
        """Start monitoring for a specific scenario"""
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> None:
        """Stop all monitoring activities"""
        pass
    
    @abstractmethod
    def log_thermal_event(self, cell_id: int, event_type: str, 
                         temperature: float, timestamp: datetime) -> None:
        """Log a thermal event"""
        pass
    
    @abstractmethod
    def log_detection_event(self, detection_results: P3EResults) -> None:
        """Log detection system results"""
        pass
    
    @abstractmethod
    def send_alert(self, alert: Alert) -> None:
        """Send an alert notification"""
        pass
    
    @abstractmethod
    def generate_report(self, scenario_name: str, 
                       report_type: str = "summary") -> str:
        """Generate monitoring report"""
        pass
    
    @abstractmethod
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring system status"""
        pass
    
    @abstractmethod
    def configure_alerts(self, alert_config: Dict[str, Any]) -> None:
        """Configure alert settings"""
        pass


class DataExporter(ABC):
    """
    Abstract base class for exporting runaway simulation data
    
    This interface defines data export capabilities for analysis
    and reporting purposes.
    """
    
    @abstractmethod
    def export_thermal_data(self, thermal_states: List[Dict[int, ThermalState]], 
                          format_type: str = "csv") -> str:
        """Export thermal state data"""
        pass
    
    @abstractmethod
    def export_detection_data(self, detection_results: List[P3EResults], 
                            format_type: str = "csv") -> str:
        """Export detection results data"""
        pass
    
    @abstractmethod
    def export_scenario_summary(self, scenario: RunawayScenario, 
                              results: Dict[str, Any]) -> str:
        """Export scenario summary report"""
        pass
    
    @abstractmethod
    def configure_export_settings(self, settings: Dict[str, Any]) -> None:
        """Configure export settings"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats"""
        pass


# Custom Exception Classes for Runaway Simulation
class RunawaySimulationError(Exception):
    """Base exception for runaway simulation errors"""
    pass


class ThermalModelError(RunawaySimulationError):
    """Raised when thermal model encounters an error"""
    pass


class DetectionError(RunawaySimulationError):
    """Raised when P3E detection system encounters an error"""
    pass


class ScenarioError(RunawaySimulationError):
    """Raised when scenario management encounters an error"""
    pass


class ConfigurationError(RunawaySimulationError):
    """Raised when configuration is invalid"""
    pass


# Type aliases for better code readability
CellId = int
Temperature = float  # °C
HeatGeneration = float  # W
Voltage = float  # V
Current = float  # A
RiskScore = float  # 0-1
PropagationRisk = Tuple[CellId, CellId, float]
ThermalGradient = float  # °C/min
EventCallback = callable
AlertCallback = callable

# Constants for runaway simulation
DEFAULT_CELL_COUNT = 8
DEFAULT_AMBIENT_TEMP = 25.0  # °C
DEFAULT_UPDATE_INTERVAL = 1.0  # seconds
RUNAWAY_ONSET_TEMP = 130.0  # °C
PROPAGATION_TEMP = 200.0  # °C
EMERGENCY_TEMP = 400.0  # °C

# Register address mappings for runaway data
RUNAWAY_REGISTER_BASE = 46
THERMAL_REGISTER_RANGE = range(46, 56)      # High-precision temperatures
DETECTION_REGISTER_RANGE = range(56, 61)   # P3E detection status
EMERGENCY_REGISTER_RANGE = range(61, 66)   # Emergency actions and status

# Runaway register definitions
RUNAWAY_REGISTERS = {
    # Thermal Model Data (46-55)
    46: "thermal_cell1_temp",      # High-precision cell 1 temperature (0.01°C)
    47: "thermal_cell2_temp",      # High-precision cell 2 temperature
    48: "thermal_cell3_temp",      # High-precision cell 3 temperature
    49: "thermal_cell4_temp",      # High-precision cell 4 temperature
    50: "thermal_cell5_temp",      # High-precision cell 5 temperature
    51: "thermal_cell6_temp",      # High-precision cell 6 temperature
    52: "thermal_cell7_temp",      # High-precision cell 7 temperature
    53: "thermal_cell8_temp",      # High-precision cell 8 temperature
    54: "thermal_gradient_max",    # Maximum thermal gradient (°C/min)
    55: "thermal_propagation_risk", # Overall propagation risk (0-1000 scale)
    
    # Detection Status (56-60)
    56: "p3e_prevention_status",   # Prevention layer status (bitfield)
    57: "p3e_protection_status",   # Protection layer status (bitfield)
    58: "p3e_propagation_status",  # Propagation layer status (bitfield)
    59: "p3e_emergency_status",    # Emergency layer status (bitfield)
    60: "runaway_detection_flags", # Combined detection flags (bitfield)
    
    # Emergency Actions (61-65)
    61: "emergency_actions",       # Active emergency actions (bitfield)
    62: "runaway_cell_mask",      # Bitmask of cells in runaway (bits 0-7)
    63: "time_to_propagation",    # Estimated time to propagation (seconds)
    64: "suppression_system",     # Fire suppression system status
    65: "evacuation_timer"        # Evacuation countdown timer (seconds)
}