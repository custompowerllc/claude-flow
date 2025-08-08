# BK8520 Electronic Load Control - REST API Documentation

## Overview

The BK8520 Electronic Load Control provides a comprehensive REST API for programmatic control of BK8520 electronic load devices. This API enables remote control of discharge operations, battery testing, and monitoring of device parameters.

**Base URL:** `http://10.100.10.190:8000`  
**API Version:** 1.0.0  
**Content-Type:** `application/json`

## Table of Contents

1. [Authentication](#authentication)
2. [Response Format](#response-format)
3. [Device Management](#device-management)
4. [Device Control](#device-control)
5. [Battery Testing](#battery-testing)
6. [Error Handling](#error-handling)
7. [Code Examples](#code-examples)

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Response Format

All API responses follow a consistent JSON format:

```json
{
  "success": boolean,
  "message": "string",
  "data": object | null
}
```

- `success`: Indicates if the operation was successful
- `message`: Human-readable description of the result
- `data`: Response payload (varies by endpoint)

## Device Management

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

**cURL Example:**
```bash
curl http://10.100.10.190:8000/api/health
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

**Parameters:**
- `port` (required): Serial port path (e.g., "/dev/ttyUSB0", "COM3")
- `baudrate` (optional): Communication speed, default 9600
- `timeout` (optional): Connection timeout in seconds, default 3.0
- `reset_input_on_connect` (optional): Reset input state on connection, default true

**cURL Example:**
```bash
curl -X POST http://10.100.10.190:8000/api/device/connect \
  -H "Content-Type: application/json" \
  -d '{"port": "/dev/ttyUSB0", "baudrate": 9600}'
```

### Disconnect Device

Disconnect from the current BK8520 device.

**Endpoint:** `POST /api/device/disconnect`

**Response Example:**
```json
{
  "success": true,
  "message": "Device disconnected",
  "data": null
}
```

**cURL Example:**
```bash
curl -X POST http://10.100.10.190:8000/api/device/disconnect
```

### Get Device Status

Get the current connection and operational status of the device.

**Endpoint:** `GET /api/device/status`

**Response Example:**
```json
{
  "success": true,
  "message": "Device status retrieved",
  "data": {
    "connected": true,
    "port": "/dev/ttyUSB0",
    "status": {
      "input_active": true,
      "remote_mode": false,
      "protection_active": false,
      "raw_status": 1
    }
  }
}
```

**cURL Example:**
```bash
curl http://10.100.10.190:8000/api/device/status
```

### Get Device Information

Get detailed device information including model, firmware, and specifications.

**Endpoint:** `GET /api/device/info`

**Response Example:**
```json
{
  "success": true,
  "message": "Device info retrieved",
  "data": {
    "model": "8520",
    "firmware": " 6001",
    "max_voltage": 120.0,
    "max_current": 60.0,
    "max_power": 999.0,
    "status": {
      "input_active": true,
      "remote_mode": false,
      "protection_active": false,
      "raw_status": 1
    },
    "port": "/dev/ttyUSB0"
  }
}
```

**cURL Example:**
```bash
curl http://10.100.10.190:8000/api/device/info
```

## Device Control

### Get Current Readings

Get real-time voltage, current, and power measurements.

**Endpoint:** `GET /api/device/readings`

**Response Example:**
```json
{
  "success": true,
  "message": "Readings retrieved",
  "data": {
    "voltage": 12.0,
    "current": 0.0,
    "power": 0.0,
    "timestamp": 1986603.273
  }
}
```

**cURL Example:**
```bash
curl http://10.100.10.190:8000/api/device/readings
```

### Control Input

Turn the device input on or off.

**Endpoint:** `POST /api/device/input`

**Request Body:**
```json
{
  "enabled": boolean
}
```

**Parameters:**
- `enabled` (required): true to turn input on, false to turn off

**cURL Examples:**
```bash
# Turn input ON
curl -X POST http://10.100.10.190:8000/api/device/input \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Turn input OFF
curl -X POST http://10.100.10.190:8000/api/device/input \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### Set Discharge Current

Set the discharge current for constant current mode.

**Endpoint:** `POST /api/device/current`

**Request Body:**
```json
{
  "current": number
}
```

**Parameters:**
- `current` (required): Discharge current in amperes (0.0 - 60.0A)

**Response Example:**
```json
{
  "success": true,
  "message": "Current set to 1.0A",
  "data": {
    "current": 1.0
  }
}
```

**cURL Example:**
```bash
curl -X POST http://10.100.10.190:8000/api/device/current \
  -H "Content-Type: application/json" \
  -d '{"current": 1.0}'
```

### Set Battery Cutoff Voltage

Set the minimum voltage at which the device will stop discharging.

**Endpoint:** `POST /api/device/voltage`

**Request Body:**
```json
{
  "voltage": number
}
```

**Parameters:**
- `voltage` (required): Cutoff voltage in volts (0.0 - 120.0V)

**Response Example:**
```json
{
  "success": true,
  "message": "Battery voltage set to 10.0V",
  "data": {
    "voltage": 10.0
  }
}
```

**cURL Example:**
```bash
curl -X POST http://10.100.10.190:8000/api/device/voltage \
  -H "Content-Type: application/json" \
  -d '{"voltage": 10.0}'
```

### Set Operation Mode

Set the device operation mode.

**Endpoint:** `POST /api/device/mode`

**Request Body:**
```json
{
  "mode": integer
}
```

**Parameters:**
- `mode` (required): Operation mode
  - `0`: CC (Constant Current)
  - `1`: CV (Constant Voltage)
  - `2`: CW (Constant Wattage)
  - `3`: CR (Constant Resistance)

**Response Example:**
```json
{
  "success": true,
  "message": "Operation mode set to CC",
  "data": {
    "mode": 0,
    "mode_name": "CC"
  }
}
```

**cURL Example:**
```bash
curl -X POST http://10.100.10.190:8000/api/device/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": 0}'
```

### Set Maximum Limits

#### Set Maximum Current
**Endpoint:** `POST /api/device/max-current`

```bash
curl -X POST http://10.100.10.190:8000/api/device/max-current \
  -H "Content-Type: application/json" \
  -d '{"current": 30.0}'
```

#### Set Maximum Power
**Endpoint:** `POST /api/device/max-power`

```bash
curl -X POST http://10.100.10.190:8000/api/device/max-power \
  -H "Content-Type: application/json" \
  -d '{"power": 500.0}'
```

#### Set Maximum Voltage
**Endpoint:** `POST /api/device/max-voltage`

```bash
curl -X POST http://10.100.10.190:8000/api/device/max-voltage \
  -H "Content-Type: application/json" \
  -d '{"voltage": 48.0}'
```

### Setup Discharge

Configure the device for constant current discharge operation.

**Endpoint:** `POST /api/device/setup-discharge`

**Request Body:**
```json
{
  "current": number
}
```

**cURL Example:**
```bash
curl -X POST http://10.100.10.190:8000/api/device/setup-discharge \
  -H "Content-Type: application/json" \
  -d '{"current": 2.0}'
```

## Battery Testing

### Start Battery Test

Start an automated battery capacity test.

**Endpoint:** `POST /api/battery-test/start`

**Request Body:**
```json
{
  "discharge_current": number,
  "cutoff_voltage": number,
  "max_time_hours": 24.0
}
```

**Parameters:**
- `discharge_current` (required): Discharge current in amperes
- `cutoff_voltage` (required): Minimum voltage to stop test in volts
- `max_time_hours` (optional): Maximum test duration in hours, default 24.0

**cURL Example:**
```bash
curl -X POST http://10.100.10.190:8000/api/battery-test/start \
  -H "Content-Type: application/json" \
  -d '{
    "discharge_current": 1.0,
    "cutoff_voltage": 10.5,
    "max_time_hours": 12.0
  }'
```

### Stop Battery Test

Stop the currently running battery test.

**Endpoint:** `POST /api/battery-test/stop`

**cURL Example:**
```bash
curl -X POST http://10.100.10.190:8000/api/battery-test/stop
```

### Get Battery Test Status

Get the current status of any running battery test.

**Endpoint:** `GET /api/battery-test/status`

**Response Example (No test running):**
```json
{
  "success": true,
  "message": "No battery test running",
  "data": {
    "test_active": false,
    "status": "stopped"
  }
}
```

**Response Example (Test running):**
```json
{
  "success": true,
  "message": "Battery test status",
  "data": {
    "test_active": true,
    "status": "running",
    "start_time": "2024-01-15T10:30:00Z",
    "elapsed_time": 3600,
    "current_voltage": 11.8,
    "current_current": 1.0,
    "current_power": 11.8,
    "capacity_ah": 1.0,
    "energy_wh": 11.8
  }
}
```

**cURL Example:**
```bash
curl http://10.100.10.190:8000/api/battery-test/status
```

### Get Battery Test Results

Get complete results from a battery test.

**Endpoint:** `GET /api/battery-test/results`

**cURL Example:**
```bash
curl http://10.100.10.190:8000/api/battery-test/results
```

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `422 Unprocessable Entity`: Validation error in request data
- `500 Internal Server Error`: Server error

### Error Response Format

When an error occurs, the response follows this format:

```json
{
  "success": false,
  "message": "Error description",
  "data": null
}
```

### Validation Errors (422)

For validation errors, additional detail is provided:

```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "Error message",
      "type": "error_type"
    }
  ]
}
```

## Code Examples

### Python Example

```python
import requests
import json

# Base URL for the API
BASE_URL = "http://10.100.10.190:8000"

class BK8520Client:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    def connect_device(self, port="/dev/ttyUSB0"):
        """Connect to BK8520 device"""
        response = requests.post(
            f"{self.base_url}/api/device/connect",
            json={"port": port}
        )
        return response.json()
    
    def get_readings(self):
        """Get current voltage, current, and power readings"""
        response = requests.get(f"{self.base_url}/api/device/readings")
        return response.json()
    
    def set_discharge_current(self, current):
        """Set discharge current in amperes"""
        response = requests.post(
            f"{self.base_url}/api/device/current",
            json={"current": current}
        )
        return response.json()
    
    def start_battery_test(self, discharge_current, cutoff_voltage, max_hours=24):
        """Start battery capacity test"""
        response = requests.post(
            f"{self.base_url}/api/battery-test/start",
            json={
                "discharge_current": discharge_current,
                "cutoff_voltage": cutoff_voltage,
                "max_time_hours": max_hours
            }
        )
        return response.json()
    
    def get_test_status(self):
        """Get battery test status"""
        response = requests.get(f"{self.base_url}/api/battery-test/status")
        return response.json()

# Usage example
client = BK8520Client()

# Connect to device
result = client.connect_device("/dev/ttyUSB0")
print(f"Connection: {result}")

# Get current readings
readings = client.get_readings()
print(f"Readings: {readings}")

# Set discharge current to 2A
current_result = client.set_discharge_current(2.0)
print(f"Current set: {current_result}")

# Start battery test
test_result = client.start_battery_test(
    discharge_current=1.0,
    cutoff_voltage=10.5,
    max_hours=12
)
print(f"Test started: {test_result}")
```

### JavaScript Example

```javascript
class BK8520Client {
    constructor(baseUrl = 'http://10.100.10.190:8000') {
        this.baseUrl = baseUrl;
    }

    async connectDevice(port = '/dev/ttyUSB0') {
        const response = await fetch(`${this.baseUrl}/api/device/connect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ port })
        });
        return await response.json();
    }

    async getReadings() {
        const response = await fetch(`${this.baseUrl}/api/device/readings`);
        return await response.json();
    }

    async setDischargeCurrent(current) {
        const response = await fetch(`${this.baseUrl}/api/device/current`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ current })
        });
        return await response.json();
    }

    async startBatteryTest(dischargeCurrent, cutoffVoltage, maxHours = 24) {
        const response = await fetch(`${this.baseUrl}/api/battery-test/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                discharge_current: dischargeCurrent,
                cutoff_voltage: cutoffVoltage,
                max_time_hours: maxHours
            })
        });
        return await response.json();
    }
}

// Usage example
const client = new BK8520Client();

// Connect and get readings
client.connectDevice('/dev/ttyUSB0')
    .then(result => console.log('Connected:', result))
    .then(() => client.getReadings())
    .then(readings => console.log('Readings:', readings))
    .catch(error => console.error('Error:', error));
```

### Bash Script Example

```bash
#!/bin/bash

BASE_URL="http://10.100.10.190:8000"

# Function to make API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ "$method" = "GET" ]; then
        curl -s "$BASE_URL$endpoint"
    else
        curl -s -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data"
    fi
}

# Connect to device
echo "Connecting to device..."
api_call POST "/api/device/connect" '{"port": "/dev/ttyUSB0"}'

# Set discharge current
echo "Setting discharge current to 1.5A..."
api_call POST "/api/device/current" '{"current": 1.5}'

# Get readings
echo "Getting current readings..."
api_call GET "/api/device/readings"

# Start battery test
echo "Starting battery test..."
api_call POST "/api/battery-test/start" '{
    "discharge_current": 1.0,
    "cutoff_voltage": 10.5,
    "max_time_hours": 8
}'

# Monitor test status
echo "Checking test status..."
api_call GET "/api/battery-test/status"
```

## Web Interface

In addition to the REST API, a web interface is available at:
**URL:** `http://10.100.10.190:8000`

The web interface provides a user-friendly way to:
- Monitor device status and readings in real-time
- Control discharge parameters
- Start and monitor battery tests
- View test results and charts

## Support and Troubleshooting

### Common Issues

1. **Device Connection Failed**
   - Verify the correct serial port path
   - Check that no other application is using the port
   - Ensure proper cable connection and power

2. **Permission Denied**
   - On Linux, ensure the user has access to the serial port
   - Add user to `dialout` group: `sudo usermod -a -G dialout $USER`

3. **Invalid Parameter Values**
   - Check device specifications for valid ranges
   - Voltage: 0-120V, Current: 0-60A, Power: 0-999W

### Device Specifications

- **Model**: BK8520 Electronic Load
- **Maximum Voltage**: 120V
- **Maximum Current**: 60A  
- **Maximum Power**: 999W
- **Communication**: RS232/USB Serial
- **Baud Rate**: 9600 (default)

For additional support or to report issues, please contact the system administrator.