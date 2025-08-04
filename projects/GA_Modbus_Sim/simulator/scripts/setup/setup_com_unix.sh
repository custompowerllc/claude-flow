#!/bin/bash
# Modbus BMS Simulator - Unix/Linux/macOS COM Port Setup Script
# Configures virtual serial ports for Modbus RTU testing

set -e  # Exit on any error

echo "========================================"
echo "Modbus BMS Simulator - Unix COM Setup"
echo "========================================"
echo

# Function to detect the operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]]; then
        echo "cygwin"
    elif [[ "$OSTYPE" == "msys" ]]; then
        echo "msys"
    else
        echo "unknown"
    fi
}

# Function to check if running with appropriate permissions
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        echo "Running as root user"
        return 0
    fi
    
    # Check if user is in dialout group (Linux)
    if [[ "$(detect_os)" == "linux" ]]; then
        if groups | grep -q "dialout"; then
            echo "User is in dialout group - serial port access available"
            return 0
        else
            echo "WARNING: User not in dialout group"
            echo "You may need to add your user to the dialout group:"
            echo "sudo usermod -a -G dialout \$USER"
            echo "Then log out and log back in"
            return 1
        fi
    fi
    
    return 0
}

# Function to install dependencies
install_dependencies() {
    echo "Checking system requirements..."
    
    # Check Python installation
    if ! command -v python3 &> /dev/null; then
        echo "ERROR: Python 3 is not installed"
        echo "Please install Python 3.8+ using your system package manager"
        exit 1
    fi
    
    echo "Python 3 installation found: $(python3 --version)"
    
    # Check pip installation
    if ! command -v pip3 &> /dev/null; then
        echo "ERROR: pip3 is not available"
        echo "Please install pip3 using your system package manager"
        exit 1
    fi
    
    echo "pip3 installation found: $(pip3 --version)"
    
    # Install required Python packages
    echo
    echo "Installing required Python packages..."
    pip3 install --user pyserial
    
    if [[ $? -eq 0 ]]; then
        echo "✓ pyserial installed successfully"
    else
        echo "ERROR: Failed to install pyserial"
        exit 1
    fi
}

# Function to setup virtual serial ports on Linux
setup_linux_serial() {
    echo "Setting up virtual serial ports for Linux..."
    
    # Check if socat is available
    if command -v socat &> /dev/null; then
        echo "✓ socat found - will use for virtual serial ports"
        
        # Create virtual serial port pair using socat
        echo "Creating virtual serial port pair..."
        
        # Kill any existing socat processes for our ports
        pkill -f "socat.*pty.*pty" 2>/dev/null || true
        
        # Create virtual serial port pair in background
        socat -d -d pty,raw,echo=0,link=/tmp/ttyV0 pty,raw,echo=0,link=/tmp/ttyV1 &
        SOCAT_PID=$!
        
        # Wait a moment for socat to create the links
        sleep 2
        
        if [[ -L /tmp/ttyV0 && -L /tmp/ttyV1 ]]; then
            echo "✓ Virtual serial port pair created:"
            echo "  Server side: /tmp/ttyV0 -> $(readlink /tmp/ttyV0)"
            echo "  Client side: /tmp/ttyV1 -> $(readlink /tmp/ttyV1)"
            echo "  socat PID: $SOCAT_PID"
            
            # Save the PID for cleanup
            echo $SOCAT_PID > /tmp/modbus_simulator_socat.pid
            
            # Make ports accessible
            chmod 666 /tmp/ttyV0 /tmp/ttyV1 2>/dev/null || true
            
            return 0
        else
            echo "WARNING: Failed to create virtual serial ports with socat"
            return 1
        fi
    else
        echo "WARNING: socat not found"
        echo "Please install socat for virtual serial port support:"
        echo "  Ubuntu/Debian: sudo apt-get install socat"
        echo "  CentOS/RHEL: sudo yum install socat"
        echo "  Fedora: sudo dnf install socat"
        return 1
    fi
}

# Function to setup virtual serial ports on macOS
setup_macos_serial() {
    echo "Setting up virtual serial ports for macOS..."
    
    # Check if socat is available
    if command -v socat &> /dev/null; then
        echo "✓ socat found - will use for virtual serial ports"
        
        # Create virtual serial port pair using socat
        echo "Creating virtual serial port pair..."
        
        # Kill any existing socat processes for our ports
        pkill -f "socat.*pty.*pty" 2>/dev/null || true
        
        # Create virtual serial port pair in background
        socat -d -d pty,raw,echo=0,link=/tmp/ttyV0 pty,raw,echo=0,link=/tmp/ttyV1 &
        SOCAT_PID=$!
        
        # Wait a moment for socat to create the links
        sleep 2
        
        if [[ -L /tmp/ttyV0 && -L /tmp/ttyV1 ]]; then
            echo "✓ Virtual serial port pair created:"
            echo "  Server side: /tmp/ttyV0 -> $(readlink /tmp/ttyV0)"
            echo "  Client side: /tmp/ttyV1 -> $(readlink /tmp/ttyV1)"
            echo "  socat PID: $SOCAT_PID"
            
            # Save the PID for cleanup
            echo $SOCAT_PID > /tmp/modbus_simulator_socat.pid
            
            return 0
        else
            echo "WARNING: Failed to create virtual serial ports with socat"
            return 1
        fi
    else
        echo "WARNING: socat not found"
        echo "Please install socat for virtual serial port support:"
        echo "  Using Homebrew: brew install socat"
        echo "  Using MacPorts: sudo port install socat"
        return 1
    fi
}

# Function to create configuration files
create_config() {
    echo
    echo "Creating simulator configuration files..."
    
    # Create config directory if it doesn't exist
    mkdir -p ../../config
    
    # Detect OS and set appropriate paths
    OS=$(detect_os)
    
    if [[ "$OS" == "linux" ]]; then
        SERVER_PORT="/tmp/ttyV0"
        CLIENT_PORT="/tmp/ttyV1"
        AVAILABLE_PORTS="/dev/ttyS0,/dev/ttyS1,/dev/ttyUSB0,/dev/ttyUSB1,/tmp/ttyV0,/tmp/ttyV1"
    elif [[ "$OS" == "macos" ]]; then
        SERVER_PORT="/tmp/ttyV0"
        CLIENT_PORT="/tmp/ttyV1"
        AVAILABLE_PORTS="/dev/tty.usbserial,/dev/cu.usbserial,/tmp/ttyV0,/tmp/ttyV1"
    else
        SERVER_PORT="/tmp/ttyV0"
        CLIENT_PORT="/tmp/ttyV1"
        AVAILABLE_PORTS="/dev/ttyS0,/dev/ttyS1,/tmp/ttyV0,/tmp/ttyV1"
    fi
    
    # Create Unix-specific COM port configuration
    cat > ../../config/com_ports_unix.ini << EOF
# Unix/Linux/macOS Serial Port Configuration for Modbus BMS Simulator
# Generated automatically by setup_com_unix.sh

[modbus_rtu]
# Primary serial port for simulator server
port = $SERVER_PORT
baudrate = 9600
bytesize = 8
parity = N
stopbits = 1
timeout = 1.0

[modbus_rtu_client]
# Client serial port for testing
port = $CLIENT_PORT
baudrate = 9600
bytesize = 8
parity = N
stopbits = 1
timeout = 1.0

[serial_port_settings]
# Available serial ports for testing
available_ports = $AVAILABLE_PORTS
preferred_server_port = $SERVER_PORT
preferred_client_port = $CLIENT_PORT

# Virtual serial port configuration
virtual_serial_method = socat
socat_pid_file = /tmp/modbus_simulator_socat.pid

# OS-specific settings
operating_system = $OS
user_in_dialout_group = $(groups | grep -q "dialout" && echo "true" || echo "false")
EOF
    
    echo "✓ Configuration file created: config/com_ports_unix.ini"
}

# Function to create test script
create_test_script() {
    echo
    echo "Creating serial port test script..."
    
    cat > ../test_serial_ports.py << 'EOF'
#!/usr/bin/env python3
"""Test script for Unix serial port configuration"""

import serial
import time
import sys
import os
import configparser

def read_config():
    """Read the serial port configuration"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'com_ports_unix.ini')
    
    if not os.path.exists(config_path):
        print(f"✗ Configuration file not found: {config_path}")
        return None, None
    
    config.read(config_path)
    
    try:
        server_port = config.get('modbus_rtu', 'port')
        client_port = config.get('modbus_rtu_client', 'port')
        return server_port, client_port
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        print(f"✗ Configuration error: {e}")
        return None, None

def test_serial_ports():
    """Test if serial port pair is working"""
    server_port, client_port = read_config()
    
    if not server_port or not client_port:
        return False
    
    print(f"Testing serial ports: {server_port} <-> {client_port}")
    
    # Check if ports exist
    if not os.path.exists(server_port):
        print(f"✗ Server port does not exist: {server_port}")
        return False
    
    if not os.path.exists(client_port):
        print(f"✗ Client port does not exist: {client_port}")
        return False
    
    try:
        # Try to open both serial ports
        server_serial = serial.Serial(server_port, 9600, timeout=1)
        client_serial = serial.Serial(client_port, 9600, timeout=1)
        
        print("✓ Both serial ports opened successfully")
        
        # Test communication
        test_message = b'HELLO'
        server_serial.write(test_message)
        time.sleep(0.1)
        
        received = client_serial.read(len(test_message))
        if received == test_message:
            print("✓ Serial port communication test passed")
            return True
        else:
            print(f"✗ Communication test failed. Sent: {test_message}, Received: {received}")
            return False
            
    except serial.SerialException as e:
        print(f"✗ Serial port test failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    finally:
        try:
            server_serial.close()
            client_serial.close()
        except:
            pass

if __name__ == '__main__':
    print("Testing serial port configuration...")
    success = test_serial_ports()
    sys.exit(0 if success else 1)
EOF
    
    chmod +x ../test_serial_ports.py
    echo "✓ Test script created: scripts/test_serial_ports.py"
}

# Function to create cleanup script
create_cleanup_script() {
    echo
    echo "Creating cleanup script..."
    
    cat > cleanup_serial_ports.sh << 'EOF'
#!/bin/bash
# Cleanup script for virtual serial ports

echo "Cleaning up virtual serial ports..."

# Kill socat processes
if [[ -f /tmp/modbus_simulator_socat.pid ]]; then
    PID=$(cat /tmp/modbus_simulator_socat.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "Stopping socat process (PID: $PID)..."
        kill $PID
        sleep 1
        if kill -0 $PID 2>/dev/null; then
            echo "Force killing socat process..."
            kill -9 $PID
        fi
    fi
    rm -f /tmp/modbus_simulator_socat.pid
fi

# Remove virtual port links
rm -f /tmp/ttyV0 /tmp/ttyV1

echo "✓ Cleanup completed"
EOF
    
    chmod +x cleanup_serial_ports.sh
    echo "✓ Cleanup script created: setup/cleanup_serial_ports.sh"
}

# Main execution
main() {
    echo "Detected OS: $(detect_os)"
    echo
    
    # Check permissions
    check_permissions
    
    # Install dependencies
    install_dependencies
    
    # Setup virtual serial ports based on OS
    OS=$(detect_os)
    case $OS in
        "linux")
            setup_linux_serial
            ;;
        "macos")
            setup_macos_serial
            ;;
        *)
            echo "WARNING: Unsupported OS for automatic setup: $OS"
            echo "Manual serial port configuration may be required"
            ;;
    esac
    
    # Create configuration files
    create_config
    
    # Create test script
    create_test_script
    
    # Create cleanup script
    create_cleanup_script
    
    echo
    echo "========================================"
    echo "Unix Serial Port Setup Complete!"
    echo "========================================"
    echo
    echo "Configuration Summary:"
    if [[ -L /tmp/ttyV0 && -L /tmp/ttyV1 ]]; then
        echo "- Server Serial Port: /tmp/ttyV0 -> $(readlink /tmp/ttyV0)"
        echo "- Client Serial Port: /tmp/ttyV1 -> $(readlink /tmp/ttyV1)"
    else
        echo "- Server Serial Port: /tmp/ttyV0 (will be created when needed)"
        echo "- Client Serial Port: /tmp/ttyV1 (will be created when needed)"
    fi
    echo "- Baudrate: 9600"
    echo "- Configuration file: config/com_ports_unix.ini"
    echo
    echo "Next Steps:"
    echo "1. Test serial port configuration: python3 scripts/test_serial_ports.py"
    echo "2. If test fails, check that socat is running and ports exist"
    echo "3. Start the Modbus BMS Simulator with RTU mode"
    echo
    echo "Troubleshooting:"
    echo "- Ensure socat is installed and running"
    echo "- Check that virtual port links exist in /tmp/"
    echo "- Verify user permissions for serial port access"
    echo "- Use 'cleanup_serial_ports.sh' to reset virtual ports"
    echo
    
    # Optional: Run the test immediately
    read -p "Would you like to test the serial port configuration now? (y/N): " choice
    case "$choice" in
        y|Y|yes|YES)
            echo
            echo "Running serial port test..."
            python3 ../test_serial_ports.py
            ;;
        *)
            echo "You can test later by running: python3 scripts/test_serial_ports.py"
            ;;
    esac
    
    echo
    echo "Setup script completed."
}

# Run main function
main "$@"