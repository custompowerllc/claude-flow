"""
Core interfaces for the Modbus BMS Simulator.

This module defines the abstract base classes and interfaces that provide
the contract for all major components of the simulator system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
import threading
from datetime import datetime


class SimulatorState(Enum):
    """Enumeration of possible simulator states."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class Platform(Enum):
    """Supported platforms for virtual COM port management."""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"


@dataclass
class ComPortConfig:
    """Configuration for COM port parameters."""
    baudrate: int = 9600
    parity: str = 'E'  # Even parity
    stopbits: int = 1
    bytesize: int = 8
    timeout: float = 1.0


@dataclass
class VirtualPortPair:
    """Represents a virtual COM port pair."""
    port1: str
    port2: str
    config: ComPortConfig
    created_at: datetime
    process_id: Optional[int] = None
    is_active: bool = False


@dataclass
class RegisterData:
    """Represents data for a single Modbus register."""
    address: int
    value: int
    data_type: str
    unit: str
    description: str
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    last_updated: Optional[datetime] = None


@dataclass
class SimulationProfile:
    """Configuration for data simulation behavior."""
    voltage_min: int = 3200  # mV
    voltage_max: int = 4200  # mV
    temperature_min: int = 200  # 0.1°C (20°C)
    temperature_max: int = 400  # 0.1°C (40°C)
    current_min: int = -5000  # mA
    current_max: int = 5000   # mA
    noise_factor: float = 0.02  # 2% noise
    update_interval: float = 1.0  # seconds
    drift_rate: float = 0.001  # value drift per update


class VirtualComPortManager(ABC):
    """
    Abstract base class for managing virtual COM ports across platforms.
    
    This interface provides a unified API for creating and managing virtual
    COM port pairs on different operating systems.
    """
    
    @abstractmethod
    def get_platform(self) -> Platform:
        """Get the current platform."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if virtual COM port functionality is available on this system."""
        pass
    
    @abstractmethod
    def create_port_pair(self, port1: str, port2: str, config: ComPortConfig) -> VirtualPortPair:
        """
        Create a virtual COM port pair.
        
        Args:
            port1: Name of the first port (e.g., "COM3", "ttyV0")
            port2: Name of the second port (e.g., "COM4", "ttyV1")
            config: Configuration for the port parameters
            
        Returns:
            VirtualPortPair object representing the created pair
            
        Raises:
            PortCreationError: If the port pair cannot be created
            PortInUseError: If either port is already in use
        """
        pass
    
    @abstractmethod
    def destroy_port_pair(self, pair: VirtualPortPair) -> None:
        """
        Destroy a virtual COM port pair.
        
        Args:
            pair: The VirtualPortPair to destroy
            
        Raises:
            PortDestructionError: If the port pair cannot be destroyed
        """
        pass
    
    @abstractmethod
    def list_active_pairs(self) -> List[VirtualPortPair]:
        """
        List all active virtual port pairs managed by this instance.
        
        Returns:
            List of active VirtualPortPair objects
        """
        pass
    
    @abstractmethod
    def is_port_available(self, port: str) -> bool:
        """
        Check if a port name is available for use.
        
        Args:
            port: Port name to check
            
        Returns:
            True if the port is available, False otherwise
        """
        pass
    
    @abstractmethod
    def cleanup_all(self) -> None:
        """Clean up all virtual ports created by this manager."""
        pass


class RegisterManager(ABC):
    """
    Abstract base class for managing Modbus register data.
    
    This interface handles the simulation and management of BMS register data
    that will be served via Modbus requests.
    """
    
    @abstractmethod
    def initialize_registers(self, start_address: int, count: int) -> None:
        """
        Initialize the register bank with the specified range.
        
        Args:
            start_address: Starting register address
            count: Number of registers to initialize
        """
        pass
    
    @abstractmethod
    def get_register(self, address: int) -> RegisterData:
        """
        Get data for a specific register.
        
        Args:
            address: Register address
            
        Returns:
            RegisterData object for the specified address
            
        Raises:
            RegisterNotFoundError: If the register address is not valid
        """
        pass
    
    @abstractmethod
    def get_registers(self, start_address: int, count: int) -> List[RegisterData]:
        """
        Get data for a range of registers.
        
        Args:
            start_address: Starting register address
            count: Number of registers to retrieve
            
        Returns:
            List of RegisterData objects
            
        Raises:
            RegisterRangeError: If the specified range is invalid
        """
        pass
    
    @abstractmethod
    def set_register(self, address: int, value: int) -> None:
        """
        Set the value of a specific register.
        
        Args:
            address: Register address
            value: New value for the register
            
        Raises:
            RegisterNotFoundError: If the register address is not valid
            RegisterValueError: If the value is outside valid range
        """
        pass
    
    @abstractmethod
    def update_simulation(self) -> None:
        """Update all register values based on simulation profiles."""
        pass
    
    @abstractmethod
    def set_simulation_profile(self, profile: SimulationProfile) -> None:
        """
        Set the simulation profile for data generation.
        
        Args:
            profile: SimulationProfile with simulation parameters
        """
        pass
    
    @abstractmethod
    def get_register_values(self, start_address: int, count: int) -> List[int]:
        """
        Get raw register values for Modbus response.
        
        Args:
            start_address: Starting register address
            count: Number of registers to retrieve
            
        Returns:
            List of integer register values
        """
        pass


class ModbusServer(ABC):
    """
    Abstract base class for Modbus RTU server functionality.
    
    This interface defines the contract for serving Modbus RTU requests
    over a serial connection.
    """
    
    @abstractmethod
    def configure(self, port: str, config: ComPortConfig, slave_id: int = 1) -> None:
        """
        Configure the Modbus server.
        
        Args:
            port: Serial port name to bind to
            config: COM port configuration
            slave_id: Modbus slave ID to respond to
        """
        pass
    
    @abstractmethod
    def start(self) -> None:
        """
        Start the Modbus server.
        
        Raises:
            ServerStartError: If the server cannot be started
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """
        Stop the Modbus server.
        
        Raises:
            ServerStopError: If the server cannot be stopped gracefully
        """
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """Check if the server is currently running."""
        pass
    
    @abstractmethod
    def set_register_manager(self, register_manager: RegisterManager) -> None:
        """
        Set the register manager for handling register data.
        
        Args:
            register_manager: RegisterManager instance to use for data
        """
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get server statistics.
        
        Returns:
            Dictionary containing server statistics like request count,
            error count, uptime, etc.
        """
        pass


class SimulatorController(ABC):
    """
    Abstract base class for the main simulator controller.
    
    This interface coordinates all components of the simulator and provides
    the main control interface.
    """
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the simulator with configuration.
        
        Args:
            config: Configuration dictionary
            
        Raises:
            InitializationError: If initialization fails
        """
        pass
    
    @abstractmethod
    def start(self) -> None:
        """
        Start the simulator.
        
        This will:
        1. Create virtual COM port pair
        2. Start the Modbus server
        3. Begin data simulation
        
        Raises:
            SimulatorStartError: If the simulator cannot be started
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """
        Stop the simulator.
        
        This will:
        1. Stop the Modbus server
        2. Destroy virtual COM port pair
        3. Clean up resources
        
        Raises:
            SimulatorStopError: If the simulator cannot be stopped gracefully
        """
        pass
    
    @abstractmethod
    def get_state(self) -> SimulatorState:
        """Get the current simulator state."""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive simulator status.
        
        Returns:
            Dictionary containing status information for all components
        """
        pass
    
    @abstractmethod
    def reload_config(self, config: Dict[str, Any]) -> None:
        """
        Reload configuration without stopping the simulator.
        
        Args:
            config: New configuration dictionary
            
        Raises:
            ConfigurationError: If the new configuration is invalid
        """
        pass


class DataSimulator(ABC):
    """
    Abstract base class for simulating realistic BMS data.
    
    This interface defines how different types of BMS data (voltage,
    temperature, current, status) should be generated and updated.
    """
    
    @abstractmethod
    def generate_voltage_data(self, cell_id: int, profile: SimulationProfile) -> int:
        """
        Generate realistic voltage data for a battery cell.
        
        Args:
            cell_id: Cell identifier (0-based)
            profile: Simulation profile with parameters
            
        Returns:
            Voltage value in millivolts
        """
        pass
    
    @abstractmethod
    def generate_temperature_data(self, sensor_id: int, profile: SimulationProfile) -> int:
        """
        Generate realistic temperature data.
        
        Args:
            sensor_id: Temperature sensor identifier (0-based)
            profile: Simulation profile with parameters
            
        Returns:
            Temperature value in 0.1°C units
        """
        pass
    
    @abstractmethod
    def generate_current_data(self, profile: SimulationProfile) -> int:
        """
        Generate realistic current measurement data.
        
        Args:
            profile: Simulation profile with parameters
            
        Returns:
            Current value in milliamps
        """
        pass
    
    @abstractmethod
    def generate_status_data(self, status_type: str) -> int:
        """
        Generate status and flag data.
        
        Args:
            status_type: Type of status data to generate
            
        Returns:
            Status value as integer
        """
        pass
    
    @abstractmethod
    def update_all_data(self, register_manager: RegisterManager, profile: SimulationProfile) -> None:
        """
        Update all simulated data in the register manager.
        
        Args:
            register_manager: RegisterManager to update
            profile: Simulation profile with parameters
        """
        pass


class EventNotifier(ABC):
    """
    Abstract base class for event notification system.
    
    This interface allows components to publish and subscribe to events
    for loose coupling and observability.
    """
    
    @abstractmethod
    def subscribe(self, event_type: str, callback: callable) -> str:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
            
        Returns:
            Subscription ID for unsubscribing
        """
        pass
    
    @abstractmethod
    def unsubscribe(self, subscription_id: str) -> None:
        """
        Unsubscribe from an event.
        
        Args:
            subscription_id: ID returned from subscribe()
        """
        pass
    
    @abstractmethod
    def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Publish an event.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        pass


# Custom Exception Classes
class SimulatorError(Exception):
    """Base exception for simulator errors."""
    pass


class PortCreationError(SimulatorError):
    """Raised when virtual port creation fails."""
    pass


class PortInUseError(SimulatorError):
    """Raised when attempting to use a port that's already in use."""
    pass


class PortDestructionError(SimulatorError):
    """Raised when virtual port destruction fails."""
    pass


class RegisterNotFoundError(SimulatorError):
    """Raised when accessing a non-existent register."""
    pass


class RegisterRangeError(SimulatorError):
    """Raised when register range is invalid."""
    pass


class RegisterValueError(SimulatorError):
    """Raised when register value is invalid."""
    pass


class ServerStartError(SimulatorError):
    """Raised when Modbus server fails to start."""
    pass


class ServerStopError(SimulatorError):
    """Raised when Modbus server fails to stop."""
    pass


class InitializationError(SimulatorError):
    """Raised when simulator initialization fails."""
    pass


class SimulatorStartError(SimulatorError):
    """Raised when simulator fails to start."""
    pass


class SimulatorStopError(SimulatorError):
    """Raised when simulator fails to stop."""
    pass


class ConfigurationError(SimulatorError):
    """Raised when configuration is invalid."""
    pass


# Type aliases for better code readability
RegisterAddress = int
RegisterValue = int
PortName = str
SlaveId = int
EventCallback = callable
SubscriptionId = str

# Constants
DEFAULT_SLAVE_ID = 1
DEFAULT_REGISTER_START = 10
DEFAULT_REGISTER_COUNT = 36
DEFAULT_MODBUS_QUERY_ADDRESS = 9

# Register address ranges for different data types
VOLTAGE_REGISTERS = range(10, 22)      # Addresses 10-21 (12 cells)
TEMPERATURE_REGISTERS = range(22, 28)   # Addresses 22-27 (6 sensors)
CURRENT_REGISTERS = range(28, 34)       # Addresses 28-33 (6 measurements)
STATUS_REGISTERS = range(34, 40)        # Addresses 34-39 (6 status words)
BALANCING_REGISTERS = range(40, 46)     # Addresses 40-45 (6 balancing states)