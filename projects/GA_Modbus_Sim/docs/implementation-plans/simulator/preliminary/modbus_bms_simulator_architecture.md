# Modbus BMS Simulator Architecture

## Executive Summary

This document defines the high-level architecture for a comprehensive Modbus BMS (Battery Management System) simulator designed to support testing and development of Modbus client applications. The simulator provides virtual COM port functionality, comprehensive BMS register simulation, configurable failure scenarios, and a rich CLI interface.

## 1. System Overview

### 1.1 Purpose
The Modbus BMS Simulator enables development teams to:
- Test Modbus client applications without physical BMS hardware
- Simulate various battery conditions and failure scenarios
- Validate data logging and monitoring systems
- Perform regression testing with reproducible conditions

### 1.2 Key Requirements
- Virtual COM port implementation for seamless device simulation
- Modbus RTU protocol compliance
- Comprehensive BMS register simulation (voltage, current, temperature, SOC, etc.)
- Rich CLI interface using Python Rich library
- Configurable test scenarios and failure modes
- Plugin architecture for extensible battery models
- Real-time data persistence and state management
- Multi-threading support for concurrent operations

## 2. High-Level Architecture

### 2.1 System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Modbus BMS Simulator                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   CLI Interface │  │  Web Dashboard  │  │   Config Mgmt   │  │
│  │   (Rich UI)     │  │   (Optional)    │  │   (YAML/JSON)   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Scenario Engine │  │  Plugin System  │  │ State Manager   │  │
│  │ (Test Scripts)  │  │ (Battery Models)│  │ (Persistence)   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Modbus Handler  │  │ Register Bank   │  │ Virtual COM     │  │
│  │ (RTU Protocol)  │  │ (BMS Registers) │  │ (Serial Bridge) │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Threading      │  │   Logging       │  │   Monitoring    │  │
│  │  Coordinator    │  │   System        │  │   & Metrics     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

## 3. Core Architecture Components

### 3.1 Virtual COM Port Implementation

**Component**: `VirtualCOMPort`
**Technology**: Python `pty` (Unix) / `com0com` (Windows) / `socat` alternative
**Responsibility**: Create virtual serial port pairs for Modbus communication

```python
class VirtualCOMPort:
    """
    Cross-platform virtual COM port implementation
    Creates virtual serial port pairs for Modbus communication
    """
    
    Strategy Pattern:
    - UnixVirtualPort (pty-based)
    - WindowsVirtualPort (com0com integration)
    - CrossPlatformVirtualPort (pyserial-asyncio fallback)
```

**Key Features**:
- Automatic port pair creation (master/slave)
- Cross-platform compatibility
- Dynamic port allocation
- Connection state monitoring
- Error handling and recovery

### 3.2 Modbus Protocol Handler

**Component**: `ModbusHandler`
**Technology**: pymodbus server framework
**Responsibility**: Handle Modbus RTU protocol communications

```python
class ModbusHandler:
    """
    Modbus RTU protocol handler with BMS-specific register mapping
    Supports standard Modbus functions with BMS register semantics
    """
    
    Supported Functions:
    - 0x03: Read Holding Registers (BMS status registers)
    - 0x04: Read Input Registers (sensor readings)
    - 0x06: Write Single Register (control commands)
    - 0x10: Write Multiple Registers (configuration)
```

**Key Features**:
- BMS-specific register mapping
- Configurable slave IDs
- Exception handling and error responses
- Request/response logging
- Performance metrics

### 3.3 BMS Register Simulation Framework

**Component**: `BMSRegisterBank`
**Technology**: Custom register simulation with realistic battery physics
**Responsibility**: Simulate comprehensive BMS register behavior

```python
class BMSRegisterBank:
    """
    Comprehensive BMS register simulation with realistic battery behavior
    Supports multiple battery chemistry models and failure scenarios
    """
    
    Register Categories:
    - Cell Voltages (0x1000-0x1007): Individual cell voltage simulation
    - Pack Measurements (0x2000-0x2010): Pack voltage, current, SOC
    - Temperature Sensors (0x3000-0x3003): Thermal simulation
    - Protection Status (0x4000-0x4010): Safety system simulation
    - Configuration (0x5000-0x5020): BMS settings and limits
    - Diagnostics (0x6000-0x6030): Health and diagnostic data
```

**Key Features**:
- Realistic battery physics simulation
- Dynamic register updates based on battery state
- Configurable cell count and pack configuration
- Temperature-dependent behavior modeling
- SOC calculation algorithms
- Protection system simulation

### 3.4 CLI Interface Design with Rich Integration

**Component**: `SimulatorCLI`
**Technology**: Python Rich library
**Responsibility**: Professional terminal interface for simulator control

```python
class SimulatorCLI:
    """
    Rich-based CLI interface with real-time monitoring and control
    Provides professional terminal UI for simulator operations
    """
    
    UI Components:
    - Live Dashboard: Real-time BMS data display
    - Command Interface: Interactive command execution
    - Scenario Control: Test scenario management
    - Log Viewer: Real-time log streaming
    - Status Panel: System health monitoring
```

**Key Features**:
- Real-time data visualization with tables and charts
- Interactive command interface with auto-completion
- Color-coded status indicators
- Progress bars for long-running operations
- Split-pane layout for multiple data views
- Keyboard shortcuts for common operations

### 3.5 Configuration System

**Component**: `ConfigurationManager`
**Technology**: YAML/JSON configuration with schema validation
**Responsibility**: Manage simulator configuration and test scenarios

```python
class ConfigurationManager:
    """
    Hierarchical configuration management with validation
    Supports multiple configuration profiles and inheritance
    """
    
    Configuration Hierarchy:
    - Default Settings: Base simulator configuration
    - Battery Profiles: Chemistry-specific parameters
    - Test Scenarios: Predefined test conditions
    - User Overrides: Runtime configuration changes
```

**Configuration Structure**:
```yaml
simulator:
  hardware:
    cell_count: 8
    chemistry: "LiFePO4"  # LiIon, LiFePO4, NiMH
    capacity_ah: 100
    nominal_voltage: 3.2
  
  communication:
    virtual_port: "auto"  # auto, COM3, /dev/ttyUSB0
    slave_id: 1
    baudrate: 9600
    parity: "even"
  
  scenarios:
    normal_operation:
      soc_range: [20, 80]
      temperature_range: [15, 35]
      current_profile: "constant_discharge"
    
    failure_modes:
      cell_overvoltage:
        target_cell: 6
        trigger_voltage: 4.3
        response: "protection_active"
```

### 3.6 Plugin Architecture for Battery Models

**Component**: `PluginSystem`
**Technology**: Dynamic module loading with plugin interface
**Responsibility**: Extensible battery chemistry and behavior models

```python
class BatteryModelPlugin:
    """
    Abstract base class for battery model plugins
    Enables custom battery chemistry and behavior simulation
    """
    
    Plugin Types:
    - ChemistryModel: Battery chemistry-specific behavior
    - FaultSimulator: Failure mode simulation
    - LoadProfile: Current/power profile simulation
    - ThermalModel: Temperature behavior simulation
```

**Plugin Interface**:
```python
@abstractmethod
def update_state(self, current_state: BatteryState, 
                dt: float) -> BatteryState:
    """Update battery state based on physics model"""
    
@abstractmethod
def get_register_values(self, state: BatteryState) -> Dict[int, int]:
    """Convert battery state to Modbus register values"""
    
@abstractmethod
def handle_fault(self, fault_type: str, 
                parameters: Dict) -> FaultResponse:
    """Simulate fault conditions and responses"""
```

### 3.7 Data Persistence and State Management

**Component**: `StateManager`
**Technology**: SQLite for session data, JSON for snapshots
**Responsibility**: Maintain simulator state and historical data

```python
class StateManager:
    """
    Comprehensive state management with persistence
    Supports state snapshots, replay, and historical analysis
    """
    
    State Components:
    - Current State: Real-time battery and system state
    - Historical Data: Time-series data for analysis
    - Session Management: Test session tracking
    - Snapshot System: State capture and restore
```

**Key Features**:
- Automatic state snapshots at configurable intervals
- State replay for test reproduction
- Historical data analysis capabilities
- Session management with metadata
- Export functionality for external analysis

### 3.8 Multi-threading Architecture

**Component**: `ThreadingCoordinator`
**Technology**: Python asyncio with thread pool for blocking operations
**Responsibility**: Coordinate concurrent simulator operations

```python
class ThreadingCoordinator:
    """
    Asynchronous coordination of simulator components
    Manages concurrent operations without blocking
    """
    
    Thread Management:
    - Main Event Loop: Asyncio-based coordination
    - Modbus Server Thread: Protocol handling
    - UI Update Thread: Rich interface updates
    - State Update Thread: Battery physics simulation
    - Logging Thread: Asynchronous log processing
```

**Key Design Principles**:
- Lock-free communication using queues
- Event-driven architecture for responsiveness
- Graceful shutdown with cleanup
- Error isolation between threads
- Performance monitoring and optimization

## 4. Detailed Component Design

### 4.1 Virtual COM Port Strategy

**Cross-Platform Implementation**:

1. **Unix/Linux Strategy** (Primary):
   - Use `pty.openpty()` for pseudo-terminal pairs
   - Create symbolic links for predictable device names
   - Implement proper cleanup on shutdown

2. **Windows Strategy**:
   - Integration with `com0com` virtual port driver
   - Fallback to named pipes for development
   - Registry management for port persistence

3. **Development Strategy**:
   - TCP socket bridge for remote testing
   - Loopback serial port simulation
   - Mock device for unit testing

### 4.2 BMS Register Architecture

**Register Map Design**:

```python
class BMSRegisterMap:
    """
    Comprehensive BMS register mapping with semantic meaning
    Based on common BMS implementations and standards
    """
    
    # Cell voltage registers (0x1000-0x1007)
    CELL_VOLTAGE_BASE = 0x1000
    CELL_COUNT = 8
    
    # Pack measurements (0x2000-0x2010)
    PACK_VOLTAGE = 0x2000
    PACK_CURRENT = 0x2001
    PACK_SOC = 0x2002
    PACK_SOH = 0x2003
    PACK_CAPACITY_REMAINING = 0x2004
    
    # Temperature sensors (0x3000-0x3003)
    TEMP_SENSOR_BASE = 0x3000
    TEMP_SENSOR_COUNT = 4
    
    # Protection status (0x4000-0x4010)
    PROTECTION_STATUS = 0x4000
    ALARM_STATUS = 0x4001
    FAULT_STATUS = 0x4002
    
    # Configuration registers (0x5000-0x5020)
    CONFIG_BASE = 0x5000
    CELL_OV_THRESHOLD = 0x5000
    CELL_UV_THRESHOLD = 0x5001
    PACK_OC_THRESHOLD = 0x5002
```

### 4.3 Real-time Simulation Engine

**Physics-Based Simulation**:

```python
class BatteryPhysicsEngine:
    """
    Real-time battery physics simulation
    Implements simplified but realistic battery behavior
    """
    
    def simulate_discharge(self, current: float, dt: float):
        """Simulate battery discharge with voltage sag"""
        
    def simulate_temperature(self, ambient: float, current: float):
        """Thermal simulation with heating effects"""
        
    def simulate_aging(self, cycles: int, temperature: float):
        """Battery aging and capacity fade simulation"""
        
    def simulate_cell_balance(self, cell_voltages: List[float]):
        """Cell balancing system simulation"""
```

### 4.4 Scenario Engine Design

**Test Scenario Framework**:

```python
class ScenarioEngine:
    """
    Programmable test scenario execution
    Supports scripted test sequences and conditions
    """
    
    def load_scenario(self, scenario_name: str):
        """Load and validate test scenario"""
        
    def execute_scenario(self, scenario: TestScenario):
        """Execute scenario with real-time monitoring"""
        
    def inject_fault(self, fault_type: str, parameters: Dict):
        """Inject fault conditions during scenario execution"""
```

## 5. Implementation Strategy

### 5.1 Development Phases

**Phase 1: Core Infrastructure**
- Virtual COM port implementation
- Basic Modbus server setup
- Minimal register simulation
- CLI framework setup

**Phase 2: BMS Simulation**
- Comprehensive register mapping
- Battery physics simulation
- Configuration system
- State persistence

**Phase 3: Advanced Features**
- Plugin architecture
- Scenario engine
- Rich UI enhancements
- Performance optimization

**Phase 4: Testing & Validation**
- Integration testing
- Performance benchmarking
- Documentation completion
- User acceptance testing

### 5.2 Technology Stack

**Core Dependencies**:
- Python 3.8+ (for asyncio and typing improvements)
- pymodbus 3.0+ (modern Modbus implementation)
- Rich 13.0+ (terminal UI framework)
- PyYAML (configuration management)
- SQLite (state persistence)

**Platform-Specific Dependencies**:
- Unix: pty (built-in)
- Windows: pywin32, com0com
- Cross-platform: pyserial-asyncio

**Development Dependencies**:
- pytest (testing framework)
- black (code formatting)
- mypy (type checking)
- sphinx (documentation)

### 5.3 Performance Considerations

**Real-time Requirements**:
- Register updates at 10Hz minimum
- Modbus response time < 100ms
- UI refresh rate at 2Hz
- State persistence without blocking

**Memory Management**:
- Circular buffers for historical data
- Configurable data retention periods
- Memory pool for register updates
- Efficient state serialization

**Threading Optimization**:
- Minimal context switching
- Lock-free data structures where possible
- Event-driven communication
- Graceful degradation under load

## 6. Security Considerations

### 6.1 Input Validation
- Modbus request validation
- Configuration file schema validation
- Command input sanitization
- Register value range checking

### 6.2 Resource Protection
- Memory usage limits
- File system access controls
- Network binding restrictions
- Process isolation

## 7. Extensibility Points

### 7.1 Plugin Interfaces
- Battery chemistry models
- Communication protocols
- Data export formats
- User interface extensions

### 7.2 Configuration Extensions
- Custom register mappings
- Protocol variations
- Hardware profiles
- Test scenario templates

## 8. Testing Strategy

### 8.1 Unit Testing
- Component isolation testing
- Mock external dependencies
- Register simulation validation
- Protocol compliance testing

### 8.2 Integration Testing
- End-to-end communication testing
- Multi-client scenario testing
- Performance benchmarking
- Platform compatibility testing

### 8.3 Validation Testing
- Real BMS comparison testing
- Long-running stability testing
- Fault injection testing
- User acceptance testing

## 9. Documentation Strategy

### 9.1 Technical Documentation
- API documentation with examples
- Architecture decision records
- Plugin development guide
- Troubleshooting guide

### 9.2 User Documentation
- Quick start guide
- Configuration reference
- Scenario development tutorial
- FAQ and troubleshooting

## 10. Deployment Considerations

### 10.1 Packaging
- Python wheel distribution
- Docker containerization
- Platform-specific installers
- Dependency management

### 10.2 Installation
- Automated dependency installation
- Virtual COM port driver setup
- Configuration file generation
- Initial validation testing

This architecture provides a robust, extensible foundation for the Modbus BMS simulator while maintaining simplicity in core operations and providing rich functionality for advanced testing scenarios.