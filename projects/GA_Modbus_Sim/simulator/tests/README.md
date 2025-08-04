# Modbus BMS Simulator - Test Suite

This directory contains comprehensive unit and integration tests for the Modbus BMS Simulator Phase 1 implementation.

## 📁 Test Structure

```
tests/
├── unit/                           # Unit tests for individual components
│   ├── test_modbus_server.py      # Modbus server functionality tests
│   ├── test_register_handler.py   # Register value handling tests
│   └── test_com_port.py           # Virtual COM port tests
├── integration/                    # End-to-end integration tests
│   └── test_modbus_integration.py # Complete workflow tests
├── conftest.py                    # Pytest configuration and fixtures
├── pytest.ini                    # Pytest settings
├── requirements.txt               # Test dependencies
├── run_tests.py                   # Test runner script
└── README.md                      # This file
```

## 🧪 Test Categories

### Unit Tests

**test_modbus_server.py**
- Server initialization and configuration
- Modbus protocol compliance (GA app compatibility)
- `read_input_registers` implementation
- Error handling and edge cases
- Performance and memory usage
- Concurrent request handling

**test_register_handler.py**  
- BMS register value generation
- Physics-based battery simulation (8S LiFePO4)
- Data consistency validation
- Scenario-based value generation
- Register value range validation
- State management and updates

**test_com_port.py**
- Virtual COM port creation (com0com/socat)
- Cross-platform compatibility (Windows/Linux/macOS)
- Port discovery and validation
- Serial communication testing
- Error handling and cleanup
- Resource management

### Integration Tests

**test_modbus_integration.py**
- Complete server + client communication
- GA Modbus Python App protocol compatibility
- CSV data logging validation
- Real-world scenario testing
- Performance under load
- Multi-client support
- End-to-end workflow validation

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install test requirements
python run_tests.py install

# Or manually:
pip install -r requirements.txt
```

### 2. Run Tests

```bash
# Run all tests (recommended)
python run_tests.py all -v

# Run specific test suites
python run_tests.py unit           # Unit tests only
python run_tests.py integration    # Integration tests only
python run_tests.py performance    # Performance tests
python run_tests.py serial         # Hardware-dependent tests

# Generate coverage report
python run_tests.py all -c
```

### 3. Check Dependencies

```bash
# Verify all required packages are installed
python run_tests.py check
```

## 📊 Test Coverage

The test suite provides comprehensive coverage of:

- **Modbus Protocol**: 100% GA app compatibility validation
- **Register Mapping**: All 36 registers (addresses 10-45) tested
- **Data Accuracy**: Physics-based LiFePO4 battery simulation
- **Error Handling**: Edge cases and fault conditions
- **Performance**: Load testing and memory usage validation
- **Cross-Platform**: Windows, Linux, and macOS support

## 🎯 Key Test Scenarios

### GA App Compatibility Tests
- Exact Modbus query: `read_input_registers(address=9, count=36)`
- Register mapping validation (registers 10-45)
- CSV output format verification
- Data type and range validation

### BMS Physics Simulation Tests
- 8S LiFePO4 cell voltage ranges (2.5V - 3.65V)
- Pack voltage = sum of cell voltages
- Cell delta calculation accuracy
- Temperature sensor simulation (-40°C to +85°C)
- Current simulation for different scenarios
- SOC/SOH calculations and relationships

### Virtual COM Port Tests
- com0com support (Windows)
- socat support (Linux/macOS)
- Port pair creation and cleanup
- Communication validation
- Error handling for missing tools

### Performance Tests
- 10+ queries per second capability
- Memory usage stability
- Concurrent client support
- Extended operation reliability

## 📋 Test Markers

Tests are organized with pytest markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests  
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run performance tests
pytest -m "slow or performance"

# Run serial hardware tests
pytest -m serial
```

## 🔧 Configuration

### Pytest Settings (`pytest.ini`)
- Test discovery patterns
- Output formatting
- Marker definitions
- Warning filters
- Timeout settings

### Test Fixtures (`conftest.py`)
- Temporary directories
- Mock register maps
- Realistic BMS data
- Serial port mocks
- Test utilities

## 📈 Running Tests in CI/CD

For automated testing environments:

```bash
# Fast test suite (no hardware dependencies)
pytest -m "not serial and not slow" --tb=short

# Full test suite with coverage
pytest --cov=../src --cov-report=xml --cov-fail-under=80

# Performance validation
pytest -m performance --benchmark-only
```

## 🐛 Debugging Failed Tests

### Common Issues

1. **Missing Dependencies**
   ```bash
   python run_tests.py check
   python run_tests.py install
   ```

2. **Virtual COM Port Tools Missing**
   - Windows: Install com0com
   - Linux/macOS: Install socat
   - Tests will use fallback mocks if tools unavailable

3. **Port Already in Use**
   - Tests use dynamic port allocation
   - Cleanup happens automatically after each test

4. **Timeout Issues**
   - Increase timeout in pytest.ini
   - Check system performance during tests

### Verbose Output

```bash
# Maximum verbosity for debugging
pytest -vvv --tb=long --capture=no
```

## 🔍 Test Data Validation

### Register Value Ranges
- Cell voltages: 2500-3650mV (LiFePO4 safe range)
- Pack voltage: 20000-29200mV (8S pack)
- Cell delta: 0-500mV (healthy battery range)
- Temperatures: -400 to 850 (in tenths of degrees)
- SOC/SOH: 0-100%
- Current: -50A to +50A

### CSV Format Validation
- Header matches GA app exactly
- Timestamp format: "YYYY-MM-DD HH:MM:SS"
- Column order matches register sequence
- Data types are numeric where expected

## 📚 Additional Resources

- [GA Modbus Python App Documentation](../../README.md)
- [Implementation Plan](../../docs/implementation-plans/simulator/CORRECTED_IMPLEMENTATION_PLAN.md)
- [Register Mapping Analysis](../../docs/implementation-plans/simulator/FINAL_REGISTER_MAPPING_ANALYSIS.md)

## ⚡ Performance Benchmarks

Expected test performance:
- Unit tests: < 30 seconds
- Integration tests: < 60 seconds  
- Performance tests: < 120 seconds
- Full suite with coverage: < 180 seconds

## 🤝 Contributing

When adding new tests:

1. Follow existing naming conventions
2. Add appropriate markers
3. Include docstrings explaining test purpose
4. Validate against realistic BMS data ranges
5. Ensure cross-platform compatibility
6. Add cleanup in tearDown methods

## 📝 Test Reports

Generate comprehensive test reports:

```bash
# HTML report with coverage
python run_tests.py report

# Files generated:
# - test_report.html (test results)
# - htmlcov/index.html (coverage report)
```