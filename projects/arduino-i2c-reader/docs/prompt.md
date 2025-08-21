# Arduino I2C Reader - Development Prompt

## Project Overview

Create an Arduino Mega 2560-based I2C reader system that can query and parse data from Texas Instruments BQ fuel gauge and AFE (Analog Front End) I2C devices. This system should serve as a diagnostic and monitoring tool for battery management systems.

## Hardware Configuration

### Target Platform
- **Arduino Mega 2560** with multiple I2C interfaces
- **I2C Bus**: Use Wire library (pins 20/21 - SDA/SCL)
- **Secondary I2C**: Available on pins 70/71 if needed for bus isolation

### I2C Device Architecture

Based on the GEHC battery management system implementation, the shared I2C bus contains:

1. **LT8491 Battery Charger**
   - I2C Address: `0x29` (7-bit address)
   - Address format for Arduino Wire: `0x52` (8-bit write address)
   - Primary function: Battery charging controller with telemetry

2. **TI BQ AFE Cell Monitor** 
   - I2C Address: `0x08` (7-bit address)
   - Function: Cell voltage monitoring and protection
   - R_sense: 0.5mΩ for current measurement

3. **TI BQ Fuel Gauge (BQ34Z100)**
   - I2C Address: `0x55` (7-bit address) 
   - Function: State of charge, capacity, and fuel gauge data
   - Unsealing keys: `0x17916789` and `0x1791AABB`
   - **Device Confirmed**: Real hardware testing shows `bq34z100` with firmware version `2_02`

## Key I2C Implementation Requirements

### Bus Sharing Considerations
- **Non-blocking Communication**: Implement state machine-based I2C communication to prevent bus conflicts
- **Device Detection**: Implement robust device presence detection before attempting communication
- **Error Handling**: Graceful handling when devices are not present or not responding
- **Timeout Management**: 100ms timeout for I2C operations to prevent hanging

### Communication Protocol
- **CRC8 Checksums**: Implement CRC8 validation for data integrity where applicable
- **Register Access**: Support both single-byte and multi-byte register reads/writes
- **Word Operations**: Handle 16-bit register operations with proper endianness

## TI BQ Fuel Gauge (BQ34Z100) Interface

### Real Hardware Data Analysis
Based on actual fuel gauge datalog from hardware testing, the following parameters and values have been confirmed:

#### Confirmed Device Information
- **Device**: `bq34z100` (confirmed via register read)
- **Firmware Version**: `2_02` 
- **Device Version**: `0100_2_02`
- **Battery Configuration**: 4.3Ah capacity (4300-4311 mAh observed)
- **Voltage Range**: ~52.1V nominal (52104-52117 mV observed)
- **Current Range**: 281-308 mA typical operation
- **Temperature**: 24.7-24.8°C operational range

#### Observed Register Values and Patterns
```cpp
// Confirmed register data from real hardware logs:
// Control Status: 0x000D (consistent across all samples)
// State of Charge: 100% (full battery during testing)
// Voltage: 52117 mV (typical), occasional 52104 mV
// Current: 281-308 mA (positive = charging)
// Average Current: 304-307 mA
// Temperature: -39.2°C offset indicates raw ADC value needs conversion
// Internal Temperature: 24.7-24.8°C (processed value)
// Remaining Capacity: 4303-4311 mAh (increases during charging)
// Full Charge Capacity: Matches remaining capacity at 100% SOC
// Cycle Count: 4 cycles
// State of Health: 92%
// Flags: 0x09E1, Flags B: 0x0A00, GridNumber: 0x0600
```

#### Critical Observations for Arduino Implementation
1. **Temperature Conversion**: Raw temperature shows -39.2°C, but internal temp shows 24.7°C
2. **Capacity Tracking**: Values increment during charging (4303→4311 mAh observed)
3. **Voltage Stability**: Voltage very stable at 52.1V with occasional minor variations
4. **Current Direction**: Positive values indicate charging current
5. **Status Consistency**: Control status and flags remain stable during operation

### Key Registers and Data Points

#### Primary Status Registers
```cpp
// Control and Status Registers
#define FG_CONTROL_STATUS     0x0000  // Control Status register
#define FG_OPERATION_STATUS   0x0054  // Operation status
#define FG_GAUGING_STATUS     0x0056  // Gauging status 
#define FG_MFG_STATUS         0x0057  // Manufacturing status
#define FG_BATTERY_STATUS     0x000A  // Battery status flags

// Core Battery Data
#define FG_STATE_OF_CHARGE    0x002C  // SOC percentage (0-100%)
#define FG_STATE_OF_HEALTH    0x002E  // SOH percentage
#define FG_VOLTAGE            0x0008  // Battery voltage (mV)
#define FG_CURRENT            0x000C  // Current (mA, signed)
#define FG_TEMPERATURE        0x0006  // Temperature (0.1K units)
#define FG_REMAINING_CAPACITY 0x0010  // Remaining capacity (mAh)
#define FG_FULL_CHARGE_CAP    0x0012  // Full charge capacity (mAh)
#define FG_DESIGN_CAPACITY    0x0018  // Design capacity (mAh)
#define FG_CYCLE_COUNT        0x0017  // Cycle count
```

#### Critical Status Bits
```cpp
// Control Status (0x0000) Bit Definitions
#define CS_SHUTDOWN_STATUS    (1 << 15)  // SS: Shutdown Status
#define CS_CALIBRATION_MODE   (1 << 14)  // CAL: Calibration Mode  
#define CS_INIT_COMPLETE      (1 << 10)  // INITCOMP: Initialization Complete

// Battery Status (0x000A) Bit Definitions  
#define BS_FULLY_CHARGED      (1 << 12)  // FC: Fully Charged
#define BS_FULLY_DISCHARGED   (1 << 13)  // FD: Fully Discharged
#define BS_CHARGE_INHIBIT     (1 << 14)  // CHGINH: Charge Inhibit
#define BS_TEMP_CHARGE_ALLOW  (1 << 11)  // TCA: Temperature Charge Allowed
#define BS_TEMP_DISCHARGE_ALLOW (1 << 10) // TDA: Temperature Discharge Allowed

// Manufacturing Status (0x0057) Bit Definitions
#define MS_CHARGING           (1 << 7)   // CHG: Charging
#define MS_DISCHARGING        (1 << 14)  // DSG: Discharging  
#define MS_FULLY_CHARGED      (1 << 9)   // FC: Fully Charged
#define MS_FULLY_DISCHARGED   (1 << 8)   // FD: Fully Discharged
```

### Security and Access Control
```cpp
// Fuel Gauge Security Keys
#define FG_UNSEAL_KEY         0x17916789UL  // Unseal key for basic access
#define FG_FULL_UNSEAL_KEY    0x1791AABBUL  // Full access key

// Security Commands
#define CMD_UNSEAL            0x0414    // Unseal command  
#define CMD_FULL_ACCESS       0x0415    // Full access command
#define CMD_SEAL              0x0030    // Seal device command
```

## TI BQ AFE Cell Monitor Interface

### Key Functions and Data
```cpp
// AFE Core Functions
#define AFE_RSENSE_MILLIOHM   0.5f      // Current sense resistor value

// Cell Voltage Monitoring (up to 16 cells typical)
uint16_t afe_get_cell_voltage(uint8_t cell_number);   // Individual cell voltage
uint16_t afe_get_cell_min_voltage();                  // Minimum cell voltage
uint16_t afe_get_cell_max_voltage();                  // Maximum cell voltage  
uint16_t afe_get_cell_voltage_delta();                // Max - Min cell voltage
uint16_t afe_get_stack_voltage();                     // Total stack voltage
uint16_t afe_get_pack_voltage();                      // Pack voltage

// Current and Temperature
int16_t afe_get_current();                            // Pack current (mA)
uint16_t afe_get_temperature(uint8_t sensor);         // Temperature sensor
uint16_t afe_get_internal_temperature();              // Internal temperature

// Protection and Status
uint16_t afe_get_control_status();                    // Control status register
uint8_t afe_get_safety_alert_a();                     // Safety alert A
uint8_t afe_get_safety_status_a();                    // Safety status A  
uint8_t afe_get_protection_alert_a();                 // Protection alert A
uint8_t afe_get_protection_status_a();                // Protection status A
uint16_t afe_get_battery_status();                    // Battery status
uint16_t afe_get_alarm_status();                      // Alarm status
uint8_t afe_get_fet_status();                         // FET control status
uint16_t afe_get_cell_balance_active();               // Active cell balancing
```

## LT8491 Charger Interface

### Key Telemetry Registers
```cpp
// LT8491 Telemetry Registers (from GEHC implementation)
#define LT8491_TELE_VIN       0x00    // Input voltage
#define LT8491_TELE_IIN       0x01    // Input current  
#define LT8491_TELE_VOUT      0x02    // Output voltage
#define LT8491_TELE_IOUT      0x08    // Output current
#define LT8491_TELE_TEMP      0x04    // Temperature
#define LT8491_TELE_DUTY      0x05    // PWM duty cycle
#define LT8491_TELE_FREQ      0x06    // Switching frequency

// Control Registers
#define LT8491_CTRL_CONFIG    0x10    // Configuration
#define LT8491_CTRL_ENABLE    0x11    // Enable/disable
#define LT8491_DEVICE_ID      0x91    // Expected device ID
```

## Arduino Implementation Structure

### Core Classes and Functions

```cpp
class I2CDeviceManager {
private:
    bool device_present[3];  // Track AFE, FG, LT8491 presence
    uint32_t last_query_time[3];
    
public:
    bool initializeDevices();
    bool detectDevice(uint8_t address);
    void queryAllDevices();
    bool isDeviceResponding(uint8_t device_id);
};

class BQFuelGauge {
private:
    uint8_t i2c_address = 0x55;
    bool sealed_state = true;
    
public:
    bool initialize();
    bool unseal();
    bool seal(); 
    uint16_t getStateOfCharge();
    uint16_t getVoltage();
    int16_t getCurrent();
    uint16_t getTemperature();
    uint16_t getRemainingCapacity();
    uint16_t getFullChargeCapacity();
    uint16_t getCycleCount();
    uint16_t getBatteryStatus();
    bool isCharging();
    bool isDischarging();
};

class BQAnalogFrontEnd {
private:
    uint8_t i2c_address = 0x08;
    
public:
    bool initialize();
    uint16_t getCellVoltage(uint8_t cell);
    uint16_t getMinCellVoltage();
    uint16_t getMaxCellVoltage(); 
    uint16_t getCellVoltageDelta();
    int16_t getPackCurrent();
    uint16_t getPackVoltage();
    uint16_t getTemperature(uint8_t sensor);
    uint16_t getProtectionStatus();
    uint16_t getAlarmStatus();
    bool isCellBalancingActive();
};

class LT8491Charger {
private:
    uint8_t i2c_address = 0x29;  // 7-bit address
    
public:
    bool initialize();
    bool detectDevice();
    uint16_t getInputVoltage();
    uint16_t getInputCurrent();
    uint16_t getOutputVoltage();
    uint16_t getOutputCurrent();
    uint16_t getTemperature();
    uint8_t getDutyCycle();
    bool isCharging();
    void enableCharging(bool enable);
};
```

### Data Logging and Output

```cpp
// Data structure for complete system snapshot
struct BatterySystemData {
    // Timestamps
    unsigned long timestamp;
    
    // Fuel Gauge Data
    uint16_t soc_percent;           // State of charge (%)
    uint16_t soh_percent;           // State of health (%)
    uint16_t fg_voltage_mv;         // Battery voltage (mV)
    int16_t fg_current_ma;          // Current (mA)
    uint16_t fg_temp_kelvin;        // Temperature (0.1K)
    uint16_t remaining_capacity;     // Remaining capacity (mAh)
    uint16_t full_charge_capacity;   // Full charge capacity (mAh)
    uint16_t cycle_count;           // Cycle count
    uint16_t fg_status;             // Status flags
    
    // AFE Data  
    uint16_t cell_voltages[16];     // Individual cell voltages
    uint16_t min_cell_voltage;      // Minimum cell voltage
    uint16_t max_cell_voltage;      // Maximum cell voltage
    uint16_t cell_delta;            // Max - Min cell voltage
    int16_t afe_current_ma;         // AFE measured current
    uint16_t afe_temperatures[4];   // Temperature sensors
    uint16_t protection_status;     // Protection status
    uint16_t alarm_status;          // Alarm status
    
    // LT8491 Charger Data
    uint16_t charger_vin;           // Input voltage
    uint16_t charger_iin;           // Input current
    uint16_t charger_vout;          // Output voltage  
    uint16_t charger_iout;          // Output current
    uint16_t charger_temp;          // Charger temperature
    uint8_t charger_duty;           // PWM duty cycle
    bool charger_enabled;           // Charging status
    
    // System Status
    bool afe_online;                // AFE communication status
    bool fg_online;                 // Fuel gauge communication status  
    bool charger_online;            // Charger communication status
};
```

## Communication Protocol Implementation

### I2C Helper Functions
```cpp
// Low-level I2C communication
bool i2c_write_register(uint8_t device_addr, uint8_t reg_addr, uint8_t value);
bool i2c_write_register_word(uint8_t device_addr, uint8_t reg_addr, uint16_t value);
uint8_t i2c_read_register(uint8_t device_addr, uint8_t reg_addr);
uint16_t i2c_read_register_word(uint8_t device_addr, uint8_t reg_addr);
bool i2c_device_present(uint8_t device_addr);

// Timeout and error handling
void i2c_reset_bus();
bool i2c_wait_for_response(uint32_t timeout_ms);
```

### Error Handling and Recovery
```cpp
enum I2CErrorCode {
    I2C_SUCCESS = 0,
    I2C_DEVICE_NOT_FOUND = 1,
    I2C_TIMEOUT = 2, 
    I2C_DATA_ERROR = 3,
    I2C_BUS_ERROR = 4,
    I2C_CRC_ERROR = 5
};

class I2CErrorHandler {
public:
    void logError(uint8_t device_addr, I2CErrorCode error);
    void attemptRecovery(uint8_t device_addr);
    bool isDeviceHealthy(uint8_t device_addr);
    void resetErrorCounts();
};
```

## Serial Output Format

### Human-Readable Output
```
=== Battery System Status ===
Timestamp: 12345678 ms

Fuel Gauge (0x55):
  SOC: 85% | SOH: 98% | Voltage: 3.87V | Current: -1250mA 
  Capacity: 2450/2890 mAh | Cycles: 45 | Temp: 25.3°C
  Status: DISCHARGING | Flags: 0x2008

AFE Monitor (0x08):
  Cells: 3.850V 3.847V 3.851V 3.849V (Δ=4mV)
  Pack: 15.397V | Current: -1248mA | Temp: 24.8°C
  Protection: 0x0000 | Alarms: 0x0000 | Balance: OFF

LT8491 Charger (0x29):
  Input: 15.2V / 0.85A | Output: 15.4V / 1.2A  
  Temperature: 28.5°C | Duty: 65% | Status: CHARGING
  
Bus Status: AFE:OK FG:OK CHG:OK
```

### CSV Data Logging Format
```
timestamp,soc_pct,soh_pct,fg_voltage_mv,fg_current_ma,fg_temp_k,remaining_mah,full_mah,cycles,cell1_mv,cell2_mv,cell3_mv,cell4_mv,min_cell_mv,max_cell_mv,delta_mv,afe_current_ma,afe_temp_c,protection_status,alarm_status,charger_vin_mv,charger_iin_ma,charger_vout_mv,charger_iout_ma,charger_temp_c,charger_duty_pct,charger_enabled,afe_online,fg_online,charger_online
```

## Key Features to Implement

### Core Functionality
1. **Device Auto-Detection**: Scan I2C bus and identify present devices
2. **Continuous Monitoring**: Periodic polling of all devices with configurable intervals
3. **Data Validation**: CRC checking and range validation for critical parameters
4. **Error Recovery**: Automatic retry and bus recovery on communication failures
5. **Data Logging**: Both human-readable and CSV formats for analysis

### Advanced Features  
1. **SOC-Based Charging Control**: Monitor SOC and provide charging recommendations
2. **Cell Balance Monitoring**: Track cell voltage differences and balancing status
3. **Thermal Management**: Monitor temperatures and flag thermal issues
4. **Alarm Processing**: Decode and report protection and alarm conditions
5. **Historical Trending**: Track key parameters over time

### Safety Considerations
1. **Timeout Protection**: Prevent infinite loops on I2C failures
2. **Bus Recovery**: Reset I2C bus on persistent errors
3. **Graceful Degradation**: Continue operation even if some devices fail
4. **Data Validation**: Sanity check all readings before reporting
5. **Error Logging**: Comprehensive error tracking for diagnostics

## Testing and Validation

### Test Scenarios
1. **Individual Device Communication**: Test each device in isolation
2. **Concurrent Access**: Verify no bus conflicts during simultaneous queries
3. **Error Injection**: Test response to device disconnection/failure
4. **Long-Term Stability**: Extended operation testing
5. **Data Accuracy**: Validation against known reference values

### Performance Targets
- **Query Rate**: Complete system scan every 1-5 seconds
- **Response Time**: Individual device queries < 100ms
- **Error Rate**: < 1% communication failures under normal conditions
- **Recovery Time**: < 5 seconds to recover from bus errors

## Python Companion Application

### Serial Communication Interface

Implement a companion Python application to parse and display data from the Arduino transmitted via serial communications. The Python application will serve as the primary user interface for monitoring the battery management system.

#### Phase 1: CLI Dashboard Application
```python
class ArduinoBatteryMonitor:
    def __init__(self, serial_port='/dev/ttyUSB0', baud_rate=115200):
        """Initialize serial connection to Arduino"""
        
    def parse_serial_data(self, raw_data):
        """Parse incoming Arduino data packets"""
        
    def display_realtime_dashboard(self):
        """CLI-based real-time data dashboard"""
        
    def log_data_to_csv(self, filename):
        """Log parsed data to CSV for analysis"""
        
    def generate_reports(self):
        """Generate summary reports and trends"""
```

**CLI Dashboard Features:**
- Real-time battery status display with color-coded health indicators
- Live cell voltage monitoring with visual bar graphs
- Current/voltage/temperature trend displays
- Alarm and protection status notifications
- Data logging controls and export options
- Historical data visualization (ASCII charts)

#### Phase 2: GUI Application Planning
**Future GUI Implementation:**
- Tkinter/PyQt-based graphical interface
- Real-time plotting with matplotlib integration
- Interactive data exploration and analysis tools
- Configuration management for Arduino parameters
- Advanced alarm management and notification system
- Multi-battery system support for fleet monitoring

#### Serial Protocol Specification
```python
# Expected Arduino serial output format
# JSON-based for easy parsing:
{
    "timestamp": 1234567890,
    "fuel_gauge": {
        "soc": 85, "voltage": 3870, "current": -1250,
        "temperature": 253, "capacity": 2450, "cycles": 45
    },
    "afe": {
        "cells": [3850, 3847, 3851, 3849],
        "pack_voltage": 15397, "current": -1248,
        "protection": 0, "alarms": 0
    },
    "charger": {
        "input_v": 15200, "output_v": 15400,
        "current": 1200, "temperature": 285, "enabled": true
    },
    "status": {
        "afe_online": true, "fg_online": true, "charger_online": true
    }
}
```

This Arduino I2C reader system should provide comprehensive monitoring and diagnostic capabilities for TI BQ-based battery management systems, with robust error handling and clear data presentation suitable for both human operators and automated analysis systems. The companion Python application will enhance usability with modern CLI dashboards and future GUI capabilities for advanced battery management workflows.