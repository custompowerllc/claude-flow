# BK-Integration CLI Usage Guide

## Quick Start

The BK-Integration CLI provides unified control for BK8520 Electronic Load and BK9206b Power Supply devices through a comprehensive command-line interface.

### Prerequisites

1. **Python Environment**: Python 3.8 or higher with virtual environment
2. **Device Connectivity**: Both BK8520 and BK9206b must be accessible via their API endpoints
3. **Configuration**: Valid `config.json` file with device settings

### Installation & Setup

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Install dependencies  
venv/bin/pip install click rich httpx requests fastapi uvicorn pydantic python-dotenv pyyaml pandas numpy

# 3. Copy and configure settings
cp config.example.json config.json
# Edit config.json with your device IP addresses and settings

# 4. Use the convenience wrapper script
chmod +x bk-cli.sh
./bk-cli.sh --help
```

## Core Commands

### Device Management

```bash
# Check device status
./bk-cli.sh device status

# Connect to both devices with safety validation
./bk-cli.sh device connect

# Show detailed device information
./bk-cli.sh device info

# Safely disconnect from devices
./bk-cli.sh device disconnect
```

### Configuration Management

```bash
# Display current configuration
./bk-cli.sh config show

# Validate configuration and test profiles
./bk-cli.sh config validate
```

### Battery Testing

```bash
# List available test profiles
./bk-cli.sh test list-profiles

# Validate test setup without running (dry-run)
./bk-cli.sh test battery --profile default --dry-run

# Run battery test with default profile
./bk-cli.sh test battery --profile default

# Run multiple cycles with high-capacity profile
./bk-cli.sh test battery --profile high_capacity --cycles 3

# Create custom test profile
./bk-cli.sh test create-profile \
  --profile custom_24v \
  --voltage 28.4 \
  --current 3.0 \
  --discharge 8.0 \
  --cutoff 21.0 \
  --rest 120
```

### Real-time Monitoring

```bash
# Basic monitoring (Ctrl+C to stop)
./bk-cli.sh monitor

# Monitor with custom update interval
./bk-cli.sh monitor --interval 0.5

# Monitor for specific duration with data export
./bk-cli.sh monitor --duration 300 --export test_data.csv

# High-frequency monitoring
./bk-cli.sh monitor --interval 0.1 --duration 60
```

### Safety Monitoring

```bash
# Show safety system status
./bk-cli.sh safety status

# View recent safety events
./bk-cli.sh safety events

# Filter events by level and device
./bk-cli.sh safety events --level warning --device bk8520 --hours 12
```

### API Server Mode

```bash
# Start REST API server
./bk-cli.sh serve --port 8080

# Start with auto-reload for development
./bk-cli.sh serve --host 0.0.0.0 --port 8080 --reload
```

## Configuration

### Device Settings

The `config.json` file contains device endpoints and safety limits:

```json
{
  "devices": {
    "load_tester": {
      "name": "BK8520",
      "device_url": "http://10.100.10.190:8000",
      "port": 8000,
      "serial_port": "/dev/ttyUSB0"
    },
    "power_supply": {
      "name": "BK9206b", 
      "device_url": "http://10.100.10.190:5300",
      "port": 5300
    }
  }
}
```

### Test Profiles

Built-in profiles:
- **default**: Standard 12V lead-acid (16.8V charge, 2.0A charge current, 5.0A discharge)
- **high_capacity**: Large batteries (16.8V charge, 4.0A charge current, 10.0A discharge)  
- **low_current**: Sensitive batteries (16.8V charge, 1.0A charge current, 2.0A discharge)

### Environment Variables

Override configuration with environment variables:

```bash
export BK_LOAD_URL="http://192.168.1.100:8000"
export BK_POWER_URL="http://192.168.1.100:5300"
export BK_LOAD_PORT="/dev/ttyUSB1"
export BK_LOG_LEVEL="DEBUG"
```

## Safety Features

### Input Validation
- All parameters validated against device specifications
- Voltage limits: Load 120V max, Power 60V max
- Current limits: Load 60A max, Power 5A max

### Emergency Stops
- **Ctrl+C**: Immediate shutdown during any operation
- **Safety Monitor**: Automatic protection on parameter violations
- **Connection Health**: Automatic detection of communication failures

### Monitoring Thresholds
```json
{
  "safety": {
    "voltage_tolerance_percent": 5.0,
    "current_tolerance_percent": 10.0,
    "max_consecutive_failures": 5
  }
}
```

## Logging and Troubleshooting

### Log Files
- **Location**: `bk_integration.log` (configurable)
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Rotation**: Automatic with size limits

### Verbose Mode
```bash
# Enable detailed logging
./bk-cli.sh --verbose device status
```

### Common Issues

1. **Connection Failures**: Check device IP addresses and API availability
2. **Configuration Errors**: Use `config validate` to identify issues
3. **Permission Errors**: Ensure serial port access permissions
4. **Safety Violations**: Review safety event logs

## API Integration

When running in server mode, the CLI exposes REST endpoints:

### Health Check
```bash
curl http://localhost:8080/api/health
```

### Start Battery Test
```bash
curl -X POST http://localhost:8080/api/test/battery \
  -H "Content-Type: application/json" \
  -d '{"profile": "default", "cycles": 1}'
```

### WebSocket Monitoring
```javascript
const ws = new WebSocket('ws://localhost:8080/ws/monitor');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Device readings:', data);
};
```

## Advanced Usage

### Batch Operations
```bash
# Run multiple test profiles in sequence
for profile in default high_capacity low_current; do
  ./bk-cli.sh test battery --profile $profile --cycles 1
  sleep 60  # Rest between tests
done
```

### Data Analysis
```bash
# Export monitoring data for analysis
./bk-cli.sh monitor --duration 3600 --export hourly_data.csv
# Process with pandas, Excel, etc.
```

### Custom Scripting
```python
import subprocess
import json

# Run CLI and capture output
result = subprocess.run([
  './bk-cli.sh', 'device', 'status'
], capture_output=True, text=True)

print("Device status:", result.stdout)
```

## Performance Optimization

### Monitoring Intervals
- **Real-time**: 0.1s (high CPU usage)
- **Standard**: 1.0s (balanced)
- **Low-frequency**: 5.0s+ (minimal overhead)

### Resource Usage
- **Memory**: ~50MB baseline + data logging
- **Network**: Minimal HTTP requests to device APIs
- **Storage**: Log files and exported data only

## Support and Documentation

- **Configuration Reference**: See `config.example.json`
- **API Documentation**: Available in `docs/api/` directory  
- **Device Manuals**: Check manufacturer documentation
- **Error Codes**: See device API documentation for specific error meanings