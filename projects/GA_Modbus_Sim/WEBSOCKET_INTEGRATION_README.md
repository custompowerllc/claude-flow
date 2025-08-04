# WebSocket Integration for Modbus Standalone Logger

## Overview

The WebSocket integration adds real-time data streaming capabilities to the existing Modbus standalone logger. This allows external applications, dashboards, and monitoring systems to receive live Modbus data in real-time while maintaining full CSV logging functionality.

## Features

- **Dual Output**: Simultaneous CSV logging and WebSocket broadcasting
- **Zero Impact**: WebSocket functionality doesn't affect existing CSV logging
- **Multiple Clients**: Support for concurrent WebSocket connections
- **Configurable**: Host, port, and enable/disable options via TOML config and CLI args
- **Thread-Safe**: WebSocket server runs in separate thread with message queuing
- **Error Resilient**: Automatic client cleanup and reconnection handling
- **Rich Data**: Broadcasts both Modbus data and session metadata

## Configuration

### TOML Configuration

Add the following section to your `modbus-standalone-cli-config.toml`:

```toml
[websocket]
enabled = true
host = "localhost"
port = 8765
auto_start = true
```

### Command Line Arguments

```bash
# Enable WebSocket server
python modbus_standalone_logger.py --websocket-enabled

# Disable WebSocket server
python modbus_standalone_logger.py --websocket-disabled

# Custom host and port
python modbus_standalone_logger.py --websocket-host 0.0.0.0 --websocket-port 8080

# Complete example with WebSocket
python modbus_standalone_logger.py --port COM3 --sn 0573 --websocket-enabled --websocket-port 8080
```

## Data Format

WebSocket messages are JSON formatted with the following structure:

### Connection Message
```json
{
  "type": "connection",
  "status": "connected",
  "message": "Connected to Modbus data stream",
  "timestamp": "2025-08-04T04:35:00.000Z"
}
```

### Data Message
```json
{
  "type": "data",
  "timestamp": "2025-08-04T04:35:00.000Z",
  "data": {
    "session": {
      "serial_number": "0573",
      "rma_number": "8765",
      "record_count": 42
    },
    "modbus_data": {
      "afe_pack_volt": 3700,
      "afe_pack_current": 1500,
      "afe_soc": 85,
      "afe_cell_volt_max": 3750,
      "afe_cell_volt_min": 3680,
      "afe_cell_volt_delta": 70,
      "afe_temp_max": 25,
      "afe_temp_min": 23
    },
    "timestamp": "2025-08-04 04:35:00"
  }
}
```

## Usage Examples

### 1. Basic Usage
```bash
# Start logger with WebSocket enabled (default)
python modbus_standalone_logger.py --port COM3 --sn 0573

# WebSocket server will start automatically on ws://localhost:8765
```

### 2. Custom Configuration
```bash
# Use custom host and port
python modbus_standalone_logger.py \
  --port COM3 \
  --sn 0573 \
  --websocket-host 0.0.0.0 \
  --websocket-port 9000
```

### 3. Disable WebSocket
```bash
# Run with only CSV logging (no WebSocket)
python modbus_standalone_logger.py \
  --port COM3 \
  --sn 0573 \
  --websocket-disabled
```

## Client Examples

### HTML/JavaScript Client

Use the provided `websocket_test_client.html`:
1. Open the file in a web browser
2. Enter WebSocket URL (default: ws://localhost:8765)
3. Click Connect
4. View real-time data in the dashboard

### Python Client

Use the provided `websocket_python_client.py`:

```bash
# Connect to default server
python websocket_python_client.py

# Connect to custom server
python websocket_python_client.py --host 192.168.1.100 --port 8080

# Connect for specific duration
python websocket_python_client.py --duration 60
```

### Custom JavaScript Client

```javascript
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = function(event) {
    console.log('Connected to Modbus data stream');
};

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    
    if (message.type === 'data') {
        const modbusData = message.data.modbus_data;
        const session = message.data.session;
        
        console.log(`Battery ${session.serial_number}: SOC ${modbusData.afe_soc}%`);
        console.log(`Pack Voltage: ${modbusData.afe_pack_volt}mV`);
        console.log(`Cell Delta: ${modbusData.afe_cell_volt_delta}mV`);
    }
};

ws.onclose = function(event) {
    console.log('Connection closed');
};
```

## Integration with Dashboards

### Grafana Integration

1. Use Grafana WebSocket data source plugin
2. Connect to `ws://your-host:8765`
3. Parse JSON data and create visualizations

### Custom Dashboard

The WebSocket data format is designed to be easily consumed by custom dashboards:

- Real-time battery metrics
- Session tracking
- Historical data correlation
- Multi-device monitoring

## Performance Considerations

- **Message Queuing**: Data is queued for WebSocket broadcasting to prevent blocking CSV logging
- **Client Management**: Automatic cleanup of disconnected clients
- **Thread Safety**: WebSocket server runs in dedicated thread
- **Memory Usage**: Configurable queue size to prevent memory issues
- **CPU Impact**: Minimal impact on Modbus polling and CSV writing

## Troubleshooting

### Connection Issues

1. **Port Already in Use**: Change WebSocket port using `--websocket-port`
2. **Firewall Blocking**: Ensure port is open for WebSocket connections
3. **Host Configuration**: Use `0.0.0.0` to allow external connections

### Performance Issues

1. **High Memory Usage**: Check number of connected clients
2. **Slow Response**: Reduce logging interval or limit WebSocket clients
3. **Connection Drops**: Check network stability and client implementations

### Common Errors

```bash
# WebSocket server failed to start
WARNING: Failed to start WebSocket server, continuing with CSV logging only

# Client connection issues
ERROR: Error broadcasting to client: Connection closed
```

## Status and Monitoring

Check WebSocket status using:

```bash
python modbus_standalone_logger.py --status
```

Output includes:
- WebSocket server status (Running/Stopped/Disabled)
- Number of connected clients
- Message queue size

## Dependencies

Additional dependencies for WebSocket functionality:

```bash
pip install websockets
```

Note: If websockets is not installed, the logger will continue to work with CSV logging only.

## Security Considerations

- **Network Security**: WebSocket server binds to localhost by default
- **Authentication**: No built-in authentication (add reverse proxy if needed)
- **Data Exposure**: All Modbus data is broadcast to connected clients
- **Rate Limiting**: No built-in rate limiting (implement at client level)

## Future Enhancements

Planned improvements:
- Authentication support
- Data filtering options
- Compression for large datasets
- Historical data replay
- Client-specific data subscriptions

## Examples Repository

Find more examples and integration guides in the project documentation:
- Dashboard templates
- Client libraries
- Integration examples
- Performance benchmarks