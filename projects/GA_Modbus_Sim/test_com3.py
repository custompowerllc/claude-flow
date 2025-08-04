#!/usr/bin/env python3
"""
Test COM3 availability and basic modbus functionality
"""

# removed unused imports: sys, pathlib.Path

def test_com3_availability():
    """Test if COM3 is available"""
    print("Testing COM3 availability...")
    
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        
        print(f"Found {len(ports)} total ports:")
        for port in ports:
            print(f"  - {port.device}: {port.description}")
        
        # Check specifically for COM3
        com3_found = any(port.device == 'COM3' for port in ports)
        
        if com3_found:
            print("✅ COM3 is available!")
            return True
        else:
            print("❌ COM3 not found in available ports")
            
            # Check for any COM ports
            com_ports = [p for p in ports if p.device.startswith('COM')]
            if com_ports:
                print("Available COM ports:")
                for port in com_ports:
                    print(f"  - {port.device}")
            else:
                print("No COM ports found")
            
            return False
            
    except ImportError:
        print("❌ PySerial not available")
        return False
    except Exception as e:
        print(f"❌ Error checking ports: {e}")
        return False

def test_basic_connection():
    """Test basic serial connection to COM3"""
    print("\nTesting basic serial connection...")
    
    try:
        import serial
        
        # Try to open COM3
        try:
            ser = serial.Serial('COM3', 9600, timeout=1)
            print("✅ Successfully opened COM3")
            ser.close()
            print("✅ Successfully closed COM3")
            return True
        except serial.SerialException as e:
            print(f"❌ Failed to open COM3: {e}")
            return False
        except Exception as e:
            print(f"❌ Error with COM3: {e}")
            return False
            
    except ImportError:
        print("❌ PySerial not available for connection test")
        return False

def test_modbus_availability():
    """Test if modbus library is available"""
    print("\nTesting Modbus library availability...")
    
    try:
        from pymodbus.client import ModbusSerialClient
        print("✅ PyModbus library available")
        
        # Try to create a client (don't connect yet)
        try:
            _ = ModbusSerialClient(port='COM3', baudrate=9600, parity='E')
            print("✅ ModbusSerialClient created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating ModbusSerialClient: {e}")
            return False
            
    except ImportError:
        print("❌ PyModbus not available")
        print("Install with: pip install pymodbus")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("COM3 and Modbus Connectivity Test")
    print("=" * 60)
    
    tests = [
        ("Port Availability", test_com3_availability),
        ("Serial Connection", test_basic_connection), 
        ("Modbus Library", test_modbus_availability)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name} Test:")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:20} {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! COM3 should work for data logging.")
        print("\nNext steps:")
        print("1. Run: python3 src/modbus_standalone_logger.py --list-ports")
        print("2. Run: python3 src/modbus_standalone_logger.py --port COM3 --sn 0573 --rma 8765")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        print("\nTroubleshooting:")
        print("- Ensure COM3 device is connected")
        print("- Install missing dependencies: pip install pymodbus pyserial rich")
        print("- Check if COM3 is in use by another application")
    
    print("=" * 60)

if __name__ == "__main__":
    main()