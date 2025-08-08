# BK-Integration Implementation Guide

## Architecture Overview

The BK-Integration CLI will serve as a unified control interface for both the BK8520 Electronic Load and BK9206b Power Supply, enabling comprehensive battery testing workflows through a single command-line application.

### System Architecture

```mermaid
graph TB
    subgraph "BK-Integration CLI"
        CLI[Click CLI]
        RICH[Rich Display]
        CFG[Config Manager]
        HTTP[HTTP Client Layer]
        
        subgraph "API Clients"
            BK8520[BK8520 API Client :8000]
            BK9206[BK9206b API Client :5300]
        end
        
        CLI --> HTTP
        RICH --> HTTP
        CFG --> HTTP
        HTTP --> BK8520
        HTTP --> BK9206
    end
    
    BK8520 --> LOAD[BK8520 Load Tester<br/>FastAPI Server]
    BK9206 --> POWER[BK9206b Power Supply<br/>FastAPI Server]
    
    style CLI fill:#e1f5fe
    style RICH fill:#e1f5fe
    style CFG fill:#e1f5fe
    style HTTP fill:#fff3e0
    style BK8520 fill:#c8e6c9
    style BK9206 fill:#c8e6c9
    style LOAD fill:#ffcdd2
    style POWER fill:#ffcdd2
```

### Component Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Config
    participant BK8520_Client
    participant BK9206b_Client
    participant BK8520_API
    participant BK9206b_API
    
    User->>CLI: bk-integration test battery
    CLI->>Config: Load configuration
    Config-->>CLI: Return config
    
    CLI->>BK9206b_Client: Start charging
    BK9206b_Client->>BK9206b_API: POST /api/output/enable
    BK9206b_API-->>BK9206b_Client: Success
    
    loop Monitor Charging
        CLI->>BK9206b_Client: Get status
        BK9206b_Client->>BK9206b_API: GET /api/status
        BK9206b_API-->>BK9206b_Client: Status data
    end
    
    CLI->>BK9206b_Client: Stop charging
    BK9206b_Client->>BK9206b_API: POST /api/output/disable
    
    Note over CLI: Rest period
    
    CLI->>BK8520_Client: Start discharge
    BK8520_Client->>BK8520_API: POST /api/device/input
    BK8520_API-->>BK8520_Client: Success
    
    loop Monitor Discharge
        CLI->>BK8520_Client: Get readings
        BK8520_Client->>BK8520_API: GET /api/device/readings
        BK8520_API-->>BK8520_Client: Measurement data
    end
    
    CLI->>BK8520_Client: Stop discharge
    BK8520_Client->>BK8520_API: POST /api/device/input
    
    CLI-->>User: Test results
```

## Battery Testing Workflow

```mermaid
flowchart LR
    Start([Start Test]) --> Connect[Connect Devices]
    Connect --> CheckConn{Connected?}
    CheckConn -->|No| Error[Show Error]
    CheckConn -->|Yes| Charge[Charge Phase]
    
    Charge --> MonitorCharge{Taper<br/>Detected?}
    MonitorCharge -->|No| Charge
    MonitorCharge -->|Yes| Rest1[Rest Period]
    
    Rest1 --> Discharge[Discharge Phase]
    Discharge --> MonitorDischarge{Cutoff<br/>Reached?}
    MonitorDischarge -->|No| Discharge
    MonitorDischarge -->|Yes| Rest2[Rest Period]
    
    Rest2 --> Recharge[Recharge Phase]
    Recharge --> Complete[Calculate Results]
    Complete --> End([End Test])
    
    Error --> End
    
    style Start fill:#4CAF50
    style End fill:#FF5252
    style Charge fill:#2196F3
    style Discharge fill:#FF9800
    style Recharge fill:#2196F3
    style Complete fill:#9C27B0
```

## State Management

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Connecting: Connect command
    Connecting --> Connected: Success
    Connecting --> Error: Failure
    Error --> Idle: Reset
    
    Connected --> Charging: Start charge
    Charging --> Resting: Taper detected
    Resting --> Discharging: Start discharge
    Discharging --> Resting2: Cutoff reached
    Resting2 --> Recharging: Start recharge
    Recharging --> Complete: Charge complete
    Complete --> Idle: Reset
    
    Charging --> Error: Fault
    Discharging --> Error: Fault
    Recharging --> Error: Fault
```

## API Integration Architecture

```mermaid
graph LR
    subgraph "External Applications"
        APP1[Python App]
        APP2[Curl/REST]
        APP3[WebSocket Client]
    end
    
    subgraph "BK-Integration API"
        REST[REST API<br/>:8080]
        WS[WebSocket<br/>/ws/monitor]
    end
    
    subgraph "Device APIs"
        DEV1[BK8520 API<br/>:8000]
        DEV2[BK9206b API<br/>:5300]
    end
    
    APP1 --> REST
    APP2 --> REST
    APP3 --> WS
    
    REST --> DEV1
    REST --> DEV2
    WS --> DEV1
    WS --> DEV2
    
    style REST fill:#FFD700
    style WS fill:#FFD700
```

## Data Flow Diagram

```mermaid
graph TD
    subgraph "Input Layer"
        CLI_CMD[CLI Commands]
        REST_REQ[REST Requests]
        CONFIG[Config File]
    end
    
    subgraph "Processing Layer"
        PARSER[Command Parser]
        VALIDATOR[Input Validator]
        ORCHESTRATOR[Test Orchestrator]
    end
    
    subgraph "Device Layer"
        BK8520_CTL[BK8520 Controller]
        BK9206_CTL[BK9206b Controller]
    end
    
    subgraph "Output Layer"
        CONSOLE[Console Display]
        JSON_OUT[JSON Response]
        LOG_FILE[Log File]
        METRICS[Test Metrics]
    end
    
    CLI_CMD --> PARSER
    REST_REQ --> PARSER
    CONFIG --> VALIDATOR
    
    PARSER --> VALIDATOR
    VALIDATOR --> ORCHESTRATOR
    
    ORCHESTRATOR --> BK8520_CTL
    ORCHESTRATOR --> BK9206_CTL
    
    BK8520_CTL --> METRICS
    BK9206_CTL --> METRICS
    
    METRICS --> CONSOLE
    METRICS --> JSON_OUT
    METRICS --> LOG_FILE
```

## Test Profile Configuration

```mermaid
graph TB
    subgraph "Test Profiles"
        DEFAULT[Default Profile<br/>CV: 16.8V<br/>CC: 2.0A<br/>Discharge: 5.0A]
        HIGH[High Capacity<br/>CV: 16.8V<br/>CC: 4.0A<br/>Discharge: 10.0A]
        CUSTOM[Custom Profile<br/>User Defined]
    end
    
    subgraph "Test Phases"
        CHARGE[Charge Phase]
        REST[Rest Phase]
        DISCHARGE[Discharge Phase]
        RECHARGE[Recharge Phase]
    end
    
    DEFAULT --> CHARGE
    HIGH --> CHARGE
    CUSTOM --> CHARGE
    
    CHARGE --> REST
    REST --> DISCHARGE
    DISCHARGE --> RECHARGE
    
    style DEFAULT fill:#E3F2FD
    style HIGH fill:#FFF3E0
    style CUSTOM fill:#E8F5E9
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        DEV[Local Development<br/>Python 3.6+]
    end
    
    subgraph "Testing"
        UNIT[Unit Tests<br/>pytest]
        INT[Integration Tests]
        E2E[E2E Tests]
    end
    
    subgraph "Deployment Options"
        LOCAL[Local Install<br/>pip install]
        DOCKER[Docker Container<br/>bk-integration:latest]
        SYSTEMD[System Service<br/>systemd unit]
    end
    
    subgraph "Production"
        API_SRV[API Server<br/>:8080]
        DEVICES[Device Controllers]
    end
    
    DEV --> UNIT
    DEV --> INT
    INT --> E2E
    
    E2E --> LOCAL
    E2E --> DOCKER
    E2E --> SYSTEMD
    
    LOCAL --> API_SRV
    DOCKER --> API_SRV
    SYSTEMD --> API_SRV
    
    API_SRV --> DEVICES
```

---

*Note: The complete implementation details, code examples, installation instructions, and API reference can be found in the full documentation.*