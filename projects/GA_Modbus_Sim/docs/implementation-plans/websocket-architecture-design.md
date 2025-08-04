# WebSocket Architecture Design for GA Modbus Simulator Integration

**Architect**: Claude Code Architecture Agent  
**Date**: 2025-08-04  
**Version**: 1.0  

## Executive Summary

This document outlines the comprehensive WebSocket architecture for integrating real-time data streaming into the GA Modbus Simulator system. The design enables multiple concurrent dashboard connections while maintaining backward compatibility with the existing CSV-based system.

## Current System Analysis

### Existing Architecture
- **Server**: `modbus_standalone_logger.py` - Writes CSV files with Modbus data
- **Dashboard**: `modbus_dashboard.py` - Reads CSV files for visualization
- **Data Flow**: Logger → CSV Files → Dashboard (polling-based)
- **Limitations**: File I/O bottleneck, no real-time updates, single CSV per session

### Performance Requirements
- **Latency**: <10ms for real-time data updates
- **Memory**: <50MB overhead for WebSocket infrastructure
- **Concurrency**: 5+ concurrent dashboard connections
- **Throughput**: 500ms data intervals with minimal latency

## WebSocket Architecture Design

### 1. Server Architecture (`modbus_standalone_logger.py`)

#### 1.1 Core Components

```python
# WebSocket Server Integration
class WebSocketModbusServer:
    """WebSocket server integrated with existing Modbus logger"""
    
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients = set()  # Connected WebSocket clients
        self.data_buffer = deque(maxlen=100)  # Recent data buffer
        self.csv_writer = None  # Existing CSV writer
        self.is_running = False
        
    async def start_server(self):
        """Start WebSocket server alongside CSV logging"""
        
    async def handle_client(self, websocket, path):
        """Handle new client connections"""
        
    async def broadcast_data(self, data):
        """Broadcast data to all connected clients"""
        
    def integrate_with_csv_logger(self, csv_logger):
        """Integration point with existing CSV logger"""
```

#### 1.2 Integration Strategy

**Minimal Code Changes**: Extend existing `StandaloneModbusLogger` class:

```python
class StandaloneModbusLogger:
    def __init__(self):
        # Existing initialization
        self.websocket_server = None
        self.websocket_enabled = False
    
    def enable_websocket(self, port=8765):
        """Enable WebSocket server"""
        self.websocket_server = WebSocketModbusServer(port=port)
        self.websocket_enabled = True
    
    def log_current_data(self, slave_id=1):
        """Extended to broadcast WebSocket data"""
        # Existing CSV logging
        success = self._existing_csv_log(slave_id)
        
        # WebSocket broadcast
        if self.websocket_enabled and success:
            asyncio.create_task(
                self.websocket_server.broadcast_data(self.last_data)
            )
        
        return success
```

#### 1.3 Hybrid Data Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Modbus BMS    │────│  Standalone      │────│   CSV Files     │
│   Hardware      │    │  Logger          │    │  (Existing)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  WebSocket       │
                       │  Broadcast       │
                       └──────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │ Dashboard 1 │ │ Dashboard 2 │ │ Dashboard N │
        │ (Real-time) │ │ (Real-time) │ │ (Real-time) │
        └─────────────┘ └─────────────┘ └─────────────┘
```

### 2. Message Protocol Specification

#### 2.1 JSON Message Format

**Data Update Message**:
```json
{
  "type": "data_update",
  "timestamp": "2025-08-04T04:32:00.123Z",
  "session": {
    "serial_number": "0520",
    "rma_number": "8765",
    "com_port": "COM3",
    "interval": 0.5
  },
  "data": {
    "afe_cell_volt1": 3206,
    "afe_cell_volt2": 3205,
    "afe_cell_volt3": 3204,
    "afe_cell_volt4": 3203,
    "afe_cell_volt5": 3202,
    "afe_cell_volt6": 3201,
    "afe_cell_volt7": 3200,
    "afe_cell_volt8": 3199,
    "afe_pack_volt": 25620,
    "fg_current": -1250,
    "afe_cell_volt_delta": 7,
    "fg_state_of_charge": 75,
    "afe_temp1": 3030,
    "afe_temp2": 3025
  },
  "statistics": {
    "record_count": 1542,
    "logging_duration": "00:12:51",
    "min_cell_voltage": 3.199,
    "max_cell_voltage": 3.206,
    "avg_cell_voltage": 3.2025
  }
}
```

**Client Connection Message**:
```json
{
  "type": "connection",
  "action": "connect",
  "client_id": "dashboard_001",
  "capabilities": ["real_time", "historical"],
  "timestamp": "2025-08-04T04:32:00.123Z"
}
```

**Server Status Message**:
```json
{
  "type": "status",
  "server_status": "active",
  "logging_active": true,
  "connected_clients": 3,
  "csv_file": "20250804_043200-0520-8765.csv",
  "uptime": "01:23:45"
}
```

#### 2.2 Message Types

| Type | Direction | Purpose | Frequency |
|------|-----------|---------|-----------|
| `data_update` | Server → Client | Real-time BMS data | Every 500ms |
| `connection` | Client → Server | Client connect/disconnect | On connection |
| `status` | Server → Client | Server status info | Every 30s |
| `error` | Bi-directional | Error notifications | As needed |
| `historical_request` | Client → Server | Request historical data | On demand |
| `historical_response` | Server → Client | Historical data chunk | On demand |

### 3. Client Architecture (`modbus_dashboard.py`)

#### 3.1 WebSocket Client Integration

```python
class ModbusDashboard:
    def __init__(self, csv_file=None, websocket_url=None):
        self.websocket_mode = websocket_url is not None
        self.websocket_url = websocket_url
        self.websocket = None
        self.csv_file = csv_file  # Fallback mode
        
    async def connect_websocket(self):
        """Connect to WebSocket server"""
        
    async def handle_websocket_message(self, message):
        """Handle incoming WebSocket messages"""
        
    def update_plots_websocket(self, data):
        """Update plots with WebSocket data"""
        
    def fallback_to_csv(self):
        """Fallback to CSV mode if WebSocket fails"""
```

#### 3.2 Dual-Mode Operation

**WebSocket Mode** (Primary):
- Real-time data updates via WebSocket
- <10ms latency for data visualization
- Automatic reconnection on connection loss

**CSV Fallback Mode**:
- Traditional file-based polling
- Activated when WebSocket unavailable
- Seamless transition with user notification

#### 3.3 Connection Management

```python
class WebSocketConnectionManager:
    """Manages WebSocket connection lifecycle"""
    
    def __init__(self, url, reconnect_interval=5):
        self.url = url
        self.reconnect_interval = reconnect_interval
        self.connection_attempts = 0
        self.max_attempts = 10
        
    async def connect_with_retry(self):
        """Connect with exponential backoff"""
        
    async def handle_disconnect(self):
        """Handle connection loss gracefully"""
        
    def get_connection_status(self):
        """Return connection health status"""
```

### 4. Performance Optimizations

#### 4.1 Memory Management

**Data Buffer Strategy**:
```python
class DataBuffer:
    """Efficient data buffering for WebSocket transmission"""
    
    def __init__(self, max_size=1000):
        self.buffer = deque(maxlen=max_size)
        self.compression_enabled = True
        
    def add_data_point(self, data):
        """Add data with optional compression"""
        
    def get_recent_data(self, count=100):
        """Get recent data for new clients"""
```

**Memory Footprint**:
- WebSocket server: ~5MB
- Client connections: ~1MB per client
- Data buffer: ~10MB (1000 data points)
- **Total overhead**: <50MB (within requirements)

#### 4.2 Latency Optimization

**Server Side**:
- Asynchronous WebSocket handling
- Direct data broadcast (no queuing)
- Binary message compression for large datasets

**Client Side**:
- Non-blocking plot updates
- Selective data processing (only changed values)
- Efficient matplotlib animation

#### 4.3 Concurrent Connection Handling

```python
async def handle_multiple_clients(self):
    """Efficiently handle 5+ concurrent connections"""
    
    # Connection pool management
    active_connections = set()
    
    # Broadcast optimization
    async def broadcast_to_clients(data):
        if not active_connections:
            return
            
        message = json.dumps(data)
        await asyncio.gather(
            *[client.send(message) for client in active_connections],
            return_exceptions=True
        )
```

### 5. Backward Compatibility Strategy

#### 5.1 CSV System Preservation

**Dual Output Mode**:
- CSV files continue to be written
- WebSocket operates independently
- Zero impact on existing CSV workflow

**Configuration Options**:
```toml
[websocket]
enabled = true
port = 8765
host = "localhost"
max_clients = 10

[logging]
csv_enabled = true  # Always enabled
websocket_enabled = true  # Optional
```

#### 5.2 Gradual Migration Path

**Phase 1**: WebSocket as optional feature
- Existing dashboards continue using CSV
- New dashboards can use WebSocket
- Both modes supported simultaneously

**Phase 2**: WebSocket as primary
- New installations default to WebSocket
- CSV remains as backup/export feature
- Migration tools for existing setups

### 6. Error Handling and Recovery

#### 6.1 Connection Failure Scenarios

**Server Failures**:
- WebSocket server crash → CSV mode continues
- Modbus connection loss → All clients notified
- Memory exhaustion → Graceful degradation

**Client Failures**:
- Network interruption → Automatic reconnection
- Dashboard crash → Server cleans up connection
- Data corruption → Request fresh data

#### 6.2 Failover Mechanisms

```python
class FailoverManager:
    """Manages failover between WebSocket and CSV modes"""
    
    def __init__(self):
        self.primary_mode = "websocket"
        self.fallback_mode = "csv"
        self.failover_threshold = 3  # Connection failures
        
    async def check_health(self):
        """Monitor connection health"""
        
    async def initiate_failover(self):
        """Switch to fallback mode"""
        
    async def attempt_recovery(self):
        """Try to restore primary mode"""
```

### 7. Security Considerations

#### 7.1 Local Network Security

**Connection Restrictions**:
- Bind to localhost by default
- Optional LAN binding with authentication
- No external internet exposure

**Message Validation**:
```python
def validate_message(message):
    """Validate incoming WebSocket messages"""
    try:
        data = json.loads(message)
        required_fields = ['type', 'timestamp']
        return all(field in data for field in required_fields)
    except json.JSONDecodeError:
        return False
```

#### 7.2 Data Integrity

**Message Authentication**:
- Optional HMAC signatures for critical data
- Sequence numbers to detect dropped messages
- Checksums for data validation

### 8. Testing Strategy

#### 8.1 Load Testing

**Concurrent Connection Test**:
```python
async def test_concurrent_connections():
    """Test 5+ simultaneous dashboard connections"""
    clients = []
    for i in range(10):
        client = await websockets.connect("ws://localhost:8765")
        clients.append(client)
    
    # Verify all receive data simultaneously
    # Measure latency for each client
```

**Memory Usage Test**:
```python
def test_memory_footprint():
    """Verify <50MB memory overhead"""
    import psutil
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # Start WebSocket server with 10 clients
    # Run for 1 hour with 500ms intervals
    
    final_memory = process.memory_info().rss
    overhead = final_memory - initial_memory
    assert overhead < 50 * 1024 * 1024  # 50MB
```

#### 8.2 Latency Testing

**Real-time Performance**:
```python
async def test_latency():
    """Verify <10ms latency requirement"""
    import time
    
    start_time = time.time()
    # Send data from server
    await websocket_server.broadcast_data(test_data)
    
    # Measure client reception time
    receive_time = await client.receive()
    latency = (receive_time - start_time) * 1000  # ms
    
    assert latency < 10  # <10ms requirement
```

### 9. Implementation Phases

#### Phase 1: Core WebSocket Infrastructure (Week 1)
- [ ] WebSocket server integration in `modbus_standalone_logger.py`
- [ ] Basic message protocol implementation
- [ ] Client connection handling
- [ ] Unit tests for core functionality

#### Phase 2: Dashboard Integration (Week 2)
- [ ] WebSocket client in `modbus_dashboard.py`
- [ ] Real-time plot updates
- [ ] Connection management and failover
- [ ] Integration tests

#### Phase 3: Performance Optimization (Week 3)
- [ ] Memory usage optimization
- [ ] Latency reduction techniques
- [ ] Concurrent connection scaling
- [ ] Load testing and benchmarking

#### Phase 4: Production Readiness (Week 4)
- [ ] Error handling and recovery
- [ ] Configuration management
- [ ] Documentation and deployment guides
- [ ] Final testing and validation

### 10. Configuration Management

#### 10.1 Server Configuration

```toml
# modbus-websocket-config.toml
[websocket]
enabled = true
host = "localhost"
port = 8765
max_clients = 10
buffer_size = 1000
compression = true

[compatibility]
csv_logging = true  # Always enabled
fallback_mode = "csv"
migration_support = true

[performance]
broadcast_interval = 0.5  # seconds
memory_limit = 50  # MB
connection_timeout = 30  # seconds
```

#### 10.2 Client Configuration

```toml
# dashboard-websocket-config.toml
[connection]
websocket_url = "ws://localhost:8765"
reconnect_attempts = 10
reconnect_interval = 5  # seconds

[fallback]
csv_fallback = true
csv_poll_interval = 1.0  # seconds
```

### 11. Architecture Decision Records (ADRs)

#### ADR-001: WebSocket over HTTP Polling
**Decision**: Use WebSocket for real-time communication
**Rationale**: 
- Lower latency (<10ms vs >100ms)
- Reduced server load
- True real-time updates
- Better user experience

#### ADR-002: JSON Message Protocol
**Decision**: Use JSON for message serialization
**Rationale**:
- Human-readable for debugging
- Standard web technology
- Flexible schema evolution
- Good compression ratio

#### ADR-003: Backward Compatibility Preservation
**Decision**: Maintain CSV logging alongside WebSocket
**Rationale**:
- Zero risk migration
- Existing tools continue working
- Data export capabilities
- Reliability through redundancy

#### ADR-004: localhost-only Default Binding
**Decision**: Bind WebSocket server to localhost by default
**Rationale**:
- Security by default
- No external exposure
- LAN access optional
- Minimal attack surface

### 12. Monitoring and Metrics

#### 12.1 Key Performance Indicators

| Metric | Target | Measurement |
|--------|--------|-------------|
| Latency | <10ms | End-to-end data transmission |
| Memory Usage | <50MB | Total WebSocket overhead |
| Concurrent Clients | 5+ | Simultaneous connections |
| Uptime | >99.9% | WebSocket server availability |
| Data Loss | 0% | Message delivery guarantee |

#### 12.2 Health Check Endpoints

```python
class HealthMonitor:
    """WebSocket server health monitoring"""
    
    def get_metrics(self):
        return {
            "connected_clients": len(self.clients),
            "messages_sent": self.message_count,
            "uptime": time.time() - self.start_time,
            "memory_usage": psutil.Process().memory_info().rss,
            "last_error": self.last_error_time
        }
```

### 13. Future Enhancements

#### 13.1 Advanced Features
- **Historical Data Streaming**: Efficient replay of past sessions
- **Real-time Alerts**: WebSocket-based alert notifications
- **Multi-device Support**: Connect multiple BMS units
- **Cloud Integration**: Optional cloud data streaming

#### 13.2 Scalability Improvements
- **Clustering**: Multiple WebSocket servers with load balancing
- **Message Queuing**: Redis/RabbitMQ for high-throughput scenarios
- **Data Compression**: Advanced compression for bandwidth optimization

### 14. Conclusion

This WebSocket architecture provides a robust, scalable, and backward-compatible solution for real-time data streaming in the GA Modbus Simulator system. The design meets all performance requirements while maintaining the reliability and functionality of the existing CSV-based approach.

The implementation phases ensure a gradual, low-risk migration path that preserves existing workflows while enabling modern real-time capabilities for enhanced user experience and system monitoring.

---

**Next Steps**: 
1. Review and approve architecture design
2. Begin Phase 1 implementation
3. Set up testing infrastructure
4. Coordinate with other swarm agents for implementation

**Architecture Review Checklist**:
- [ ] Performance requirements validated
- [ ] Security considerations addressed
- [ ] Backward compatibility ensured  
- [ ] Error handling comprehensive
- [ ] Testing strategy defined
- [ ] Implementation phases realistic