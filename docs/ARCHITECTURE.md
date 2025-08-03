# Modbus BMS Simulator - System Architecture

## Overview

The Modbus BMS Simulator is a comprehensive simulation tool that emulates an 8S LiFePO4 Battery Management System (BMS) with full Modbus RTU/TCP protocol support. The architecture is designed for modularity, extensibility, and real-time performance.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Interface Layer                      │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │  Rich Console   │ │   Dashboard     │ │   Interactive   │   │
│  │   Commands      │ │   View          │ │   Mode          │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Core Simulation Engine                       │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │   Scenario      │ │   Battery       │ │   Event         │   │
│  │   Manager       │ │   Model         │ │   Engine        │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      Modbus Protocol Layer                      │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │   RTU Server    │ │   TCP Server    │ │   Register      │   │
│  │   Handler       │ │   Handler       │ │   Map           │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Communication Layer                          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │  Virtual COM    │ │   TCP Socket    │ │   Plugin        │   │
│  │  Port Manager   │ │   Manager       │ │   Interface     │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Virtual COM Port Implementation Strategy

**Design Decision**: Use platform-specific virtual serial port implementations with a unified abstraction layer.

#### Components:
- **VirtualPortManager**: Main controller for virtual port lifecycle
- **Platform Adapters**: 
  - Windows: com0com integration
  - Linux: socat/pty integration  
  - macOS: BSD pty implementation
- **Port Configuration**: Baudrate, parity, data bits, stop bits
- **Connection Manager**: Handle multiple simultaneous connections

#### Implementation Strategy:
```typescript
interface VirtualPortConfig {
  portName: string;
  baudRate: number;
  dataBits: 5 | 6 | 7 | 8;
  stopBits: 1 | 2;
  parity: 'none' | 'even' | 'odd';
  flowControl: boolean;
}

class VirtualPortManager {
  createPort(config: VirtualPortConfig): Promise<VirtualPort>;
  destroyPort(portName: string): Promise<void>;
  listPorts(): VirtualPort[];
}
```

### 2. Modbus RTU/TCP Protocol Handling

**Design Decision**: Implement a dual-stack protocol handler with shared register mapping and separate transport layers.

#### Protocol Stack Architecture:
```
┌─────────────────────────────────────────┐
│        Modbus Application Layer         │
│  ┌─────────────────┐ ┌─────────────────┐│
│  │  Function Code  │ │   Exception     ││
│  │   Handlers      │ │   Handling      ││
│  └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────┘
                  │
┌─────────────────────────────────────────┐
│         Protocol Data Unit (PDU)        │
│  ┌─────────────────┐ ┌─────────────────┐│
│  │   CRC/LRC       │ │   Frame         ││
│  │  Validation     │ │  Parsing        ││
│  └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────┘
                  │
┌─────────────────────────────────────────┐
│           Transport Layer               │
│  ┌─────────────────┐ ┌─────────────────┐│
│  │   RTU Serial    │ │   TCP Socket    ││
│  │   Transport     │ │   Transport     ││
│  └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────┘
```

#### Supported Function Codes:
- **0x01**: Read Coils
- **0x02**: Read Discrete Inputs  
- **0x03**: Read Holding Registers
- **0x04**: Read Input Registers
- **0x05**: Write Single Coil
- **0x06**: Write Single Register
- **0x0F**: Write Multiple Coils
- **0x10**: Write Multiple Registers

### 3. 8S LiFePO4 Battery Register Mapping

**Design Decision**: Create a comprehensive register map that accurately represents real BMS functionality with configurable cell count.

#### Register Layout (Base Address: 40001):

| Address Range | Description | Access | Data Type |
|---------------|-------------|---------|-----------|
| 40001-40008   | Cell Voltages (V * 1000) | RO | uint16 |
| 40009-40016   | Cell Temperatures (°C * 10) | RO | int16 |
| 40017         | Pack Voltage (V * 100) | RO | uint16 |
| 40018         | Pack Current (A * 100) | RO | int16 |
| 40019         | Pack Temperature (°C * 10) | RO | int16 |
| 40020         | State of Charge (%) | RO | uint16 |
| 40021         | State of Health (%) | RO | uint16 |
| 40022         | Remaining Capacity (Ah * 100) | RO | uint16 |
| 40023         | Cycle Count | RO | uint16 |
| 40024-40031   | Cell Balancing Status | RO | uint16 |
| 40032-40047   | Protection Status Flags | RO | uint16 |
| 40048         | BMS Status | RO | uint16 |
| 40049         | Charge/Discharge MOS Status | RW | uint16 |
| 40050-40057   | Alarm Thresholds | RW | uint16 |

#### Protection Status Flags:
```typescript
enum ProtectionFlags {
  CELL_OVERVOLTAGE = 0x0001,
  CELL_UNDERVOLTAGE = 0x0002,
  PACK_OVERVOLTAGE = 0x0004,
  PACK_UNDERVOLTAGE = 0x0008,
  CHARGE_OVERCURRENT = 0x0010,
  DISCHARGE_OVERCURRENT = 0x0020,
  CHARGE_OVERTEMP = 0x0040,
  CHARGE_UNDERTEMP = 0x0080,
  DISCHARGE_OVERTEMP = 0x0100,
  DISCHARGE_UNDERTEMP = 0x0200,
  COMMUNICATION_ERROR = 0x0400,
  BALANCING_ERROR = 0x0800
}
```

### 4. Rich CLI Interface with Real-time Updates

**Design Decision**: Use React Ink for rich terminal UI with component-based architecture and real-time data streaming.

#### CLI Architecture:
```
┌─────────────────────────────────────────┐
│            Main CLI App                 │
│  ┌─────────────────┐ ┌─────────────────┐│
│  │   Command       │ │   Interactive   ││
│  │   Router        │ │   Mode          ││
│  └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────┘
                  │
┌─────────────────────────────────────────┐
│          Dashboard Components           │
│  ┌─────────────────┐ ┌─────────────────┐│
│  │   Battery       │ │   Connection    ││
│  │   Status        │ │   Status        ││
│  └─────────────────┘ └─────────────────┘│
│  ┌─────────────────┐ ┌─────────────────┐│
│  │   Cell Grid     │ │   Logs Panel    ││
│  │   Display       │ │                 ││
│  └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────┘
                  │
┌─────────────────────────────────────────┐
│           Real-time Engine              │
│  ┌─────────────────┐ ┌─────────────────┐│
│  │   Event         │ │   Data          ││
│  │   Emitter       │ │   Streams       ││
│  └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────┘
```

#### CLI Commands:
- `start`: Start simulation with configuration
- `dashboard`: Launch interactive dashboard
- `scenario`: Load/run predefined scenarios
- `config`: Configure BMS parameters
- `logs`: View detailed logs
- `plugins`: Manage plugin ecosystem

### 5. Configurable Scenario Engine

**Design Decision**: Create a declarative scenario system with YAML configuration and JavaScript scripting support.

#### Scenario Configuration Structure:
```yaml
scenario:
  name: "Charge Cycle Test"
  duration: "30m"
  steps:
    - time: "0s"
      action: "set_current"
      value: 10.0
      unit: "A"
    - time: "5m"
      action: "trigger_protection"
      protection: "CELL_OVERVOLTAGE"
      cell: 3
    - time: "10m"
      action: "set_temperature"
      cells: [1, 2, 3]
      value: 45.0
      unit: "C"
  conditions:
    - trigger: "soc >= 80"
      action: "reduce_current"
      value: 5.0
```

#### Scenario Engine Components:
- **ScenarioLoader**: Parse YAML/JSON scenario files
- **TimelineManager**: Execute time-based events
- **ConditionEvaluator**: Monitor and react to system conditions
- **ActionExecutor**: Apply changes to battery model
- **EventLogger**: Record scenario execution history

### 6. Plugin Architecture for Extensibility

**Design Decision**: Implement a hook-based plugin system with TypeScript support and sandboxed execution.

#### Plugin Interface:
```typescript
interface BMSPlugin {
  name: string;
  version: string;
  description: string;
  
  // Lifecycle hooks
  onInit?(context: PluginContext): Promise<void>;
  onStart?(context: PluginContext): Promise<void>;
  onStop?(context: PluginContext): Promise<void>;
  
  // Data hooks
  onRegisterRead?(address: number, value: number): number;
  onRegisterWrite?(address: number, value: number): boolean;
  onProtectionTriggered?(protection: ProtectionFlags): void;
  
  // Custom endpoints
  registerEndpoints?(router: Express.Router): void;
}

interface PluginContext {
  logger: Logger;
  config: ConfigManager;
  battery: BatteryModel;
  modbus: ModbusServer;
  events: EventEmitter;
}
```

#### Plugin Discovery and Loading:
- **Plugin Directory**: `./plugins/` with auto-discovery
- **NPM Packages**: Support for installable plugins
- **Hot Reload**: Development-friendly plugin reloading
- **Dependency Management**: Plugin dependency resolution
- **Security Sandbox**: Isolated execution environment

## Data Flow Architecture

### Real-time Data Pipeline:
```
Battery Model → Register Map → Modbus Protocol → Transport Layer → Client
      ↑              ↑              ↑               ↑            ↑
   Scenario      Plugin         Event           Connection    External
   Engine        Hooks         System           Manager       Client
      ↑              ↑              ↑               ↑            ↑
   CLI Commands → Configuration → Logging → Monitoring → Dashboard
```

### Event-Driven Architecture:
- **Battery Events**: Voltage changes, temperature updates, protection triggers
- **Connection Events**: Client connect/disconnect, communication errors
- **System Events**: Configuration changes, plugin loading, scenario execution
- **User Events**: CLI commands, dashboard interactions

## Performance Considerations

### Real-time Requirements:
- **Register Update Rate**: 100ms intervals (configurable)
- **Modbus Response Time**: <10ms for standard requests
- **CLI Refresh Rate**: 200ms for dashboard updates
- **Event Processing**: Non-blocking async event handling

### Memory Management:
- **Circular Buffers**: For historical data storage
- **Connection Pooling**: Efficient client connection handling
- **Plugin Isolation**: Memory-safe plugin execution
- **Garbage Collection**: Optimized for real-time performance

## Security Architecture

### Communication Security:
- **Input Validation**: All Modbus requests validated
- **Rate Limiting**: Protection against DOS attacks
- **Connection Limits**: Maximum client connections
- **Protocol Compliance**: Strict Modbus specification adherence

### Plugin Security:
- **Sandboxed Execution**: Isolated plugin runtime
- **Permission System**: Granular access controls
- **Code Validation**: Plugin code safety checks
- **Resource Limits**: CPU and memory constraints

## Configuration Management

### Hierarchical Configuration:
1. **Default Configuration**: Built-in sensible defaults
2. **System Configuration**: `/etc/modbus-bms-sim/config.yaml`
3. **User Configuration**: `~/.modbus-bms-sim/config.yaml`
4. **Project Configuration**: `./config.yaml`
5. **Environment Variables**: Runtime overrides
6. **CLI Arguments**: Immediate overrides

### Configuration Schema:
```yaml
battery:
  cellCount: 8
  nominalVoltage: 3.2
  capacity: 280
  chemistry: "LiFePO4"

modbus:
  rtu:
    enabled: true
    port: "/dev/ttyS0"
    baudRate: 9600
    slaveId: 1
  tcp:
    enabled: true
    port: 502
    interface: "0.0.0.0"

simulation:
  updateInterval: 100
  realtimeFactor: 1.0
  
plugins:
  directory: "./plugins"
  autoLoad: true
  
logging:
  level: "info"
  file: "./logs/bms-sim.log"
  maxSize: "10MB"
  maxFiles: 5
```

## Technology Stack

### Core Technologies:
- **Runtime**: Node.js 18+ with TypeScript
- **CLI Framework**: Commander.js + React Ink
- **Modbus Library**: Custom implementation with jsmodbus base
- **Serial Communication**: node-serialport
- **Configuration**: cosmiconfig + Joi validation
- **Logging**: Winston with custom formatters
- **Testing**: Jest + Supertest for integration tests

### Development Tools:
- **Build System**: tsup for fast TypeScript compilation
- **Package Manager**: pnpm for efficient dependency management
- **Documentation**: TypeDoc for API docs
- **Linting**: ESLint + Prettier
- **CI/CD**: GitHub Actions

## Deployment Architecture

### Distribution Strategy:
- **NPM Package**: Global CLI installation
- **Docker Container**: Containerized deployment
- **Standalone Binary**: Packaged with pkg
- **Development Mode**: Local source installation

### Runtime Environments:
- **Development**: Hot-reload with ts-node
- **Testing**: Isolated test environment
- **Production**: Optimized compiled JavaScript
- **Docker**: Multi-stage build for minimal image

This architecture provides a solid foundation for a comprehensive, extensible, and performant Modbus BMS Simulator that meets all specified requirements while maintaining clean separation of concerns and enabling future enhancements.