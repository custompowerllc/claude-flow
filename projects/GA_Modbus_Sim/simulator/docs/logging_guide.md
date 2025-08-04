# GA Modbus Simulator - Logging Configuration Guide

## Overview

The GA Modbus BMS Simulator includes comprehensive logging capabilities to help with debugging, monitoring, and troubleshooting. This guide covers all aspects of logging configuration and usage.

## Quick Start

### Basic Logging
```bash
# Standard logging (INFO level) - default
python3 run_simulator.py --port COM4

# Verbose logging (DEBUG level)
python3 run_simulator.py --port COM4 --verbose
```

## Log Levels

The simulator uses Python's standard logging levels:

| Level | Description | Use Case |
|-------|-------------|----------|
| `DEBUG` | Detailed diagnostic information | Development, troubleshooting |
| `INFO` | General operational messages | Normal operation |
| `WARNING` | Important alerts | Potential issues |
| `ERROR` | Error conditions | Failed operations |

### Setting Log Levels

**Command Line:**
```bash
# Enable DEBUG level logging
python3 run_simulator.py --port COM4 --verbose

# Standard INFO level (default)
python3 run_simulator.py --port COM4
```

**Programmatic:**
```python
import logging

# Set to DEBUG level
logging.basicConfig(level=logging.DEBUG)

# Set to INFO level
logging.basicConfig(level=logging.INFO)
```

## Log Output Format

The default log format includes:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**Example output:**
```
2025-01-01 10:30:45,123 - simulator.src.core.modbus_server - INFO - ModbusSimulatorServer initialized for COM4
2025-01-01 10:30:45,124 - simulator.src.core.register_handler - INFO - RegisterHandler initialized with 36 registers
2025-01-01 10:30:45,125 - simulator.src.core.modbus_server - INFO - Starting Modbus server on COM4
```

## Component-Specific Logging

### ModbusSimulatorServer Logs

**INFO Level:**
- Server initialization
- Server start/stop events
- Port validation results
- Connection status

**DEBUG Level:**
- Register update cycles
- Detailed server state changes
- Thread management

**Example:**
```
INFO - ModbusSimulatorServer initialized for COM4
INFO - Port COM4 is available
INFO - Starting Modbus server on COM4
INFO - Starting Modbus RTU server on COM4
INFO - Modbus server started successfully
DEBUG - Updated 36 registers
```

### RegisterHandler Logs

**INFO Level:**
- Handler initialization
- Scenario changes
- Register map loading

**DEBUG Level:**
- Individual register updates
- Simulation state changes
- Value calculations

**WARNING Level:**
- Unknown register access
- Import fallbacks

**Example:**
```
INFO - RegisterHandler initialized with 36 registers
INFO - Set scenario to: Charging - 1A (charging)
DEBUG - Updated simulation for scenario: Charging - 1A
DEBUG - Updated register afe_current = 1000
WARNING - Unknown register: invalid_register_name
```

### ComPortManager Logs

**INFO Level:**
- Port availability checks
- Port recommendations

**WARNING Level:**
- Port conflicts
- Device detection issues

**Example:**
```
INFO - Found 5 available ports
WARNING - Port COM3 may be in use by GA device
INFO - Recommended ports: COM4, COM5
```

## Advanced Logging Configuration

### File Output

To save logs to a file, modify the logging configuration:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simulator.log'),
        logging.StreamHandler()  # Also log to console
    ]
)
```

### Multiple Handlers

Configure different outputs for different log levels:

```python
import logging

# Create logger
logger = logging.getLogger('simulator')
logger.setLevel(logging.DEBUG)

# Create formatters
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
simple_formatter = logging.Formatter('%(levelname)s: %(message)s')

# File handler for detailed logs
file_handler = logging.FileHandler('simulator_debug.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(detailed_formatter)

# Console handler for important messages
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(simple_formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)
```

### Rotating Logs

For long-running instances, use rotating file handlers:

```python
import logging
from logging.handlers import RotatingFileHandler

# Rotating file handler (10MB max, 3 backups)
rotating_handler = RotatingFileHandler(
    'simulator.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=3
)
rotating_handler.setLevel(logging.INFO)
rotating_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)

logger = logging.getLogger('simulator')
logger.addHandler(rotating_handler)
```

### Time-Based Rotation

For daily log rotation:

```python
import logging
from logging.handlers import TimedRotatingFileHandler

# Daily rotation at midnight
time_handler = TimedRotatingFileHandler(
    'simulator.log',
    when='midnight',
    interval=1,
    backupCount=7  # Keep 7 days
)
time_handler.setLevel(logging.INFO)
```

## Filtering Logs

### By Component

```python
# Only log from ModbusSimulatorServer
logging.getLogger('simulator.src.core.modbus_server').setLevel(logging.DEBUG)
logging.getLogger('simulator.src.core.register_handler').setLevel(logging.WARNING)
```

### By Level

```python
# Custom filter to exclude DEBUG from console but allow in file
class LevelFilter(logging.Filter):
    def __init__(self, level):
        self.level = level
    
    def filter(self, record):
        return record.levelno >= self.level

console_handler.addFilter(LevelFilter(logging.INFO))
file_handler.addFilter(LevelFilter(logging.DEBUG))
```

## Performance Considerations

### DEBUG Level Impact

DEBUG logging can impact performance:
- High-frequency register updates are logged
- Detailed thread operations are captured
- I/O operations increase

**Recommendations:**
- Use DEBUG only during development/troubleshooting
- Use INFO for production environments
- Consider filtered logging for specific components

### Log File Size Management

Monitor log file sizes in production:
- Implement log rotation
- Set appropriate retention periods
- Monitor disk space usage

## Common Logging Patterns

### Startup Sequence

```
INFO - ModbusSimulatorServer initialized for COM4
INFO - RegisterHandler initialized with 36 registers
INFO - Port COM4 is available
INFO - Server context created with 36 registers
INFO - Starting Modbus server on COM4
INFO - Starting Modbus RTU server on COM4
INFO - Modbus server started successfully
```

### Normal Operation

```
DEBUG - Updated 36 registers
DEBUG - Updated simulation for scenario: Idle - Balanced
DEBUG - Updated register afe_cell_volt1 = 3800
DEBUG - Updated register afe_pack_volt = 30400
```

### Error Conditions

```
ERROR - Port COM4 is not available: [Errno 2] could not open port COM4
ERROR - Error starting server: Port COM4 unavailable
WARNING - Port COM4 not found. Available: ['COM3', 'COM5']
```

### Scenario Changes

```
INFO - Set scenario to: Charging - 1A (charging)
DEBUG - Updated simulation for scenario: Charging - 1A
DEBUG - Current simulation: 1000mA, SOC: 65%, Temp: 25.5°C
```

## Troubleshooting with Logs

### Common Issues and Log Patterns

**Port Not Available:**
```
ERROR - Port COM4 is not available: [Errno 2] could not open port COM4
```
*Solution: Check port availability with `--list-ports`*

**Server Start Failure:**
```
ERROR - Failed to start Modbus server
ERROR - Error starting server: [specific error message]
```
*Solution: Check port permissions and availability*

**Register Update Issues:**
```
WARNING - Unknown register: invalid_register_name
ERROR - Error updating register afe_current: [error details]
```
*Solution: Verify register names and value ranges*

**Simulation Problems:**
```
ERROR - Error updating simulation: [error details]
DEBUG - Updated simulation for scenario: [scenario name]
```
*Solution: Check scenario configuration and parameters*

## Best Practices

### Development
- Use DEBUG level for detailed troubleshooting
- Monitor specific component logs
- Use file output for log analysis

### Production
- Use INFO level for normal operation
- Implement log rotation
- Monitor for ERROR and WARNING messages
- Set up log aggregation for multiple instances

### Performance Testing
- Disable DEBUG logging during performance tests
- Use filtered logging for specific metrics
- Monitor log I/O impact on overall performance

## Integration Examples

### With Systemd (Linux)

```ini
[Unit]
Description=GA Modbus Simulator
After=network.target

[Service]
Type=simple
User=simulator
WorkingDirectory=/opt/ga-simulator
ExecStart=/usr/bin/python3 run_simulator.py --port /dev/ttyUSB0 --verbose
StandardOutput=journal
StandardError=journal
Restart=always

[Install]
WantedBy=multi-user.target
```

### With Docker

```dockerfile
FROM python:3.9-slim

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

# Configure logging to container stdout
ENV PYTHONUNBUFFERED=1

CMD ["python3", "run_simulator.py", "--port", "/dev/ttyUSB0", "--verbose"]
```

### With Monitoring Systems

```python
# Example: Sending logs to external monitoring
import logging
import requests

class MonitoringHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            # Send error logs to monitoring system
            requests.post('http://monitoring/api/alerts', {
                'level': record.levelname,
                'message': record.getMessage(),
                'timestamp': record.created
            })

logger.addHandler(MonitoringHandler())
```

This comprehensive logging system enables effective monitoring, debugging, and maintenance of the GA Modbus BMS Simulator.