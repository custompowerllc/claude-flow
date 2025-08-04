# WebSocket Integration Sequence Diagram

## Real-Time Data Flow with WebSocket Communication

```mermaid
sequenceDiagram
    participant User
    participant Logger as Modbus Logger<br/>(Server)
    participant ModbusDevice as Modbus Device
    participant WebSocketServer as WebSocket Server<br/>(Logger Thread)
    participant Dashboard as Dashboard<br/>(Client)
    participant CSVFile as CSV File

    Note over User, CSVFile: System Initialization

    User->>Logger: Start logging session
    Logger->>Logger: Initialize WebSocket server
    Logger->>WebSocketServer: Start server on port 8765
    Logger->>ModbusDevice: Connect to Modbus device
    Logger->>CSVFile: Create CSV file
    
    Note over User, CSVFile: Dashboard Connection

    User->>Dashboard: Start dashboard
    Dashboard->>WebSocketServer: Connect to ws://localhost:8765
    WebSocketServer->>Dashboard: Connection established
    WebSocketServer->>Dashboard: Send session_info message
    
    Note over Logger, Dashboard: Real-Time Data Loop

    loop Every 0.5 seconds (or configured interval)
        Logger->>ModbusDevice: Read Modulus registers
        ModbusDevice->>Logger: Return battery data
        Logger->>CSVFile: Write data row (backup)
        Logger->>WebSocketServer: Queue data for broadcast
        WebSocketServer->>Dashboard: Broadcast data message
        Dashboard->>Dashboard: Parse and update plots
        Dashboard->>Dashboard: Update statistics
    end

    Note over User, CSVFile: Error Handling & Reconnection

    WebSocketServer-->>Dashboard: Connection lost
    Dashboard->>Dashboard: Attempt reconnection (max 30 tries)
    
    alt WebSocket reconnection successful
        Dashboard->>WebSocketServer: Reconnect
        WebSocketServer->>Dashboard: Connection re-established
        WebSocketServer->>Dashboard: Send current session info
        Note right of Dashboard: Resume real-time updates
    else WebSocket reconnection failed
        Dashboard->>CSVFile: Fallback to CSV polling
        Note right of Dashboard: Continue with CSV-based updates
        loop Every 1 second
            Dashboard->>CSVFile: Read new CSV data
            CSVFile->>Dashboard: Return new rows
            Dashboard->>Dashboard: Parse and update plots
        end
    end

    Note over User, CSVFile: Session Termination

    User->>Logger: Stop logging (Ctrl+C)
    Logger->>WebSocketServer: Send logging_stopped message
    WebSocketServer->>Dashboard: Broadcast logging_stopped
    Logger->>WebSocketServer: Stop WebSocket server
    Logger->>ModbusDevice: Disconnect
    Logger->>CSVFile: Close CSV file
    
    Dashboard->>Dashboard: Handle logging stopped
    Dashboard->>Dashboard: Show final statistics
```

## WebSocket Message Flow Detail

```mermaid
sequenceDiagram
    participant Logger as Logger Thread
    participant WSServer as WebSocket Server
    participant Client1 as Dashboard 1
    participant Client2 as Dashboard 2

    Note over Logger, Client2: Message Broadcasting Architecture

    Logger->>WSServer: queue_data(modbus_data)
    WSServer->>WSServer: Create JSON message with sequence number
    
    par Broadcast to all clients
        WSServer->>Client1: Send data message
        WSServer->>Client2: Send data message
    end
    
    Note over Logger, Client2: Connection Management

    Client1->>WSServer: New connection
    WSServer->>Client1: Send session_info
    WSServer->>Client1: Send message_history (last 100 messages)
    
    Client2--xWSServer: Connection lost
    WSServer->>WSServer: Remove client from broadcast list
    WSServer->>WSServer: Queue messages for potential reconnection
    
    Client2->>WSServer: Reconnection attempt
    WSServer->>Client2: Send queued messages
    WSServer->>Client2: Resume normal broadcasting
```

## Error Handling and Fallback Sequence

```mermaid
sequenceDiagram
    participant Dashboard
    participant WSConnection as WebSocket Connection
    participant CSVFallback as CSV File Reader
    participant UIDisplay as Dashboard UI

    Note over Dashboard, UIDisplay: Normal WebSocket Operation

    Dashboard->>WSConnection: Maintain connection
    WSConnection->>Dashboard: Receive real-time data
    Dashboard->>UIDisplay: Update plots (real-time)

    Note over Dashboard, UIDisplay: Connection Failure Detection

    WSConnection--xDashboard: Connection timeout/error
    Dashboard->>Dashboard: Start reconnection timer
    Dashboard->>UIDisplay: Show "Attempting reconnection..."

    Note over Dashboard, UIDisplay: Reconnection Attempts

    loop Reconnection attempts (max 30)
        Dashboard->>WSConnection: Attempt reconnection
        alt Connection successful
            WSConnection->>Dashboard: Connection restored
            Dashboard->>UIDisplay: Show "Connected via WebSocket"
            break Resume normal operation
        else Connection failed
            Dashboard->>Dashboard: Wait 2 seconds (exponential backoff)
            Dashboard->>UIDisplay: Update retry counter
        end
    end

    Note over Dashboard, UIDisplay: Fallback to CSV Mode

    Dashboard->>CSVFallback: Initialize CSV file reader
    Dashboard->>UIDisplay: Show "Using CSV fallback mode"
    
    loop CSV polling mode
        Dashboard->>CSVFallback: Poll for new data
        CSVFallback->>Dashboard: Return new CSV rows
        Dashboard->>UIDisplay: Update plots (slower refresh)
        Dashboard->>Dashboard: Wait 1 second
    end

    Note over Dashboard, UIDisplay: Optional WebSocket Recovery

    Dashboard->>WSConnection: Periodic reconnection check
    alt WebSocket available again
        WSConnection->>Dashboard: Connection successful
        Dashboard->>CSVFallback: Stop CSV polling
        Dashboard->>UIDisplay: Show "Reconnected to WebSocket"
    end
```

## Data Message Structure Flow

```mermaid
flowchart TD
    A[Modbus Device Data] --> B[Logger: Raw Register Values]
    B --> C{Data Processing}
    C --> D[Scale Values<br/>Apply Filters]
    C --> E[CSV Format]
    D --> F[WebSocket Message]
    E --> G[CSV File Write]
    
    F --> H{WebSocket Message Type}
    H -->|data| I[Real-time Data Payload]
    H -->|status| J[Status Information]
    H -->|error| K[Error Messages]
    H -->|config| L[Configuration Updates]
    
    I --> M[JSON Serialization]
    J --> M
    K --> M
    L --> M
    
    M --> N[WebSocket Broadcast]
    N --> O[Dashboard 1]
    N --> P[Dashboard 2]
    N --> Q[Dashboard N...]
    
    G --> R[CSV File]
    R --> S[Fallback Reader]
    S --> T[Dashboard<br/>CSV Mode]
    
    style F fill:#e1f5fe
    style M fill:#f3e5f5
    style N fill:#e8f5e8
    style R fill:#fff3e0
```

## Configuration and Deployment Sequence

```mermaid
sequenceDiagram
    participant Admin as System Administrator
    participant ConfigFile as Configuration Files
    participant Logger as Logger Process
    participant WSServer as WebSocket Server
    participant Dashboard as Dashboard Process

    Note over Admin, Dashboard: Initial Configuration

    Admin->>ConfigFile: Edit modbus-standalone-cli-config.toml
    Note right of ConfigFile: [websocket]<br/>enabled = true<br/>port = 8765<br/>host = "localhost"
    
    Admin->>Logger: Start logger with WebSocket enabled
    Logger->>ConfigFile: Load WebSocket configuration
    Logger->>WSServer: Initialize with config parameters
    
    Note over Admin, Dashboard: Dashboard Configuration

    Admin->>Dashboard: Start with WebSocket URL
    Note right of Admin: python modbus_dashboard.py<br/>--websocket ws://localhost:8765<br/>--fallback-csv data.csv
    
    Dashboard->>WSServer: Connect using configured URL
    WSServer->>Dashboard: Establish connection
    
    Note over Admin, Dashboard: Runtime Management

    Admin->>Logger: Monitor WebSocket status
    Logger->>Admin: Report connection count and status
    Admin->>Dashboard: Monitor data source mode
    Dashboard->>Admin: Report connection state and performance
    
    Note over Admin, Dashboard: Configuration Updates

    Admin->>ConfigFile: Update WebSocket port
    Admin->>Logger: Restart with new configuration
    Logger->>WSServer: Restart on new port
    Admin->>Dashboard: Update connection URL
    Dashboard->>WSServer: Reconnect to new port
```

## Performance Optimization Sequence

```mermaid
sequenceDiagram
    participant Logger as Logger Process
    participant Buffer as Message Buffer
    participant Compressor as Data Compressor
    participant WSServer as WebSocket Server
    participant Clients as Multiple Clients

    Note over Logger, Clients: High-Frequency Data Optimization

    loop Every 100ms (high frequency)
        Logger->>Buffer: Add data point to batch
        Buffer->>Buffer: Check batch size/timeout
        
        alt Batch ready (size=5 or timeout=0.5s)
            Buffer->>Compressor: Compress batch data
            Compressor->>WSServer: Send compressed batch
            WSServer->>Clients: Broadcast to all clients
            Buffer->>Buffer: Clear batch buffer
        end
    end

    Note over Logger, Clients: Memory Management

    WSServer->>WSServer: Monitor message queue size
    alt Queue size > threshold
        WSServer->>WSServer: Drop oldest messages
        WSServer->>Clients: Send queue_overflow warning
    end

    Note over Logger, Clients: Connection Quality Optimization

    WSServer->>Clients: Monitor client response times
    alt Slow client detected
        WSServer->>WSServer: Reduce message frequency for slow client
        WSServer->>Clients: Send adaptive_rate_notice
    end
```

This sequence diagram illustrates the complete WebSocket integration workflow, including:

1. **System initialization** with WebSocket server setup
2. **Real-time data flow** from Modbus device through WebSocket to dashboard
3. **Error handling and fallback** to CSV mode when WebSocket fails
4. **Message broadcasting** to multiple clients
5. **Configuration management** and deployment procedures
6. **Performance optimization** strategies for high-frequency data

The diagram shows how the WebSocket integration maintains backward compatibility while providing enhanced real-time performance and multi-client support.