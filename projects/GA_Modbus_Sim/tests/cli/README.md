# CLI Unit Tests

This directory contains comprehensive unit tests for the CLI interface components of the GA BMS Monitor application.

## Test Structure

```
tests/cli/
├── __init__.py                    # Package initialization
├── fixtures.py                    # Test fixtures and mock objects
├── test_bms_cli.py               # Tests for main BMS CLI interface
├── test_cli_demo.py              # Tests for CLI demo interface
├── test_temp_cli_launcher.py     # Tests for CLI launcher
├── test_cli_integration.py       # Integration tests for CLI workflows
├── test_runner.py                # Test runner utility
└── README.md                     # This file
```

## Test Coverage

### Main CLI Interface (`test_bms_cli.py`)
- **BMSCLIShell class**: 50+ test cases covering all CLI commands
- **Connection Management**: Connect, disconnect, status checking
- **Session Management**: Create, list, load, delete sessions
- **Data Logging**: Start/stop logging, monitoring threads
- **Plugin System**: Plugin loading, execution, management
- **Settings Management**: Configuration get/set operations
- **Auto Features**: Auto start/stop, runaway detection
- **Error Handling**: Invalid commands, connection failures
- **Command Line Arguments**: Single command execution, script mode

### CLI Demo Interface (`test_cli_demo.py`)
- **Demo Commands**: All demo commands (status, data, sessions, plugins)
- **Rich Integration**: Rich formatting with fallback to plain text
- **Help System**: Help commands for all demo features
- **Interactive Mode**: Command completion and error handling
- **Styling**: Rich table and panel creation

### CLI Launcher (`test_temp_cli_launcher.py`)
- **Path Management**: Project root calculation, sys.path modifications
- **Import Handling**: Successful imports, fallback mechanisms
- **Error Recovery**: ImportError handling, graceful degradation
- **Environment Setup**: PYTHONPATH configuration
- **Edge Cases**: Permission errors, keyboard interrupts

### Integration Tests (`test_cli_integration.py`)
- **Complete Workflows**: End-to-end monitoring workflows
- **Session Management**: Full session lifecycle testing
- **Plugin Workflows**: Plugin loading and execution
- **Configuration Management**: Settings modification workflows
- **Error Recovery**: Connection failure handling
- **Performance**: Rapid command execution, memory usage

## Test Fixtures

The `fixtures.py` file provides comprehensive mock objects:

- **MockModbusWorker**: Simulates Modbus communication
- **MockSessionManager**: Handles session management testing
- **MockConfigManager**: Configuration management testing
- **MockPluginManager**: Plugin system testing
- **Sample Data**: Battery data and session data for testing

## Running Tests

### Prerequisites
Install test dependencies:
```bash
pip install pytest pytest-cov
```

### Run All CLI Tests
```bash
python3 tests/cli/test_runner.py
```

### Run Specific Test
```bash
python3 tests/cli/test_runner.py test_bms_cli
```

### Run with Coverage
```bash
python3 tests/cli/test_runner.py coverage
```

### Using pytest directly
```bash
# Run all CLI tests
pytest tests/cli/ -v

# Run specific test file
pytest tests/cli/test_bms_cli.py -v

# Run with coverage
pytest tests/cli/ --cov=src.cli --cov=cli_demo --cov=temp_cli_launcher --cov-report=html
```

## Test Categories

### Unit Tests
- Individual function and method testing
- Mock object isolation
- Component behavior verification

### Integration Tests
- Complete workflow testing
- Multi-component interaction
- Error handling scenarios

### Performance Tests
- Rapid command execution
- Memory usage monitoring
- Thread safety verification

## Mock Strategy

The tests use extensive mocking to:
- Isolate CLI components from hardware dependencies
- Simulate various error conditions
- Test edge cases and error recovery
- Verify component interactions

## Key Testing Principles

1. **Isolation**: Each test is independent and doesn't affect others
2. **Mocking**: Hardware dependencies are mocked for reliable testing
3. **Coverage**: All major code paths and error conditions are tested
4. **Integration**: Real-world workflows are tested end-to-end
5. **Performance**: Response times and resource usage are verified

## Adding New Tests

When adding new CLI features:

1. **Update fixtures.py**: Add new mock objects as needed
2. **Add unit tests**: Test individual components in isolation
3. **Add integration tests**: Test complete workflows
4. **Update this README**: Document new test coverage

## Test Results

All tests should pass with the current implementation. If tests fail:

1. Check dependency installation (pytest, mock libraries)
2. Verify Python path configuration
3. Review any changes to CLI interface
4. Check mock object compatibility

## Continuous Integration

These tests are designed to run in CI/CD environments:
- No external dependencies required
- All hardware interactions are mocked
- Fast execution time
- Comprehensive coverage reporting