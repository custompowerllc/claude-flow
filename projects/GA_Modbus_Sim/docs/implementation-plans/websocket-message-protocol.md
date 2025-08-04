# WebSocket Message Protocol Specification

**Version**: 1.0  
**Date**: 2025-08-04  
**Author**: Claude Code Architecture Agent  

## Protocol Overview

This document defines the WebSocket message protocol for real-time communication between the GA Modbus Simulator logger and dashboard clients.

## Message Structure

### Base Message Format

All messages follow this JSON structure:

```json
{
  "type": "message_type",
  "timestamp": "ISO8601_timestamp",
  "version": "1.0",
  "payload": {}
}
```

## Message Types

### 1. Data Update Messages

**Type**: `data_update`  
**Direction**: Server → Client  
**Frequency**: Every 500ms (configurable)  

#### Full Data Update
```json
{
  "type": "data_update",
  "timestamp": "2025-08-04T04:32:00.123Z",
  "version": "1.0",
  "payload": {
    "session": {
      "serial_number": "0520",
      "rma_number": "8765",
      "com_port": "COM3",
      "interval": 0.5,
      "session_id": "session_20250804_043200",
      "logging_duration": "00:12:51"
    },
    "modbus_data": {
      "slave_id": 1,
      "register_base": 10,
      "raw_registers": [3206, 3205, 3204, 3203, 3202, 3201, 3200, 3199, 25620, -1250, 7, 75, 3030, 3025],
      "parsed_data": {
        "cell_voltages": {
          "afe_cell_volt1": 3206,
          "afe_cell_volt2": 3205,
          "afe_cell_volt3": 3204,
          "afe_cell_volt4": 3203,
          "afe_cell_volt5": 3202,
          "afe_cell_volt6": 3201,
          "afe_cell_volt7": 3200,
          "afe_cell_volt8": 3199
        },
        "pack_data": {
          "afe_pack_volt": 25620,
          "fg_current": -1250,
          "afe_cell_volt_delta": 7,
          "fg_state_of_charge": 75
        },
        "temperature": {
          "afe_temp1": 3030,
          "afe_temp2": 3025
        }
      }
    },
    "statistics": {
      "record_count": 1542,
      "min_cell_voltage": 3199,
      "max_cell_voltage": 3206,
      "avg_cell_voltage": 3202.5,
      "peak_delta": {
        "value": 45,
        "timestamp": "2025-08-04T04:25:15.456Z",
        "cell_voltages_at_peak": {
          "afe_cell_volt1": 3245,
          "afe_cell_volt2": 3200,
          "afe_cell_volt3": 3198,
          "afe_cell_volt4": 3201,
          "afe_cell_volt5": 3203,
          "afe_cell_volt6": 3199,
          "afe_cell_volt7": 3202,
          "afe_cell_volt8": 3197
        }
      }
    },
    "filter_status": {
      "cell_delta_filter": {
        "enabled": true,
        "window_size": 5,
        "spike_threshold": 2.0,
        "filtered_count": 3
      }
    }
  }
}
```

#### Compressed Data Update (for high frequency)
```json
{
  "type": "data_update_compressed",
  "timestamp": "2025-08-04T04:32:00.623Z",
  "version": "1.0",
  "payload": {
    "delta_data": {
      "afe_cell_volt1": 3207,  // Only changed values
      "fg_current": -1255,
      "afe_cell_volt_delta": 8
    },
    "record_count": 1543
  }
}
```

### 2. Connection Management Messages

#### Client Connection Request
**Type**: `connection_request`  
**Direction**: Client → Server  

```json
{
  "type": "connection_request",
  "timestamp": "2025-08-04T04:32:00.123Z",
  "version": "1.0",
  "payload": {
    "client_id": "dashboard_001",
    "client_type": "modbus_dashboard",
    "capabilities": [
      "real_time_data",
      "historical_data",
      "compression",
      "delta_updates"
    ],
    "preferred_update_rate": 500,  // milliseconds
    "data_preferences": {
      "include_raw_registers": false,
      "include_statistics": true,
      "compression_enabled": true
    }
  }
}
```

#### Server Connection Response
**Type**: `connection_response`  
**Direction**: Server → Client  

```json
{
  "type": "connection_response",
  "timestamp": "2025-08-04T04:32:00.125Z",
  "version": "1.0",
  "payload": {
    "status": "accepted",  // "accepted" | "rejected" | "queued"
    "client_id": "dashboard_001",
    "assigned_id": "conn_001",
    "server_capabilities": [
      "real_time_data",
      "historical_data",
      "compression",
      "delta_updates",
      "replay"
    ],
    "update_rate": 500,  // milliseconds (confirmed rate)
    "max_buffer_size": 1000,
    "session_info": {
      "current_session": "session_20250804_043200",
      "logging_active": true,
      "csv_file": "20250804_043200-0520-8765.csv"
    }
  }
}
```

#### Client Disconnection
**Type**: `disconnect`  
**Direction**: Client → Server  

```json
{
  "type": "disconnect",
  "timestamp": "2025-08-04T04:32:00.123Z",
  "version": "1.0",
  "payload": {
    "client_id": "dashboard_001",
    "reason": "user_requested"  // "user_requested" | "error" | "timeout"
  }
}
```

### 3. Server Status Messages

#### Status Update
**Type**: `server_status`  
**Direction**: Server → Client  
**Frequency**: Every 30 seconds or on status change  

```json
{
  "type": "server_status",
  "timestamp": "2025-08-04T04:32:00.123Z",
  "version": "1.0",
  "payload": {
    "server_status": "active",  // "active" | "error" | "maintenance"
    "logging_status": {
      "active": true,
      "csv_file": "20250804_043200-0520-8765.csv",
      "records_written": 1542,
      "last_write": "2025-08-04T04:31:59.623Z"
    },
    "modbus_status": {
      "connected": true,
      "port": "COM3",
      "slave_id": 1,
      "last_successful_read": "2025-08-04T04:31:59.500Z",
      "error_count": 0
    },
    "websocket_status": {
      "connected_clients": 3,
      "total_messages_sent": 15420,
      "uptime": "01:23:45",
      "memory_usage": {
        "total_mb": 12.5,
        "buffer_mb": 8.2,
        "connections_mb": 4.3
      }
    }
  }
}
```

### 4. Historical Data Messages

#### Historical Data Request
**Type**: `historical_request`  
**Direction**: Client → Server  

```json
{
  "type": "historical_request",
  "timestamp": "2025-08-04T04:32:00.123Z",
  "version": "1.0",
  "payload": {
    "client_id": "dashboard_001",
    "request_id": "hist_001",
    "time_range": {
      "start": "2025-08-04T04:00:00.000Z",
      "end": "2025-08-04T04:30:00.000Z"
    },
    "data_filter": {
      "parameters": ["cell_voltages", "pack_voltage", "current"],
      "sample_rate": 1.0,  // seconds (downsampling)
      "max_points": 1000
    }
  }
}
```

#### Historical Data Response
**Type**: `historical_response`  
**Direction**: Server → Client  

```json
{
  "type": "historical_response",
  "timestamp": "2025-08-04T04:32:00.123Z",
  "version": "1.0",
  "payload": {
    "request_id": "hist_001",
    "status": "success",  // "success" | "error" | "partial"
    "data_points": 856,
    "chunk_info": {
      "chunk_number": 1,
      "total_chunks": 1,
      "is_final": true
    },
    "data": [
      {
        "timestamp": "2025-08-04T04:00:00.500Z",
        "afe_cell_volt1": 3206,
        "afe_cell_volt2": 3205,
        "afe_pack_volt": 25620,
        "fg_current": -1250
      }
      // ... more data points
    ]
  }
}
```

### 5. Error Messages

#### Error Notification
**Type**: `error`  
**Direction**: Bi-directional  

```json
{
  "type": "error",
  "timestamp": "2025-08-04T04:32:00.123Z",
  "version": "1.0",
  "payload": {
    "error_code": "MODBUS_CONNECTION_LOST",
    "error_level": "warning",  // "info" | "warning" | "error" | "critical"
    "message": "Modbus connection lost. Attempting reconnection...",
    "details": {
      "port": "COM3",
      "last_successful_read": "2025-08-04T04:31:45.123Z",
      "retry_attempt": 1,
      "max_retries": 5
    },
    "recovery_action": "automatic_retry",
    "estimated_recovery_time": 10  // seconds
  }
}
```

### 6. Control Messages

#### Logging Control
**Type**: `logging_control`  
**Direction**: Client → Server  

```json
{
  "type": "logging_control",
  "timestamp": "2025-08-04T04:32:00.123Z",
  "version": "1.0",
  "payload": {
    "action": "pause",  // "start" | "pause" | "resume" | "stop"
    "client_id": "dashboard_001",
    "authorization": "admin_token_here"  // If required
  }
}
```

#### Configuration Update
**Type**: `config_update`  
**Direction**: Client → Server  

```json
{
  "type": "config_update",
  "timestamp": "2025-08-04T04:32:00.123Z",
  "version": "1.0",
  "payload": {
    "client_id": "dashboard_001",
    "configuration": {
      "update_rate": 1000,  // Change to 1 second intervals
      "filter_settings": {
        "cell_delta_filter": {
          "enabled": false
        }
      }
    }
  }
}
```

## Protocol Features

### 1. Message Compression

For high-frequency data transmission, messages can be compressed using gzip:

```python
import gzip
import json

def compress_message(message_dict):
    """Compress WebSocket message"""
    json_str = json.dumps(message_dict)
    compressed = gzip.compress(json_str.encode('utf-8'))
    return compressed

def decompress_message(compressed_data):
    """Decompress WebSocket message"""
    decompressed = gzip.decompress(compressed_data)
    return json.loads(decompressed.decode('utf-8'))
```

### 2. Delta Updates

To reduce bandwidth, only changed values are transmitted:

```python
def create_delta_update(previous_data, current_data):
    """Create delta update message"""
    delta = {}
    for key, value in current_data.items():
        if key not in previous_data or previous_data[key] != value:
            delta[key] = value
    return delta
```

### 3. Message Validation

```python
import jsonschema

def validate_message(message, message_type):
    """Validate message against schema"""
    schema = get_schema_for_type(message_type)
    try:
        jsonschema.validate(message, schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e)
```

## Error Codes

| Code | Description | Recovery Action |
|------|-------------|-----------------|
| `CONNECTION_TIMEOUT` | Client connection timeout | Reconnect |
| `MODBUS_CONNECTION_LOST` | Modbus hardware disconnected | Check hardware |
| `INVALID_MESSAGE_FORMAT` | Malformed JSON message | Fix client code |
| `UNSUPPORTED_MESSAGE_TYPE` | Unknown message type | Update protocol version |
| `RATE_LIMIT_EXCEEDED` | Too many messages from client | Throttle requests |
| `BUFFER_OVERFLOW` | Server buffer full | Increase buffer or reduce rate |
| `CSV_WRITE_ERROR` | Cannot write to CSV file | Check disk space/permissions |
| `AUTHENTICATION_FAILED` | Invalid credentials | Provide valid credentials |

## Implementation Guidelines

### 1. Server Implementation

```python
import asyncio
import websockets
import json
from datetime import datetime

class WebSocketProtocolHandler:
    def __init__(self):
        self.protocol_version = "1.0"
        self.connected_clients = {}
        
    async def handle_message(self, websocket, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'connection_request':
                await self.handle_connection_request(websocket, data)
            elif message_type == 'historical_request':
                await self.handle_historical_request(websocket, data)
            # ... handle other message types
                
        except json.JSONDecodeError:
            await self.send_error(websocket, "INVALID_MESSAGE_FORMAT", 
                                 "Message is not valid JSON")
    
    async def send_data_update(self, data):
        """Send data update to all connected clients"""
        message = {
            "type": "data_update",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": self.protocol_version,
            "payload": data
        }
        
        # Broadcast to all clients
        if self.connected_clients:
            await asyncio.gather(
                *[client.send(json.dumps(message)) 
                  for client in self.connected_clients.values()],
                return_exceptions=True
            )
```

### 2. Client Implementation

```python
import asyncio
import websockets
import json

class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.websocket = None
        self.connected = False
        
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.url)
            self.connected = True
            
            # Send connection request
            await self.send_connection_request()
            
            # Start message handler
            await self.message_handler()
            
        except Exception as e:
            print(f"Connection failed: {e}")
            self.connected = False
    
    async def send_connection_request(self):
        """Send connection request to server"""
        message = {
            "type": "connection_request",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0",
            "payload": {
                "client_id": "dashboard_001",
                "client_type": "modbus_dashboard",
                "capabilities": ["real_time_data", "historical_data"]
            }
        }
        await self.websocket.send(json.dumps(message))
    
    async def message_handler(self):
        """Handle incoming messages"""
        async for message in self.websocket:
            try:
                data = json.loads(message)
                await self.process_message(data)
            except json.JSONDecodeError:
                print("Received invalid JSON message")
```

## Testing Protocol

### 1. Message Validation Tests

```python
def test_data_update_message():
    """Test data update message format"""
    message = {
        "type": "data_update",
        "timestamp": "2025-08-04T04:32:00.123Z",
        "version": "1.0",
        "payload": {
            "session": {"serial_number": "0520"},
            "modbus_data": {"afe_cell_volt1": 3206}
        }
    }
    
    is_valid, error = validate_message(message, "data_update")
    assert is_valid, f"Message validation failed: {error}"
```

### 2. Protocol Compliance Tests

```python
async def test_connection_flow():
    """Test complete connection flow"""
    # 1. Client sends connection request
    # 2. Server responds with connection response
    # 3. Server starts sending data updates
    # 4. Client processes data updates
    # 5. Client sends disconnect message
```

## Version Compatibility

### Version 1.0 (Current)
- Basic real-time data updates
- Connection management
- Historical data requests
- Error handling

### Future Versions
- **1.1**: Multi-device support, enhanced compression
- **1.2**: Authentication and authorization
- **2.0**: Binary protocol option, advanced features

## Conclusion

This WebSocket message protocol provides a comprehensive, extensible foundation for real-time communication in the GA Modbus Simulator system. The protocol supports efficient data transmission, robust error handling, and backward compatibility while maintaining the flexibility for future enhancements.