# GEHC PHTC RS422 Communication Protocol Test Application - Development Prompt

## 🎯 Project Overview

Develop a Python application to test the GEHC PHTC Communication Protocol over RS422 interface. The application will send predefined commands to a PHTC (Portable Healthcare Terminal Controller) device, receive responses, parse the data with proper scaling and data types, and display results using the Rich library.

## 📋 Core Requirements

### 1. Communication Protocol Implementation
- **Protocol**: RS422 serial communication (GE Healthcare Protocol)
- **Baud Rate**: 115200 (configurable via config.json)
- **Data Format**: 8N1 (8 data bits, no parity, 1 stop bit)
- **Message Structure**: Following GEHC RS422 Protocol Structure
  - **Preamble**: `0xAA` (GE Healthcare Protocol identifier)
  - **Synchronization Header**: `0x23` (Host to Battery) / `0x40` (Battery to Host)
  - **Command Message Code Byte**
  - **Number of Data Bytes**
  - **Data Bytes** (if any)
  - **CRC-8 checksum** (SMBus PEC polynomial)

### 2. Command Processing Workflow
1. **Load Commands**: Read command list from JSON configuration file
2. **Iterate Commands**: Process each command sequentially with minimum 0.5-second delay
3. **Send Command**: Transmit formatted command to PHTC device
4. **Wait for Response**: Listen for device response with timeout
5. **Parse Response**: Extract and validate response data
6. **Process Data**: Apply scaling, data type conversion, and unit formatting
7. **Display Results**: Show formatted output to console using Rich library
8. **Continue Loop**: Move to next command until all processed

### 3. Data Processing & Parsing
- **Data Types**: Support for unsigned int, signed int, word, boolean, string, block data
- **Scaling/Granularity**: Apply appropriate scaling factors from protocol specification
- **Units**: Display values with correct units (mV, mA, %, °C, minutes, etc.)
- **Error Handling**: Validate CRC-8, handle communication timeouts, malformed responses

### 4. Configuration Management
- **config.json Structure**:
  ```json
  {
    "serial_com_port": "COM3",
    "baud_rate": 115200,
    "timeout_ms": 1000,
    "inter_command_delay": 0.5,
    "retry_count": 3
  }
  ```

### 5. Console Output with Rich Library
- **Real-time Display**: Show command sending and response receiving
- **Formatted Tables**: Display parsed data in structured format
- **Progress Indicators**: Show command processing progress
- **Color Coding**: Success (green), warnings (yellow), errors (red)
- **Summary Report**: Final summary of all responses and their interpreted values

## 🏗️ Technical Architecture

### Module Structure
```
gehc_phtc_test/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── communication/
│   │   ├── __init__.py
│   │   ├── serial_handler.py   # RS422 serial communication
│   │   └── protocol.py         # GEHC protocol implementation
│   ├── parsing/
│   │   ├── __init__.py
│   │   ├── message_parser.py   # Response message parsing
│   │   └── data_processor.py   # Data scaling and conversion
│   ├── config/
│   │   ├── __init__.py
│   │   └── config_manager.py   # Configuration handling
│   └── display/
│       ├── __init__.py
│       └── console_display.py  # Rich library output formatting
├── config/
│   ├── config.json            # Serial port and timing configuration
│   └── commands.json          # PHTC command definitions
├── tests/
│   ├── __init__.py
│   ├── test_communication.py
│   ├── test_parsing.py
│   └── test_integration.py
├── requirements.txt
├── setup.py
└── README.md
```

### Key Classes and Methods

#### SerialHandler Class
```python
class SerialHandler:
    def __init__(self, port: str, baud_rate: int, timeout: float)
    def connect(self) -> bool
    def disconnect(self) -> None
    def send_command(self, command: bytes) -> bool
    def receive_response(self) -> Optional[bytes]
    def is_connected(self) -> bool
```

#### ProtocolHandler Class
```python
class ProtocolHandler:
    def format_command(self, command_code: int, data: bytes = b'') -> bytes
    def validate_response(self, response: bytes) -> bool
    def calculate_crc8(self, data: bytes) -> int
    def extract_response_data(self, response: bytes) -> Tuple[int, bytes]
    def build_ge_message(self, command_code: int, data: bytes = b'') -> bytes
    def parse_ge_response(self, response: bytes) -> Tuple[bool, int, bytes]
```

#### MessageParser Class
```python
class MessageParser:
    def parse_response(self, command_code: int, response_data: bytes) -> Dict[str, Any]
    def apply_scaling(self, value: int, scaling_info: Dict) -> float
    def format_with_units(self, value: float, unit: str) -> str
    def get_command_info(self, command_code: int) -> Dict[str, Any]
```

#### ConsoleDisplay Class
```python
class ConsoleDisplay:
    def show_startup_banner(self)
    def display_command_sending(self, command_info: Dict)
    def display_response_received(self, response_data: Dict)
    def show_progress(self, current: int, total: int)
    def display_final_summary(self, results: List[Dict])
    def show_error(self, error_message: str)
```

## 📊 Protocol Specification Integration

### GE Healthcare Protocol Message Format
Based on the RS422 implementation report, the complete message structure is:
```
[0xAA] [0x23] [CMD] [LEN] [DATA...] [CRC8]
```
- **Preamble (0xAA)**: GE Healthcare Protocol identifier
- **Sync Header (0x23)**: Host-to-battery direction indicator  
- **Command Code**: SMBus-compatible command byte (0x00-0xFF)
- **Data Length**: Number of data bytes following
- **Data Bytes**: Command payload (optional)
- **CRC-8**: SMBus PEC polynomial checksum

### Command Data Structure (from gehc-rs422-protocol.json)
- **68 Total Commands** available in the protocol specification
- **Command Categories**:
  - Basic battery data (voltage, current, SOC, capacity)
  - Cell monitoring (individual cell voltages)
  - Temperature sensors (up to 8 sensors)
  - Safety and protection (fault/warning registers)
  - Device information (manufacturer, serial number, etc.)
  - Advanced features (AtRate calculations, time predictions)

### Data Type Mapping
```python
DATA_TYPE_MAPPING = {
    "unsigned int": {"size": 2, "format": "H", "signed": False},
    "signed int": {"size": 2, "format": "h", "signed": True},
    "word": {"size": 2, "format": "H", "signed": False},
    "Boolean": {"size": 2, "format": "H", "converter": lambda x: bool(x)},
    "string": {"size": "variable", "format": "s"},
    "block data": {"size": "variable", "format": "raw"}
}
```

### Scaling and Units Processing
```python
SCALING_INFO = {
    "0x09": {"unit": "mV", "granularity": 10, "range": "0 to 65535"},
    "0x0A": {"unit": "mA", "granularity": 100, "range": "0 to ±50000"},
    "0x08": {"unit": "°C", "granularity": 1, "range": "-40 to 120"},
    "0x0D": {"unit": "%", "granularity": 1, "range": "0 to 100"},
    # ... additional scaling definitions
}
```

## 🔄 Development Workflow with Claude Flow Agents

### Parallel Agent Development Strategy
1. **Architecture Agent**: Design overall system architecture and module interfaces
2. **Communication Agent**: Implement RS422 serial communication and protocol handling
3. **Parser Agent**: Develop message parsing, data scaling, and type conversion
4. **Display Agent**: Create Rich library console output and formatting
5. **Configuration Agent**: Handle JSON configuration and command loading
6. **Testing Agent**: Develop comprehensive unit and integration tests
7. **Integration Agent**: Coordinate component integration and final testing

### Agent Coordination Requirements
- **Shared Memory**: Use Claude Flow memory for cross-agent state coordination
- **Hook Integration**: Mandatory pre-task, post-edit, and post-task hooks
- **Parallel Execution**: All agents work concurrently with proper synchronization
- **Performance Monitoring**: Track development progress and bottlenecks

## 🧪 Testing Strategy

### Unit Testing Requirements
- **Communication Layer**: Mock serial port for protocol testing
- **Parser Layer**: Test data scaling, type conversion, unit formatting
- **Configuration Layer**: Validate JSON loading and error handling
- **Display Layer**: Test Rich library output formatting

### Integration Testing
- **End-to-End Workflow**: Complete command send/receive/parse cycle
- **Error Scenarios**: Timeout handling, CRC validation failures
- **Edge Cases**: Malformed responses, communication interruptions
- **Performance Testing**: Timing validation, memory usage monitoring

### Hardware Testing (if available)
- **Real PHTC Device**: Test with actual hardware communication
- **Command Validation**: Verify all implemented commands work correctly
- **Long-term Stability**: Extended operation testing
- **Error Recovery**: Test communication failure recovery

## 📦 Dependencies and Environment

### Python Requirements
```txt
pyserial>=3.5
rich>=13.0.0
pydantic>=2.0.0
pytest>=7.0.0
pytest-mock>=3.10.0
black>=23.0.0
mypy>=1.0.0
```

### Development Environment
- **Python Version**: 3.8+ (prefer 3.11+)
- **Virtual Environment**: Required for dependency isolation
- **Code Style**: Black formatter, type hints with mypy
- **Documentation**: Comprehensive docstrings and README

### Hardware Requirements
- **RS422 Interface**: USB-to-RS422 converter or built-in RS422 port
- **PHTC Device**: For real hardware testing (optional for development)
- **Test Environment**: Windows/Linux compatibility

## 🎯 Success Criteria

### Functional Requirements
- [x] Successfully send commands to PHTC device over RS422
- [x] Receive and validate responses with CRC-8 checking
- [x] Parse response data with correct data types and scaling
- [x] Display formatted output with units using Rich library
- [x] Handle configuration through JSON files
- [x] Implement proper error handling and recovery
- [x] Maintain minimum 0.5-second delay between commands

### Quality Requirements
- [x] 90%+ test coverage across all modules
- [x] Type hints for all public interfaces
- [x] Comprehensive error logging
- [x] Performance monitoring and optimization
- [x] Clean, maintainable code structure
- [x] Detailed documentation and examples

### Performance Requirements
- [x] Command processing latency < 100ms (excluding communication time)
- [x] Memory usage < 50MB during operation
- [x] Support for continuous operation (hours)
- [x] Graceful degradation on communication errors
- [x] Real-time console updates without blocking

## 🚀 Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
- Serial communication handler
- Basic protocol implementation
- Configuration management
- Project structure setup

### Phase 2: Message Processing (Week 1-2)
- Response parsing and validation
- Data type conversion and scaling
- Unit formatting and display
- Error handling implementation

### Phase 3: User Interface (Week 2)
- Rich library integration
- Console output formatting
- Progress indicators and status display
- Command execution workflow

### Phase 4: Testing & Validation (Week 2-3)
- Comprehensive unit testing
- Integration testing
- Hardware validation (if available)
- Performance optimization

### Phase 5: Documentation & Deployment (Week 3)
- User documentation
- API documentation
- Deployment packaging
- Final validation and release

## 📝 Documentation Requirements

### User Documentation
- **Installation Guide**: Setup instructions and dependencies
- **Configuration Guide**: JSON file configuration and command setup
- **Usage Examples**: Common use cases and command examples
- **Troubleshooting**: Common issues and solutions

### Developer Documentation
- **Architecture Overview**: System design and module interactions
- **API Reference**: Class and method documentation
- **Protocol Implementation**: GEHC RS422 protocol details
- **Extension Guide**: Adding new commands and features

### Testing Documentation
- **Test Plans**: Comprehensive testing strategy
- **Test Results**: Validation results and performance metrics
- **Hardware Setup**: Physical test environment configuration
- **Automation**: Continuous integration and testing automation

This prompt provides a comprehensive foundation for developing the GEHC PHTC RS422 communication test application using Claude Flow's parallel agent development methodology. The structured approach ensures all requirements are addressed while maintaining code quality and performance standards.