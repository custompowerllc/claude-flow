#!/usr/bin/env python3
"""Direct device control script for BK8520 and BK9206b."""

import sys
import time
import json
from pathlib import Path

# Add the project to Python path
sys.path.insert(0, str(Path(__file__).parent))

from bk_integration.config import ConfigManager
from bk_integration.clients.bk8520 import BK8520Client
from bk_integration.clients.bk9206b import BK9206bClient
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

def main():
    """Main function to set BK9206b and monitor BK8520."""
    
    # Load configuration
    try:
        config_path = Path(__file__).parent / "config.json"
        config = ConfigManager(config_path)
        console.print("✅ Configuration loaded successfully", style="green")
    except Exception as e:
        console.print(f"❌ Error loading configuration: {e}", style="red")
        return 1
    
    # Initialize clients
    try:
        power_client = BK9206bClient(config.get_power_config())
        load_client = BK8520Client(config.get_load_config())
        console.print("✅ Device clients initialized", style="green")
    except Exception as e:
        console.print(f"❌ Error initializing clients: {e}", style="red")
        return 1
    
    console.print("\n🔧 Setting BK9206b Power Supply Parameters:", style="bold blue")
    
    # Set BK9206b to 22V and 4A
    try:
        console.print("Setting voltage to 22.0V...")
        voltage_result = power_client.set_voltage(22.0)
        if voltage_result.get('success'):
            console.print("✅ Voltage set to 22.0V", style="green")
        else:
            console.print(f"❌ Voltage setting failed: {voltage_result.get('message', 'Unknown error')}", style="red")
            
        console.print("Setting current limit to 4.0A...")
        current_result = power_client.set_current(4.0)
        if current_result.get('success'):
            console.print("✅ Current limit set to 4.0A", style="green")
        else:
            console.print(f"❌ Current setting failed: {current_result.get('message', 'Unknown error')}", style="red")
            
        console.print("Enabling power output...")
        output_result = power_client.enable_output()
        if output_result.get('success'):
            console.print("✅ Power output enabled", style="green bold")
        else:
            console.print(f"❌ Output enable failed: {output_result.get('message', 'Unknown error')}", style="red")
            
    except Exception as e:
        console.print(f"❌ Error configuring BK9206b: {e}", style="red")
        return 1
    
    # Wait a moment for settings to take effect
    time.sleep(2)
    
    console.print("\n📊 Starting Monitoring:", style="bold blue")
    console.print("Press Ctrl+C to stop monitoring\n")
    
    try:
        monitor_count = 0
        while True:
            monitor_count += 1
            
            # Get status from both devices
            try:
                power_status = power_client.get_status()
                load_readings = load_client.get_readings()
                
                # Create status table
                table = Table(title=f"Device Monitoring (Update #{monitor_count})", box=box.ROUNDED)
                table.add_column("Device", style="cyan", width=15)
                table.add_column("Parameter", style="blue", width=20)
                table.add_column("Value", style="green", width=15)
                table.add_column("Status", style="yellow", width=20)
                
                # BK9206b Power Supply data
                if isinstance(power_status, dict):
                    if 'error' not in power_status:
                        voltage_set = power_status.get('voltage_setpoint', 'N/A')
                        voltage_actual = power_status.get('voltage_actual', 'N/A')
                        current_set = power_status.get('current_setpoint', 'N/A')
                        current_actual = power_status.get('current_actual', 'N/A')
                        output_enabled = power_status.get('output_enabled', False)
                        
                        table.add_row("BK9206b", "Voltage Setpoint", f"{voltage_set}V", "✅ Set" if voltage_set != 'N/A' else "❌ Error")
                        table.add_row("BK9206b", "Voltage Actual", f"{voltage_actual}V", f"{'✅' if abs(float(voltage_actual or 0) - 22.0) < 0.5 else '⚠️'} Measured")
                        table.add_row("BK9206b", "Current Setpoint", f"{current_set}A", "✅ Set" if current_set != 'N/A' else "❌ Error")
                        table.add_row("BK9206b", "Current Actual", f"{current_actual}A", "📊 Measured")
                        table.add_row("BK9206b", "Output", "ON" if output_enabled else "OFF", f"{'✅' if output_enabled else '❌'} Status")
                    else:
                        table.add_row("BK9206b", "Status", "ERROR", f"❌ {power_status.get('error', 'Unknown')}")
                
                # BK8520 Load Tester data
                if isinstance(load_readings, dict):
                    if 'error' not in load_readings:
                        load_voltage = load_readings.get('voltage', 0)
                        load_current = load_readings.get('current', 0)
                        load_power = load_readings.get('power', 0)
                        load_mode = load_readings.get('mode', 'Unknown')
                        
                        # Check if BK8520 sees the expected 22V
                        voltage_ok = abs(load_voltage - 22.0) < 1.0 if load_voltage > 0 else False
                        
                        table.add_row("BK8520", "Measured Voltage", f"{load_voltage:.2f}V", f"{'✅' if voltage_ok else '⚠️'} {'Close to 22V' if voltage_ok else 'Different from 22V'}")
                        table.add_row("BK8520", "Measured Current", f"{load_current:.2f}A", "📊 Load Current")
                        table.add_row("BK8520", "Measured Power", f"{load_power:.2f}W", "📊 Load Power")
                        table.add_row("BK8520", "Mode", load_mode, "📋 Load Mode")
                    else:
                        table.add_row("BK8520", "Status", "ERROR", f"❌ {load_readings.get('error', 'Unknown')}")
                
                # Clear screen and display table
                console.clear()
                console.print(table)
                
                # Show summary status
                if isinstance(power_status, dict) and isinstance(load_readings, dict):
                    if 'error' not in power_status and 'error' not in load_readings:
                        power_voltage = power_status.get('voltage_actual', 0)
                        load_voltage = load_readings.get('voltage', 0)
                        
                        console.print(f"\n🎯 Verification Result:")
                        if abs(load_voltage - 22.0) < 1.0 and load_voltage > 0:
                            console.print(f"✅ SUCCESS: BK8520 sees {load_voltage:.2f}V (close to target 22V)", style="green bold")
                        elif load_voltage > 0:
                            console.print(f"⚠️ WARNING: BK8520 sees {load_voltage:.2f}V (target was 22V)", style="yellow")
                        else:
                            console.print("❌ No voltage detected on BK8520", style="red")
                
                console.print(f"\n⏱️ Next update in 2 seconds... (Press Ctrl+C to stop)")
                
            except Exception as e:
                console.print(f"❌ Error during monitoring: {e}", style="red")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        console.print("\n\n🛑 Monitoring stopped by user", style="yellow")
        
        # Ask if user wants to disable output
        try:
            response = input("\n❓ Disable BK9206b output? (y/N): ")
            if response.lower().startswith('y'):
                disable_result = power_client.disable_output()
                if disable_result.get('success'):
                    console.print("✅ BK9206b output disabled", style="green")
                else:
                    console.print(f"❌ Failed to disable output: {disable_result.get('message', 'Unknown error')}", style="red")
        except:
            pass
    
    return 0


if __name__ == "__main__":
    sys.exit(main())