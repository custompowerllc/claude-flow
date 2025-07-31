# GEHC Patient Table Battery Pack Simulator

## Overview
The **C# Serial Communication GUI** application is designed to interface with devices (e.g., battery management systems) over a serial communication protocol. This Windows Forms application facilitates sending commands, receiving responses, and visualizing data in a user-friendly graphical interface. It also supports loading command metadata from a CSV file and dynamically updating UI elements based on the commands.

## Features
- **Serial Communication**: Connect to devices via serial ports with customizable baud rates.
- **Dynamic Command Loading**: Read commands and descriptions from a CSV file.
- **Command Execution**: Send commands and receive responses in real-time.
- **Data Visualization**: Display command responses in a DataGridView for easy interpretation.
- **Error Handling**: Handles timeouts, malformed messages, and connection errors gracefully.
- **CRC Validation**: Implements CRC-8 checksum validation to ensure message integrity.

## How It Works

### Application Flow
1. **Serial Port Setup**:
    - Detects available serial ports and populates a dropdown menu.
    - Allows users to select a port and specify a baud rate (default: 9600).
    - Connect or disconnect from the selected port using the "Connect" button.

2. **Command Loading**:
    - Reads a `Battery_Info.csv` file to load available commands and their descriptions.
    - Displays commands in a DataGridView with columns for Code, Description, Value, and a "Read" button.

3. **Command Execution**:
    - When the "Read" button is clicked for a command, the application:
        - Constructs a request message with a synchronization header, command code, and CRC-8.
        - Sends the request to the connected device.
        - Waits for a response (with a 5-second timeout).

4. **Response Handling**:
    - Validates the response using the CRC-8 checksum.
    - Extracts and interprets the response data based on the command.
    - Updates the Value column in the DataGridView with the parsed response.

### CRC-8 Calculation
The CRC-8 checksum is calculated using the SMBus polynomial (`x^8 + x^2 + x^1 + 1`, or `0x07`) for both outgoing requests and incoming responses to ensure data integrity.

### Timeout Handling
The application includes a 5-second timeout for receiving responses. If no valid response is received within this time, an error message is logged in the console.

## Commands Supported
The application dynamically supports any command listed in the `Battery_Info.csv` file. Each command includes:
- **Code**: The hexadecimal identifier of the command.
- **Description**: A brief explanation of the command.

Commonly supported commands include:
- Remaining Capacity Alarm
- Voltage
- Current
- Cycle Count
- Battery State of Health (SOH)

## Example Communication
### Incoming Message:
```
[0x23, 0x09, 0x00, 0xAC]  // Request for Voltage
```
### Outgoing Response:
```
[0x40, 0x09, 0x02, 0x34, 0x12, 0xE5]  // Voltage: 0x1234 mV
```

## Setup
1. Clone the repository or copy the code to your local machine.
2. Open the solution file (`GEHC_Forms_GUI.sln`) in Visual Studio.
3. Build and run the application.

## Requirements
- **Environment**: Windows OS with .NET Framework installed.
- **Development Tools**: Visual Studio 2019 or later.
- **Dependencies**: The `Battery_Info.csv` file containing command definitions.

## Configuration
- **Baud Rate**: Default is 9600 but can be changed in the GUI.
- **Timeout**: 5 seconds for receiving responses.

## License
This project is copyrighted and protected by Custom Power LLC.

## Contact
For any questions, please contact [Custom Power LLC](https://www.custompower.com/).

