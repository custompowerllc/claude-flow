You are claude-flow, a claude code task orchestrator. 

Reference the following projects

B&K Precision BK8520 Load Tester FastAPI Controls
@projects/bk8500b_python_app_load_tester

B&K Precision 9206B Power Supply FastAPI Controls
@projects/bk9206b 

Objective: 

Create a integrated interface that can control and monitor both the BK8520 load tester and the BK9206b power supply. This way, we have a single inteface to run charge,  discharge, and test battery packs. 

- Python application (cross platform)
- Python version 3.6+
- CLI interface
- config file that stores the url of both the load tester and power supply as well as initial settings of communication
- in this case the load tester would be the bk8520 and the power supply would be the bk9206b
- use rich and click library
- this application would accept calls from other applications and other application could pass parameters and arguments
- use curl commands


# Current Implementation:

## BK8520 Electronic Load Control:
  - Web Interface and REST API control is running on http://10.100.10.190:8000
  - Openapi API and schema docs avaliable at http://10.100.10.190:8000/docs
  - Server: uvicorn 
  - Reference API: @claude-flow/projects/bk-integration/docs/BK8520-API-Documentation.md


## BK9206b Power Supply Controller:
  - Web Interface and REST API control is running on http://10.100.10.190:5300
  - Openapi API and schema docs avaliable at http://10.100.10.190:5300/docs
  - Server: uvicorn 
  - Reference API: @claude-flow/projects/bk-integration/docs/BK9206b-API-Documentation.md

# API Examples:


### Health Check

Check if the API service is running.

**Endpoint:** `GET /api/health`

**Response Example:**
```json
{
  "success": true,
  "message": "BK8520 Web API is running",
  "data": {
    "status": "healthy"
  }
}
```


### Connect Device

Connect to a BK8520 device via serial port.

**Endpoint:** `POST /api/device/connect`

**Request Body:**
```json
{
  "port": "string",
  "baudrate": 9600,
  "timeout": 3.0,
  "reset_input_on_connect": true
}
```

### Device setup

#### Initial Setup

- The application will use config.json for configuration 
  
- The config.json will store:
  - The device url 

For example, the BK8520
  - device_address: 10.100.10.190
  - device_url: http://10.100.10.190:8000
  - port: 8000
  - serial_port: /dev/ttyUSB0


  #### Device Connection

  1. After using the connect endpoint api, the device will be connected.

# Implementation Guide

## Architecture Overview

The BK-Integration CLI will serve as a unified control interface for both the BK8520 Electronic Load and BK9206b Power Supply, enabling comprehensive battery testing workflows through a single command-line application.

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   BK-Integration CLI                     │
│                    (Python 3.6+)                        │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Click CLI  │  │ Rich Display │  │  Config Mgr  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────┤
│            HTTP Client Layer (requests/httpx)           │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────┐  ┌─────────────────────────┐ │
│  │  BK8520 API Client   │  │  BK9206b API Client   │ │
│  │  :8000                │  │  :5300                │ │
│  └──────────────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
               ↓                            ↓
    ┌─────────────────────┐      ┌─────────────────────┐
    │  BK8520 Load Tester │      │  BK9206b Power      │
    │  FastAPI Server     │      │  Supply FastAPI     │
    └─────────────────────┘      └─────────────────────┘
```

### Key Components

1. **CLI Interface Layer**: Click-based command structure with Rich formatting
2. **Configuration Manager**: JSON-based configuration with environment variable support
3. **API Client Layer**: Abstracted HTTP client for both devices
4. **Device Controllers**: Device-specific logic and workflow orchestration
5. **Battery Test Orchestrator**: Coordinates multi-device testing workflows

## Configuration File Structure

### config.json

```json
{
  "devices": {
    "load_tester": {
      "name": "BK8520",
      "device_address": "10.100.10.190",
      "device_url": "http://10.100.10.190:8000",
      "port": 8000,
      "serial_port": "/dev/ttyUSB0",
      "connection": {
        "baudrate": 9600,
        "timeout": 3.0,
        "reset_input_on_connect": true
      },
      "defaults": {
        "mode": "CC",
        "max_current": 10.0,
        "max_voltage": 60.0,
        "max_power": 300.0
      }
    },
    "power_supply": {
      "name": "BK9206b",
      "device_address": "10.100.10.190",
      "device_url": "http://10.100.10.190:5300",
      "port": 5300,
      "defaults": {
        "voltage": 15.0,
        "current_limit": 2.0,
        "taper_threshold": 0.1,
        "taper_duration": 60
      }
    }
  },
  "test_profiles": {
    "default": {
      "charge_voltage": 16.8,
      "charge_current": 2.0,
      "discharge_current": 5.0,
      "cutoff_voltage": 10.0,
      "rest_time": 60
    },
    "high_capacity": {
      "charge_voltage": 16.8,
      "charge_current": 4.0,
      "discharge_current": 10.0,
      "cutoff_voltage": 10.0,
      "rest_time": 120
    }
  },
  "logging": {
    "level": "INFO",
    "file": "bk_integration.log",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  },
  "api": {
    "timeout": 30,
    "retry_count": 3,
    "retry_delay": 1.0
  }
}
```

### Environment Variables

```bash
# Override configuration via environment variables
export BK_LOAD_URL=http://10.100.10.190:8000
export BK_POWER_URL=http://10.100.10.190:5300
export BK_LOAD_PORT=/dev/ttyUSB0
export BK_LOG_LEVEL=DEBUG
```

## CLI Implementation with Click and Rich

### Project Structure

```
bk-integration/
├── bk_integration/
│   ├── __init__.py
│   ├── cli.py           # Main CLI entry point
│   ├── config.py        # Configuration management
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── bk8520.py    # BK8520 API client
│   │   └── bk9206b.py   # BK9206b API client
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── device.py    # Device management commands
│   │   ├── test.py      # Battery testing commands
│   │   ├── monitor.py   # Real-time monitoring
│   │   └── profile.py   # Test profile management
│   └── utils/
│       ├── __init__.py
│       ├── display.py   # Rich display utilities
│       └── logging.py   # Logging configuration
├── config.json
├── requirements.txt
└── setup.py
```

### Main CLI Implementation (cli.py)

```python
import click
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
import json
from pathlib import Path
from .config import ConfigManager
from .clients import BK8520Client, BK9206bClient

console = Console()

@click.group()
@click.option('--config', '-c', default='config.json', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """BK-Integration: Unified control for BK8520 and BK9206b devices"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = ConfigManager(config)
    ctx.obj['load_client'] = BK8520Client(ctx.obj['config'].get_load_config())
    ctx.obj['power_client'] = BK9206bClient(ctx.obj['config'].get_power_config())

@cli.group()
def device():
    """Device management commands"""
    pass

@device.command()
@click.pass_context
def status(ctx):
    """Show status of both devices"""
    with console.status("[bold green]Checking device status..."):
        load_status = ctx.obj['load_client'].get_status()
        power_status = ctx.obj['power_client'].get_status()
    
    # Create status table
    table = Table(title="Device Status", show_header=True)
    table.add_column("Device", style="cyan", no_wrap=True)
    table.add_column("Connection", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Details", style="white")
    
    # Add load tester status
    table.add_row(
        "BK8520 Load",
        "✓ Connected" if load_status.get('connected') else "✗ Disconnected",
        "Active" if load_status.get('status', {}).get('input_active') else "Idle",
        f"V: {load_status.get('voltage', 0):.2f}V, I: {load_status.get('current', 0):.2f}A"
    )
    
    # Add power supply status
    table.add_row(
        "BK9206b Power",
        "✓ Connected" if power_status.get('success') else "✗ Disconnected",
        "Output ON" if power_status.get('data', {}).get('output_enabled') else "Output OFF",
        f"V: {power_status.get('data', {}).get('voltage_actual', 0):.2f}V, I: {power_status.get('data', {}).get('current_actual', 0):.2f}A"
    )
    
    console.print(table)

@device.command()
@click.pass_context
def connect(ctx):
    """Connect to both devices"""
    with console.status("[bold green]Connecting to devices..."):
        # Connect BK8520
        load_result = ctx.obj['load_client'].connect()
        if load_result['success']:
            console.print("[green]✓[/green] BK8520 Load Tester connected")
        else:
            console.print(f"[red]✗[/red] BK8520 connection failed: {load_result['message']}")
        
        # BK9206b auto-connects, just verify
        power_result = ctx.obj['power_client'].health_check()
        if power_result['success']:
            console.print("[green]✓[/green] BK9206b Power Supply connected")
        else:
            console.print(f"[red]✗[/red] BK9206b connection failed: {power_result['message']}")

@cli.group()
def test():
    """Battery testing commands"""
    pass

@test.command()
@click.option('--profile', '-p', default='default', help='Test profile to use')
@click.option('--cycles', '-n', default=1, help='Number of charge/discharge cycles')
@click.pass_context
def battery(ctx, profile, cycles):
    """Run complete battery test cycle"""
    config = ctx.obj['config']
    test_profile = config.get_test_profile(profile)
    
    console.print(f"[bold cyan]Starting battery test with profile: {profile}[/bold cyan]")
    console.print(f"Cycles: {cycles}")
    
    for cycle in range(1, cycles + 1):
        console.rule(f"[bold]Cycle {cycle}/{cycles}[/bold]")
        
        # Charging phase
        with console.status("[bold green]Charging battery..."):
            ctx.obj['power_client'].set_voltage(test_profile['charge_voltage'])
            ctx.obj['power_client'].set_current(test_profile['charge_current'])
            ctx.obj['power_client'].enable_output()
            # Monitor charging until taper detected
            
        # Rest phase
        console.print(f"[yellow]Resting for {test_profile['rest_time']} seconds...[/yellow]")
        
        # Discharge phase
        with console.status("[bold red]Discharging battery..."):
            ctx.obj['power_client'].disable_output()
            ctx.obj['load_client'].setup_discharge(
                current=test_profile['discharge_current'],
                cutoff_voltage=test_profile['cutoff_voltage']
            )
            ctx.obj['load_client'].enable_input()
            # Monitor discharge until cutoff
        
        # Display results
        console.print("[bold green]Cycle complete![/bold green]")

@cli.command()
@click.option('--interval', '-i', default=1.0, help='Update interval in seconds')
@click.pass_context
def monitor(ctx, interval):
    """Real-time monitoring of both devices"""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    
    layout["header"].update("[bold]BK-Integration Real-Time Monitor[/bold]")
    layout["main"].split_row(
        Layout(name="load"),
        Layout(name="power")
    )
    
    with Live(layout, refresh_per_second=1/interval) as live:
        while True:
            # Update load tester display
            load_data = ctx.obj['load_client'].get_readings()
            load_table = Table(title="BK8520 Load Tester")
            load_table.add_column("Parameter", style="cyan")
            load_table.add_column("Value", style="green")
            load_table.add_row("Voltage", f"{load_data.get('voltage', 0):.3f} V")
            load_table.add_row("Current", f"{load_data.get('current', 0):.3f} A")
            load_table.add_row("Power", f"{load_data.get('power', 0):.3f} W")
            layout["load"].update(load_table)
            
            # Update power supply display
            power_data = ctx.obj['power_client'].get_status()
            power_table = Table(title="BK9206b Power Supply")
            power_table.add_column("Parameter", style="cyan")
            power_table.add_column("Value", style="green")
            power_table.add_row("Voltage", f"{power_data.get('voltage_actual', 0):.3f} V")
            power_table.add_row("Current", f"{power_data.get('current_actual', 0):.3f} A")
            power_table.add_row("Mode", power_data.get('operating_mode', 'N/A'))
            layout["power"].update(power_table)

if __name__ == '__main__':
    cli()
```

## Battery Testing Workflows

### 1. Charge Cycle Workflow

```python
def charge_battery(power_client, voltage, current, taper_threshold=0.1, taper_duration=60):
    """
    Charge battery using CV/CC method with taper detection
    
    Steps:
    1. Set voltage and current limits
    2. Enable output
    3. Monitor current until taper detected
    4. Return charge statistics
    """
    # Configure power supply
    power_client.set_voltage(voltage)
    power_client.set_current(current)
    power_client.set_taper_threshold(taper_threshold)
    power_client.set_taper_duration(taper_duration)
    
    # Start charging
    power_client.enable_output()
    
    # Monitor charging
    charge_data = []
    taper_detected = False
    start_time = time.time()
    
    while not taper_detected:
        status = power_client.get_status()
        charge_data.append({
            'time': time.time() - start_time,
            'voltage': status['voltage_actual'],
            'current': status['current_actual'],
            'power': status['power_actual'],
            'mode': status['operating_mode']
        })
        
        if status['operating_mode'] == 'TAPER':
            taper_detected = True
        
        time.sleep(1)
    
    # Stop charging
    power_client.disable_output()
    
    return {
        'duration': time.time() - start_time,
        'energy_delivered': calculate_energy(charge_data),
        'final_voltage': charge_data[-1]['voltage'],
        'data': charge_data
    }
```

### 2. Discharge Cycle Workflow

```python
def discharge_battery(load_client, current, cutoff_voltage, mode='CC'):
    """
    Discharge battery using electronic load
    
    Steps:
    1. Configure discharge parameters
    2. Enable input
    3. Monitor until cutoff voltage reached
    4. Return discharge statistics
    """
    # Configure load tester
    load_client.set_mode(mode)
    load_client.set_current(current)
    load_client.set_voltage(cutoff_voltage)
    
    # Start discharge
    load_client.enable_input()
    
    # Monitor discharge
    discharge_data = []
    cutoff_reached = False
    start_time = time.time()
    
    while not cutoff_reached:
        readings = load_client.get_readings()
        discharge_data.append({
            'time': time.time() - start_time,
            'voltage': readings['voltage'],
            'current': readings['current'],
            'power': readings['power']
        })
        
        if readings['voltage'] <= cutoff_voltage:
            cutoff_reached = True
        
        time.sleep(1)
    
    # Stop discharge
    load_client.disable_input()
    
    return {
        'duration': time.time() - start_time,
        'capacity': calculate_capacity(discharge_data),
        'energy': calculate_energy(discharge_data),
        'final_voltage': discharge_data[-1]['voltage'],
        'data': discharge_data
    }
```

### 3. Complete Test Cycle

```python
def complete_battery_test(power_client, load_client, test_profile):
    """
    Run complete charge-discharge-charge cycle
    
    Returns comprehensive battery metrics:
    - Charge acceptance
    - Discharge capacity
    - Round-trip efficiency
    - Internal resistance estimation
    """
    results = {
        'test_start': datetime.now().isoformat(),
        'profile': test_profile,
        'cycles': []
    }
    
    # Initial charge
    console.print("[bold green]Phase 1: Initial Charge[/bold green]")
    charge1 = charge_battery(
        power_client,
        test_profile['charge_voltage'],
        test_profile['charge_current']
    )
    
    # Rest period
    console.print(f"[yellow]Resting for {test_profile['rest_time']}s...[/yellow]")
    time.sleep(test_profile['rest_time'])
    
    # Discharge test
    console.print("[bold red]Phase 2: Capacity Test[/bold red]")
    discharge = discharge_battery(
        load_client,
        test_profile['discharge_current'],
        test_profile['cutoff_voltage']
    )
    
    # Rest period
    time.sleep(test_profile['rest_time'])
    
    # Recharge
    console.print("[bold green]Phase 3: Recharge[/bold green]")
    charge2 = charge_battery(
        power_client,
        test_profile['charge_voltage'],
        test_profile['charge_current']
    )
    
    # Calculate metrics
    results['capacity_ah'] = discharge['capacity']
    results['energy_wh'] = discharge['energy']
    results['efficiency'] = (discharge['energy'] / charge1['energy_delivered']) * 100
    results['test_duration'] = sum([charge1['duration'], discharge['duration'], charge2['duration']])
    
    return results
```

## Inter-Application Communication

### Curl Command Examples

#### Basic Device Control

```bash
# Check system health
curl -X GET http://localhost:8080/api/health

# Connect devices
curl -X POST http://localhost:8080/api/devices/connect

# Get device status
curl -X GET http://localhost:8080/api/devices/status

# Start battery test with default profile
curl -X POST http://localhost:8080/api/test/battery \
  -H "Content-Type: application/json" \
  -d '{"profile": "default", "cycles": 1}'

# Start battery test with custom parameters
curl -X POST http://localhost:8080/api/test/battery/custom \
  -H "Content-Type: application/json" \
  -d '{
    "charge_voltage": 16.8,
    "charge_current": 2.0,
    "discharge_current": 5.0,
    "cutoff_voltage": 10.0,
    "cycles": 3
  }'

# Get test status
curl -X GET http://localhost:8080/api/test/status

# Get test results
curl -X GET http://localhost:8080/api/test/results/latest

# Real-time monitoring (WebSocket)
curl --include \
     --no-buffer \
     --header "Connection: Upgrade" \
     --header "Upgrade: websocket" \
     --header "Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==" \
     --header "Sec-WebSocket-Version: 13" \
     http://localhost:8080/ws/monitor
```

#### Advanced Operations

```bash
# Set power supply parameters
curl -X POST http://localhost:8080/api/power/set \
  -H "Content-Type: application/json" \
  -d '{"voltage": 15.0, "current": 2.0}'

# Set load tester parameters
curl -X POST http://localhost:8080/api/load/set \
  -H "Content-Type: application/json" \
  -d '{"mode": "CC", "current": 5.0, "cutoff_voltage": 10.0}'

# Enable/disable devices
curl -X POST http://localhost:8080/api/power/output/enable
curl -X POST http://localhost:8080/api/power/output/disable
curl -X POST http://localhost:8080/api/load/input/enable
curl -X POST http://localhost:8080/api/load/input/disable

# Export test data
curl -X GET http://localhost:8080/api/test/export?format=csv > test_results.csv
curl -X GET http://localhost:8080/api/test/export?format=json > test_results.json
```

### REST API Server Implementation

```python
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
from pydantic import BaseModel

app = FastAPI(title="BK-Integration API", version="1.0.0")

class TestProfile(BaseModel):
    charge_voltage: float
    charge_current: float
    discharge_current: float
    cutoff_voltage: float
    cycles: int = 1
    rest_time: int = 60

class DeviceStatus(BaseModel):
    load_connected: bool
    power_connected: bool
    load_status: dict
    power_status: dict

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "message": "BK-Integration API is running",
        "version": "1.0.0"
    }

@app.post("/api/devices/connect")
async def connect_devices():
    """Connect to both devices"""
    # Implementation here
    return {"success": True, "message": "Devices connected"}

@app.get("/api/devices/status")
async def get_device_status():
    """Get status of both devices"""
    # Implementation here
    return DeviceStatus(
        load_connected=True,
        power_connected=True,
        load_status={},
        power_status={}
    )

@app.post("/api/test/battery")
async def start_battery_test(profile: TestProfile):
    """Start battery test with specified profile"""
    # Implementation here
    return {
        "success": True,
        "message": "Battery test started",
        "test_id": "test_123456"
    }

@app.websocket("/ws/monitor")
async def websocket_monitor(websocket: WebSocket):
    """WebSocket endpoint for real-time monitoring"""
    await websocket.accept()
    try:
        while True:
            # Send real-time data
            data = {
                "timestamp": datetime.now().isoformat(),
                "load": load_client.get_readings(),
                "power": power_client.get_status()
            }
            await websocket.send_json(data)
            await asyncio.sleep(0.1)  # 100ms update rate
    except Exception as e:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### External Application Integration

```python
# Example: Integration from another Python application
import requests
import json

class BKIntegrationClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def connect_devices(self):
        """Connect to BK devices"""
        response = self.session.post(f"{self.base_url}/api/devices/connect")
        return response.json()
    
    def start_battery_test(self, profile):
        """Start battery test with profile"""
        response = self.session.post(
            f"{self.base_url}/api/test/battery",
            json=profile
        )
        return response.json()
    
    def get_test_status(self):
        """Get current test status"""
        response = self.session.get(f"{self.base_url}/api/test/status")
        return response.json()
    
    def get_test_results(self, test_id=None):
        """Get test results"""
        url = f"{self.base_url}/api/test/results"
        if test_id:
            url += f"/{test_id}"
        response = self.session.get(url)
        return response.json()

# Usage example
client = BKIntegrationClient()
client.connect_devices()

# Start a test
test_profile = {
    "charge_voltage": 16.8,
    "charge_current": 2.0,
    "discharge_current": 5.0,
    "cutoff_voltage": 10.0,
    "cycles": 1
}
result = client.start_battery_test(test_profile)
test_id = result['test_id']

# Monitor test progress
import time
while True:
    status = client.get_test_status()
    if status['completed']:
        break
    print(f"Test progress: {status['progress']}%")
    time.sleep(5)

# Get results
results = client.get_test_results(test_id)
print(f"Battery capacity: {results['capacity_ah']} Ah")
print(f"Battery energy: {results['energy_wh']} Wh")
```

## Installation and Usage

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/bk-integration.git
cd bk-integration

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Requirements.txt

```txt
click>=8.0.0
rich>=10.0.0
requests>=2.26.0
httpx>=0.23.0
fastapi>=0.68.0
uvicorn>=0.15.0
websockets>=10.0
pydantic>=1.8.0
python-dotenv>=0.19.0
pytest>=7.0.0
pytest-asyncio>=0.18.0
```

### Basic Usage

```bash
# Show help
bk-integration --help

# Check device status
bk-integration device status

# Connect to devices
bk-integration device connect

# Run battery test with default profile
bk-integration test battery

# Run battery test with specific profile
bk-integration test battery --profile high_capacity --cycles 3

# Real-time monitoring
bk-integration monitor

# Start API server
bk-integration serve --port 8080

# List available test profiles
bk-integration profile list

# Create custom test profile
bk-integration profile create --name "custom" \
  --charge-voltage 16.8 \
  --charge-current 3.0 \
  --discharge-current 7.5 \
  --cutoff-voltage 10.0
```

### Advanced Usage

```bash
# Run with custom configuration
bk-integration --config /path/to/config.json device status

# Enable debug logging
export BK_LOG_LEVEL=DEBUG
bk-integration test battery

# Run in daemon mode
bk-integration serve --daemon --pid-file /var/run/bk-integration.pid

# Export test results
bk-integration test export --format csv --output results.csv
bk-integration test export --format json --output results.json

# Calibration mode
bk-integration calibrate --device load --current 5.0
bk-integration calibrate --device power --voltage 15.0
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

EXPOSE 8080

CMD ["bk-integration", "serve", "--host", "0.0.0.0", "--port", "8080"]
```

```bash
# Build Docker image
docker build -t bk-integration:latest .

# Run container
docker run -d \
  --name bk-integration \
  -p 8080:8080 \
  -v $(pwd)/config.json:/app/config.json \
  --device /dev/ttyUSB0:/dev/ttyUSB0 \
  bk-integration:latest
```

## Testing and Validation

### Unit Tests

```python
# tests/test_clients.py
import pytest
from bk_integration.clients import BK8520Client, BK9206bClient

def test_bk8520_client_connect():
    client = BK8520Client({"device_url": "http://localhost:8000"})
    result = client.connect()
    assert result['success'] == True

def test_bk9206b_client_status():
    client = BK9206bClient({"device_url": "http://localhost:5300"})
    result = client.get_status()
    assert 'voltage_actual' in result

# tests/test_workflows.py
import pytest
from bk_integration.workflows import charge_battery, discharge_battery

@pytest.mark.asyncio
async def test_charge_workflow():
    # Test charging workflow
    pass

@pytest.mark.asyncio
async def test_discharge_workflow():
    # Test discharge workflow
    pass
```

### Integration Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bk_integration --cov-report=html

# Run specific test file
pytest tests/test_clients.py

# Run with verbose output
pytest -v
```

## Troubleshooting

### Common Issues

1. **Connection Issues**
   - Verify device URLs are correct in config.json
   - Check network connectivity to devices
   - Ensure serial port permissions (Linux: add user to dialout group)

2. **Serial Port Access (Linux)**
   ```bash
   # Add user to dialout group
   sudo usermod -a -G dialout $USER
   # Logout and login for changes to take effect
   ```

3. **API Timeout**
   - Increase timeout in config.json
   - Check device response times
   - Verify network latency

4. **WebSocket Connection Failed**
   - Ensure WebSocket support in network infrastructure
   - Check firewall rules for WebSocket traffic
   - Verify proxy configuration if applicable

## API Reference Summary

### CLI Commands
- `device status` - Show device status
- `device connect` - Connect to devices
- `test battery` - Run battery test
- `monitor` - Real-time monitoring
- `serve` - Start API server

### REST API Endpoints
- `GET /api/health` - Health check
- `POST /api/devices/connect` - Connect devices
- `GET /api/devices/status` - Device status
- `POST /api/test/battery` - Start test
- `GET /api/test/status` - Test status
- `GET /api/test/results` - Test results
- `WS /ws/monitor` - Real-time monitoring

### Configuration Options
- Device URLs and ports
- Test profiles
- Logging configuration
- API settings

## Conclusion

The BK-Integration CLI provides a comprehensive solution for controlling and monitoring both the BK8520 Electronic Load and BK9206b Power Supply through a unified interface. The implementation leverages modern Python libraries (Click for CLI, Rich for display) and provides both command-line and REST API interfaces for maximum flexibility in integration scenarios.
   