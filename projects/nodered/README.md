# Node-RED with Modbus RTU and Serial Modules

A complete Node-RED installation with Modbus RTU and serial communication support.

## Installation Complete ✓

All required packages have been installed:
- **Node-RED Core** (v4.1.0)
- **Modbus Support** (node-red-contrib-modbus v5.43.0)
- **Serial Port Support** (node-red-node-serialport v2.0.3)
- **SerialPort Library** (v13.0.0)

## Quick Start

### Cross-Platform Support (Windows & Linux)

#### Method 1: NPM Script (Works on Both)
```bash
cd projects/nodered
npm start
```

#### Method 2: Platform-Specific Scripts

**Windows (PowerShell/CMD):**
```batch
cd projects\nodered
start.bat
```
Or:
```powershell
npm start
```

**Linux/macOS:**
```bash
cd projects/nodered
./start.sh
```

#### Method 3: Direct Command (Both Platforms)
```bash
cd projects/nodered
npx node-red -s ./settings.js -u ./data
```

#### Method 4: Custom Express Server (Both Platforms)
```bash
cd projects/nodered
npm run start-custom
```

## Access Node-RED

Once started, access Node-RED at:
- **Editor UI**: http://localhost:1880
- **API Endpoints**: http://localhost:1880/api

## Available Nodes

### Modbus Nodes (node-red-contrib-modbus)
- **Modbus Read** - Read from Modbus registers
- **Modbus Write** - Write to Modbus registers
- **Modbus Server** - Create a Modbus TCP/RTU server
- **Modbus Flex Getter** - Flexible read operations
- **Modbus Flex Writer** - Flexible write operations
- **Modbus Queue** - Queue Modbus operations

### Serial Nodes (node-red-node-serialport)
- **Serial In** - Receive data from serial port
- **Serial Out** - Send data to serial port
- **Serial Request** - Send and wait for response

## Configuration Examples

### Modbus RTU Configuration
1. Add a Modbus node to your flow
2. Configure the connection:
   - Type: **Serial**
   - Serial Port: `/dev/ttyUSB0` (Linux) or `COM1` (Windows)
   - Baud Rate: `9600` (or as required)
   - Data Bits: `8`
   - Stop Bits: `1`
   - Parity: `none`/`even`/`odd`
3. Set Unit ID (slave address)
4. Configure register addresses

### Serial Port Configuration
1. Add a Serial node to your flow
2. Configure the port:
   - Serial Port: `/dev/ttyUSB0` (Linux) or `COM1` (Windows)
   - Baud Rate: `9600` (or as required)
   - Data Bits: `8`
   - Stop Bits: `1`
   - Parity: `none`

## Project Structure
```
projects/nodered/
├── node_modules/        # Installed packages
├── data/               # Node-RED user data
│   ├── flows.json      # Flow configuration
│   └── context/        # Context storage
├── lib/                # Custom libraries
├── flows/              # Additional flow files
├── settings.js         # Node-RED settings
├── start-nodered.js    # Custom start script
├── package.json        # NPM configuration
└── README.md          # This file
```

## Common Serial Ports

### Linux
- `/dev/ttyUSB0`, `/dev/ttyUSB1` - USB serial adapters
- `/dev/ttyS0`, `/dev/ttyS1` - Hardware serial ports
- `/dev/ttyACM0` - Arduino/USB CDC devices

### Windows
- `COM1`, `COM2`, `COM3`, etc.

### macOS
- `/dev/tty.usbserial-*`
- `/dev/tty.usbmodem-*`

## Troubleshooting

### Permission Issues (Linux)
If you get permission errors accessing serial ports:
```bash
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

### Port Already in Use
Make sure no other application is using port 1880. Change the port in `settings.js` if needed:
```javascript
uiPort: process.env.PORT || 3000,
```

### Serial Port Not Found
- Check device is connected: `ls /dev/tty*`
- Install drivers if needed
- Check permissions

## Additional Resources
- [Node-RED Documentation](https://nodered.org/docs/)
- [Modbus Nodes Documentation](https://flows.nodered.org/node/node-red-contrib-modbus)
- [Serial Port Documentation](https://flows.nodered.org/node/node-red-node-serialport)

## Security Note
The current configuration has no authentication enabled. To secure your Node-RED instance, uncomment and configure the `adminAuth` section in `settings.js`.