# GA Modbus Simulator - Logging Troubleshooting Guide

## Overview

This guide addresses common logging issues and provides solutions for diagnosing problems with the GA Modbus BMS Simulator's logging system.

## Quick Diagnostics

### Check Current Logging Status

```bash
# Test basic logging functionality
python3 run_simulator.py --list-ports

# Test verbose logging
python3 run_simulator.py --list-ports --verbose
```

**Expected Output:**
- Standard: Shows port list with INFO-level messages
- Verbose: Shows additional DEBUG messages about port detection

## Common Logging Issues

### 1. No Log Output Visible

**Symptoms:**
- Simulator runs but no log messages appear
- Console output is empty or minimal

**Possible Causes:**
- Logging level set too high
- Output redirected to file
- Console encoding issues

**Solutions:**

**Check Logging Configuration:**
```bash
# Force verbose mode
python3 run_simulator.py --port COM4 --verbose
```

**Verify Python Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')
logger.info("Test message")
```

**Check Environment Variables:**
```bash
# Check if logging is being redirected
echo $PYTHONUNBUFFERED
env | grep -i log
```

### 2. Too Much Log Output

**Symptoms:**
- Console flooded with DEBUG messages
- Performance degradation
- Difficult to find important information

**Solutions:**

**Reduce Logging Level:**
```bash
# Remove --verbose flag
python3 run_simulator.py --port COM4  # INFO level only
```

**Filter Specific Components:**
```python
import logging

# Reduce specific component logging
logging.getLogger('simulator.src.core.register_handler').setLevel(logging.WARNING)
logging.getLogger('pymodbus').setLevel(logging.ERROR)
```

**Use Custom Configuration:**
```python
# In run_simulator.py, modify logging setup:
logging.basicConfig(
    level=logging.INFO,  # Change from DEBUG
    format='%(levelname)s: %(message)s'  # Simplified format
)
```

### 3. Missing Debug Information

**Symptoms:**
- ERROR messages appear but no context
- Difficult to diagnose issues
- Missing detailed operation logs

**Solutions:**

**Enable Debug Mode:**
```bash
python3 run_simulator.py --port COM4 --verbose
```

**Add Custom Debug Logging:**
```python
# Temporary debug additions
import logging
logging.getLogger('simulator').setLevel(logging.DEBUG)

# Add to specific operations
logger.debug("Port validation: port={}, available={}".format(port, available))
```

**Check Component-Specific Logging:**
```python
# Enable specific component debugging
logging.getLogger('simulator.src.core.modbus_server').setLevel(logging.DEBUG)
logging.getLogger('simulator.src.core.register_handler').setLevel(logging.DEBUG)
```

### 4. Log Messages Not Formatted Correctly

**Symptoms:**
- Timestamps missing
- Component names unclear
- Inconsistent message format

**Solutions:**

**Standard Format Configuration:**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

**Detailed Format for Debugging:**
```python
detailed_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
```

**Custom Format Examples:**
```python
# Minimal format
simple_format = logging.Formatter('%(levelname)s: %(message)s')

# With thread info
thread_format = logging.Formatter(
    '%(asctime)s [%(threadName)s] %(name)s - %(levelname)s - %(message)s'
)
```

### 5. Performance Impact from Logging

**Symptoms:**
- Simulator runs slowly
- High CPU usage
- Delayed responses to Modbus queries

**Diagnosis:**
```bash
# Compare performance with different logging levels
time python3 run_simulator.py --port COM4 --verbose  # DEBUG
time python3 run_simulator.py --port COM4           # INFO
```

**Solutions:**

**Reduce Logging Frequency:**
```python
# In register_handler.py, reduce update logging
def update_simulation(self):
    # Log every 10th update instead of every update
    self._update_count = getattr(self, '_update_count', 0) + 1
    if self._update_count % 10 == 0:
        self.logger.debug("Updated simulation (count: {})".format(self._update_count))
```

**Use Conditional Logging:**
```python
# Only log if debug level is enabled
if self.logger.isEnabledFor(logging.DEBUG):
    self.logger.debug("Expensive debug operation: {}".format(expensive_calculation()))
```

**Async Logging (Advanced):**
```python
import logging.handlers
import queue

# Use QueueHandler for non-blocking logging
log_queue = queue.Queue()
queue_handler = logging.handlers.QueueHandler(log_queue)
logger.addHandler(queue_handler)
```

### 6. Log File Issues

**Symptoms:**
- Cannot write to log file
- Log file permissions denied
- Log files growing too large

**File Permission Issues:**
```bash
# Check file permissions
ls -la simulator.log

# Fix permissions
chmod 644 simulator.log
chown $USER simulator.log
```

**Directory Issues:**
```bash
# Ensure log directory exists
mkdir -p logs
python3 run_simulator.py --port COM4 --log-file logs/simulator.log
```

**File Size Management:**
```python
import logging.handlers

# Rotating file handler
handler = logging.handlers.RotatingFileHandler(
    'simulator.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

## Advanced Troubleshooting

### Component-Specific Debugging

**ModbusSimulatorServer Issues:**
```python
# Enable detailed server logging
import logging
logging.getLogger('simulator.src.core.modbus_server').setLevel(logging.DEBUG)

# Check specific operations
logger.debug("Server state: {}".format(self.state))
logger.debug("Port config: {}".format(self.config))
```

**RegisterHandler Issues:**
```python
# Debug register updates
logging.getLogger('simulator.src.core.register_handler').setLevel(logging.DEBUG)

# Check register values
logger.debug("Register values: {}".format(self._registers))
logger.debug("Scenario: {}".format(self.current_scenario))
```

**PyModbus Integration:**
```python
# Enable pymodbus logging
logging.getLogger('pymodbus').setLevel(logging.DEBUG)

# This will show Modbus protocol details
```

### Custom Logging Solutions

**Add Request/Response Logging:**
```python
class LoggingModbusServer(ModbusSimulatorServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_logger = logging.getLogger('modbus.requests')
    
    def log_request(self, request):
        self.request_logger.info("Request: addr={}, count={}".format(
            request.address, request.count
        ))
```

**Add Performance Logging:**
```python
import time
import logging

class PerformanceLogger:
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger('performance')
    
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, *args):
        duration = time.time() - self.start
        self.logger.info("{} took {:.3f}s".format(self.name, duration))

# Usage
with PerformanceLogger("register_update"):
    update_registers()
```

### Environment-Specific Issues

**Windows Console Encoding:**
```bash
# Set console code page for UTF-8
chcp 65001

# Or use environment variable
set PYTHONIOENCODING=utf-8
python3 run_simulator.py --port COM4 --verbose
```

**Linux/macOS Terminal:**
```bash
# Check locale settings
locale

# Set UTF-8 if needed
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
```

**Docker Container Logging:**
```dockerfile
# Ensure unbuffered output
ENV PYTHONUNBUFFERED=1

# Configure logging for container
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO
```

## Diagnostic Scripts

### Log Level Test Script

```python
#!/usr/bin/env python3
"""Test logging configuration"""

import logging
import sys

def test_logging():
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger('test')
    
    # Test all levels
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")
    
    print("Logging test complete. If you see 5 messages above, logging is working.")

if __name__ == "__main__":
    test_logging()
```

### Component Isolation Test

```python
#!/usr/bin/env python3
"""Test individual component logging"""

import sys
import logging
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_components():
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        from src.core.register_handler import RegisterHandler
        print("✓ RegisterHandler logging test:")
        handler = RegisterHandler()
        print("  RegisterHandler initialized successfully")
    except Exception as e:
        print("✗ RegisterHandler error:", e)
    
    try:
        from src.core.modbus_server import ModbusSimulatorServer, ServerConfig
        print("✓ ModbusSimulatorServer logging test:")
        config = ServerConfig(port="TEST")
        server = ModbusSimulatorServer(config)
        print("  ModbusSimulatorServer initialized successfully")
    except Exception as e:
        print("✗ ModbusSimulatorServer error:", e)

if __name__ == "__main__":
    test_components()
```

## Best Practices for Logging Troubleshooting

### 1. Systematic Approach

1. **Isolate the Issue:**
   - Test with minimal configuration
   - Enable verbose mode
   - Check one component at a time

2. **Document Symptoms:**
   - What specific log messages are missing/wrong?
   - When does the issue occur?
   - What is the expected vs. actual behavior?

3. **Test Solutions Incrementally:**
   - Change one setting at a time
   - Verify each change
   - Document what works

### 2. Logging Levels Strategy

- **Development:** Use DEBUG for detailed information
- **Testing:** Use INFO for operation tracking
- **Production:** Use WARNING for important alerts only
- **Troubleshooting:** Temporarily enable DEBUG for specific components

### 3. Performance Monitoring

```python
# Monitor logging performance impact
import time
import logging

class TimingHandler(logging.Handler):
    def emit(self, record):
        start = time.time()
        super().emit(record)
        duration = time.time() - start
        if duration > 0.01:  # Log slow logging operations
            print(f"Slow log operation: {duration:.3f}s")
```

This troubleshooting guide should help identify and resolve most logging-related issues with the GA Modbus BMS Simulator.