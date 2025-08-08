#!/usr/bin/env python3
"""Direct serial control of BK9206b and monitoring of BK8520."""

import serial
import time
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

def send_command(ser, command, expect_response=True):
    """Send a command to the device and get response."""
    try:
        # Clear buffers
        ser.flushInput()
        ser.flushOutput()
        
        # Send command
        ser.write((command + '\r\n').encode('utf-8'))
        time.sleep(0.2)
        
        if not expect_response:
            return True, ""
        
        # Read response
        response = ""
        start_time = time.time()
        while time.time() - start_time < 2:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                response += data
                if '\r' in data or '\n' in data or len(response) > 50:
                    break
            time.sleep(0.1)
        
        return True, response.strip()
        
    except Exception as e:
        return False, str(e)

def main():
    """Control BK9206b and monitor both devices."""
    console.print("🔧 Direct Serial Control - BK9206b Power Supply", style="bold blue")
    console.print("Setting BK9206b to 22V @ 4A and monitoring voltage on BK8520\n")
    
    bk9206b_ser = None
    bk8520_ser = None
    
    try:
        # Connect to BK9206b Power Supply
        console.print("📡 Connecting to BK9206b on /dev/ttyUSB2...")
        bk9206b_ser = serial.Serial('/dev/ttyUSB2', 9600, timeout=3)
        time.sleep(1)
        console.print("✅ BK9206b connected", style="green")
        
        # Verify device identity
        success, response = send_command(bk9206b_ser, "*IDN?")
        if success and "9206B" in response:
            console.print(f"✅ Device confirmed: {response}", style="green")
        else:
            console.print(f"⚠️  Unexpected response: {response}", style="yellow")
        
        # Configure BK9206b
        console.print("\n🎯 Configuring BK9206b Power Supply:", style="bold blue")
        
        # Set voltage to 22V
        console.print("Setting voltage to 22.0V...")
        success, _ = send_command(bk9206b_ser, "VOLT 22.0", expect_response=False)
        if success:
            console.print("✅ Voltage command sent", style="green")
        else:
            console.print("❌ Failed to set voltage", style="red")
            
        # Set current limit to 4A
        console.print("Setting current limit to 4.0A...")
        success, _ = send_command(bk9206b_ser, "CURR 4.0", expect_response=False)
        if success:
            console.print("✅ Current limit command sent", style="green")
        else:
            console.print("❌ Failed to set current", style="red")
        
        # Enable output
        console.print("Enabling output...")
        success, _ = send_command(bk9206b_ser, "OUTP ON", expect_response=False)
        if success:
            console.print("✅ Output enabled", style="green bold")
        else:
            console.print("❌ Failed to enable output", style="red")
        
        time.sleep(2)  # Allow settings to stabilize
        
        # Try to connect to BK8520 for monitoring
        try:
            console.print("\n📡 Attempting to connect to BK8520 on /dev/ttyUSB0...")
            bk8520_ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
            bk8520_connected = True
            console.print("✅ BK8520 connected", style="green")
        except Exception as e:
            console.print(f"⚠️  BK8520 connection failed: {e}", style="yellow")
            console.print("Will monitor BK9206b output only", style="yellow")
            bk8520_connected = False
        
        # Start monitoring
        console.print("\n📊 Starting Real-time Monitoring:", style="bold blue")
        console.print("Press Ctrl+C to stop and disable output\n")
        
        monitor_count = 0
        while True:
            monitor_count += 1
            
            # Create monitoring table
            table = Table(
                title=f"Device Monitoring - Update #{monitor_count}",
                box=box.ROUNDED,
                title_style="bold blue"
            )
            table.add_column("Device", style="cyan", width=15)
            table.add_column("Parameter", style="blue", width=20)
            table.add_column("Value", style="green", width=15)
            table.add_column("Status", style="yellow", width=25)
            
            # Monitor BK9206b
            try:
                # Get voltage setting and measurement
                success, volt_set = send_command(bk9206b_ser, "VOLT?")
                success2, volt_meas = send_command(bk9206b_ser, "MEAS:VOLT?")
                success3, curr_set = send_command(bk9206b_ser, "CURR?")
                success4, curr_meas = send_command(bk9206b_ser, "MEAS:CURR?")
                success5, output_state = send_command(bk9206b_ser, "OUTP?")
                
                if success and volt_set:
                    voltage_setpoint = float(volt_set)
                    table.add_row("BK9206b", "Voltage Setpoint", f"{voltage_setpoint:.2f}V", "⚙️  Set to 22V")
                
                if success2 and volt_meas:
                    voltage_actual = float(volt_meas)
                    voltage_ok = abs(voltage_actual - 22.0) < 0.5
                    table.add_row("BK9206b", "Voltage Output", f"{voltage_actual:.3f}V", 
                                 f"{'✅' if voltage_ok else '⚠️'} {'Target achieved!' if voltage_ok else 'Different from 22V'}")
                
                if success3 and curr_set:
                    current_setpoint = float(curr_set)
                    table.add_row("BK9206b", "Current Limit", f"{current_setpoint:.2f}A", "⚙️  Set to 4A")
                
                if success4 and curr_meas:
                    current_actual = float(curr_meas)
                    table.add_row("BK9206b", "Current Output", f"{current_actual:.3f}A", "📊 Load dependent")
                
                if success5 and output_state:
                    output_on = output_state.strip() == "1"
                    table.add_row("BK9206b", "Output State", "ON" if output_on else "OFF", 
                                 f"{'✅' if output_on else '❌'} Power output")
                
            except Exception as e:
                table.add_row("BK9206b", "Error", str(e)[:20], "❌ Communication issue")
            
            # Try to get BK8520 readings (if connected)
            if bk8520_connected and bk8520_ser:
                try:
                    # Try various BK8520 commands to get voltage reading
                    commands_to_try = ["MEAS:VOLT?", "VOLT?", ":MEAS:VOLT?", "FETC:VOLT?"]
                    voltage_reading = None
                    
                    for cmd in commands_to_try:
                        success, response = send_command(bk8520_ser, cmd)
                        if success and response and response.replace('.', '').replace('-', '').isdigit():
                            voltage_reading = float(response)
                            break
                    
                    if voltage_reading is not None:
                        voltage_match = abs(voltage_reading - 22.0) < 1.0
                        table.add_row("BK8520", "Measured Voltage", f"{voltage_reading:.3f}V",
                                     f"{'✅' if voltage_match else '⚠️'} {'Sees BK9206b output!' if voltage_match else 'Different voltage'}")
                    else:
                        table.add_row("BK8520", "Status", "No reading", "❌ No voltage data")
                        
                except Exception as e:
                    table.add_row("BK8520", "Error", str(e)[:20], "❌ Communication issue")
            
            # Display table
            console.clear()
            console.print(table)
            
            # Show verification summary
            try:
                if success2 and volt_meas:
                    voltage_actual = float(volt_meas)
                    console.print(f"\n🎯 **Verification Result:**")
                    if abs(voltage_actual - 22.0) < 0.5:
                        console.print(f"✅ **SUCCESS**: BK9206b is outputting {voltage_actual:.3f}V (target: 22V)", style="green bold")
                        if bk8520_connected and voltage_reading is not None:
                            if abs(voltage_reading - 22.0) < 1.0:
                                console.print(f"✅ **CONFIRMED**: BK8520 also sees {voltage_reading:.3f}V", style="green bold")
                            else:
                                console.print(f"⚠️  **NOTE**: BK8520 sees {voltage_reading:.3f}V (different from BK9206b)", style="yellow")
                    else:
                        console.print(f"⚠️  **WARNING**: BK9206b outputting {voltage_actual:.3f}V (target: 22V)", style="yellow")
            except:
                pass
            
            console.print(f"\n⏱️  Next update in 2 seconds... (Ctrl+C to stop)")
            time.sleep(2)
            
    except KeyboardInterrupt:
        console.print("\n\n🛑 Monitoring stopped by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
    finally:
        # Cleanup - disable output for safety
        if bk9206b_ser and bk9206b_ser.is_open:
            try:
                console.print("\n🔒 Disabling BK9206b output for safety...")
                send_command(bk9206b_ser, "OUTP OFF", expect_response=False)
                console.print("✅ BK9206b output disabled", style="green")
                bk9206b_ser.close()
            except:
                pass
        
        if bk8520_ser and bk8520_ser.is_open:
            try:
                bk8520_ser.close()
            except:
                pass
        
        console.print("🏁 Session complete", style="blue")

if __name__ == "__main__":
    main()