# GA Modbus Simulator - Log File Locations and Management

## Overview

This document describes the default and configurable log file locations for the GA Modbus BMS Simulator, along with management recommendations for different deployment scenarios.

## Default Log Output

### Console Output (Default)
By default, the simulator logs to the console (stdout/stderr) with no persistent file storage.

**Configuration:**
- **Level:** INFO (standard), DEBUG (with --verbose)
- **Format:** `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Location:** Terminal/console output only

**Example:**
```bash
python3 run_simulator.py --port COM4
# Logs appear in terminal
```

## Log File Locations by Configuration

### 1. Basic File Logging

**Default Directory:** `./logs/`
**Configurable:** Yes

```python
from config.logging.file_logging import setup_file_logging

# Default location: ./logs/
logger = setup_file_logging()

# Custom location: /var/log/simulator/
logger = setup_file_logging(log_dir="/var/log/simulator")
```

**Files Created:**
- `simulator.log` - All log messages (rotating, max 10MB, 5 backups)
- `simulator_errors.log` - ERROR level and above (rotating, max 5MB, 3 backups)

### 2. Daily Rotation Logging

**Default Directory:** `./logs/`

```python
from config.logging.file_logging import setup_daily_logging

logger = setup_daily_logging(log_dir="daily_logs", days_to_keep=7)
```

**Files Created:**
- `simulator.log` - Current day's logs
- `simulator.log.2025-01-01` - Previous day's logs (dated)
- Automatic cleanup after specified days

### 3. Component-Specific Logging

**Default Directory:** `./logs/`

```python
from config.logging.file_logging import setup_component_logging

logger = setup_component_logging(log_dir="component_logs")
```

**Files Created:**
- `server.log` - ModbusSimulatorServer logs
- `registers.log` - RegisterHandler logs  
- `ports.log` - ComPortManager logs
- `modbus.log` - PyModbus library logs

### 4. Production Logging

**Default Directory:** `./logs/`
**Recommended:** `/var/log/ga-simulator/`

```python
from config.logging.production_logging import setup_production_logging

logger = setup_production_logging(
    log_dir="/var/log/ga-simulator",
    service_name="ga-modbus-simulator"
)
```

**Files Created:**
- `ga-modbus-simulator_errors.json` - Error logs in JSON format
- `ga-modbus-simulator_events.json` - Application events in JSON format
- `ga-modbus-simulator_operations.log` - Operational logs
- `simulator_metrics.json` - Metrics data (if monitoring enabled)

## Platform-Specific Locations

### Windows

**Recommended Locations:**
- Development: `.\logs\` (relative to simulator directory)
- Service: `C:\ProgramData\GA-Simulator\logs\`
- User: `%APPDATA%\GA-Simulator\logs\`

**Example:**
```bash
# Development
python3 run_simulator.py --port COM4 --log-dir .\logs

# Service installation
python3 run_simulator.py --port COM4 --log-dir "C:\ProgramData\GA-Simulator\logs"
```

### Linux

**Recommended Locations:**
- Development: `./logs/` (relative to simulator directory)
- System service: `/var/log/ga-simulator/`
- User service: `~/.local/share/ga-simulator/logs/`

**Permissions Setup:**
```bash
# Create system log directory
sudo mkdir -p /var/log/ga-simulator
sudo chown ga-simulator:ga-simulator /var/log/ga-simulator
sudo chmod 755 /var/log/ga-simulator

# Create user log directory
mkdir -p ~/.local/share/ga-simulator/logs
```

### macOS

**Recommended Locations:**
- Development: `./logs/` (relative to simulator directory)
- User service: `~/Library/Logs/GA-Simulator/`
- System service: `/var/log/ga-simulator/`

**Example:**
```bash
# User logs
mkdir -p ~/Library/Logs/GA-Simulator
python3 run_simulator.py --port /dev/cu.usbserial-1234 --log-dir ~/Library/Logs/GA-Simulator
```

## Docker Container Locations

### Volume Mounting
```yaml
version: '3.8'
services:
  ga-simulator:
    image: ga-simulator:latest
    volumes:
      - ./host_logs:/app/logs  # Mount host directory
      - /dev/ttyUSB0:/dev/ttyUSB0
    environment:
      - LOG_DIR=/app/logs
```

### Named Volumes
```yaml
version: '3.8'
services:
  ga-simulator:
    image: ga-simulator:latest
    volumes:
      - ga_simulator_logs:/app/logs
      - /dev/ttyUSB0:/dev/ttyUSB0

volumes:
  ga_simulator_logs:
```

### Container Paths
- **Default:** `/app/logs/`
- **Configurable:** Via `LOG_DIR` environment variable
- **Output:** Usually redirected to Docker logging driver

## Log Rotation and Retention

### Size-Based Rotation

**Default Settings:**
- **Max file size:** 10MB (main log), 5MB (error log)
- **Backup count:** 5 (main), 3 (error)
- **Naming pattern:** `filename.log.1`, `filename.log.2`, etc.

**Configuration:**
```python
setup_file_logging(
    max_bytes=50*1024*1024,  # 50MB
    backup_count=10          # 10 backup files
)
```

### Time-Based Rotation

**Default Settings:**
- **Rotation:** Daily at midnight
- **Retention:** 7 days
- **Naming pattern:** `filename.log.YYYY-MM-DD`

**Configuration:**
```python
setup_daily_logging(
    days_to_keep=30  # Keep 30 days of logs
)
```

### Production Rotation

**Settings:**
- **Error logs:** 50MB max, 10 backups
- **Event logs:** 100MB max, 5 backups
- **Operations:** 50MB max, 3 backups
- **Metrics:** Hourly rotation, 24 hours retention

## Disk Space Management

### Monitoring Log Disk Usage

```bash
# Check log directory size
du -sh /var/log/ga-simulator/

# Monitor in real-time
watch -n 5 'du -sh /var/log/ga-simulator/*'

# Find large log files
find /var/log/ga-simulator -type f -size +100M
```

### Automated Cleanup Scripts

**Daily Cleanup (Linux/macOS):**
```bash
#!/bin/bash
# cleanup_logs.sh

LOG_DIR="/var/log/ga-simulator"
RETENTION_DAYS=30

# Remove logs older than retention period
find "$LOG_DIR" -name "*.log.*" -type f -mtime +$RETENTION_DAYS -delete

# Compress old logs
find "$LOG_DIR" -name "*.log.*" -type f -mtime +7 -not -name "*.gz" -exec gzip {} \;

echo "Log cleanup completed at $(date)"
```

**Windows PowerShell:**
```powershell
# cleanup_logs.ps1
$LogDir = "C:\ProgramData\GA-Simulator\logs"
$RetentionDays = 30

Get-ChildItem -Path $LogDir -Recurse -File | 
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$RetentionDays) } |
    Remove-Item -Force

Write-Host "Log cleanup completed at $(Get-Date)"
```

### Cron Job Setup (Linux)

```bash
# Add to crontab
crontab -e

# Daily cleanup at 2 AM
0 2 * * * /path/to/cleanup_logs.sh >> /var/log/ga-simulator/cleanup.log 2>&1
```

## Log File Permissions

### Recommended Permissions

**Linux/macOS:**
- **Directories:** `755` (rwxr-xr-x)
- **Log files:** `644` (rw-r--r--)
- **Owner:** Service user (e.g., `ga-simulator`)
- **Group:** Service group or `adm`

**Setup Commands:**
```bash
# Set directory permissions
chmod 755 /var/log/ga-simulator

# Set file permissions
chmod 644 /var/log/ga-simulator/*.log

# Set ownership
chown -R ga-simulator:ga-simulator /var/log/ga-simulator
```

**Windows:**
- **Service account:** Full control
- **Administrators:** Full control
- **Users:** Read access only

## Centralized Logging

### Rsyslog Configuration (Linux)

```bash
# /etc/rsyslog.d/50-ga-simulator.conf

# GA Simulator logs
:programname,isequal,"ga-simulator" /var/log/ga-simulator/rsyslog.log
& stop
```

### Journald Integration (systemd)

```bash
# View simulator logs
journalctl -u ga-simulator.service

# Follow logs in real-time
journalctl -u ga-simulator.service -f

# Export logs
journalctl -u ga-simulator.service --since="2025-01-01" --until="2025-01-02" > simulator_logs.txt
```

### Syslog-ng Configuration

```bash
# /etc/syslog-ng/conf.d/ga-simulator.conf

source s_ga_simulator {
    file("/var/log/ga-simulator/operations.log"
         follow-freq(1)
         flags(no-parse));
};

destination d_ga_simulator_remote {
    syslog("log-server.example.com"
           port(514)
           transport("udp"));
};

log {
    source(s_ga_simulator);
    destination(d_ga_simulator_remote);
};
```

## Monitoring and Alerting

### Log File Monitoring

**File Size Alerts:**
```bash
#!/bin/bash
# monitor_log_size.sh

MAX_SIZE_MB=100
LOG_FILE="/var/log/ga-simulator/simulator.log"

if [ -f "$LOG_FILE" ]; then
    SIZE_MB=$(du -m "$LOG_FILE" | cut -f1)
    if [ $SIZE_MB -gt $MAX_SIZE_MB ]; then
        echo "WARNING: Log file $LOG_FILE is ${SIZE_MB}MB (exceeds ${MAX_SIZE_MB}MB)"
        # Send alert (email, webhook, etc.)
    fi
fi
```

**Log Growth Rate:**
```bash
#!/bin/bash
# monitor_log_growth.sh

LOG_FILE="/var/log/ga-simulator/simulator.log"
GROWTH_FILE="/tmp/log_growth_check"

if [ -f "$GROWTH_FILE" ]; then
    OLD_SIZE=$(cat "$GROWTH_FILE")
    NEW_SIZE=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE")
    GROWTH=$((NEW_SIZE - OLD_SIZE))
    
    # Alert if growth > 10MB in check interval
    if [ $GROWTH -gt 10485760 ]; then
        echo "WARNING: Rapid log growth detected: $GROWTH bytes"
    fi
fi

stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" > "$GROWTH_FILE"
```

## Troubleshooting Log File Issues

### Common Problems

**Permission Denied:**
```bash
# Check permissions
ls -la /var/log/ga-simulator/

# Fix permissions
sudo chown -R ga-simulator:ga-simulator /var/log/ga-simulator/
sudo chmod 755 /var/log/ga-simulator/
sudo chmod 644 /var/log/ga-simulator/*.log
```

**Disk Full:**
```bash
# Check disk space
df -h /var/log

# Emergency cleanup
find /var/log/ga-simulator -name "*.log.*" -mtime +1 -delete
```

**Log Rotation Not Working:**
```bash
# Check logrotate configuration
sudo logrotate -d /etc/logrotate.d/ga-simulator

# Force rotation
sudo logrotate -f /etc/logrotate.d/ga-simulator
```

**Missing Log Files:**
```bash
# Check if directory exists
ls -la /var/log/ga-simulator/

# Check service status
systemctl status ga-simulator

# Check for write permissions
sudo -u ga-simulator touch /var/log/ga-simulator/test.log
```

This guide provides comprehensive information about log file locations and management for all deployment scenarios of the GA Modbus BMS Simulator.