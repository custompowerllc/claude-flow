# GA Modbus Simulator - Logging Configuration Examples

This directory contains example logging configurations for different use cases and environments.

## Configuration Files

### `basic_logging.py`
**Use Case:** Development and basic troubleshooting
- Console output with standard formatting
- Configurable INFO/DEBUG levels
- Minimal setup for quick testing

**Features:**
- Simple console logging
- Verbose mode support
- External library noise reduction

**Usage:**
```python
from config.logging.basic_logging import setup_basic_logging

# Standard logging
logger = setup_basic_logging(verbose=False)

# Debug logging
debug_logger = setup_basic_logging(verbose=True)
```

### `file_logging.py`
**Use Case:** Development and testing environments
- File-based logging with rotation
- Multiple output targets (console + files)
- Component-specific logging

**Features:**
- Rotating file handlers
- Separate error logs
- Daily rotation options
- Component isolation

**Usage:**
```python
from config.logging.file_logging import setup_file_logging

# Basic file logging
logger = setup_file_logging(log_dir="logs", verbose=True)

# Daily rotation
logger = setup_daily_logging(log_dir="daily_logs", days_to_keep=7)

# Component-specific logs
logger = setup_component_logging(log_dir="component_logs")
```

### `production_logging.py`
**Use Case:** Production environments
- High-performance logging
- JSON structured output
- Monitoring system integration
- Docker container support

**Features:**
- JSON formatting for log aggregation
- Performance filtering
- Metrics collection
- Health monitoring
- Docker-optimized output

**Usage:**
```python
from config.logging.production_logging import setup_production_logging

# Production environment
logger = setup_production_logging(service_name="ga-simulator")

# Docker containers
docker_logger = setup_docker_logging()

# With monitoring
logger, metrics_logger = setup_monitoring_logging()
```

## Integration Examples

### Modify `run_simulator.py`

To use custom logging configurations, modify the logging setup in `run_simulator.py`:

```python
# At the top of run_simulator.py
import sys
from pathlib import Path

# Add config directory to path
config_dir = Path(__file__).parent / "config"
sys.path.insert(0, str(config_dir))

# Import desired logging configuration
from logging.production_logging import setup_production_logging

def main():
    args = parse_arguments()
    
    # Replace the existing logging setup with custom configuration
    if args.production:
        logger = setup_production_logging()
    elif args.verbose:
        from logging.basic_logging import setup_basic_logging
        logger = setup_basic_logging(verbose=True)
    else:
        from logging.file_logging import setup_file_logging
        logger = setup_file_logging(verbose=args.verbose)
    
    # ... rest of main function
```

### Environment-Specific Configurations

#### Development Environment
```python
# config/development.py
from logging.basic_logging import setup_basic_logging
from logging.file_logging import setup_file_logging

def setup_dev_logging():
    # Console for immediate feedback
    console_logger = setup_basic_logging(verbose=True)
    
    # File for detailed analysis
    file_logger = setup_file_logging(log_dir="dev_logs", verbose=True)
    
    return console_logger
```

#### Staging Environment
```python
# config/staging.py
from logging.file_logging import setup_file_logging

def setup_staging_logging():
    return setup_file_logging(
        log_dir="staging_logs",
        max_bytes=50*1024*1024,  # 50MB
        backup_count=10,
        verbose=False
    )
```

#### Production Environment
```python
# config/production.py
from logging.production_logging import setup_production_logging

def setup_prod_logging():
    return setup_production_logging(
        log_dir="/var/log/ga-simulator",
        service_name="ga-modbus-simulator"
    )
```

## Docker Integration

### Dockerfile
```dockerfile
FROM python:3.9-slim

# Install dependencies
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

# Copy application
COPY . /app/
WORKDIR /app

# Configure logging for container
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Use production logging configuration
CMD ["python3", "-c", "from config.logging.production_logging import setup_docker_logging; setup_docker_logging(); exec(open('run_simulator.py').read())"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  ga-simulator:
    build: .
    environment:
      - LOG_LEVEL=INFO
      - SERVICE_NAME=ga-modbus-simulator
    volumes:
      - /dev/ttyUSB0:/dev/ttyUSB0
      - ./logs:/app/logs
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Monitoring Integration

### ELK Stack (Elasticsearch, Logstash, Kibana)

#### Logstash Configuration
```ruby
input {
  file {
    path => "/var/log/ga-simulator/ga-modbus-simulator_events.json"
    codec => "json"
    type => "ga-simulator-events"
  }
  file {
    path => "/var/log/ga-simulator/ga-modbus-simulator_errors.json"
    codec => "json"
    type => "ga-simulator-errors"
  }
}

filter {
  if [type] == "ga-simulator-events" {
    mutate {
      add_field => { "service" => "ga-modbus-simulator" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "ga-simulator-%{+YYYY.MM.dd}"
  }
}
```

### Prometheus Integration

```python
# config/prometheus_logging.py
from prometheus_client import Counter, Histogram, Gauge
import logging

# Metrics
log_messages = Counter('log_messages_total', 'Total log messages', ['level', 'component'])
request_duration = Histogram('modbus_request_duration_seconds', 'Modbus request duration')
active_connections = Gauge('modbus_active_connections', 'Number of active connections')

class PrometheusHandler(logging.Handler):
    def emit(self, record):
        log_messages.labels(
            level=record.levelname,
            component=record.name
        ).inc()
```

### Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "GA Modbus Simulator",
    "panels": [
      {
        "title": "Log Messages by Level",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(log_messages_total[5m])",
            "legendFormat": "{{level}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(log_messages_total{level=\"ERROR\"}[5m])"
          }
        ]
      }
    ]
  }
}
```

## Testing Configurations

### Automated Testing
```python
# test_logging_config.py
import logging
import tempfile
import json
from pathlib import Path

def test_production_logging():
    with tempfile.TemporaryDirectory() as temp_dir:
        from config.logging.production_logging import setup_production_logging
        
        logger = setup_production_logging(log_dir=temp_dir)
        
        # Test various log levels
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        
        # Verify log files exist
        log_path = Path(temp_dir)
        assert (log_path / "ga-modbus-simulator_events.json").exists()
        assert (log_path / "ga-modbus-simulator_errors.json").exists()
        
        # Verify JSON format
        with open(log_path / "ga-modbus-simulator_events.json") as f:
            for line in f:
                log_entry = json.loads(line.strip())
                assert 'timestamp' in log_entry
                assert 'level' in log_entry
                assert 'message' in log_entry
```

### Performance Testing
```python
# test_logging_performance.py
import time
import logging
from config.logging.production_logging import setup_production_logging

def test_logging_performance():
    logger = setup_production_logging()
    
    # Test high-frequency logging
    start_time = time.time()
    for i in range(1000):
        logger.info(f"Performance test message {i}")
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"1000 log messages took {duration:.3f} seconds")
    print(f"Rate: {1000/duration:.1f} messages/second")
```

## Best Practices

### Configuration Selection
- **Development:** Use `basic_logging.py` with verbose mode
- **Testing:** Use `file_logging.py` with component separation
- **Staging:** Use `file_logging.py` with production-like settings
- **Production:** Use `production_logging.py` with monitoring
- **Containers:** Use `setup_docker_logging()` from production config

### Performance Considerations
- Enable DEBUG logging only when needed
- Use log rotation to prevent disk space issues
- Consider async logging for high-frequency operations
- Monitor log file sizes and I/O impact

### Security
- Avoid logging sensitive information (passwords, keys)
- Use appropriate file permissions (644 for log files)
- Consider log encryption for sensitive environments
- Implement log retention policies

### Monitoring
- Set up alerts for ERROR and CRITICAL messages
- Monitor log file growth rates
- Track application-specific metrics
- Use structured logging for easier analysis

This configuration system provides flexible logging options for all deployment scenarios while maintaining consistency and ease of use.