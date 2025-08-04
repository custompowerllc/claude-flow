# Modbus BMS Simulator Architecture Design

## Overview

This document outlines the architectural design for a cross-platform Modbus BMS (Battery Management System) simulator that creates virtual COM ports and serves Modbus RTU requests for testing and development purposes.

## System Requirements

### Functional Requirements
- **Virtual COM Port Management**: Create and manage virtual COM port pairs across Windows, Linux, and macOS
- **Modbus RTU Server**: Implement a pymodbus-compatible RTU server with specific register mappings
- **Register Simulation**: Simulate 36 BMS registers (addresses 10-45) with realistic battery data
- **Cross-Platform Support**: Seamless operation on Windows (com0com), Linux/macOS (socat)
- **Configuration Management**: Flexible configuration for COM port settings and register data

### Technical Requirements
- **Baudrate**: 9600 bps
- **Parity**: Even (E)
- **Stop Bits**: 1
- **Data Bits**: 8
- **Slave ID**: 1
- **Register Range**: Input registers 10-45 (36 registers total)
- **Query Pattern**: `read_input_registers(address=9, count=36, slave=1)`

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Modbus BMS Simulator                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌──────────────────┐  ┌─────────────────┐   │
│  │ CLI Interface │  │   Web Interface  │  │  Config Manager │   │
│  └───────────────┘  └──────────────────┘  └─────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                     Application Layer                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Simulator Controller                          │ │
│  │  - Lifecycle Management                                    │ │
│  │  - State Coordination                                      │ │
│  │  - Error Handling                                          │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                      Service Layer                             │
│  ┌──────────────────┐              ┌──────────────────────────┐ │
│  │   Modbus Server  │              │    Register Manager     │ │
│  │   - RTU Protocol │              │   - Data Simulation     │ │
│  │   - Request      │◄────────────►│   - Value Generation    │ │
│  │     Handling     │              │   - State Management    │ │
│  │   - pymodbus     │              │   - Validation          │ │
│  │     Integration  │              │                         │ │
│  └──────────────────┘              └──────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                  Virtual COM Port Layer                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │           Virtual COM Port Manager                         │ │
│  │                                                            │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │   Windows   │  │    Linux    │  │        macOS        │ │ │
│  │  │  com0com    │  │    socat    │  │        socat        │ │ │
│  │  │  Handler    │  │   Handler   │  │       Handler       │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                    Hardware Abstraction                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Serial Port Interface                      │ │
│  │  - Cross-platform serial communication                    │ │
│  │  - pyserial integration                                    │ │
│  │  - Connection management                                   │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Virtual COM Port Manager

The Virtual COM Port Manager provides a unified interface for creating and managing virtual COM port pairs across different operating systems.

#### Platform-Specific Implementations

**Windows (com0com)**
```
┌─────────────────────────────────────┐
│         com0com Manager             │
├─────────────────────────────────────┤
│  - Install/uninstall com0com        │
│  - Create virtual port pairs        │
│  - Configure port parameters        │
│  - Handle Windows-specific quirks   │
└─────────────────────────────────────┘
```

**Linux/macOS (socat)**
```
┌─────────────────────────────────────┐
│          socat Manager              │
├─────────────────────────────────────┤
│  - Create pseudo-terminals          │
│  - Manage symlinks                  │
│  - Handle permissions               │
│  - Process lifecycle management     │
└─────────────────────────────────────┘
```

#### Interface Design
```python
class VirtualComPortManager(ABC):
    @abstractmethod
    def create_port_pair(self, port1: str, port2: str) -> Tuple[str, str]:
        """Create a virtual COM port pair"""
        
    @abstractmethod
    def destroy_port_pair(self, port1: str, port2: str) -> None:
        """Destroy a virtual COM port pair"""
        
    @abstractmethod
    def list_ports(self) -> List[str]:
        """List available virtual ports"""
        
    @abstractmethod
    def is_port_available(self, port: str) -> bool:
        """Check if a port is available for use"""
```

### 2. Modbus Server Architecture

The Modbus server is built on pymodbus and provides RTU protocol support with custom register handling.

```
┌─────────────────────────────────────────────────────────────┐
│                    Modbus RTU Server                       │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌─────────────────┐  ┌──────────────┐   │
│  │   Request     │  │    Protocol     │  │   Response   │   │
│  │   Parser      │  │    Handler      │  │   Builder    │   │
│  └───────────────┘  └─────────────────┘  └──────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Function Code Handlers                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  - Read Input Registers (0x04)                         │ │
│  │  - Error Handling                                       │ │
│  │  - Data Validation                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     Data Store Interface                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │               Custom Register Bank                      │ │
│  │  - Input Registers (addresses 10-45)                   │ │
│  │  - Dynamic data generation                              │ │
│  │  - State persistence                                    │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 3. Register Management System

The register management system simulates realistic BMS data for the 36 registers.

#### Register Mapping (Addresses 10-45)
```
Address Range | Data Type    | Description                  | Unit
10-15        | Voltage      | Cell voltages 1-6           | mV
16-21        | Voltage      | Cell voltages 7-12          | mV
22-27        | Temperature  | Temperature sensors 1-6     | 0.1°C
28-33        | Current      | Current measurements         | mA
34-39        | Status       | Status flags and states     | Binary
40-45        | Balancing    | Balancing status per cell   | Binary
```

#### Data Simulation Engine
```
┌─────────────────────────────────────────────────────────────┐
│                Data Simulation Engine                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   Voltage       │  │   Temperature   │                   │
│  │   Simulator     │  │   Simulator     │                   │
│  │  - Realistic    │  │  - Thermal      │                   │
│  │    profiles     │  │    modeling     │                   │
│  │  - Drift        │  │  - Ambient      │                   │
│  │  - Noise        │  │    variations   │                   │
│  └─────────────────┘  └─────────────────┘                   │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   Current       │  │    Status       │                   │
│  │   Simulator     │  │   Simulator     │                   │
│  │  - Load         │  │  - Fault        │                   │
│  │    profiles     │  │    injection    │                   │
│  │  - Transients   │  │  - State        │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

## Communication Flow

### 1. Client Request Flow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   BMS Client    │───►│  Virtual COM     │───►│  Modbus Server  │
│                 │    │  Port Pair       │    │                 │
│ read_input_     │    │  (COM3↔COM4)     │    │  Slave ID: 1    │
│ registers(9,36,1)│    │                  │    │  Registers:     │
│                 │    │                  │    │  10-45          │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 2. Response Flow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Register Data  │◄───│   Data Store     │◄───│  Request Parser │
│  Serialization  │    │   (36 registers) │    │                 │
│                 │    │                  │    │  Address: 9     │
│  [reg10, reg11, │    │  reg10: 3421mV   │    │  Count: 36      │
│   ..., reg45]   │    │  reg11: 3398mV   │    │  Slave: 1       │
│                 │    │  ...             │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Cross-Platform Considerations

### Windows Implementation
```python
class WindowsComPortManager(VirtualComPortManager):
    def __init__(self):
        self.com0com_path = self._detect_com0com()
        self.active_pairs = {}
    
    def create_port_pair(self, port1: str, port2: str) -> Tuple[str, str]:
        # Use setupc.exe to create virtual port pair
        # Handle Windows UAC requirements
        # Configure port parameters
        pass
```

### Linux/macOS Implementation
```python
class UnixComPortManager(VirtualComPortManager):
    def __init__(self):
        self.socat_processes = {}
        self.symlink_paths = {}
    
    def create_port_pair(self, port1: str, port2: str) -> Tuple[str, str]:
        # Create socat pseudo-terminal pair
        # Set up symbolic links
        # Handle permissions
        pass
```

## Configuration Management

### Configuration Schema
```json
{
  "virtual_ports": {
    "enabled": true,
    "windows": {
      "com0com_path": "C:\\Program Files\\com0com\\",
      "default_ports": ["COM3", "COM4"]
    },
    "unix": {
      "symlink_base": "/tmp/ttyV",
      "default_ports": ["ttyV0", "ttyV1"]
    }
  },
  "modbus": {
    "slave_id": 1,
    "baudrate": 9600,
    "parity": "E",
    "stopbits": 1,
    "bytesize": 8,
    "timeout": 1.0
  },
  "simulation": {
    "voltage_range": [3200, 4200],
    "temperature_range": [200, 400],
    "current_range": [-5000, 5000],
    "update_interval": 1.0
  }
}
```

## Error Handling Strategy

### Virtual COM Port Errors
- **Creation Failures**: Fallback to alternative port names
- **Permission Issues**: Provide clear instructions for user privileges
- **Driver Missing**: Guide users through driver installation

### Modbus Communication Errors
- **Invalid Requests**: Return appropriate Modbus exception codes
- **Timeout Handling**: Configurable timeout and retry mechanisms
- **Data Corruption**: Checksum validation and error recovery

### Simulation Errors
- **Data Generation**: Graceful degradation with default values
- **Configuration Errors**: Validation and fallback to defaults
- **Resource Exhaustion**: Memory and CPU usage monitoring

## Security Considerations

### Virtual Port Security
- **Access Control**: Ensure only authorized processes can access virtual ports
- **Resource Cleanup**: Proper cleanup of virtual ports on shutdown
- **Process Isolation**: Prevent interference between multiple simulator instances

### Modbus Security
- **Request Validation**: Strict validation of Modbus requests
- **Rate Limiting**: Prevent resource exhaustion from rapid requests
- **Data Sanitization**: Ensure simulated data doesn't contain sensitive information

## Performance Requirements

### Response Time
- **Modbus Response**: < 100ms for typical requests
- **Port Creation**: < 5 seconds for virtual port pair setup
- **Data Generation**: < 10ms for register value updates

### Resource Usage
- **Memory**: < 50MB base memory footprint
- **CPU**: < 5% CPU usage during normal operation
- **Disk I/O**: Minimal disk usage for configuration and logging

## Testing Strategy

### Unit Testing
- **Component Isolation**: Test each component independently
- **Mock Dependencies**: Use mocks for external dependencies
- **Cross-Platform**: Run tests on all supported platforms

### Integration Testing
- **End-to-End**: Test complete client-server communication
- **Platform-Specific**: Verify platform-specific implementations
- **Error Scenarios**: Test error handling and recovery

### Performance Testing
- **Load Testing**: Multiple concurrent clients
- **Stress Testing**: Resource exhaustion scenarios
- **Endurance Testing**: Long-running stability tests

## Future Enhancements

### Phase 2 Considerations
- **Multiple Slave Support**: Support for multiple Modbus slaves
- **TCP Support**: Modbus TCP in addition to RTU
- **Advanced Simulation**: Physics-based battery modeling
- **Real-time Monitoring**: Web-based real-time data visualization
- **Configuration UI**: Graphical configuration interface

### Scalability
- **Multi-Instance**: Support multiple simulator instances
- **Distributed Simulation**: Network-based distributed simulation
- **Plugin Architecture**: Extensible simulation models

## Decision Records

### ADR-001: Virtual COM Port Technology Choice
- **Decision**: Use com0com for Windows, socat for Unix
- **Rationale**: Most stable and widely supported solutions
- **Alternatives Considered**: Virtual serial port drivers, kernel modules
- **Status**: Accepted

### ADR-002: Modbus Library Selection
- **Decision**: Use pymodbus library
- **Rationale**: Mature, well-documented, active community
- **Alternatives Considered**: modbus-tk, custom implementation
- **Status**: Accepted

### ADR-003: Register Address Mapping
- **Decision**: Map registers 10-45 to client query address 9 + offset
- **Rationale**: Matches existing BMS client implementation expectations
- **Alternatives Considered**: Direct 1:1 mapping, configurable offset
- **Status**: Accepted

### ADR-004: Data Simulation Approach
- **Decision**: Real-time generation with configurable profiles
- **Rationale**: Provides realistic testing scenarios with flexibility
- **Alternatives Considered**: Pre-recorded data, static values
- **Status**: Accepted

## Conclusion

This architecture provides a robust, cross-platform foundation for the Modbus BMS Simulator. The design emphasizes modularity, testability, and maintainability while meeting all functional requirements. The layered architecture allows for future enhancements and platform-specific optimizations.

The implementation will proceed in phases:
1. **Phase 1**: Core virtual COM port and basic Modbus server
2. **Phase 2**: Advanced simulation and monitoring features
3. **Phase 3**: Web interface and distributed capabilities

This design document serves as the blueprint for the implementation teams and will be updated as the project evolves.