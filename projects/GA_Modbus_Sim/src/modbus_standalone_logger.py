#!/usr/bin/env python3
"""
Standalone Modbus Logger CLI Application

Author: Alan Hu
Title: Firmware Engineer
Company: Custom Power LLC
Date: August 3, 2025

A standalone command-line interface for logging Modbus data from GA BMS systems.
This application provides a simplified interface without the complex session management,
focusing purely on data logging with historical tracking.

Features:
- Command line arguments for quick operation
- Interactive mode when no arguments provided
- TOML configuration file for persistent settings
- Historical tracking of previous serial numbers, RMA numbers, and paths
- Serial port listing and management
- Moving average filter for cell delta values
- Rich console formatting for better user experience
"""

import sys
import os
import argparse
import time
import csv
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Core imports
from src.modbus_query_test import (
    read_battery_registers, 
    list_available_serial_ports,
    register_map,
    parse_id_registers
)

# Import Rich for enhanced visuals
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.live import Live
    from rich import box
    from rich.columns import Columns
    RICH_AVAILABLE = True
except ImportError:
    print("Warning: Rich not installed. Install with: pip install rich")
    RICH_AVAILABLE = False
    Console = None

# Import TOML for configuration
try:
    import tomli
    import tomli_w
    TOML_AVAILABLE = True
except ImportError:
    print("Warning: TOML libraries not installed. Install with: pip install tomli tomli-w")
    TOML_AVAILABLE = False

# Import Serial for port listing
try:
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    print("Warning: PySerial not installed. Some features may not work.")
    SERIAL_AVAILABLE = False

# Import pymodbus
try:
    from pymodbus.client import ModbusSerialClient
    MODBUS_AVAILABLE = True
except ImportError:
    print("Warning: PyModbus not installed. Install with: pip install pymodbus")
    MODBUS_AVAILABLE = False

# Import WebSocket and asyncio for real-time broadcasting
try:
    import asyncio
    import websockets
    import threading
    import queue
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    print("Warning: WebSockets not installed. Install with: pip install websockets")
    WEBSOCKETS_AVAILABLE = False


class MovingAverageFilter:
    """Moving average filter for smoothing cell delta spikes"""
    
    def __init__(self, window_size: int = 5, spike_threshold_multiplier: float = 2.0):
        self.window_size = window_size
        self.spike_threshold_multiplier = spike_threshold_multiplier
        self.history: List[float] = []
        self.enabled = True
    
    def filter_value(self, value: float) -> float:
        """Apply moving average filter to detect and smooth spikes"""
        if not self.enabled:
            return value
        
        # Add value to history
        self.history.append(value)
        
        # Keep only the last window_size values
        if len(self.history) > self.window_size:
            self.history.pop(0)
        
        # If we don't have enough history, return the value as-is
        if len(self.history) < 3:
            return value
        
        # Calculate average of all but the current value
        historical_values = self.history[:-1]
        if not historical_values:
            return value
        
        average = sum(historical_values) / len(historical_values)
        
        # Handle zero/negative averages
        if average <= 0:
            return value
        
        # Check if current value is a spike
        deviation = abs(value - average)
        threshold = average * self.spike_threshold_multiplier
        
        if deviation > threshold:
            # Return the average instead of the spike
            return average
        
        return value


class WebSocketBroadcaster:
    """WebSocket server for broadcasting real-time Modbus data"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.data_queue = queue.Queue()
        self.server = None
        self.loop = None
        self.thread = None
        self.running = False
        
    async def register_client(self, websocket, path):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        print(f"WebSocket client connected from {websocket.remote_address}. Total clients: {len(self.clients)}")
        
        try:
            # Send welcome message
            welcome_msg = {
                "type": "connection",
                "status": "connected",
                "message": "Connected to Modbus data stream",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(welcome_msg))
            
            # Keep connection alive and handle disconnect
            await websocket.wait_closed()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            print(f"WebSocket client disconnected. Total clients: {len(self.clients)}")
    
    async def broadcast_data(self, data: Dict[str, Any]):
        """Broadcast data to all connected clients"""
        if not self.clients:
            return
        
        # Prepare broadcast message
        message = {
            "type": "data",
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Convert to JSON
        json_message = json.dumps(message, default=str)
        
        # Broadcast to all clients
        disconnected_clients = set()
        for client in self.clients:
            try:
                await client.send(json_message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected_clients
    
    def queue_data(self, data: Dict[str, Any]):
        """Queue data for broadcasting (thread-safe)"""
        try:
            self.data_queue.put_nowait(data)
        except queue.Full:
            # If queue is full, remove oldest item and add new one
            try:
                self.data_queue.get_nowait()
                self.data_queue.put_nowait(data)
            except queue.Empty:
                pass
    
    async def data_sender(self):
        """Coroutine to send queued data to clients"""
        while self.running:
            try:
                # Check for queued data with timeout
                try:
                    data = self.data_queue.get(timeout=0.1)
                    await self.broadcast_data(data)
                except queue.Empty:
                    await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
            except Exception as e:
                print(f"Error in data sender: {e}")
                await asyncio.sleep(0.1)
    
    def start_server(self):
        """Start the WebSocket server in a separate thread"""
        if not WEBSOCKETS_AVAILABLE:
            print("Warning: WebSockets not available. Cannot start WebSocket server.")
            return False
        
        if self.running:
            print("WebSocket server is already running.")
            return True
        
        def run_server():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            async def server_main():
                self.running = True
                
                # Start the WebSocket server
                self.server = await websockets.serve(
                    self.register_client,
                    self.host,
                    self.port,
                    ping_interval=20,
                    ping_timeout=10
                )
                
                print(f"WebSocket server started on ws://{self.host}:{self.port}")
                
                # Start the data sender coroutine
                data_sender_task = asyncio.create_task(self.data_sender())
                
                try:
                    # Wait for server shutdown
                    await self.server.wait_closed()
                except Exception as e:
                    print(f"WebSocket server error: {e}")
                finally:
                    data_sender_task.cancel()
                    self.running = False
            
            try:
                self.loop.run_until_complete(server_main())
            except Exception as e:
                print(f"Error running WebSocket server: {e}")
            finally:
                self.loop.close()
        
        # Start server in separate thread
        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()
        
        # Give the server a moment to start
        time.sleep(0.5)
        
        return True
    
    def stop_server(self):
        """Stop the WebSocket server"""
        if not self.running:
            return
        
        self.running = False
        
        if self.server and self.loop:
            # Schedule server shutdown
            future = asyncio.run_coroutine_threadsafe(self.server.close(), self.loop)
            try:
                future.result(timeout=5.0)
            except Exception as e:
                print(f"Error stopping WebSocket server: {e}")
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5.0)
        
        print("WebSocket server stopped.")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current WebSocket server status"""
        return {
            "running": self.running,
            "host": self.host,
            "port": self.port,
            "connected_clients": len(self.clients),
            "queue_size": self.data_queue.qsize()
        }


class StandaloneModbusLogger:
    """Standalone Modbus logger with minimal dependencies"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.config_file = Path("modbus-standalone-cli-config.toml")
        self.history_file = Path("modbus-logger-history.json")
        
        # Configuration
        self.config = self._load_config()
        self.history = self._load_history()
        
        # Current session data
        self.current_session = None
        self.is_logging = False
        self.log_file = None
        self.log_writer = None
        
        # Modbus client
        self.client = None
        self.is_connected = False
        
        # Moving average filter for cell delta
        self.cell_delta_filter = MovingAverageFilter(
            window_size=self.config.get('filter', {}).get('window_size', 5),
            spike_threshold_multiplier=self.config.get('filter', {}).get('spike_threshold', 2.0)
        )
        self.cell_delta_filter.enabled = self.config.get('filter', {}).get('enabled', True)
        
        # WebSocket broadcaster for real-time data streaming
        websocket_config = self.config.get('websocket', {})
        self.websocket_broadcaster = WebSocketBroadcaster(
            host=websocket_config.get('host', 'localhost'),
            port=websocket_config.get('port', 8765)
        )
        self.websocket_enabled = websocket_config.get('enabled', True)
        self.websocket_auto_start = websocket_config.get('auto_start', True)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from TOML file"""
        default_config = {
            'connection': {
                'port': '',
                'baudrate': 9600,
                'parity': 'E',
                'stopbits': 1,
                'bytesize': 8,
                'slave_id': 1,
                'timeout': 1.0
            },
            'logging': {
                'output_path': './logs',
                'interval': 0.5,
                'auto_create_dirs': True
            },
            'metadata': {
                'serial_number': '',
                'rma_number': ''
            },
            'filter': {
                'enabled': True,
                'window_size': 5,
                'spike_threshold': 2.0
            },
            'websocket': {
                'enabled': True,
                'host': 'localhost',
                'port': 8765,
                'auto_start': True
            }
        }
        
        if not TOML_AVAILABLE or not self.config_file.exists():
            return default_config
        
        try:
            with open(self.config_file, 'rb') as f:
                config = tomli.load(f)
            
            # Merge with defaults
            def merge_dict(base, update):
                for key, value in update.items():
                    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                        merge_dict(base[key], value)
                    else:
                        base[key] = value
            
            merge_dict(default_config, config)
            return default_config
            
        except Exception as e:
            self._print_error(f"Error loading config: {e}")
            return default_config
    
    def _save_config(self):
        """Save configuration to TOML file"""
        if not TOML_AVAILABLE:
            return
        
        try:
            with open(self.config_file, 'wb') as f:
                tomli_w.dump(self.config, f)
        except Exception as e:
            self._print_error(f"Error saving config: {e}")
    
    def _load_history(self) -> Dict[str, Any]:
        """Load historical data from JSON file"""
        default_history = {
            'serial_numbers': [],
            'rma_numbers': [],
            'output_paths': [],
            'ports': [],
            'sessions': []
        }
        
        if not self.history_file.exists():
            return default_history
        
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            # Merge with defaults
            for key in default_history:
                if key not in history:
                    history[key] = default_history[key]
            
            return history
            
        except Exception as e:
            self._print_error(f"Error loading history: {e}")
            return default_history
    
    def _save_history(self):
        """Save historical data to JSON file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            self._print_error(f"Error saving history: {e}")
    
    def _add_to_history(self, category: str, value: str, max_items: int = 10):
        """Add value to history category with deduplication"""
        if category not in self.history:
            self.history[category] = []
        
        # Remove if already exists
        if value in self.history[category]:
            self.history[category].remove(value)
        
        # Add to front
        self.history[category].insert(0, value)
        
        # Limit size
        self.history[category] = self.history[category][:max_items]
        
        self._save_history()
    
    def _print(self, *args, style=None, **kwargs):
        """Print with Rich formatting if available"""
        if self.console and style:
            self.console.print(*args, style=style, **kwargs)
        else:
            print(*args, **kwargs)
    
    def _print_success(self, message: str):
        """Print success message"""
        if self.console:
            self.console.print(f"✓ {message}", style="bold green")
        else:
            print(f"✓ {message}")
    
    def _print_error(self, message: str):
        """Print error message"""
        if self.console:
            self.console.print(f"✗ {message}", style="bold red")
        else:
            print(f"✗ {message}")
    
    def _print_warning(self, message: str):
        """Print warning message"""
        if self.console:
            self.console.print(f"⚠ {message}", style="bold yellow")
        else:
            print(f"⚠ {message}")
    
    def _print_info(self, message: str):
        """Print info message"""
        if self.console:
            self.console.print(f"ℹ {message}", style="bold blue")
        else:
            print(f"ℹ {message}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print("\nShutting down gracefully...")
        self.stop_logging()
        self.disconnect()
        if self.websocket_enabled:
            self.websocket_broadcaster.stop_server()
        sys.exit(0)
    
    def show_banner(self):
        """Show application banner"""
        if self.console:
            banner_text = Text()
            banner_text.append("Standalone Modbus Logger", style="bold blue")
            banner_text.append(" v1.0.0\n", style="dim")
            banner_text.append("GA BMS Data Logger - Simplified CLI Interface\n\n", style="white")
            
            banner_text.append("Features:\n", style="bold green")
            banner_text.append("• Command line arguments for quick operation\n", style="green")
            banner_text.append("• Interactive mode with configuration prompts\n", style="green")
            banner_text.append("• Historical tracking of settings and sessions\n", style="green")
            banner_text.append("• Moving average filter for cell delta smoothing\n", style="green")
            banner_text.append("• WebSocket server for real-time data streaming\n", style="green")
            banner_text.append("• TOML configuration file support\n", style="green")
            
            panel = Panel(
                banner_text,
                title="🔋 Standalone Modbus Logger",
                border_style="blue",
                padding=(1, 2)
            )
            
            self.console.print(panel)
        else:
            print("Standalone Modbus Logger v1.0.0")
            print("GA BMS Data Logger - Simplified CLI Interface")
            print("=" * 50)
    
    def list_ports(self) -> List[str]:
        """List available serial ports"""
        if not SERIAL_AVAILABLE:
            self._print_error("PySerial not available. Cannot list ports.")
            return []
        
        try:
            ports = list(serial.tools.list_ports.comports())
            if not ports:
                self._print_warning("No serial ports found.")
                return []
            
            if self.console:
                table = Table(title="📡 Available Serial Ports", show_header=True, header_style="bold blue")
                table.add_column("Port", style="cyan", width=12)
                table.add_column("Description", style="white", width=40)
                table.add_column("Hardware ID", style="dim", width=30)
                
                for port in ports:
                    table.add_row(port.device, port.description, port.hwid or "N/A")
                
                self.console.print(table)
            else:
                print("\nAvailable Serial Ports:")
                for i, port in enumerate(ports, 1):
                    print(f"  {i}. {port.device} - {port.description}")
            
            return [port.device for port in ports]
            
        except Exception as e:
            self._print_error(f"Error listing ports: {e}")
            return []
    
    def list_history(self):
        """List historical data"""
        if self.console:
            # Create columns for different history types
            tables = []
            
            # Serial numbers
            if self.history['serial_numbers']:
                sn_table = Table(title="Serial Numbers", show_header=False, box=box.ROUNDED)
                sn_table.add_column("Value", style="cyan")
                for sn in self.history['serial_numbers'][:5]:
                    sn_table.add_row(sn)
                tables.append(sn_table)
            
            # RMA numbers
            if self.history['rma_numbers']:
                rma_table = Table(title="RMA Numbers", show_header=False, box=box.ROUNDED)
                rma_table.add_column("Value", style="yellow")
                for rma in self.history['rma_numbers'][:5]:
                    rma_table.add_row(rma)
                tables.append(rma_table)
            
            # Output paths
            if self.history['output_paths']:
                path_table = Table(title="Output Paths", show_header=False, box=box.ROUNDED)
                path_table.add_column("Value", style="green")
                for path in self.history['output_paths'][:5]:
                    path_table.add_row(str(path))
                tables.append(path_table)
            
            if tables:
                columns = Columns(tables, equal=True)
                self.console.print(Panel(columns, title="📋 Recent History", border_style="blue"))
            else:
                self._print_info("No historical data available.")
        else:
            print("\nHistorical Data:")
            print("Serial Numbers:", ", ".join(self.history['serial_numbers'][:5]))
            print("RMA Numbers:", ", ".join(self.history['rma_numbers'][:5]))
            print("Output Paths:", ", ".join(self.history['output_paths'][:5]))
    
    def interactive_setup(self) -> Dict[str, Any]:
        """Interactive setup for logging parameters"""
        self._print_info("Interactive setup mode - Configure logging parameters")
        
        params = {}
        
        # Serial port selection
        available_ports = self.list_ports()
        if available_ports:
            if self.console:
                port = Prompt.ask(
                    "Select serial port",
                    choices=available_ports,
                    default=self.config['connection']['port'] or available_ports[0]
                )
            else:
                print(f"\nAvailable ports: {', '.join(available_ports)}")
                port = input(f"Select serial port [{self.config['connection']['port'] or available_ports[0]}]: ").strip()
                if not port:
                    port = self.config['connection']['port'] or available_ports[0]
        else:
            port = input("Enter serial port: ").strip()
        
        params['port'] = port
        
        # Output path
        default_path = self.config['logging']['output_path']
        if self.console:
            output_path = Prompt.ask("Output directory", default=default_path)
        else:
            output_path = input(f"Output directory [{default_path}]: ").strip()
            if not output_path:
                output_path = default_path
        
        params['output_path'] = output_path
        
        # Serial number
        default_sn = self.config['metadata']['serial_number']
        if not default_sn and self.history['serial_numbers']:
            default_sn = self.history['serial_numbers'][0]
        
        if self.console and self.history['serial_numbers']:
            serial_number = Prompt.ask(
                "Serial number",
                choices=self.history['serial_numbers'] + ["new"],
                default=default_sn or "new"
            )
            if serial_number == "new":
                serial_number = Prompt.ask("Enter new serial number")
        else:
            serial_number = input(f"Serial number [{default_sn}]: ").strip()
            if not serial_number:
                serial_number = default_sn
        
        params['serial_number'] = serial_number
        
        # RMA number (optional)
        default_rma = self.config['metadata']['rma_number']
        if not default_rma and self.history['rma_numbers']:
            default_rma = self.history['rma_numbers'][0]
        
        if self.console and self.history['rma_numbers']:
            rma_number = Prompt.ask(
                "RMA number (optional - press Enter to skip)",
                choices=self.history['rma_numbers'] + ["new", "skip"],
                default="skip" if not default_rma else default_rma
            )
            if rma_number == "skip":
                rma_number = ""
            elif rma_number == "new":
                rma_number = Prompt.ask("Enter new RMA number (or press Enter to skip)", default="")
        else:
            rma_number = input(f"RMA number (optional) [{default_rma or 'press Enter to skip'}]: ").strip()
            if not rma_number:
                rma_number = default_rma or ""
        
        params['rma_number'] = rma_number
        
        # Confirm settings
        if self.console:
            self._print_info("Configuration Summary:")
            table = Table(show_header=False, box=box.ROUNDED)
            table.add_column("Parameter", style="bold")
            table.add_column("Value", style="cyan")
            
            table.add_row("Serial Port", params['port'])
            table.add_row("Output Path", params['output_path'])
            table.add_row("Serial Number", params['serial_number'])
            table.add_row("RMA Number", params['rma_number'])
            
            self.console.print(table)
            
            if not Confirm.ask("Start logging with these settings?"):
                self._print_warning("Logging cancelled by user.")
                return None
        else:
            print("\nConfiguration Summary:")
            print(f"  Serial Port: {params['port']}")
            print(f"  Output Path: {params['output_path']}")
            print(f"  Serial Number: {params['serial_number']}")
            print(f"  RMA Number: {params['rma_number']}")
            
            confirm = input("\nStart logging with these settings? [y/N]: ").strip().lower()
            if confirm not in ['y', 'yes']:
                self._print_warning("Logging cancelled by user.")
                return None
        
        return params
    
    def connect(self, port: str, baudrate: int = 9600, parity: str = 'E', stopbits: int = 1, 
                bytesize: int = 8, slave_id: int = 1, timeout: float = 1.0) -> bool:
        """Connect to Modbus device"""
        if not MODBUS_AVAILABLE:
            self._print_error("PyModbus not available. Cannot connect.")
            return False
        
        if self.is_connected:
            self._print_warning("Already connected. Disconnect first.")
            return True
        
        try:
            self.client = ModbusSerialClient(
                port=port,
                baudrate=baudrate,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize,
                timeout=timeout
            )
            
            if self.client.connect():
                self.is_connected = True
                self._add_to_history('ports', port)
                self._print_success(f"Connected to {port}")
                return True
            else:
                self._print_error(f"Failed to connect to {port}")
                return False
                
        except Exception as e:
            self._print_error(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Modbus device"""
        if self.client and self.is_connected:
            self.client.close()
            self.is_connected = False
            self._print_success("Disconnected from Modbus device")
    
    def read_data(self, slave_id: int = 1) -> Optional[Dict[str, Any]]:
        """Read battery data from Modbus device"""
        if not self.is_connected or not self.client:
            self._print_error("Not connected to Modbus device")
            return None
        
        try:
            # Read input registers (same as original implementation)
            response = self.client.read_input_registers(
                address=9,  # Start at register 9 (data starts at 10)
                count=len(register_map),
                slave=slave_id
            )
            
            if response.isError():
                self._print_error(f"Modbus read error: {response}")
                return None
            
            # Parse register values
            values = response.registers
            mapped_data = {}
            
            for i, value in enumerate(values):
                register_address = 10 + i  # Start at register 10
                parameter_name = register_map.get(register_address, f"Unknown Register {register_address}")
                mapped_data[parameter_name] = value
            
            # Apply moving average filter to cell delta if enabled
            if 'afe_cell_volt_delta' in mapped_data and self.cell_delta_filter.enabled:
                original_delta = mapped_data['afe_cell_volt_delta']
                filtered_delta = self.cell_delta_filter.filter_value(float(original_delta))
                mapped_data['afe_cell_volt_delta'] = int(filtered_delta)
            
            return mapped_data
            
        except Exception as e:
            self._print_error(f"Error reading data: {e}")
            return None
    
    def start_logging(self, output_path: str, serial_number: str, rma_number: str, 
                     interval: float = 0.5) -> bool:
        """Start logging data to CSV file"""
        if self.is_logging:
            self._print_warning("Already logging. Stop current logging first.")
            return False
        
        if not self.is_connected:
            self._print_error("Not connected to Modbus device")
            return False
        
        # Create output directory
        output_dir = Path(output_path)
        if self.config['logging']['auto_create_dirs']:
            output_dir.mkdir(parents=True, exist_ok=True)
        
        if not output_dir.exists():
            self._print_error(f"Output directory does not exist: {output_path}")
            return False
        
        # Generate filename with timestamp, serial number, and optionally RMA number
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if rma_number:
            filename = f"{timestamp}-{serial_number}-{rma_number}.csv"
        else:
            filename = f"{timestamp}-{serial_number}.csv"
        self.log_file = output_dir / filename
        
        try:
            # Initialize CSV file with headers
            csv_file = open(self.log_file, 'w', newline='')
            self.log_writer = csv.writer(csv_file)
            
            # Write header
            header = ['Timestamp'] + list(register_map.values())
            self.log_writer.writerow(header)
            csv_file.flush()
            
            # Create current session data
            self.current_session = {
                'filename': str(self.log_file),
                'serial_number': serial_number,
                'rma_number': rma_number,
                'start_time': datetime.now(),
                'interval': interval,
                'record_count': 0,
                'csv_file': csv_file
            }
            
            self.is_logging = True
            
            # Update history
            self._add_to_history('serial_numbers', serial_number)
            if rma_number:  # Only add to history if RMA number is provided
                self._add_to_history('rma_numbers', rma_number)
            self._add_to_history('output_paths', output_path)
            
            # Update config
            self.config['metadata']['serial_number'] = serial_number
            self.config['metadata']['rma_number'] = rma_number
            self.config['logging']['output_path'] = output_path
            self._save_config()
            
            # Start WebSocket server if enabled and auto-start is configured
            if self.websocket_enabled and self.websocket_auto_start:
                if self.websocket_broadcaster.start_server():
                    self._print_success(f"WebSocket server started on ws://{self.websocket_broadcaster.host}:{self.websocket_broadcaster.port}")
                else:
                    self._print_warning("Failed to start WebSocket server, continuing with CSV logging only")
            
            self._print_success(f"Started logging to: {filename}")
            return True
            
        except Exception as e:
            self._print_error(f"Error starting logging: {e}")
            return False
    
    def stop_logging(self):
        """Stop logging data"""
        if not self.is_logging:
            self._print_warning("Not currently logging")
            return
        
        if self.current_session and 'csv_file' in self.current_session:
            self.current_session['csv_file'].close()
            
            # Add session to history
            session_summary = {
                'filename': self.current_session['filename'],
                'serial_number': self.current_session['serial_number'],
                'rma_number': self.current_session['rma_number'],
                'start_time': self.current_session['start_time'].isoformat(),
                'end_time': datetime.now().isoformat(),
                'record_count': self.current_session['record_count'],
                'interval': self.current_session['interval']
            }
            
            self.history['sessions'].insert(0, session_summary)
            self.history['sessions'] = self.history['sessions'][:20]  # Keep last 20 sessions
            self._save_history()
            
            duration = datetime.now() - self.current_session['start_time']
            self._print_success(f"Stopped logging. Duration: {str(duration).split('.')[0]}, Records: {self.current_session['record_count']}")
        
        # Stop WebSocket server if it's running
        if self.websocket_enabled and self.websocket_broadcaster.running:
            self.websocket_broadcaster.stop_server()
            self._print_success("WebSocket server stopped")
        
        self.is_logging = False
        self.current_session = None
        self.log_writer = None
        self.log_file = None
    
    def log_current_data(self, slave_id: int = 1) -> bool:
        """Log current data to CSV file"""
        if not self.is_logging or not self.current_session:
            return False
        
        data = self.read_data(slave_id)
        if not data:
            return False
        
        try:
            # Prepare CSV row
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row_data = [timestamp]
            
            # Add data in register order
            for reg_addr in range(10, 10 + len(register_map)):
                param_name = register_map.get(reg_addr, '')
                row_data.append(data.get(param_name, ''))
            
            # Write to CSV
            self.log_writer.writerow(row_data)
            self.current_session['csv_file'].flush()
            self.current_session['record_count'] += 1
            
            # Broadcast data via WebSocket if enabled
            if self.websocket_enabled and self.websocket_broadcaster.running:
                # Prepare data for WebSocket broadcast (include metadata)
                broadcast_data = {
                    'session': {
                        'serial_number': self.current_session['serial_number'],
                        'rma_number': self.current_session['rma_number'],
                        'record_count': self.current_session['record_count']
                    },
                    'modbus_data': data,
                    'timestamp': timestamp
                }
                
                # Queue data for broadcasting (non-blocking)
                self.websocket_broadcaster.queue_data(broadcast_data)
            
            return True
            
        except Exception as e:
            self._print_error(f"Error logging data: {e}")
            return False
    
    def run_continuous_logging(self, slave_id: int = 1):
        """Run continuous logging loop"""
        if not self.is_logging:
            self._print_error("Logging not started")
            return
        
        interval = self.current_session['interval']
        
        try:
            if self.console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    console=self.console
                ) as progress:
                    task = progress.add_task("Logging data...", total=None)
                    
                    self._print_info(f"Starting continuous logging every {interval}s. Press Ctrl+C to stop.")
                    
                    while self.is_logging:
                        if self.log_current_data(slave_id):
                            progress.update(task, description=f"Records: {self.current_session['record_count']}")
                        
                        time.sleep(interval)
            else:
                print(f"Starting continuous logging every {interval}s. Press Ctrl+C to stop.")
                
                while self.is_logging:
                    if self.log_current_data(slave_id):
                        print(f"Logged record {self.current_session['record_count']}", end='\r')
                    
                    time.sleep(interval)
                    
        except KeyboardInterrupt:
            self._print_info("Logging stopped by user")
        except Exception as e:
            self._print_error(f"Error during logging: {e}")
        finally:
            self.stop_logging()
    
    def show_status(self):
        """Show current status"""
        if self.console:
            status_text = Text()
            
            # Connection status
            status_text.append("Connection: ", style="bold")
            if self.is_connected:
                status_text.append("Connected", style="bold green")
            else:
                status_text.append("Disconnected", style="bold red")
            status_text.append("\n")
            
            # Logging status
            status_text.append("Logging: ", style="bold")
            if self.is_logging:
                status_text.append("Active", style="bold green")
                if self.current_session:
                    status_text.append(f" (Records: {self.current_session['record_count']})", style="dim")
            else:
                status_text.append("Inactive", style="bold red")
            status_text.append("\n")
            
            # Filter status
            status_text.append("Cell Delta Filter: ", style="bold")
            if self.cell_delta_filter.enabled:
                status_text.append("Enabled", style="bold green")
                status_text.append(f" (Window: {self.cell_delta_filter.window_size}, Threshold: {self.cell_delta_filter.spike_threshold_multiplier}x)", style="dim")
            else:
                status_text.append("Disabled", style="bold red")
            status_text.append("\n")
            
            # WebSocket status
            status_text.append("WebSocket Server: ", style="bold")
            if self.websocket_enabled:
                ws_status = self.websocket_broadcaster.get_status()
                if ws_status['running']:
                    status_text.append("Running", style="bold green")
                    status_text.append(f" (Clients: {ws_status['connected_clients']}, Queue: {ws_status['queue_size']})", style="dim")
                else:
                    status_text.append("Stopped", style="bold yellow")
            else:
                status_text.append("Disabled", style="bold red")
            status_text.append("\n")
            
            # Current session info
            if self.current_session:
                status_text.append("\nCurrent Session:\n", style="bold blue")
                status_text.append(f"  File: {Path(self.current_session['filename']).name}\n", style="white")
                status_text.append(f"  Serial: {self.current_session['serial_number']}\n", style="white")
                status_text.append(f"  RMA: {self.current_session['rma_number']}\n", style="white")
                duration = datetime.now() - self.current_session['start_time']
                status_text.append(f"  Duration: {str(duration).split('.')[0]}\n", style="white")
            
            panel = Panel(
                status_text,
                title="📊 System Status",
                border_style="blue",
                padding=(1, 2)
            )
            
            self.console.print(panel)
        else:
            print("\nSystem Status:")
            print("=" * 30)
            print(f"Connection: {'Connected' if self.is_connected else 'Disconnected'}")
            print(f"Logging: {'Active' if self.is_logging else 'Inactive'}")
            print(f"Cell Delta Filter: {'Enabled' if self.cell_delta_filter.enabled else 'Disabled'}")
            
            # WebSocket status
            if self.websocket_enabled:
                ws_status = self.websocket_broadcaster.get_status()
                status = "Running" if ws_status['running'] else "Stopped"
                print(f"WebSocket Server: {status} (Clients: {ws_status['connected_clients']})")
            else:
                print("WebSocket Server: Disabled")
            
            if self.current_session:
                print(f"\nCurrent Session:")
                print(f"  File: {Path(self.current_session['filename']).name}")
                print(f"  Serial: {self.current_session['serial_number']}")
                print(f"  RMA: {self.current_session['rma_number']}")
                print(f"  Records: {self.current_session['record_count']}")
    
    def list_sessions(self, limit: int = 10):
        """List recent logging sessions"""
        sessions = self.history['sessions'][:limit]
        
        if not sessions:
            self._print_warning("No previous sessions found.")
            return
        
        if self.console:
            table = Table(title="📋 Recent Logging Sessions", show_header=True, header_style="bold blue")
            table.add_column("Date", style="cyan", width=16)
            table.add_column("Serial", style="white", width=12)
            table.add_column("RMA", style="white", width=12)
            table.add_column("Records", justify="right", style="green", width=8)
            table.add_column("Duration", justify="center", style="blue", width=12)
            table.add_column("File", style="dim", width=30)
            
            for session in sessions:
                try:
                    start_time = datetime.fromisoformat(session['start_time'])
                    end_time = datetime.fromisoformat(session['end_time'])
                    duration = end_time - start_time
                    
                    table.add_row(
                        start_time.strftime("%m/%d %H:%M"),
                        session['serial_number'],
                        session['rma_number'],
                        str(session['record_count']),
                        str(duration).split('.')[0],
                        Path(session['filename']).name
                    )
                except Exception as e:
                    continue
            
            self.console.print(table)
        else:
            print("\nRecent Logging Sessions:")
            print("=" * 80)
            print(f"{'Date':^16} {'Serial':^12} {'RMA':^12} {'Records':^8} {'Duration':^12} {'File':^30}")
            print("-" * 80)
            
            for session in sessions:
                try:
                    start_time = datetime.fromisoformat(session['start_time'])
                    end_time = datetime.fromisoformat(session['end_time'])
                    duration = end_time - start_time
                    
                    print(f"{start_time.strftime('%m/%d %H:%M'):^16} "
                          f"{session['serial_number']:^12} "
                          f"{session['rma_number']:^12} "
                          f"{session['record_count']:^8} "
                          f"{str(duration).split('.')[0]:^12} "
                          f"{Path(session['filename']).name:^30}")
                except Exception:
                    continue


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Standalone Modbus Logger for GA BMS Systems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python modbus_standalone_logger.py
  
  # Quick logging with arguments
  python modbus_standalone_logger.py --port COM3 --serial-number 0573 --rma-number 8765
  
  # Specify custom output path
  python modbus_standalone_logger.py --port COM3 --output-path ./data --sn 0573 --rma 8765
  
  # List available ports
  python modbus_standalone_logger.py --list-ports
  
  # Show historical data
  python modbus_standalone_logger.py --history
        """
    )
    
    # Connection arguments
    parser.add_argument('--port', help='Serial port (e.g., COM3, /dev/ttyUSB0)')
    parser.add_argument('--baudrate', type=int, default=9600, help='Baud rate (default: 9600)')
    parser.add_argument('--parity', choices=['N', 'E', 'O'], default='E', help='Parity (default: E)')
    parser.add_argument('--stopbits', type=int, default=1, help='Stop bits (default: 1)')
    parser.add_argument('--bytesize', type=int, default=8, help='Data bits (default: 8)')
    parser.add_argument('--slave-id', type=int, default=1, help='Modbus slave ID (default: 1)')
    
    # Logging arguments
    parser.add_argument('--output-path', help='Output directory for CSV files')
    parser.add_argument('--serial-number', '--sn', help='Battery serial number')
    parser.add_argument('--rma-number', '--rma', help='RMA number (optional)')
    parser.add_argument('--interval', type=float, default=0.5, help='Logging interval in seconds (default: 0.5)')
    
    # WebSocket arguments
    parser.add_argument('--websocket-enabled', action='store_true', help='Enable WebSocket server')
    parser.add_argument('--websocket-disabled', action='store_true', help='Disable WebSocket server')
    parser.add_argument('--websocket-host', default='localhost', help='WebSocket server host (default: localhost)')
    parser.add_argument('--websocket-port', type=int, default=8765, help='WebSocket server port (default: 8765)')
    
    # Utility arguments
    parser.add_argument('--list-ports', action='store_true', help='List available serial ports')
    parser.add_argument('--history', action='store_true', help='Show historical data')
    parser.add_argument('--sessions', action='store_true', help='List recent logging sessions')
    parser.add_argument('--status', action='store_true', help='Show current status')
    
    # Interactive mode
    parser.add_argument('--interactive', '-i', action='store_true', help='Force interactive mode')
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Create logger instance
    logger = StandaloneModbusLogger()
    
    # Override WebSocket settings from command line arguments
    if args.websocket_enabled:
        logger.websocket_enabled = True
    elif args.websocket_disabled:
        logger.websocket_enabled = False
    
    # Update WebSocket configuration if provided
    if args.websocket_host != 'localhost' or args.websocket_port != 8765:
        logger.websocket_broadcaster = WebSocketBroadcaster(
            host=args.websocket_host,
            port=args.websocket_port
        )
    
    # Show banner
    logger.show_banner()
    
    # Handle utility commands
    if args.list_ports:
        logger.list_ports()
        return
    
    if args.history:
        logger.list_history()
        return
    
    if args.sessions:
        logger.list_sessions()
        return
    
    if args.status:
        logger.show_status()
        return
    
    # Determine if we need interactive mode
    need_interactive = (
        args.interactive or 
        not args.port or 
        not args.serial_number
    )
    
    try:
        if need_interactive:
            # Interactive mode
            params = logger.interactive_setup()
            if not params:
                return
        else:
            # Command line mode
            params = {
                'port': args.port,
                'output_path': args.output_path or logger.config['logging']['output_path'],
                'serial_number': args.serial_number,
                'rma_number': args.rma_number or ''  # Default to empty string if not provided
            }
        
        # Connect to Modbus device
        if not logger.connect(
            params['port'],
            baudrate=args.baudrate,
            parity=args.parity,
            stopbits=args.stopbits,
            bytesize=args.bytesize,
            slave_id=args.slave_id
        ):
            logger._print_error("Failed to connect to Modbus device")
            return
        
        # Start logging
        if not logger.start_logging(
            params['output_path'],
            params['serial_number'],
            params['rma_number'],
            interval=args.interval
        ):
            logger._print_error("Failed to start logging")
            return
        
        # Run continuous logging
        logger.run_continuous_logging(slave_id=args.slave_id)
        
    except KeyboardInterrupt:
        logger._print_info("Application interrupted by user")
    except Exception as e:
        logger._print_error(f"Unexpected error: {e}")
    finally:
        # Cleanup
        logger.stop_logging()
        logger.disconnect()
        if logger.websocket_enabled:
            logger.websocket_broadcaster.stop_server()


if __name__ == "__main__":
    main()