# WebSocket Integration Technical Details

## Architecture Overview

The WebSocket integration provides real-time data streaming between the Modbus logger and dashboard applications using a client-server architecture.

### Components

1. **WebSocket Server** (in `modbus_standalone_logger.py`)
   - Embedded WebSocket server using `websockets` library
   - Runs on `ws://localhost:8765` by default
   - Broadcasts real-time Modbus data to connected clients

2. **WebSocket Client** (in `modbus_dashboard.py`)
   - Connects to WebSocket server for real-time data
   - Falls back to CSV file reading if WebSocket unavailable
   - Handles automatic reconnection with exponential backoff

3. **Message Protocol**
   - JSON-based message format
   - Two message types: `connection` and `data`
   - Includes timestamps and structured data

## Implementation Details

### WebSocket Server (`WebSocketBroadcaster` class)

#### Key Methods:
```python
async def register_client(self, websocket):
    """Register new WebSocket client and handle connection lifecycle"""
    
async def broadcast_data(self, data: Dict[str, Any]):
    """Broadcast data to all connected clients"""
    
def queue_data(self, data: Dict[str, Any]):
    """Thread-safe data queuing for broadcasting"""
    
async def data_sender(self):
    """Async coroutine to send queued data to clients"""
```

#### Server Configuration:
- **Host:** `localhost` (configurable)
- **Port:** `8765` (configurable) 
- **Ping Interval:** 20 seconds
- **Ping Timeout:** 10 seconds
- **Auto-start:** Configurable via TOML config

#### Threading Model:
- WebSocket server runs in separate daemon thread
- Uses `asyncio` event loop for async operations
- Thread-safe queue for data communication between main thread and WebSocket thread

### WebSocket Client (`WebSocketDataSource` class)

#### Key Features:
- **Automatic Reconnection:** Exponential backoff with jitter
- **Connection State Tracking:** `disconnected`, `connecting`, `connected`, `reconnecting`
- **Error Handling:** Comprehensive error catching and reporting
- **Fallback Mechanism:** Seamless CSV fallback when WebSocket fails

#### Reconnection Logic:
```python
async def _handle_reconnection(self):
    delay = min(self.reconnect_interval * (2 ** (self.reconnect_count - 1)), 60)
    delay += random.uniform(0, 1)  # Add jitter
```

### Message Protocol

#### Connection Message:
```json
{
  "type": "connection",
  "status": "connected",
  "message": "Connected to Modbus data stream",
  "timestamp": "2025-08-04 11:16:23"
}
```

#### Data Message Structure:
```json
{
  "type": "data",
  "timestamp": "2025-08-04T11:16:23",
  "data": {
    "session": {
      "serial_number": "0001",
      "rma_number": "test", 
      "record_count": 123
    },
    "modbus_data": {
      "afe_pack_volt": 26500,        // mV
      "afe_cell_volt1": 3240,       // mV  
      "afe_cell_volt2": 3242,       // mV
      "afe_cell_volt3": 3241,       // mV
      "afe_cell_volt4": 3238,       // mV
      "afe_cell_volt5": 3242,       // mV
      "afe_cell_volt6": 3241,       // mV
      "afe_cell_volt7": 3241,       // mV
      "afe_cell_volt8": 3240,       // mV
      "afe_cell_volt_delta": 25,    // mV
      "fg_current": -1500,          // mA
      "fg_state_of_charge": 85,     // %
      "afe_temp1": 3030,            // Kelvin * 10
      "afe_temp2": 3030             // Kelvin * 10
    },
    "timestamp": "2025-08-04 11:16:23"
  }
}
```

## Data Flow

### Logger to WebSocket Server:
1. Modbus data read from COM port every 0.5 seconds
2. Data parsed and processed by `log_current_data()`
3. Data queued using `websocket_broadcaster.queue_data()`
4. Background `data_sender()` coroutine broadcasts to all clients

### WebSocket to Dashboard:
1. Dashboard `WebSocketDataSource` connects to server
2. Receives welcome message and data messages
3. Data converted to dashboard format in `_handle_websocket_data()`
4. Dashboard charts updated in real-time

### Fallback Mechanism:
1. If WebSocket connection fails after max reconnection attempts
2. `DataSourceManager` switches to CSV mode
3. Dashboard continues reading from CSV file
4. Status shows "CSV FALLBACK MODE"

## Configuration

### TOML Configuration (`modbus-standalone-cli-config.toml`):
```toml
[websocket]
enabled = true
host = "localhost"
port = 8765
auto_start = true
```

### Command Line Options:
```bash
# Logger
--websocket-enabled        # Enable WebSocket server
--websocket-disabled       # Disable WebSocket server  
--websocket-host HOST      # WebSocket host (default: localhost)
--websocket-port PORT      # WebSocket port (default: 8765)

# Dashboard
--websocket URL            # WebSocket server URL
--websocket-fallback       # Enable CSV fallback (default: true)
```

## Error Handling

### Connection Errors:
- **10061 (Connection Refused):** Server not running
- **1011 (Internal Error):** Server-side exception
- **1006 (Abnormal Closure):** Network interruption

### Recovery Mechanisms:
- **Exponential Backoff:** Prevents connection spam
- **Max Reconnection Attempts:** 30 attempts before fallback
- **Jitter:** Randomized delays to prevent thundering herd
- **Graceful Degradation:** CSV fallback when WebSocket fails

### Debug Information:
- Connection state tracking
- Detailed error logging
- Performance metrics collection
- Message sequence validation

## Performance Characteristics

### Throughput:
- **Data Rate:** ~2 messages/second (0.5s interval)
- **Message Size:** ~1087 bytes per message
- **Bandwidth:** ~2.2 KB/s per client
- **Scalability:** Tested with 5+ concurrent clients

### Latency:
- **Local Connection:** < 10ms
- **Message Processing:** < 5ms
- **Update Frequency:** 500ms (configurable)

### Memory Usage:
- **Queue Size:** Limited to prevent memory leaks
- **Client Tracking:** Efficient set-based storage
- **Message Buffering:** Automatic cleanup of old messages

## Security Considerations

### Network Security:
- **Localhost Only:** Default binding to localhost
- **No Authentication:** Suitable for local development
- **Plain Text:** WebSocket messages not encrypted

### Production Recommendations:
- Use WSS (WebSocket Secure) for encrypted connections
- Implement authentication for multi-user environments
- Consider firewall rules for network access
- Monitor for excessive connection attempts

## Dependencies

### Python Libraries:
```python
import asyncio
import websockets  # pip install websockets
import json
import threading
import queue
import random
```

### Version Compatibility:
- **Python:** 3.7+ (asyncio support required)
- **websockets:** 8.0+ (tested with 15.0.1)
- **asyncio:** Built-in with Python 3.7+

## Testing Framework

### Test Coverage:
- **Connection Testing:** Handshake validation
- **Message Reception:** Data flow verification  
- **Protocol Validation:** JSON structure checking
- **Load Testing:** Multiple client simulation
- **Error Handling:** Failure scenario testing
- **Performance Testing:** Throughput measurement

### Test Files:
- `test_websocket_integration.py` - Comprehensive test suite
- `debug_websocket.py` - Diagnostic tool
- `test_websocket_com3.bat/.ps1` - Automation scripts