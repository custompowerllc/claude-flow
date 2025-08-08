#!/usr/bin/env python3
"""Test serial communication with both devices directly."""

import serial
import time
from rich.console import Console

console = Console()

def test_serial_port(port, device_name, baudrate=9600):
    """Test serial communication with a device."""
    console.print(f"\n🔧 Testing {device_name} on {port}", style="bold blue")
    
    try:
        # Open serial connection
        with serial.Serial(port, baudrate=baudrate, timeout=3) as ser:
            console.print(f"✅ Serial port {port} opened successfully", style="green")
            
            # Clear any existing data
            ser.flushInput()
            ser.flushOutput()
            time.sleep(0.5)
            
            # Test basic communication commands
            test_commands = [
                "*IDN?",     # Standard identification command
                "SYST:ERR?", # System error query
                "STAT?",     # Status query (BK specific)
                "*RST",      # Reset command
            ]
            
            for cmd in test_commands:
                console.print(f"📡 Sending: '{cmd}'")
                
                # Send command
                ser.write((cmd + '\r\n').encode('utf-8'))
                time.sleep(0.5)
                
                # Read response
                response = ""
                start_time = time.time()
                while time.time() - start_time < 2:
                    if ser.in_waiting > 0:
                        data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                        response += data
                        if '\r' in data or '\n' in data:
                            break
                    time.sleep(0.1)
                
                if response.strip():
                    console.print(f"📥 Response: '{response.strip()}'", style="green")
                else:
                    console.print("❌ No response received", style="red")
                
                time.sleep(0.5)
                
    except serial.SerialException as e:
        console.print(f"❌ Serial error on {port}: {e}", style="red")
        return False
    except Exception as e:
        console.print(f"❌ Unexpected error on {port}: {e}", style="red")
        return False
    
    return True

def main():
    """Test serial communication with both devices."""
    console.print("🧪 Serial Communication Test", style="bold blue")
    console.print("Testing direct serial communication with BK devices...")
    
    # Test BK8520 on /dev/ttyUSB0
    bk8520_ok = test_serial_port("/dev/ttyUSB0", "BK8520 Load Tester", 9600)
    
    # Test BK9206b on /dev/ttyUSB2  
    bk9206b_ok = test_serial_port("/dev/ttyUSB2", "BK9206b Power Supply", 9600)
    
    console.print("\n📊 Test Results Summary:", style="bold blue")
    console.print(f"BK8520 (/dev/ttyUSB0): {'✅ OK' if bk8520_ok else '❌ Failed'}")
    console.print(f"BK9206b (/dev/ttyUSB2): {'✅ OK' if bk9206b_ok else '❌ Failed'}")
    
    if not (bk8520_ok or bk9206b_ok):
        console.print("\n⚠️  Troubleshooting Tips:", style="yellow")
        console.print("1. Check that both devices are powered ON")
        console.print("2. Verify USB cables are connected properly")
        console.print("3. Ensure devices are in REMOTE mode (not LOCAL)")
        console.print("4. Try different baud rates (9600, 38400, 115200)")
        console.print("5. Check that devices support SCPI commands")

if __name__ == "__main__":
    main()