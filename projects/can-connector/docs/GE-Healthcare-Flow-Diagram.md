# GE Healthcare CAN Connector - Application Flow Diagram

This Mermaid diagram illustrates the application flow for the GE Healthcare product processor in the CAN connector system.

```mermaid
flowchart TD
    %% External Components
    CAN[CAN Bus Network<br/>29-bit Extended CAN IDs] --> |Extended CAN Messages| CANID{Validate CAN ID<br/>Must be Extended ID<br/>Non-Remote, Non-FD}
    
    %% Entry Point & Validation
    CANID --> |Valid Extended ID| FILTER{Message Filter<br/>ID & 0x400 == 0x400<br/>Required Prefix Check}
    CANID --> |Invalid: Standard ID,<br/>Remote, or CAN-FD| DISCARD[Discard Message]
    
    FILTER --> |Valid Prefix 0x400| EXTRACT[Extract Message Components<br/>ID_PREFIX_MASK applied<br/>Store m_id_prefix]
    FILTER --> |Invalid Prefix| DISCARD
    
    %% CAN ID Structure Detail
    EXTRACT --> |Parse 29-bit ID| ID_BREAKDOWN{CAN ID Breakdown<br/>29-bit Extended ID}
    ID_BREAKDOWN --> |Bits [10:2]| MSG_FIELD[Message Field: a_msg<br/>0x01-0x1D + 0x400]
    ID_BREAKDOWN --> |Bits [1:0]| PACK_FIELD[Pack Field: a_pck<br/>0-3 for PACK_0 to PACK_3]
    ID_BREAKDOWN --> |High bits| PREFIX_FIELD[ID Prefix<br/>Stored in m_id_prefix]
    
    %% Message Processing Core
    MSG_FIELD --> MSGTYPE[Message Type<br/>0x01-0x1D]
    PACK_FIELD --> PACK[Pack Identifier<br/>0-3 PACK_0 to PACK_3]
    PREFIX_FIELD --> ROUTING[Message Routing<br/>Based on ID Prefix]
    
    %% Special Message 07 Handling
    MSGTYPE --> |Message 0x07| MSG07{Message 07<br/>Special Processing}
    MSG07 --> |Parse Complex Data| MSG07_PARSE[Parse Battery Data<br/>- Voltage, Current, SoC<br/>- Temperature, State<br/>- Fault & Warning Status]
    MSG07_PARSE --> |Split into two parts| MSG07_A[Message 07-I<br/>Primary Data]
    MSG07_PARSE --> MSG07_B[Message 07-II<br/>Status Data]
    
    %% Standard Message Processing
    MSGTYPE --> |Messages 01-06, 08-1D| STANDARD[Standard Message Processing]
    STANDARD --> PARSER{Message Parser}
    
    %% Message-Specific Parsers
    PARSER --> |01| PARSE01[Parse Message 01<br/>Cell Voltages V1-V4]
    PARSER --> |02| PARSE02[Parse Message 02<br/>Cell Voltages V5-V8]
    PARSER --> |03| PARSE03[Parse Message 03<br/>Cell Voltages V9-V12]
    PARSER --> |04| PARSE04[Parse Message 04<br/>Cell Voltages V13-V16]
    PARSER --> |05| PARSE05[Parse Message 05<br/>Temperatures 1-4]
    PARSER --> |06| PARSE06[Parse Message 06<br/>Pack & Charger Voltage]
    PARSER --> |08| PARSE08[Parse Message 08<br/>Firmware Versions & Serial]
    PARSER --> |09-1D| PARSE_OTHER[Parse Other Messages<br/>Various Battery Parameters]
    
    %% Data Interpretation
    PARSE01 --> INTERPRET[Data Interpretation<br/>& Formatting]
    PARSE02 --> INTERPRET
    PARSE03 --> INTERPRET
    PARSE04 --> INTERPRET
    PARSE05 --> INTERPRET
    PARSE06 --> INTERPRET
    PARSE08 --> INTERPRET
    PARSE_OTHER --> INTERPRET
    MSG07_A --> INTERPRET
    MSG07_B --> INTERPRET
    
    %% Output Generation
    INTERPRET --> REGISTER[Add to Message Register<br/>with Parsed Data]
    REGISTER --> OUTPUT[Formatted Output<br/>- ID Interpretation<br/>- Data Interpretation]
    
    %% Query Processing Branch
    QUERY_INPUT[Query Request] --> VALIDATE_DEST{Validate Destination<br/>PACK_0 to PACK_3}
    VALIDATE_DEST --> |Valid Destination| QUERY_TYPE{Query Type}
    VALIDATE_DEST --> |Invalid| QUERY_ERROR[Query Error]
    
    QUERY_TYPE --> |Specific Message| SINGLE_QUERY[Single Message Query<br/>Messages 01-1D<br/>Empty Data Payload]
    QUERY_TYPE --> |ALL Query| ALL_QUERY[Query All Messages<br/>Command 0x0001<br/>Message 0x00]
    
    SINGLE_QUERY --> GEN_QUERY[Generate Query Message<br/>compute_outgoing_id()]
    ALL_QUERY --> GEN_QUERY
    GEN_QUERY --> |CAN ID: Prefix + MSG + PCK| OUTGOING_ID[Outgoing CAN ID<br/>Format: ID_PREFIX | MSG << 2 | PCK]
    OUTGOING_ID --> OUTGOING[Add to Outgoing Queue]
    
    %% Command Processing Branch
    COMMAND_INPUT[Command Request] --> VALIDATE_CMD_DEST{Validate Destination<br/>PACK_0 to PACK_3}
    VALIDATE_CMD_DEST --> |Valid Destination| COMMAND_TYPE{Command Type}
    VALIDATE_CMD_DEST --> |Invalid| CMD_ERROR[Command Error]
    
    COMMAND_TYPE --> |Simple Mode| SIMPLE_CMDS[Simple Commands<br/>- Query All (0x0001)<br/>- Enter Bootloader (0x0002)]
    COMMAND_TYPE --> |Advanced Mode| ADVANCED_CMDS[Advanced Commands<br/>- AFE Operations<br/>- Calibration<br/>- Configuration]
    
    SIMPLE_CMDS --> GEN_CMD[Generate Command Message<br/>Message 0x00]
    ADVANCED_CMDS --> GEN_CMD
    GEN_CMD --> |Command + Data Encoding| CMD_OUTGOING_ID[Command CAN ID<br/>Format: ID_PREFIX | 0x00 << 2 | PCK<br/>Data: Command Word + Parameters]
    CMD_OUTGOING_ID --> OUTGOING
    
    %% Configuration & State
    CONFIG[Product Configuration] --> |Mode Setting| MODE{Operating Mode}
    MODE --> |m_advanced_mode = false| SIMPLE_MODE[Simple Mode<br/>Limited Command Set]
    MODE --> |m_advanced_mode = true| ADVANCED_MODE[Advanced Mode<br/>Full Command Set]
    
    %% Status Register Processing
    STATUS_INPUT[Status Register Query] --> STATUS_LOOKUP[Lookup Status Register<br/>- Fuel Gauge Status<br/>- AFE Status<br/>- Safety Alerts]
    STATUS_LOOKUP --> STATUS_FORMAT[Format Status Data<br/>Bit Field Interpretation]
    
    %% Data Structures
    subgraph Data_Structures [Data Structures]
        DEST_SET[Destination Set<br/>PACK_0 to PACK_3]
        MSG_REG_SET[Message Register Set<br/>MESSAGE_01 to MESSAGE_1D]
        STATUS_REG_SET[Status Register Set<br/>FG & AFE Registers]
        QUERY_SET[Query Set<br/>Available Queries]
        CMD_SET[Command Set<br/>Simple/Advanced Commands]
    end
    
    %% Error Handling
    ERROR_HANDLER[Error Handler] --> |Invalid Data Length| LENGTH_ERROR[Length Error]
    ERROR_HANDLER --> |Parse Failure| PARSE_ERROR[Parse Error]
    ERROR_HANDLER --> |Invalid Command| INVALID_CMD[Invalid Command]
    
    %% Utility Functions
    subgraph Utilities [Utility Functions]
        TEMP_CONV[Temperature Conversion<br/>to_celsius()]
        ENCODE_LE[Little Endian Encoding<br/>Misc.encode_le()]
        DECODE_LE[Little Endian Decoding<br/>Misc.decode_le()]
        ID_COMPUTE[ID Computation<br/>compute_outgoing_id()]
    end
    
    %% Styling
    classDef messageNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef processNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef dataNode fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef errorNode fill:#ffebee,stroke:#b71c1c,stroke-width:2px
    classDef utilityNode fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class PARSE01,PARSE02,PARSE03,PARSE04,PARSE05,PARSE06,PARSE08,PARSE_OTHER,MSG07_A,MSG07_B messageNode
    class EXTRACT,INTERPRET,REGISTER,GEN_QUERY,GEN_CMD processNode
    class DEST_SET,MSG_REG_SET,STATUS_REG_SET,QUERY_SET,CMD_SET dataNode
    class DISCARD,QUERY_ERROR,CMD_ERROR,LENGTH_ERROR,PARSE_ERROR,INVALID_CMD errorNode
    class TEMP_CONV,ENCODE_LE,DECODE_LE,ID_COMPUTE utilityNode
```

## CAN ID Structure and Addressing

### CAN ID Format (29-bit Extended)
The GE Healthcare implementation uses a specific addressing scheme:

```
29-bit Extended CAN ID Structure:
┌─────────────────┬──────────────┬─────────┐
│   ID_PREFIX     │   MSG_ID     │  PCK_ID │
│   (High bits)   │  (Bits 10:2) │ (Bits 1:0) │
└─────────────────┴──────────────┴─────────┘

Required Pattern: ID & 0x400 == 0x400
```

### Addressing Components:
- **ID_PREFIX**: High-order bits stored in `m_id_prefix` (varies by system)
- **MSG_ID**: Message identifier (0x01-0x1D, encoded as (msg << 2))
- **PCK_ID**: Pack/destination identifier (0-3 for PACK_0 to PACK_3)

### Outgoing ID Computation:
```
Outgoing CAN ID = ID_PREFIX | (MSG << 2) | PCK
```

### Message Types by ID:
- **0x00**: Command messages (with data payload)
- **0x01-0x06**: Cell voltages and environmental data
- **0x07**: Primary battery status (special dual-processing)
- **0x08-0x1D**: Extended battery parameters and diagnostics

## Key Components Description

### 1. **Message Reception & Filtering**
- Validates incoming CAN messages for extended ID format
- Filters messages based on ID prefix (0x400 mask)
- Extracts pack and message identifiers

### 2. **Message Type Processing**
- **Message 07**: Special handling for comprehensive battery data (split into two parts)
- **Messages 01-04**: Cell voltage readings (4 cells per message)
- **Message 05**: Temperature readings from 4 sensors
- **Message 06**: Pack and charger voltage
- **Message 08**: Firmware versions and serial number
- **Messages 09-1D**: Various other battery parameters

### 3. **Data Parsing & Interpretation**
- Little-endian decoding of multi-byte values
- Unit conversions (mV to V, temperature scaling)
- Bit field extraction for status and flags
- Formatted string generation for display

### 4. **Query System**
- Individual message queries (01-1D)
- "Query All" command for comprehensive data retrieval
- Destination validation and routing

### 5. **Command System**
- **Simple Mode**: Basic operations (query all, bootloader entry)
- **Advanced Mode**: Full AFE control, calibration, configuration
- Command encoding with proper CAN ID generation

### 6. **Configuration Management**
- Operating mode selection (simple/advanced)
- Destination set management (PACK_0 to PACK_3)
- Register set definitions for messages, status, and commands

### 7. **Error Handling**
- Data length validation
- Parse failure recovery
- Invalid command rejection
- CAN ID format verification

This flow diagram represents the complete processing pipeline for GE Healthcare battery management system communication via CAN bus.