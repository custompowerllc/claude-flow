# MTI-102284-05 Final Test with Uncovered Pack

## Document Overview
- **Document Number**: MTI-102284-05
- **Title**: Test Instruction for XGD-JGTFR18650-X72PC
- **Company**: Custom Power
- **Test Type**: Final Test with uncovered Pack

## Complete Test Workflow Diagram

```mermaid
flowchart TD
    A[Start: MTI-102284-05<br/>Final Test - Uncovered Pack] --> B[Equipment Setup<br/>Section 2]
    
    B --> B1[Computer with<br/>Easy Modbus Client]
    B --> B2[Test Harness<br/>ZHB-FX0926]
    B --> B3[Power Supply<br/>Agilent U8002A, 30V/5A]
    B --> B4[Electronic Load<br/>BK8500, 300W]
    
    B1 --> C[Test Setup<br/>Section 3]
    B2 --> C
    B3 --> C
    B4 --> C
    
    C --> C1[Connect USB to<br/>ZHB-FX0926]
    C1 --> C2[Connect Load to<br/>Pack+/- Terminals]
    C2 --> C3[Set Power Supply<br/>28.4V, 5A]
    
    C3 --> D[MODBUS Communication<br/>Section 4]
    
    D --> D1[Set SIGNAL_GND<br/>Switch to ON]
    D1 --> D2[Identify COM Port<br/>via Device Manager]
    D2 --> D3[Start Easy<br/>Modbus Client]
    D3 --> D4[Configure Settings<br/>ModbusRTU Serial]
    D4 --> D5[Communication Test 1<br/>FC3, Address 16, Values 2]
    D5 --> D6{7-byte Stream<br/>Received?}
    D6 -->|Yes| D7[Communication Test 2<br/>FC3, Address 64]
    D6 -->|No| D8[Check Connection<br/>& Retry]
    D8 --> D2
    D7 --> D9[Verify SOC Reading<br/>3rd byte must be 1E or less - 30 percent max]
    
    D9 --> E[Electrical Tests<br/>Section 5]
    
    E --> E1[Verify Pack OCV<br/>25V or greater]
    E1 --> E2[SIGNAL_GND Switch Test<br/>OFF - Voltage Lost]
    E2 --> E3[SIGNAL_GND Switch Test<br/>ON - Voltage Restored]
    E3 --> E4[Charge Acceptance Test<br/>5A to 28.4V for 15 sec]
    E4 --> E5[Discharge Function Test<br/>5A discharge for 15 sec]
    
    E5 --> F[Test Validation<br/>All Parameters Check]
    
    F --> F1{All Tests<br/>Passed?}
    F1 -->|Yes| G[Test Complete<br/>✓ Pack Validated]
    F1 -->|No| H[Troubleshoot<br/>& Retry Failed Tests]
    H --> E
    
    style A fill:#e1f5fe
    style G fill:#c8e6c9
    style H fill:#ffcdd2
    style D fill:#fff3e0
    style E fill:#f3e5f5
```

## Equipment Connection Diagram

```mermaid
graph TB
    subgraph "Test Equipment"
        COMP[Computer<br/>Easy Modbus Client]
        PS[Power Supply<br/>Agilent U8002A<br/>30V/5A, ID#156]
        EL[Electronic Load<br/>BK8500<br/>300W, ID#353]
    end
    
    subgraph "Test Interface"
        TH[Test Harness<br/>ZHB-FX0926<br/>RS232 + Pack+/-]
        SGS[SIGNAL_GND<br/>Switch]
    end
    
    subgraph "Device Under Test"
        PACK[XGD-JGTFR18650-X72PC<br/>Battery Pack<br/>Uncovered]
        BMS[BMS Controller<br/>with MODBUS]
        CELLS[Li-ion Cells<br/>18650 Configuration]
    end
    
    COMP -.USB.-> TH
    TH -.RS232.-> BMS
    PS -.28.4V/5A.-> PACK
    EL -.Load.-> TH
    TH -.Pack+/-.-> PACK
    TH --> SGS
    SGS --> BMS
    
    PACK --> BMS
    PACK --> CELLS
    
    style COMP fill:#e3f2fd
    style PS fill:#ffcdd2
    style EL fill:#c8e6c9
    style PACK fill:#fff3e0
    style TH fill:#f3e5f5
```

## MODBUS Communication Test Sequence

```mermaid
sequenceDiagram
    participant User
    participant EMC as Easy Modbus Client
    participant TH as Test Harness ZHB-FX0926
    participant BMS as BMS Controller
    
    Note over User,BMS: MODBUS Communication Setup
    
    User->>TH: Set SIGNAL_GND Switch ON
    User->>EMC: Identify COM Port
    User->>EMC: Start Easy Modbus Client
    User->>EMC: Configure ModbusRTU Settings
    
    Note over User,BMS: Communication Test 1
    User->>EMC: FC3 Command (Address: 16, Values: 2)
    EMC->>TH: Modbus RTU Request
    TH->>BMS: Forward Request
    BMS-->>TH: 7-byte Response
    TH-->>EMC: Forward Response
    EMC-->>User: Display Response
    
    Note over User,BMS: Communication Test 2
    User->>EMC: FC3 Command (Address: 64)
    EMC->>TH: SOC Request
    TH->>BMS: Forward Request
    BMS-->>TH: SOC Response (3rd byte)
    TH-->>EMC: Forward Response
    EMC-->>User: Display SOC - 30% or less
    
    Note over User,BMS: Validation
    User->>User: Verify 3rd byte is 1E or less - 30 percent max
```

## Electrical Test Requirements Matrix

```mermaid
graph TD
    subgraph "Test Requirements Table"
        T1[Test 1: Pack OCV<br/>Requirement: 25V or greater]
        T2[Test 2: Charge Acceptance<br/>28.4V, 10A<br/>29V to 29.4V range<br/>9.9A to 10.1A range]
        T3[Test 3: Discharge Function<br/>20A<br/>20V to 28.4V range<br/>-19.6A to -20.4A range]
        T4[Test 4: Peak Discharge<br/>45A for 5 sec]
        T5[Test 5: Discharge Overcurrent<br/>47A for 10 sec]
    end
    
    T1 --> PASS1{Pass?}
    T2 --> PASS2{Pass?}
    T3 --> PASS3{Pass?}
    T4 --> PASS4{Pass?}
    T5 --> PASS5{Pass?}
    
    PASS1 -->|Yes| PASS2
    PASS2 -->|Yes| PASS3
    PASS3 -->|Yes| PASS4
    PASS4 -->|Yes| PASS5
    PASS5 -->|Yes| COMPLETE[All Tests Complete<br/>✓ Pack Validated]
    
    PASS1 -->|No| FAIL[Test Failed<br/>Investigate & Retry]
    PASS2 -->|No| FAIL
    PASS3 -->|No| FAIL
    PASS4 -->|No| FAIL
    PASS5 -->|No| FAIL
    
    style T1 fill:#e8f5e8
    style T2 fill:#fff3e0
    style T3 fill:#fce4ec
    style T4 fill:#f3e5f5
    style T5 fill:#ffebee
    style COMPLETE fill:#c8e6c9
    style FAIL fill:#ffcdd2
```

## Easy Modbus Client Interface

```mermaid
graph TB
    subgraph "Easy Modbus Client Functions"
        subgraph "Read Functions"
            FC1[FC1: Read Coils]
            FC2[FC2: Read Discrete Inputs]
            FC3[FC3: Read Holding Registers<br/>⭐ Primary Test Function]
            FC4[FC4: Read Input Registers]
        end
        
        subgraph "Write Functions"
            FC5[FC5: Write Single Coil]
            FC6[FC6: Write Single Register]
            FC15[FC15: Write Multiple Coils]
            FC16[FC16: Write Multiple Registers]
        end
        
        subgraph "Connection Settings"
            PROTO[Protocol: ModbusRTU Serial]
            PORT[COM Port: COM7 example]
            BAUD[Baudrate: 9600]
            PAR[Parity: None]
            STOP[Stopbits: 1]
            SLAVE[Slave ID: Configurable]
        end
    end
    
    FC3 -.Primary Test.-> TEST1[Address 16, Values 2<br/>Results in 7-byte response]
    FC3 -.SOC Test.-> TEST2[Address 64<br/>Results in SOC reading 30% or less]
    
    style FC3 fill:#c8e6c9
    style TEST1 fill:#fff3e0
    style TEST2 fill:#fff3e0
```

## Safety and Protection Features

```mermaid
flowchart LR
    subgraph "Safety Considerations"
        ELEC[Electrical Safety<br/>• Proper grounding via SIGNAL_GND<br/>• Voltage verification<br/>• Overcurrent monitoring]
        
        EQUIP[Equipment Protection<br/>• Max current limits<br/>• Pack voltage verification<br/>• Temperature monitoring]
        
        SOC[SOC Protection<br/>• Prevent drop below 25%<br/>• Monitor 24V cutoff<br/>• Reduced load testing]
    end
    
    subgraph "Critical Operations"
        SIGNAL[SIGNAL_GND Switch<br/>Critical for operation]
        ADDR[Test Addresses<br/>16 & 64 are key points]
        BYTE3[3rd Byte Monitoring<br/>Must be 1E or less - 30%]
    end
    
    ELEC --> SIGNAL
    EQUIP --> ADDR
    SOC --> BYTE3
    
    style ELEC fill:#ffcdd2
    style EQUIP fill:#fff3e0
    style SOC fill:#c8e6c9
    style SIGNAL fill:#fce4ec
```