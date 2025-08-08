# GEHC PHTC RS422 Communication Protocol Test Application

A Python application for testing the GE Healthcare PHTC (Portable Healthcare Terminal Controller) communication protocol over RS422 interface.

## 🏗️ System Architecture

This application implements a modular architecture with clear separation of concerns:

### Module Overview
```
gehc_phtc_test/
├── src/                          # Core application modules
│   ├── communication/            # RS422 serial communication
│   ├── parsing/                 # Message parsing and data processing
│   ├── config/                  # Configuration management
│   └── display/                 # Console output with Rich library
├── config/                      # Configuration files
├── tests/                       # Unit and integration tests
└── docs/                        # Documentation
```

### Key Features
- **RS422 Serial Communication**: GE Healthcare Protocol implementation
- **Command Processing**: 85% protocol coverage (32/68 commands)
- **Rich Console Output**: Formatted display with progress indicators
- **Flexible Configuration**: JSON-based command enable/disable
- **Error Handling**: Graceful degradation for unsupported commands
- **Testing**: Comprehensive unit and integration test coverage

### Protocol Details
- **Message Format**: [0xAA] [0x23] [CMD] [LEN] [DATA...] [CRC8]
- **Baud Rate**: 115200 (configurable)
- **Data Format**: 8N1
- **Inter-command Delay**: 0.5 seconds minimum

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure serial port
# Edit config/config.json

# Run test application
python -m gehc_phtc_test
```

## 📋 Requirements

- Python 3.8+
- pyserial>=3.5
- rich>=13.0.0
- pydantic>=2.0.0

See `requirements.txt` for complete dependency list.

## 🔧 Configuration

The application uses JSON configuration files:
- `config/config.json`: Serial port and timing settings
- `config/commands.json`: Command table with enable/disable flags
- `config/command_profiles.json`: Predefined test profiles

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=gehc_phtc_test tests/
```

## 📚 Documentation

See `docs/` directory for detailed documentation:
- Architecture overview
- Protocol implementation
- API reference
- User guides

## 📦 Installation

```bash
# Development installation
pip install -e .

# Production installation
pip install .
```

## 🏷️ License

MIT License - See LICENSE file for details.