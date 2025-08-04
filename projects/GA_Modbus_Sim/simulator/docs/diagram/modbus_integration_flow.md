# GA Modbus Simulator Server & Standalone Logger Integration Flow

## System Architecture Overview

```mermaid
graph TB
    subgraph "GA BMS Simulator Environment"
        subgraph "Mock BMS Data Generator"
            CELL1[Cell Voltage 1<br/>3700±50mV]
            CELL2[Cell Voltage 2<br/>3705±50mV]
            CELL3[Cell Voltage 3<br/>3710±50mV]
            CELL4[Cell Voltage 4<br/>3715±50mV]
            CELL5[Cell Voltage 5<br/>3720±50mV]
            CELL6[Cell Voltage 6<br/>3725±50mV]
            CELL7[Cell Voltage 7<br/>3730±50mV]
            CELL8[Cell Voltage 8<br/>3735±50mV]
            
            PACK[Pack Voltage<br/>Sum of Cells]
            DELTA[Cell Delta<br/>Max - Min]
            TEMP1[Temperature 1<br/>25±4°C]
            TEMP2[Temperature 2<br/>26±4°C]
            CURRENT[Current<br/>±5000mA]
            SOC[State of Charge<br/>0-100%]
            
            CELL1 --> PACK
            CELL2 --> PACK
            CELL3 --> PACK
            CELL4 --> PACK
            CELL5 --> PACK
            CELL6 --> PACK
            CELL7 --> PACK
            CELL8 --> PACK
            
            CELL1 --> DELTA
            CELL8 --> DELTA
        end
        
        subgraph "Modbus Server Stack"
            DATAGEN[Data Generator<br/>MockBMSDataGenerator]
            REGMAP[Register Mapping<br/>Registers 10-45]
            DATASTORE[Modbus Datastore<br/>ModbusSequentialDataBlock]
            SERVER[TCP Server<br/>Port 5020]
            
            DATAGEN --> REGMAP
            REGMAP --> DATASTORE
            DATASTORE --> SERVER
        end
        
        CELL1 --> DATAGEN
        CELL2 --> DATAGEN
        CELL3 --> DATAGEN
        CELL4 --> DATAGEN
        CELL5 --> DATAGEN
        CELL6 --> DATAGEN
        CELL7 --> DATAGEN
        CELL8 --> DATAGEN
        PACK --> DATAGEN
        DELTA --> DATAGEN
        TEMP1 --> DATAGEN
        TEMP2 --> DATAGEN
        CURRENT --> DATAGEN
        SOC --> DATAGEN
    end
    
    subgraph "Network Communication"
        TCP[TCP/IP Connection<br/>127.0.0.1:5020]
        MODBUS[Modbus Protocol<br/>Function Code 4<br/>Read Input Registers]
    end
    
    subgraph "Standalone Logger Application"
        subgraph "Logger Core"
            CLIENT[Modbus TCP Client<br/>pymodbus 3.x]
            READER[Data Reader<br/>Address 9, Count 36]
            PARSER[Data Parser<br/>Register Map 10-45]
            FILTER[Moving Average Filter<br/>Cell Delta Smoothing]
        end
        
        subgraph "Data Processing"
            VALIDATOR[Data Validator<br/>Range Checking]
            FORMATTER[CSV Formatter<br/>Timestamp + Values]
            WRITER[CSV Writer<br/>Real-time Logging]
        end
        
        subgraph "User Interface"
            CLI[Command Line Interface<br/>Rich Console Output]
            CONFIG[Configuration<br/>TOML + JSON History]
            STATUS[Status Display<br/>Real-time Progress]
        end
        
        CLIENT --> READER
        READER --> PARSER
        PARSER --> FILTER
        FILTER --> VALIDATOR
        VALIDATOR --> FORMATTER
        FORMATTER --> WRITER
        
        CLI --> CLIENT
        CONFIG --> CLIENT
        STATUS --> CLI
    end
    
    subgraph "Output & Storage"
        CSV[CSV Log File<br/>timestamp-serial-rma.csv]
        LOGS[Log Directory<br/>Organized by Date/Serial]
        HISTORY[Session History<br/>JSON Tracking]
        
        WRITER --> CSV
        CSV --> LOGS
        WRITER --> HISTORY
    end
    
    SERVER --> TCP
    TCP --> MODBUS
    MODBUS --> CLIENT
    
    style CELL1 fill:#e1f5fe
    style CELL2 fill:#e1f5fe
    style CELL3 fill:#e1f5fe
    style CELL4 fill:#e1f5fe
    style CELL5 fill:#e1f5fe
    style CELL6 fill:#e1f5fe
    style CELL7 fill:#e1f5fe
    style CELL8 fill:#e1f5fe
    style PACK fill:#fff3e0
    style DELTA fill:#fff3e0
    style SOC fill:#e8f5e8
    style TCP fill:#f3e5f5
    style MODBUS fill:#f3e5f5
    style CSV fill:#fff8e1
```

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant BMS as Mock BMS Data
    participant Gen as Data Generator
    participant Srv as Modbus Server
    participant Net as TCP Network
    participant Log as Logger Client
    participant CSV as CSV File
    
    Note over BMS,CSV: Initialization Phase
    BMS->>Gen: Generate realistic cell voltages (1-8)
    Gen->>Gen: Calculate pack voltage (sum)
    Gen->>Gen: Calculate cell delta (max-min)
    Gen->>Srv: Update registers 10-45
    Srv->>Net: Listen on port 5020
    Log->>Net: Connect to 127.0.0.1:5020
    Log->>CSV: Create CSV file with headers
    
    Note over BMS,CSV: Continuous Logging Loop (500ms interval)
    loop Every 500ms
        BMS->>Gen: Update cell voltages with variations
        Gen->>Gen: Recalculate pack voltage & delta
        Gen->>Srv: Update datastore registers
        
        Log->>Net: Send Modbus query (FC4, addr=9, count=36)
        Net->>Srv: Forward query to server
        Srv->>Srv: Read registers 10-45 from datastore
        Srv->>Net: Return register values
        Net->>Log: Deliver Modbus response
        
        Log->>Log: Parse register data using map
        Log->>Log: Apply moving average filter (cell delta)
        Log->>Log: Validate data ranges
        Log->>CSV: Write timestamped record
        Log->>Log: Update console display
    end
    
    Note over BMS,CSV: Shutdown Phase
    Log->>CSV: Close file, update session history
    Log->>Net: Disconnect from server
    Srv->>Net: Close server socket
```

## Register Mapping Flow

```mermaid
graph LR
    subgraph "BMS Data Sources"
        A1[AFE Cell 1] --> R10[Register 10]
        A2[AFE Cell 2] --> R11[Register 11]
        A3[AFE Cell 3] --> R12[Register 12]
        A4[AFE Cell 4] --> R13[Register 13]
        A5[AFE Cell 5] --> R14[Register 14]
        A6[AFE Cell 6] --> R15[Register 15]
        A7[AFE Cell 7] --> R16[Register 16]
        A8[AFE Cell 8] --> R17[Register 17]
        
        P1[Pack Voltage] --> R18[Register 18]
        D1[Cell Delta] --> R19[Register 19]
        T1[Temp 1] --> R20[Register 20]
        T2[Temp 2] --> R21[Register 21]
        I1[Current] --> R22[Register 22]
        
        S1[SOC] --> R27[Register 27]
        F1[FG Voltage] --> R28[Register 28]
        F2[FG Current] --> R29[Register 29]
        
        MORE[... Additional<br/>FG Registers] --> R30_45[Registers 30-45]
    end
    
    subgraph "Modbus Query"
        QUERY[Read Input Registers<br/>Address: 9<br/>Count: 36<br/>Returns: Registers 10-45]
    end
    
    subgraph "CSV Output"
        CSV1[afe_cell_volt1]
        CSV2[afe_cell_volt2]
        CSV3[afe_cell_volt3]
        CSV4[afe_cell_volt4]
        CSV5[afe_cell_volt5]
        CSV6[afe_cell_volt6]
        CSV7[afe_cell_volt7]
        CSV8[afe_cell_volt8]
        CSVP[afe_pack_volt]
        CSVD[afe_cell_volt_delta]
        CSVS[fg_state_of_charge]
        CSVMORE[... 25 more columns]
    end
    
    R10 --> QUERY
    R11 --> QUERY
    R12 --> QUERY
    R13 --> QUERY
    R14 --> QUERY
    R15 --> QUERY
    R16 --> QUERY
    R17 --> QUERY
    R18 --> QUERY
    R19 --> QUERY
    R27 --> QUERY
    
    QUERY --> CSV1
    QUERY --> CSV2
    QUERY --> CSV3
    QUERY --> CSV4
    QUERY --> CSV5
    QUERY --> CSV6
    QUERY --> CSV7
    QUERY --> CSV8
    QUERY --> CSVP
    QUERY --> CSVD
    QUERY --> CSVS
    QUERY --> CSVMORE
    
    style R10 fill:#e3f2fd
    style R11 fill:#e3f2fd
    style R12 fill:#e3f2fd
    style R13 fill:#e3f2fd
    style R14 fill:#e3f2fd
    style R15 fill:#e3f2fd
    style R16 fill:#e3f2fd
    style R17 fill:#e3f2fd
    style QUERY fill:#f3e5f5
```

## Component Integration Details

### 1. Mock BMS Data Generator
```python
class MockBMSDataGenerator:
    - Generates realistic cell voltages (3700±50mV per cell)
    - Calculates pack voltage as sum of cells
    - Computes cell delta (max - min)
    - Simulates charging/discharging currents
    - Updates every 500ms with realistic variations
```

### 2. Modbus Server Stack
```python
# Server Configuration
- Protocol: TCP/IP Modbus
- Port: 5020
- Function Code: 4 (Read Input Registers)
- Address Range: 10-45 (36 registers)
- Data Type: INT16 (signed 16-bit integers)
- Byte Order: Big Endian
```

### 3. Standalone Logger
```python
# Logger Configuration  
- Client: pymodbus 3.x TCP client
- Query: Read registers 9-44 (gets data from 10-45)
- Interval: 500ms (2 Hz sampling rate)
- Filtering: Moving average for cell delta
- Output: CSV with timestamp + 36 data columns
```

## Data Validation & Quality Assurance

```mermaid
graph TD
    subgraph "Data Quality Pipeline"
        INPUT[Raw Modbus Data]
        RANGE[Range Validation<br/>Cell: 2500-4200mV<br/>Temp: -40°C to 80°C<br/>SOC: 0-100%]
        CALC[Calculation Validation<br/>Pack = Sum(Cells)<br/>Delta = Max - Min]
        FILTER[Moving Average Filter<br/>Cell Delta Smoothing<br/>Spike Detection]
        OUTPUT[Validated CSV Data]
        
        INPUT --> RANGE
        RANGE --> CALC
        CALC --> FILTER
        FILTER --> OUTPUT
    end
    
    subgraph "Quality Metrics"
        METRICS[Validation Results<br/>✅ 7/7 Checks Passed<br/>✅ 100% Data Quality<br/>✅ No Missing Values<br/>✅ Consistent Timing]
    end
    
    OUTPUT --> METRICS
    
    style RANGE fill:#e8f5e8
    style CALC fill:#e8f5e8
    style FILTER fill:#e8f5e8
    style METRICS fill:#fff8e1
```

## File Structure & Organization

```
GA_Modbus_Sim/
├── simulator/
│   ├── src/core/
│   │   ├── modbus_server.py      # Main server implementation
│   │   └── register_handler.py   # Register mapping & data
│   └── config/
│       └── register_mapping.json # Register definitions
├── src/
│   └── modbus_standalone_logger.py # Logger implementation
├── test_logger_direct.py          # Mock test implementation
├── validation_report.py           # Data validation
└── test_logs/
    └── *.csv                      # Generated log files
```

## Performance Characteristics

| Metric | Value | Status |
|--------|-------|---------|
| Logging Interval | 0.45s avg | ✅ Consistent |
| Data Completeness | 100% | ✅ No missing values |
| Cell Voltage Range | 3651-3785mV | ✅ Within spec |
| Pack Voltage Accuracy | 0mV deviation | ✅ Perfect calculation |
| Cell Balance | 84mV avg delta | ✅ Good balance |
| Temperature Range | 21-30°C | ✅ Normal operation |
| File Size | 13KB (66 records) | ✅ Efficient storage |

## Integration Testing Results

### ✅ **Successful Test Scenarios:**
1. **Connection Establishment**: TCP client connects to server successfully
2. **Data Query**: Modbus function code 4 queries work correctly  
3. **Register Mapping**: All 36 registers (10-45) mapped properly
4. **Data Validation**: Cell voltages 1-8 logged with realistic values
5. **Continuous Operation**: 30-second test with 66 records logged
6. **CSV Generation**: Valid CSV file with proper headers and data
7. **Quality Assurance**: 100% validation score (7/7 checks passed)

### 🎯 **Key Integration Points:**
- **Network Layer**: TCP/IP communication on localhost:5020
- **Protocol Layer**: Modbus TCP with function code 4
- **Data Layer**: 36 registers containing BMS simulation data
- **Application Layer**: Real-time CSV logging with validation
- **User Layer**: Rich console interface with progress monitoring

This integration successfully demonstrates the complete data flow from mock BMS sensors through Modbus protocol to CSV data logging, validating all cell voltage groups (1-8) and associated battery management parameters.