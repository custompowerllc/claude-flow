# MTI-102284-10 Final Test with Covered Pack

## Document Overview
- **Document Number**: MTI-102284-10
- **Title**: Test Instruction for XGD-JGTFR18650-X72PC
- **Company**: Custom Power
- **Test Type**: Final Test with covered Pack

## Complete Test Workflow Diagram

```mermaid
flowchart TD
    A[Start: MTI-102284-10<br/>Final Test - Covered Pack] --> B[Equipment Setup<br/>Section 2]
    
    B --> B1[Computer with<br/>Easy Modbus Client]
    B --> B2[Test Harness<br/>ZHB-FX0926]
    B --> B3[Power Supply<br/>Agilent U8002A, 30V/5A]
    B --> B4[Electronic Load<br/>BK8500, 300W]
    
    B1 --> C[Test Setup<br/>Section 3]
    B2 --> C
    B3 --> C
    B4 --> C
    
    C --> C1[Connect USB to<br/>ZHB-FX0926]
    C1 --> C2[Connect Load to<br/>ZHB-FX0926 Pack+/-]
    C2 --> C3[Set Power Supply<br/>28.4V, 5A]
    
    C3 --> D[MODBUS Verification<br/>Section 4]
    
    D --> D1[Set SIGNAL_GND<br/>Switch to ON<br/>Maximum Extension]
    D1 --> D2[Identify COM Port<br/>Device Manager/Ports]
    D2 --> D3[Start Easy<br/>Modbus Client]
    D3 --> D4[Configure Connection<br/>ModbusRTU Serial, COM8]
    D4 --> D5[Initial Test: FC3<br/>Address 16, Values 2]
    D5 --> D6{7-byte Stream<br/>Response OK?}
    D6 -->|Yes| D7[SOC Test: FC3<br/>Address 64]
    D6 -->|No| D8[Check Settings<br/>& Connection]
    D8 --> D4
    D7 --> D9[Verify 3rd Byte<br/>≤ 1E (30%), Example: 1A=26%]
    
    D9 --> E[Electrical Tests<br/>Section 5]
    
    E --> E1[Verify Pack OCV<br/>From Requirements Table]
    E1 --> E2[Pack Enable Function<br/>Press-Hold Pack_Enable Button]
    E2 --> E2A[Pack Voltage Shows Up<br/>Release Button → 0V]
    E2A --> E3[Charge Acceptance<br/>5A to 28.4V for 15 sec]
    E3 --> E4[Discharge Function<br/>5A discharge for 15 sec]
    
    E4 --> F[Test Requirements<br/>Validation]
    
    F --> F1[Test 1: Pack OCV ≥ 25V]
    F --> F2[Test 2: Charge 28.4V/10A<br/>29V ≤ Vbat ≤ 29.4V<br/>9.9A ≤ Ibat ≤ 10.1A]
    F --> F3[Test 3: Discharge 20A<br/>20V ≤ Vbat ≤ 28.4V<br/>-19.6A ≤ Ibat ≤ -20.4A]
    F --> F4[Test 4: Peak Discharge<br/>45A for 5 sec]
    F --> F5[Test 5: Overcurrent<br/>47A for 10 sec]
    
    F1 --> G{All Tests<br/>Pass?}
    F2 --> G
    F3 --> G
    F4 --> G
    F5 --> G
    
    G -->|Yes| H[Test Complete<br/>✓ Covered Pack Validated]
    G -->|No| I[Troubleshoot<br/>& Retest Failed Items]
    I --> E
    
    style A fill:#e1f5fe
    style H fill:#c8e6c9
    style I fill:#ffcdd2
    style D fill:#fff3e0
    style E fill:#f3e5f5
    style F fill:#fce4ec
```

## Equipment and Interface Architecture

```mermaid
graph TB
    subgraph "Test Equipment Layer"
        COMP[Computer<br/>Easy Modbus Client<br/>COM8 Interface]
        PS[Power Supply<br/>Agilent U8002A<br/>30V/5A, ID#156]
        EL[Electronic Load<br/>BK8500<br/>300W, ID#353]
    end
    
    subgraph "Interface Layer"
        TH[Test Harness<br/>ZHB-FX0926<br/>RS232 + Pack+/-]
        SGS[SIGNAL_GND Switch<br/>ON/OFF Control]
        PEB[Pack_Enable Button<br/>Press-Hold Function]
    end
    
    subgraph "Device Under Test"
        subgraph "Covered Pack"
            PACK[XGD-JGTFR18650-X72PC<br/>Battery Pack<br/>(Covered/Enclosed)]
            BMS[BMS Controller<br/>MODBUS Interface]
            PROT[Protection Circuits<br/>Enable/Disable Logic]
        end
    end
    
    COMP -.USB.-> TH
    TH -.RS232.-> BMS
    PS -.Charge 28.4V.-> TH
    EL -.Load Testing.-> TH
    TH -.Pack+/-.-> PACK
    
    SGS --> TH
    PEB --> PROT
    TH --> SGS
    TH --> PEB
    
    PACK --> BMS
    PACK --> PROT
    BMS --> PROT
    
    style COMP fill:#e3f2fd
    style PS fill:#ffcdd2
    style EL fill:#c8e6c9
    style PACK fill:#fff3e0
    style TH fill:#f3e5f5
    style SGS fill:#ffebee
    style PEB fill:#e8f5e8
```

## MODBUS Communication Protocol Flow

```mermaid
sequenceDiagram
    participant User
    participant EMC as Easy Modbus Client
    participant TH as ZHB-FX0926 Harness
    participant BMS as Covered Pack BMS
    
    Note over User,BMS: Communication Setup
    User->>TH: Set SIGNAL_GND Switch ON (Max Extension)
    User->>EMC: Identify COM Port (Device Manager)
    User->>EMC: Start Easy Modbus Client
    User->>EMC: Select ModbusRTU (Serial)
    User->>EMC: Configure: COM8, 9600 baud, None parity, 1 stopbit
    
    Note over User,BMS: Initial Communication Test (4.2)
    User->>EMC: FC3 Command
    EMC->>EMC: Set Starting Address: 16
    EMC->>EMC: Set Number of Values: 2
    EMC->>TH: Modbus RTU Request
    TH->>BMS: Forward Request
    BMS-->>TH: 7-byte Response Stream
    TH-->>EMC: Forward Response
    EMC-->>User: Display 7-byte Stream
    User->>User: Verify Success
    
    Note over User,BMS: SOC Reading Test (4.3)
    User->>EMC: Change Starting Address to 64
    User->>EMC: Press FC3 Again
    EMC->>TH: SOC Request
    TH->>BMS: Forward SOC Request
    BMS-->>TH: SOC Response
    TH-->>EMC: Forward SOC Data
    EMC-->>User: Display SOC (3rd byte)
    User->>User: Verify 3rd byte ≤ 1E (30%)<br/>Example: 1A = 26%
```

## Pack Enable Function Test

```mermaid
stateDiagram-v2
    [*] --> PackDisabled: Initial State
    PackDisabled --> PackEnabled: Press & Hold Pack_Enable Button
    PackEnabled --> PackVoltageVisible: Pack Voltage Shows Up
    PackVoltageVisible --> PackDisabled: Release Pack_Enable Button
    PackDisabled --> PackVoltageZero: Pack Voltage → 0V
    PackVoltageZero --> [*]: Test Complete
    
    note right of PackEnabled: Voltage appears on load
    note right of PackDisabled: Voltage disappears
```

## Test Requirements Validation Matrix

```mermaid
graph TD
    subgraph "Test Requirements (Section 5)"
        T1[Test 1: Pack OCV<br/>≥ 25V]
        T2[Test 2: Charge Acceptance<br/>28.4V, 10A<br/>Voltage: 29V ≤ Vbat ≤ 29.4V<br/>Current: 9.9A ≤ Ibat ≤ 10.1A]
        T3[Test 3: Discharge Function<br/>20A<br/>Voltage: 20V ≤ Vbat ≤ 28.4V<br/>Current: -19.6A ≤ Ibat ≤ -20.4A]
        T4[Test 4: Peak Discharge<br/>45A for 5 seconds<br/>TBD - Requirements Not Specified]
        T5[Test 5: Discharge Overcurrent<br/>47A for 10 seconds<br/>TBD - Requirements Not Specified]
    end
    
    subgraph "Test Execution"
        SETUP[Setup Verification<br/>OCV Check]
        PE[Pack Enable Test<br/>Button Function]
        CHARGE[Charge Test<br/>5A to 28.4V, 15 sec]
        DISCHARGE[Discharge Test<br/>5A discharge, 15 sec]
    end
    
    subgraph "Validation Results"
        PASS[All Tests Pass<br/>✓ Pack Validated]
        FAIL[Test Failure<br/>Troubleshoot Required]
        NOTE[Special Note:<br/>Reduced Load Testing<br/>Prevents SOC Drop to 0%<br/>if Pack Voltage hits 24V]
    end
    
    T1 --> SETUP
    T2 --> CHARGE
    T3 --> DISCHARGE
    T4 --> PE
    T5 --> PE
    
    SETUP --> PASS
    PE --> PASS
    CHARGE --> PASS
    DISCHARGE --> PASS
    
    SETUP --> FAIL
    PE --> FAIL
    CHARGE --> FAIL
    DISCHARGE --> FAIL
    
    NOTE --> PASS
    
    style T1 fill:#e8f5e8
    style T2 fill:#fff3e0
    style T3 fill:#fce4ec
    style T4 fill:#f3e5f5
    style T5 fill:#ffebee
    style PASS fill:#c8e6c9
    style FAIL fill:#ffcdd2
    style NOTE fill:#e1f5fe
```

## Easy Modbus Client Interface Details

```mermaid
graph TB
    subgraph "Easy Modbus Client Configuration"
        subgraph "Connection Settings"
            PROTO[Protocol: ModbusRTU Serial]
            PORT[Port: COM8]
            BAUD[Baudrate: 9600]
            PARITY[Parity: None]
            STOP[Stopbits: 1]
        end
        
        subgraph "Function Codes Available"
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
        end
        
        subgraph "Test Parameters"
            TEST1[Test 1: Address 16<br/>Values: 2<br/>Expected: 7-byte stream]
            TEST2[Test 2: Address 64<br/>Expected: SOC ≤ 30%<br/>Example: 1A = 26%]
        end
    end
    
    FC3 --> TEST1
    FC3 --> TEST2
    PROTO --> FC3
    PORT --> FC3
    
    style FC3 fill:#c8e6c9
    style TEST1 fill:#fff3e0
    style TEST2 fill:#fce4ec
```

## Safety and Technical Specifications

```mermaid
flowchart LR
    subgraph "Technical Specifications"
        PACK_SPEC[Target Pack:<br/>XGD-JGTFR18650-X72PC]
        VOLT_SPEC[Test Voltages:<br/>• Charge: 28.4V<br/>• Min OCV: 25V<br/>• Low Cutoff: 24V]
        CURR_SPEC[Test Currents:<br/>• Charge: 10A<br/>• Discharge: 20A<br/>• Peak: 45A<br/>• Overcurrent: 47A]
        COMM_SPEC[Communication:<br/>• MODBUS RTU<br/>• RS232 Interface<br/>• 9600 baud, N, 1]
    end
    
    subgraph "Safety Features"
        VOLT_LIMIT[Voltage Limits:<br/>• Max Charge: 28.4V<br/>• Min Operating: 24V]
        CURR_LIMIT[Current Limits:<br/>• Peak: 5 sec @ 45A<br/>• Overcurrent: 10 sec @ 47A]
        SOC_PROTECT[SOC Protection:<br/>• Prevent drop below 25%<br/>• Modified testing approach]
    end
    
    PACK_SPEC --> VOLT_LIMIT
    VOLT_SPEC --> CURR_LIMIT
    CURR_SPEC --> SOC_PROTECT
    COMM_SPEC --> SOC_PROTECT
    
    style PACK_SPEC fill:#e1f5fe
    style VOLT_LIMIT fill:#ffcdd2
    style CURR_LIMIT fill:#fff3e0
    style SOC_PROTECT fill:#c8e6c9
```

## Document Control and Revision History

```mermaid
timeline
    title MTI-102284-10 Revision History
    
    section Revision A
        2020-10-26 : Drawn by P. English
        2022-03-31 : Checked by Kenny Le
        2022-03-31 : Approved by Adnan Khan
        2022-03-31 : Release (DCO: 3762)
    
    section Revision B
        2022-10-24 : Modified by P. English
                   : Switch from bq34Z100 to bq34110
        TBD        : Approval Date (Not Specified)
                   : DCO: 3841
```