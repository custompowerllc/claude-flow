#!/usr/bin/env python3
"""Monitor BK8520 Load Tester voltage readings."""

import sys
import time
from pathlib import Path

# Add the project to Python path
sys.path.insert(0, str(Path(__file__).parent))

from bk_integration.config import ConfigManager
from bk_integration.clients.bk8520 import BK8520Client
from rich.console import Console
from rich.table import Table
from rich import box
from rich.live import Live

console = Console()

def main():
    """Monitor BK8520 Load Tester voltage readings."""
    
    # Load configuration
    try:
        config_path = Path(__file__).parent / "config.json"
        config = ConfigManager(config_path)
        console.print("✅ Configuration loaded successfully", style="green")
    except Exception as e:
        console.print(f"❌ Error loading configuration: {e}", style="red")
        return 1
    
    # Initialize BK8520 client
    try:
        load_client = BK8520Client(config.get_load_config())
        console.print("✅ BK8520 client initialized", style="green")
    except Exception as e:
        console.print(f"❌ Error initializing BK8520 client: {e}", style="red")
        return 1
    
    console.print("\n📊 BK8520 Load Tester Monitoring", style="bold blue")
    console.print("Monitoring voltage to detect if BK9206b output is active...")
    console.print("Target: Looking for 22V from BK9206b power supply")
    console.print("Press Ctrl+C to stop\n")
    
    try:
        with Live(console=console, refresh_per_second=0.5) as live:
            monitor_count = 0
            while True:
                monitor_count += 1
                
                try:
                    # Get readings from BK8520
                    readings = load_client.get_readings()
                    
                    # Create monitoring table
                    table = Table(
                        title=f"BK8520 Load Tester - Voltage Detection (Update #{monitor_count})",
                        box=box.ROUNDED,
                        title_style="bold blue"
                    )
                    table.add_column("Parameter", style="cyan", width=20)
                    table.add_column("Value", style="green", width=15) 
                    table.add_column("Status", style="yellow", width=30)
                    
                    if isinstance(readings, dict) and 'error' not in readings:
                        voltage = readings.get('voltage', 0)
                        current = readings.get('current', 0)
                        power = readings.get('power', 0)
                        mode = readings.get('mode', 'Unknown')
                        
                        # Analyze voltage reading
                        if voltage >= 21.0 and voltage <= 23.0:
                            voltage_status = "✅ Close to target 22V!"
                            voltage_style = "green bold"
                        elif voltage > 0:
                            voltage_status = "⚠️ Different voltage detected"
                            voltage_style = "yellow"
                        else:
                            voltage_status = "❌ No voltage detected"
                            voltage_style = "red"
                        
                        table.add_row("Voltage", f"{voltage:.3f}V", voltage_status)
                        table.add_row("Current", f"{current:.3f}A", "📊 Load current draw")
                        table.add_row("Power", f"{power:.3f}W", "📊 Power consumption")
                        table.add_row("Load Mode", mode, "📋 Current operating mode")
                        
                        # Add connection status
                        connection_status = readings.get('connected', False)
                        table.add_row("Connection", "Connected" if connection_status else "Disconnected", 
                                     f"{'✅' if connection_status else '❌'} Device status")
                        
                    else:
                        error_msg = readings.get('error', 'Unknown error') if isinstance(readings, dict) else str(readings)
                        table.add_row("Status", "ERROR", f"❌ {error_msg}")
                    
                    live.update(table)
                    
                    # Show interpretation below the table
                    if isinstance(readings, dict) and 'error' not in readings:
                        voltage = readings.get('voltage', 0)
                        interpretation = "\n🎯 **Analysis:**\n"
                        
                        if voltage >= 21.0 and voltage <= 23.0:
                            interpretation += f"✅ **SUCCESS**: BK8520 is detecting {voltage:.3f}V, which indicates BK9206b is likely outputting close to 22V"
                        elif voltage > 5.0:
                            interpretation += f"⚠️ **INFO**: BK8520 detects {voltage:.3f}V - BK9206b may be set to a different voltage"
                        elif voltage > 0.1:
                            interpretation += f"🔍 **INFO**: BK8520 detects {voltage:.3f}V - Low voltage, BK9206b may be off or set very low"
                        else:
                            interpretation += "❌ **NO VOLTAGE**: BK8520 detects no voltage - BK9206b output may be disabled or not connected"
                        
                        console.print(interpretation)
                
                except Exception as e:
                    error_table = Table(title="Error", box=box.ROUNDED)
                    error_table.add_column("Issue", style="red")
                    error_table.add_row(f"Monitoring error: {e}")
                    live.update(error_table)
                
                time.sleep(2)
                
    except KeyboardInterrupt:
        console.print("\n\n🛑 Monitoring stopped by user", style="yellow")
        console.print("Final readings obtained from BK8520 Load Tester.", style="dim")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())