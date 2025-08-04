#!/usr/bin/env python3
"""
Real-time Dashboard for Standalone Modbus Logger

This dashboard reads CSV files being written by the standalone logger and displays
real-time charts and statistics.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import time
import csv
import json
from collections import deque
from typing import Dict, List, Optional, Tuple
import argparse
import threading
import random
from datetime import timedelta as td

# Import scaling functions
try:
    from utils.constants import scale_temperature, scale_current
    SCALE_FUNCTIONS_AVAILABLE = True
except ImportError:
    SCALE_FUNCTIONS_AVAILABLE = False

# Try to import toml for config reading
try:
    import tomli
    TOML_AVAILABLE = True
except ImportError:
    try:
        import toml as tomli
        TOML_AVAILABLE = True
    except ImportError:
        TOML_AVAILABLE = False

# Set matplotlib backend - try GUI first, fall back to headless if needed
import os
import platform

# Assume GUI is available initially
is_headless = False
gui_available = True

# Restore original matplotlib behavior - let it choose the best GUI backend
import matplotlib
# Don't force any backend - let matplotlib auto-detect the best available
print("Attempting to use matplotlib GUI...")
is_headless = False  # Assume GUI will work

# Try to import required libraries
try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.gridspec import GridSpec
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    print("Warning: matplotlib not installed. Install with: pip install matplotlib")
    MATPLOTLIB_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    print("Warning: pandas not installed. Install with: pip install pandas")
    PANDAS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    print("Error: numpy is required for dashboard functionality. Install with: pip install numpy")
    NUMPY_AVAILABLE = False

# WebSocket dependencies
try:
    import asyncio
    import websockets
    import json as websocket_json
    import concurrent.futures
    import threading
    WEBSOCKET_AVAILABLE = True
except ImportError:
    print("Warning: websockets not installed. Install with: pip install websockets")
    WEBSOCKET_AVAILABLE = False


class WebSocketDataSource:
    """WebSocket-based data source for dashboard with automatic reconnection"""
    
    def __init__(self, url: str, reconnect_interval: float = 2.0, max_reconnects: int = 30):
        self.url = url
        self.websocket = None
        self.connected = False
        self.reconnect_interval = reconnect_interval
        self.max_reconnects = max_reconnects
        self.reconnect_count = 0
        self.data_callback = None
        self.status_callback = None
        self.error_callback = None
        self.running = False
        self.loop = None
        self.connection_thread = None
        self.last_sequence = 0
        
        # Connection state tracking
        self.connection_state = "disconnected"  # disconnected, connecting, connected, reconnecting
        self.last_data_time = None
        self.connection_start_time = None
        
    def set_data_callback(self, callback):
        """Set callback for data messages"""
        self.data_callback = callback
        
    def set_status_callback(self, callback):
        """Set callback for status messages"""
        self.status_callback = callback
        
    def set_error_callback(self, callback):
        """Set callback for error messages"""
        self.error_callback = callback
    
    def start(self):
        """Start WebSocket connection in separate thread"""
        if self.running:
            return
            
        self.running = True
        self.connection_thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.connection_thread.start()
    
    def stop(self):
        """Stop WebSocket connection"""
        self.running = False
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self._disconnect(), self.loop)
    
    def _run_async_loop(self):
        """Run async event loop in thread"""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._connection_manager())
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"WebSocket loop error: {e}")
        finally:
            if self.loop and not self.loop.is_closed():
                self.loop.close()
    
    async def _connection_manager(self):
        """Manage WebSocket connection with automatic reconnection"""
        while self.running:
            try:
                await self._connect_and_listen()
            except Exception as e:
                if self.running:
                    if self.error_callback:
                        self.error_callback(f"Connection error: {e}")
                    await self._handle_reconnection()
    
    async def _connect_and_listen(self):
        """Connect to WebSocket and listen for messages"""
        self.connection_state = "connecting"
        self.connection_start_time = datetime.now()
        
        if self.status_callback:
            self.status_callback(f"Connecting to {self.url}...")
        
        try:
            async with websockets.connect(self.url, ping_interval=20, ping_timeout=10) as websocket:
                self.websocket = websocket
                self.connected = True
                self.connection_state = "connected"
                self.reconnect_count = 0
                
                if self.status_callback:
                    self.status_callback(f"Connected to WebSocket server")
                
                # Listen for messages
                async for message in websocket:
                    if not self.running:
                        break
                        
                    try:
                        data = websocket_json.loads(message)
                        await self._handle_message(data)
                        self.last_data_time = datetime.now()
                    except websocket_json.JSONDecodeError as e:
                        if self.error_callback:
                            self.error_callback(f"JSON decode error: {e}")
                    except Exception as e:
                        if self.error_callback:
                            self.error_callback(f"Message handling error: {e}")
                            
        except websockets.exceptions.ConnectionClosed:
            if self.running:
                if self.status_callback:
                    self.status_callback("WebSocket connection closed")
        except Exception as e:
            if self.running:
                if self.error_callback:
                    self.error_callback(f"WebSocket connection failed: {e}")
        finally:
            self.connected = False
            self.websocket = None
            if self.running:
                self.connection_state = "reconnecting"
    
    async def _handle_message(self, message: dict):
        """Handle incoming WebSocket message"""
        message_type = message.get('type', 'unknown')
        
        # Track sequence numbers for data integrity
        if 'sequence' in message:
            sequence = message['sequence']
            if self.last_sequence > 0 and sequence != self.last_sequence + 1:
                if self.error_callback:
                    self.error_callback(f"Missing messages detected: expected {self.last_sequence + 1}, got {sequence}")
            self.last_sequence = sequence
        
        if message_type == 'data' and self.data_callback:
            # Get the main data container (from WebSocket format)
            data_container = message.get('data', {})
            modbus_data = data_container.get('modbus_data', {})
            
            timestamp_str = message.get('timestamp', datetime.now().isoformat())
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
            
            # Convert to format expected by dashboard (pass the modbus_data directly)
            self.data_callback(modbus_data, timestamp)
            
        elif message_type == 'status' and self.status_callback:
            status_info = message.get('payload', {})
            self.status_callback(f"Status: {status_info}")
            
        elif message_type == 'error' and self.error_callback:
            error_info = message.get('payload', {})
            self.error_callback(f"Server error: {error_info}")
    
    async def _handle_reconnection(self):
        """Handle reconnection logic with exponential backoff"""
        if not self.running or self.reconnect_count >= self.max_reconnects:
            if self.reconnect_count >= self.max_reconnects:
                if self.status_callback:
                    self.status_callback(f"Max reconnection attempts ({self.max_reconnects}) reached. Falling back to CSV mode.")
            return
        
        self.reconnect_count += 1
        # Exponential backoff with jitter
        delay = min(self.reconnect_interval * (2 ** (self.reconnect_count - 1)), 60)
        delay += random.uniform(0, 1)  # Add jitter
        
        if self.status_callback:
            self.status_callback(f"Reconnection attempt {self.reconnect_count}/{self.max_reconnects} in {delay:.1f}s...")
        
        await asyncio.sleep(delay)
    
    async def _disconnect(self):
        """Disconnect from WebSocket"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        self.connected = False
        self.connection_state = "disconnected"
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected"""
        return self.connected and self.websocket is not None
    
    def get_connection_info(self) -> dict:
        """Get connection status information"""
        return {
            'state': self.connection_state,
            'connected': self.connected,
            'url': self.url,
            'reconnect_count': self.reconnect_count,
            'max_reconnects': self.max_reconnects,
            'last_data_time': self.last_data_time,
            'connection_start_time': self.connection_start_time
        }


class DataSourceManager:
    """Manages multiple data sources with fallback capability"""
    
    def __init__(self, csv_file: str, websocket_url: str = None):
        self.csv_file = csv_file
        self.websocket_url = websocket_url
        self.websocket_source = None
        self.current_mode = 'csv'  # 'websocket', 'csv', 'fallback'
        self.data_callback = None
        self.status_callback = None
        self.websocket_failed = False
        
        # Initialize WebSocket if URL provided
        if websocket_url and WEBSOCKET_AVAILABLE:
            self.websocket_source = WebSocketDataSource(websocket_url)
            self.websocket_source.set_data_callback(self._websocket_data_received)
            self.websocket_source.set_status_callback(self._websocket_status_received)
            self.websocket_source.set_error_callback(self._websocket_error_received)
            self.current_mode = 'websocket'
    
    def set_data_callback(self, callback):
        """Set callback for data reception"""
        self.data_callback = callback
    
    def set_status_callback(self, callback):
        """Set callback for status updates"""
        self.status_callback = callback
    
    def start(self):
        """Start the appropriate data source"""
        if self.websocket_source and not self.websocket_failed:
            if self.status_callback:
                self.status_callback("Starting WebSocket connection...")
            self.websocket_source.start()
        else:
            if self.status_callback:
                self.status_callback("Using CSV file mode")
            self.current_mode = 'csv'
    
    def stop(self):
        """Stop all data sources"""
        if self.websocket_source:
            self.websocket_source.stop()
    
    def _websocket_data_received(self, payload: dict, timestamp: datetime):
        """Handle WebSocket data reception"""
        if self.data_callback:
            # Convert WebSocket data format to CSV-compatible format
            self.data_callback(payload, timestamp, source='websocket')
    
    def _websocket_status_received(self, status: str):
        """Handle WebSocket status updates"""
        if self.status_callback:
            self.status_callback(f"WebSocket: {status}")
        
        # Check for fallback conditions
        if "fallback to CSV" in status.lower() or "max reconnection attempts" in status.lower():
            self.websocket_failed = True
            self.current_mode = 'fallback'
            if self.status_callback:
                self.status_callback("Switched to CSV fallback mode")
    
    def _websocket_error_received(self, error: str):
        """Handle WebSocket errors"""
        if self.status_callback:
            self.status_callback(f"WebSocket Error: {error}")
    
    def get_mode(self) -> str:
        """Get current data source mode"""
        return self.current_mode
    
    def is_websocket_connected(self) -> bool:
        """Check if WebSocket is connected"""
        return (self.websocket_source and 
                self.websocket_source.is_connected() and 
                not self.websocket_failed)
    
    def get_connection_info(self) -> dict:
        """Get detailed connection information"""
        info = {
            'mode': self.current_mode,
            'csv_file': self.csv_file,
            'websocket_url': self.websocket_url,
            'websocket_failed': self.websocket_failed
        }
        
        if self.websocket_source:
            info['websocket_info'] = self.websocket_source.get_connection_info()
        
        return info


class ModbusDashboard:
    """Real-time dashboard for monitoring Modbus data"""
    
    def __init__(self, csv_file: str, update_interval: int = 1000, com_port: str = None, historical_mode: bool = False, session_type: str = None, export_screenshot: str = None, headless: bool = False, websocket_url: str = None):
        self.csv_file = Path(csv_file)
        self.update_interval = update_interval  # milliseconds
        self.historical_mode = historical_mode
        self.session_type = session_type
        self.export_screenshot = export_screenshot
        self.headless = headless
        self.websocket_url = websocket_url
        
        # Initialize data source manager for WebSocket/CSV fallback
        self.data_source_manager = DataSourceManager(str(csv_file), websocket_url)
        self.data_source_manager.set_data_callback(self._handle_websocket_data)
        self.data_source_manager.set_status_callback(self._handle_status_update)
        
        # WebSocket connection status
        self.connection_status = "Initializing..."
        self.data_source_mode = "csv"  # Track current mode for UI display
        
        # Load metadata if available
        self.metadata = self.load_metadata()
        
        # Get COM port from metadata, parameter, or config
        if com_port:
            self.com_port = com_port
        elif self.metadata and 'session' in self.metadata:
            self.com_port = self.metadata['session'].get('com_port', 'Unknown')
        else:
            self.com_port = self.get_com_port_from_config()
        
        # Data storage - no maxlen in historical mode
        if self.historical_mode:
            self.timestamps = deque()
            self.cell_voltages = {f'cell_{i}': deque() for i in range(1, 9)}
            self.pack_voltage = deque()
            self.current = deque()
            self.soc = deque()
            self.cell_delta = deque()
            self.temperature1 = deque()
            self.temperature2 = deque()
        else:
            self.timestamps = deque(maxlen=300)  # Keep last 5 minutes of data
            self.cell_voltages = {f'cell_{i}': deque(maxlen=300) for i in range(1, 9)}
            self.pack_voltage = deque(maxlen=300)
            self.current = deque(maxlen=300)
            self.soc = deque(maxlen=300)
            self.cell_delta = deque(maxlen=300)
            self.temperature1 = deque(maxlen=300)
            self.temperature2 = deque(maxlen=300)
        
        # Statistics
        self.stats = {
            'min_cell_voltage': 0,
            'max_cell_voltage': 0,
            'avg_cell_voltage': 0,
            'cell_delta_current': 0,
            'pack_voltage_current': 0,
            'current_current': 0,
            'soc_current': 0,
            'temp1_current': 0,
            'temp2_current': 0,
            'record_count': 0,
            'logging_duration': timedelta(0)
        }
        
        # Peak delta tracking
        self.peak_delta_value = 0
        self.peak_delta_timestamp = None
        self.peak_delta_cell_voltages = {f'cell_{i}': 0 for i in range(1, 9)}
        
        # Track file position
        self.last_row_count = 0
        self.header_map = {}
        self.all_data = []
        
        # Performance optimization variables
        self._last_file_size = 0
        self._update_counter = 0
        self._plot_update_interval = 5  # Update plots every 5 data reads
        
        # Current spike filtering
        self.current_filter_enabled = True
        self.current_spike_threshold = 50.0  # A - values above this are considered spikes
        self.current_history = deque(maxlen=10)  # Keep last 10 current values for filtering
        
        # Screenshot functionality
        self.screenshot_enabled = False
        self.peak_delta_threshold = 50.0  # mV - threshold for significant cell delta
        self.recovery_time_seconds = 10
        self.peak_detected = False
        self.peak_detection_time = None
        self.recovery_data = []
        self.screenshot_lock = threading.Lock()
        
        # Store CSV file path for directory detection
        self.csv_file_path = Path(csv_file)
        
        # Enhanced detection for current cutoff events
        self.detect_current_cutoff = True
        self.current_cutoff_threshold = 0.5  # A - below this is considered "off"
        self.previous_current = None
        self.current_cutoff_detected = False
        
        # Extract serial number and RMA from metadata or filename
        if self.metadata and 'session' in self.metadata:
            self.serial_number = self.metadata['session'].get('serial_number', self.extract_serial_from_filename())
            self.rma_number = self.metadata['session'].get('rma_number', self.extract_rma_from_filename())
        else:
            self.serial_number = self.extract_serial_from_filename()
            self.rma_number = self.extract_rma_from_filename()
        
        # Get temperature unit from config
        self.temp_unit = self.get_temperature_unit()
        
        # Setup the figure and plots
        self.setup_plots()
        
        # If in historical mode, load all data immediately
        if self.historical_mode:
            self.load_all_historical_data()
        else:
            # Start WebSocket connection for real-time mode
            if websocket_url and not historical_mode:
                self.data_source_manager.start()
                self.data_source_mode = self.data_source_manager.get_mode()
    
    def _handle_websocket_data(self, payload: dict, timestamp: datetime, source: str = 'websocket'):
        """Handle data received from WebSocket"""
        try:
            # Store data source mode
            self.data_source_mode = source
            
            # Convert WebSocket payload to dashboard format and append to data
            self.timestamps.append(timestamp)
            
            # Parse cell voltages (WebSocket data is in mV, convert to V)
            for i in range(1, 9):
                cell_key = f'afe_cell_volt{i}'
                if cell_key in payload:
                    value = float(payload[cell_key]) / 1000.0  # Convert mV to V
                    self.cell_voltages[f'cell_{i}'].append(value)
            
            # Parse pack voltage (convert from mV to V)
            if 'afe_pack_volt' in payload:
                pack_v = float(payload['afe_pack_volt']) / 1000.0
                self.pack_voltage.append(pack_v)
            
            # Parse current (WebSocket data is in mA, convert to A)
            current_col = 'fg_current' if 'fg_current' in payload else 'afe_current'
            if current_col in payload:
                current = float(payload[current_col]) / 1000.0  # Convert mA to A
                # Apply current spike filtering
                current = self.filter_current_spike(current)
                self.current.append(current)
            
            # Parse cell delta (keep in mV)
            if 'afe_cell_volt_delta' in payload:
                delta = float(payload['afe_cell_volt_delta'])
                self.cell_delta.append(delta)
                
                # Track peak delta and corresponding cell voltages
                if delta > self.peak_delta_value:
                    self.peak_delta_value = delta
                    self.peak_delta_timestamp = timestamp
                    # Store current cell voltages at peak delta
                    for i in range(1, 9):
                        cell_key = f'cell_{i}'
                        if self.cell_voltages[cell_key]:
                            self.peak_delta_cell_voltages[cell_key] = self.cell_voltages[cell_key][-1]
            
            # Parse SOC
            if 'fg_state_of_charge' in payload:
                self.soc.append(float(payload['fg_state_of_charge']))
            
            # Parse temperature (WebSocket data might be in Kelvin×10, convert appropriately)
            if 'afe_temp1' in payload:
                temp_raw = float(payload['afe_temp1'])
                if temp_raw > 1000:  # Raw Kelvin×10 format
                    if SCALE_FUNCTIONS_AVAILABLE:
                        temp_scaled = scale_temperature(temp_raw, self.temp_unit)
                    else:
                        kelvin = temp_raw / 10.0
                        celsius = kelvin - 273.15
                        temp_scaled = celsius * 9/5 + 32 if self.temp_unit == 'F' else celsius
                elif temp_raw > 200:  # Kelvin format
                    celsius = temp_raw - 273.15
                    temp_scaled = celsius * 9/5 + 32 if self.temp_unit == 'F' else celsius
                else:  # Already in Celsius
                    temp_scaled = temp_raw * 9/5 + 32 if self.temp_unit == 'F' else temp_raw
                self.temperature1.append(temp_scaled)
            
            if 'afe_temp2' in payload:
                temp_raw = float(payload['afe_temp2'])
                if temp_raw > 1000:  # Raw Kelvin×10 format
                    if SCALE_FUNCTIONS_AVAILABLE:
                        temp_scaled = scale_temperature(temp_raw, self.temp_unit)
                    else:
                        kelvin = temp_raw / 10.0
                        celsius = kelvin - 273.15
                        temp_scaled = celsius * 9/5 + 32 if self.temp_unit == 'F' else celsius
                elif temp_raw > 200:  # Kelvin format
                    celsius = temp_raw - 273.15
                    temp_scaled = celsius * 9/5 + 32 if self.temp_unit == 'F' else celsius
                else:  # Already in Celsius
                    temp_scaled = temp_raw * 9/5 + 32 if self.temp_unit == 'F' else temp_raw
                self.temperature2.append(temp_scaled)
            
            # Update statistics
            self.stats['record_count'] += 1
            
            # Immediate axis adjustment on first data point for instant usability
            if len(self.timestamps) == 1:
                try:
                    # Force immediate relim and autoscale on first data
                    for ax in [self.ax_cells, self.ax_pack, self.ax_current, self.ax_delta, self.ax_soc, self.ax_temp]:
                        ax.relim()
                        ax.autoscale_view()
                except:
                    pass
            
        except Exception as e:
            print(f"Error processing WebSocket data: {e}")
    
    def _handle_status_update(self, status: str):
        """Handle status updates from WebSocket connection"""
        self.connection_status = status
        self.data_source_mode = self.data_source_manager.get_mode()
        print(f"Connection Status: {status}")  # For debugging
    
    def load_metadata(self) -> Optional[Dict]:
        """Load metadata JSON file if it exists"""
        metadata_file = self.csv_file.with_suffix('.json')
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load metadata file: {e}")
        return None
    
    def get_com_port_from_config(self) -> str:
        """Try to get COM port from configuration file"""
        if not TOML_AVAILABLE:
            return "Unknown"
        
        # Look for config file in current directory or parent directory
        config_paths = [
            Path("modbus-standalone-cli-config.toml"),
            Path("../modbus-standalone-cli-config.toml"),
            Path("../../modbus-standalone-cli-config.toml")
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'rb') as f:
                        config = tomli.load(f)
                    port = config.get('connection', {}).get('port', '')
                    if port:
                        return port
                except Exception:
                    continue
        
        return "Unknown"
    
    def get_temperature_unit(self) -> str:
        """Get temperature unit from config.toml"""
        if not TOML_AVAILABLE:
            return "C"
        
        # Look for config.toml file
        config_paths = [
            Path("config.toml"),
            Path("../config.toml"),
            Path("../../config.toml")
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'rb') as f:
                        config = tomli.load(f)
                    unit = config.get('display', {}).get('temperature_unit', 'C')
                    if unit in ['C', 'F']:
                        return unit
                except Exception:
                    continue
        
        return "C"  # Default to Celsius
    
    def filter_current_spike(self, current_value: float) -> float:
        """Filter current spikes using threshold and median filtering"""
        if not self.current_filter_enabled:
            return current_value
        
        # Add to history first
        self.current_history.append(current_value)
        
        # If we don't have enough history, return the value (but still add to history)
        if len(self.current_history) < 3:
            return current_value
        
        # Check if current value is a spike (much higher than recent values)
        if abs(current_value) > self.current_spike_threshold:
            # Calculate median of recent values (excluding the current one)
            recent_values = list(self.current_history)[:-1]  # Exclude the last (current) value
            if recent_values:
                median_current = sorted(recent_values)[len(recent_values) // 2]
                
                # If the spike is much larger than the median, replace with median
                if abs(current_value) > abs(median_current) * 3 and abs(current_value) > 10:
                    print(f"Current spike detected and filtered: {current_value:.1f}A → {median_current:.1f}A")
                    return median_current
        
        return current_value
    
    def extract_serial_from_filename(self) -> str:
        """Extract serial number from CSV filename"""
        filename = self.csv_file.stem
        # Pattern: YYYYMMDD_HHMMSS-{serial}-{rma}
        parts = filename.split('-')
        if len(parts) >= 3:
            return parts[1]  # Serial number is second part
        return "Unknown"
    
    def extract_rma_from_filename(self) -> str:
        """Extract RMA number from CSV filename"""
        filename = self.csv_file.stem
        # Pattern: YYYYMMDD_HHMMSS-{serial}-{rma}
        parts = filename.split('-')
        if len(parts) >= 3:
            return parts[2]  # RMA number is third part
        return "Unknown"
    
    def setup_plots(self):
        """Setup matplotlib figure and subplots"""
        try:
            # Set dark theme
            plt.style.use('dark_background')
        except Exception as e:
            print(f"Warning: Could not set dark theme: {e}")
            # Continue without dark theme
        
        # Create figure with GridSpec for flexible layout
        self.fig = plt.figure(figsize=(16, 10), facecolor='#1e1e1e')
        mode_text = 'Historical View' if self.historical_mode else 'Real-time Dashboard'
        title = f'GA BMS Standalone Logger - {mode_text}'
        
        # Add session type to title if provided
        if self.session_type:
            session_display = self.session_type.capitalize()
            if session_display == "Root":
                session_display = "General"
            title += f' | {session_display} Session'
        
        if self.com_port != "Unknown":
            title += f' | Port: {self.com_port}'
        if self.serial_number != "Unknown":
            title += f' | Serial: {self.serial_number}'
        if self.rma_number != "Unknown":
            title += f' | RMA: {self.rma_number}'
        
        # Add connection status to title
        if self.websocket_url:
            data_source_display = f"WebSocket ({self.data_source_mode.upper()})"
            title += f' | {data_source_display}'
        
        self.fig.suptitle(title, fontsize=14, fontweight='bold', color='cyan')
        
        # Create grid layout - 4 rows, with bottom row for statistics
        gs = GridSpec(4, 3, figure=self.fig, hspace=0.4, wspace=0.3, height_ratios=[1, 1, 1, 0.4])
        
        # Cell voltages plot (large, top left)
        self.ax_cells = self.fig.add_subplot(gs[0:2, 0:2])
        self.ax_cells.set_title('Cell Voltages', fontweight='bold', color='lightgreen')
        self.ax_cells.set_xlabel('Time')
        self.ax_cells.set_ylabel('Voltage (V)')
        self.ax_cells.grid(True, alpha=0.3)
        
        # Pack voltage and current (right column)
        self.ax_pack = self.fig.add_subplot(gs[0, 2])
        self.ax_pack.set_title('Pack Voltage', fontweight='bold', color='yellow')
        self.ax_pack.set_xlabel('Time')
        self.ax_pack.set_ylabel('Voltage (V)')
        self.ax_pack.grid(True, alpha=0.3)
        
        self.ax_current = self.fig.add_subplot(gs[1, 2])
        self.ax_current.set_title('Current', fontweight='bold', color='orange')
        self.ax_current.set_xlabel('Time')
        self.ax_current.set_ylabel('Current (A)')
        self.ax_current.grid(True, alpha=0.3)
        
        # Cell delta (row 3, left)
        self.ax_delta = self.fig.add_subplot(gs[2, 0])
        self.ax_delta.set_title('Cell Delta', fontweight='bold', color='red')
        self.ax_delta.set_xlabel('Time')
        self.ax_delta.set_ylabel('Delta (mV)')
        self.ax_delta.grid(True, alpha=0.3)
        
        # SOC (row 3, middle)
        self.ax_soc = self.fig.add_subplot(gs[2, 1])
        self.ax_soc.set_title('State of Charge', fontweight='bold', color='purple')
        self.ax_soc.set_xlabel('Time')
        self.ax_soc.set_ylabel('SOC (%)')
        self.ax_soc.grid(True, alpha=0.3)
        
        # Temperature (row 3, right)
        self.ax_temp = self.fig.add_subplot(gs[2, 2])
        self.ax_temp.set_title('Temperature', fontweight='bold', color='cyan')
        self.ax_temp.set_xlabel('Time')
        self.ax_temp.set_ylabel(f'Temperature (°{self.temp_unit})')
        self.ax_temp.grid(True, alpha=0.3)
        
        # Set initial sensible Y-axis ranges for better initial visibility
        # These ranges account for defective/runaway cells and edge cases
        self.ax_cells.set_ylim(2.0, 4.2)    # Cell voltage range: 2.0V-4.2V (includes defective cells)
        self.ax_pack.set_ylim(22.0, 29.0)   # Pack voltage range: 22V-29V (8S pack with margin)
        self.ax_current.set_ylim(-10.0, 10.0)  # Current range: ±10A (with margin for edge cases)
        self.ax_delta.set_ylim(0, 100)      # Cell delta range: 0-100mV (typical + edge cases)
        self.ax_soc.set_ylim(0, 100)        # SOC range: 0-100%
        self.ax_temp.set_ylim(10.0, 50.0)   # Temperature range: 10-50°C (with margin for edge cases)
        
        # Force voltage axes to use fixed decimal format (not scientific notation)
        from matplotlib.ticker import FormatStrFormatter
        self.ax_cells.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
        self.ax_pack.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
        
        # Statistics subplot (entire bottom row)
        self.ax_stats = self.fig.add_subplot(gs[3, :])
        self.ax_stats.axis('off')  # Hide axes for text display
        # Add statistics title directly in the subplot, positioned lower to avoid overlap
        self.ax_stats.text(0.02, -0.55, 'Statistics', fontsize=10, fontweight='bold', 
                          color='white', transform=self.ax_stats.transAxes)
        
        # Initialize line objects and text labels
        self.cell_lines = {}
        self.cell_texts = {}
        colors = plt.cm.tab10(np.linspace(0, 1, 8))
        for i, (cell, color) in enumerate(zip(self.cell_voltages.keys(), colors), 1):
            self.cell_lines[cell], = self.ax_cells.plot([], [], color=color, linewidth=2)
            # Add text labels for actual voltage values to the left of the plot
            # Position them outside the plot area
            row = i - 1  # 0-7
            x_pos = -0.15 * 1.6  # Position to the left of the plot, moved further by factor of 1.2
            y_pos = 0.9 - row * 0.11   # Starting at top, going down
            
            self.cell_texts[cell] = self.ax_cells.text(x_pos, y_pos, f'Cell {i}: 0.000V', 
                                                       transform=self.ax_cells.transAxes,
                                                       fontsize=8, color=color, fontweight='bold',
                                                       bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.7))
        
        self.pack_line, = self.ax_pack.plot([], [], 'y-', linewidth=2)
        self.current_line, = self.ax_current.plot([], [], 'orange', linewidth=2)
        self.delta_line, = self.ax_delta.plot([], [], 'r-', linewidth=2)
        self.soc_line, = self.ax_soc.plot([], [], 'm-', linewidth=2)
        self.temp1_line, = self.ax_temp.plot([], [], 'c-', label='Temp 1', linewidth=2)
        self.temp2_line, = self.ax_temp.plot([], [], 'b-', label='Temp 2', linewidth=2)
        self.ax_temp.legend(loc='upper left', fontsize=8)
        
        # Add statistics text in dedicated subplot positioned lower to avoid overlap
        self.stats_text = self.ax_stats.text(0.02, -0.7, '', fontsize=9, 
                                            verticalalignment='top',
                                            horizontalalignment='left',
                                            transform=self.ax_stats.transAxes,
                                            fontfamily='monospace',
                                            color='white')
        
        # Set tight layout
        try:
            plt.tight_layout()
        except:
            # Ignore tight_layout warnings
            pass
    
    def read_new_data(self) -> bool:
        """Read new data from WebSocket or CSV file (fallback) - optimized for performance"""
        # If WebSocket is connected, data is handled via callbacks
        if self.data_source_manager.is_websocket_connected():
            # WebSocket data is handled via _handle_websocket_data callback
            # Just return True to continue the update cycle
            return len(self.timestamps) > 0
        
        # Fallback to CSV file reading
        if not self.csv_file.exists():
            return False
        
        try:
            # Quick file size check to avoid unnecessary reads
            current_size = self.csv_file.stat().st_size
            if current_size == self._last_file_size:
                return False
            self._last_file_size = current_size
            
            # Read entire file (keep simple for reliability, but with optimizations)
            with open(self.csv_file, 'r', newline='') as f:
                reader = csv.reader(f)
                
                # Read header if we haven't yet
                if not self.header_map:
                    header = next(reader)
                    self.header_map = {col: idx for idx, col in enumerate(header)}
                
                # Read all rows
                all_rows = list(reader)
                
                # Check if we have new data
                if len(all_rows) <= self.last_row_count:
                    return False
                
                # Process only new rows, limit batch size for responsiveness
                new_rows = all_rows[self.last_row_count:]
                if len(new_rows) > 50:  # Process max 50 rows at once
                    new_rows = new_rows[:50]
                    
                new_data = False
                
                for row in new_rows:
                    if len(row) < len(self.header_map):
                        continue
                    
                    # Skip if this is the header row (in case file was recreated)
                    if row[0] == 'Timestamp':
                        continue
                    
                    try:
                        # Parse timestamp - try with microseconds first, then without
                        try:
                            timestamp = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
                        except ValueError:
                            timestamp = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                        self.timestamps.append(timestamp)
                    except ValueError as e:
                        print(f"Skipping row with invalid timestamp: {row[0]}")
                        continue
                    
                    # Parse cell voltages (convert from mV to V)
                    for i in range(1, 9):
                        # Try new format first (afe_cell_volt1), then legacy format (Cell1_mV, Cell1_V)
                        col_name = f'afe_cell_volt{i}'
                        legacy_col_mv = f'Cell{i}_mV'
                        legacy_col_v = f'Cell{i}_V'
                        
                        if col_name in self.header_map:
                            value = float(row[self.header_map[col_name]]) / 1000.0
                            self.cell_voltages[f'cell_{i}'].append(value)
                        elif legacy_col_mv in self.header_map:
                            value = float(row[self.header_map[legacy_col_mv]]) / 1000.0
                            self.cell_voltages[f'cell_{i}'].append(value)
                        elif legacy_col_v in self.header_map:
                            # Legacy format might have values in mV despite column name
                            value = float(row[self.header_map[legacy_col_v]])
                            # Check if value needs conversion from mV to V
                            if value > 100:  # Likely in mV (e.g., 3206)
                                value = value / 1000.0
                            self.cell_voltages[f'cell_{i}'].append(value)
                    
                    # Parse other values
                    # Try new format first, then legacy
                    pack_col = None
                    if 'afe_pack_volt' in self.header_map:
                        pack_col = 'afe_pack_volt'
                    elif 'Pack_V' in self.header_map:
                        pack_col = 'Pack_V'
                    elif 'Pack_mV' in self.header_map:
                        pack_col = 'Pack_mV'
                    
                    if pack_col:
                        pack_v = float(row[self.header_map[pack_col]])
                        # If pack voltage seems too low (like 100 instead of 26600), it might need different scaling
                        if pack_v < 1000:  # Probably needs to be treated as already in V * 100
                            pack_v = pack_v / 100.0  # Convert from V*100 to V
                        else:
                            pack_v = pack_v / 1000.0  # Convert from mV to V
                        self.pack_voltage.append(pack_v)
                    
                    # Current - use fg_current (fuel gauge current) as primary source
                    current_col = None
                    if 'fg_current' in self.header_map:
                        current_col = 'fg_current'
                    elif 'afe_current' in self.header_map:
                        current_col = 'afe_current'
                    elif 'Current' in self.header_map:
                        current_col = 'Current'
                    
                    if current_col:
                        current = float(row[self.header_map[current_col]])
                        # Current values from standalone logger are already properly scaled
                        # Just convert to amperes if they appear to be in milliamps
                        if abs(current) > 100:
                            current = current / 1000.0
                        
                        # Apply current spike filtering
                        current = self.filter_current_spike(current)
                        
                        self.current.append(current)
                    
                    # Cell delta
                    delta_col = None
                    if 'afe_cell_volt_delta' in self.header_map:
                        delta_col = 'afe_cell_volt_delta'
                    elif 'Cell_Delta_V' in self.header_map:
                        delta_col = 'Cell_Delta_V'
                    elif 'Cell_Delta_mV' in self.header_map:
                        delta_col = 'Cell_Delta_mV'
                    
                    if delta_col:
                        delta = float(row[self.header_map[delta_col]])
                        # Keep in mV
                        if delta < 1.0:
                            delta = delta * 1000.0
                        self.cell_delta.append(delta)
                        
                        # Track peak delta and corresponding cell voltages
                        if delta > self.peak_delta_value:
                            self.peak_delta_value = delta
                            self.peak_delta_timestamp = timestamp
                            # Store current cell voltages at peak delta
                            for i in range(1, 9):
                                cell_key = f'cell_{i}'
                                if self.cell_voltages[cell_key]:
                                    self.peak_delta_cell_voltages[cell_key] = self.cell_voltages[cell_key][-1]
                    
                    # SOC
                    soc_col = None
                    if 'fg_state_of_charge' in self.header_map:
                        soc_col = 'fg_state_of_charge'
                    elif 'SOC' in self.header_map:
                        soc_col = 'SOC'
                    
                    if soc_col:
                        self.soc.append(float(row[self.header_map[soc_col]]))
                    
                    # Temperature
                    temp1_col = None
                    temp2_col = None
                    if 'afe_temp1' in self.header_map:
                        temp1_col = 'afe_temp1'
                    elif 'Temp1' in self.header_map:
                        temp1_col = 'Temp1'
                    
                    if 'afe_temp2' in self.header_map:
                        temp2_col = 'afe_temp2'
                    elif 'Temp2' in self.header_map:
                        temp2_col = 'Temp2'
                    
                    if temp1_col:
                        temp_raw = float(row[self.header_map[temp1_col]])
                        # Detect temperature format and convert appropriately
                        if temp_raw > 1000:  # Raw Kelvin×10 format (e.g., 3030 for ~30°C)
                            if SCALE_FUNCTIONS_AVAILABLE:
                                temp_scaled = scale_temperature(temp_raw, self.temp_unit)
                            else:
                                kelvin = temp_raw / 10.0
                                celsius = kelvin - 273.15
                                temp_scaled = celsius * 9/5 + 32 if self.temp_unit == 'F' else celsius
                        elif temp_raw > 200:  # Kelvin format (e.g., 303 for ~30°C)
                            celsius = temp_raw - 273.15
                            temp_scaled = celsius * 9/5 + 32 if self.temp_unit == 'F' else celsius
                        else:  # Already in Celsius format
                            temp_scaled = temp_raw * 9/5 + 32 if self.temp_unit == 'F' else temp_raw
                        self.temperature1.append(temp_scaled)
                    
                    if temp2_col:
                        temp_raw = float(row[self.header_map[temp2_col]])
                        # Detect temperature format and convert appropriately
                        if temp_raw > 1000:  # Raw Kelvin×10 format (e.g., 3030 for ~30°C)
                            if SCALE_FUNCTIONS_AVAILABLE:
                                temp_scaled = scale_temperature(temp_raw, self.temp_unit)
                            else:
                                kelvin = temp_raw / 10.0
                                celsius = kelvin - 273.15
                                temp_scaled = celsius * 9/5 + 32 if self.temp_unit == 'F' else celsius
                        elif temp_raw > 200:  # Kelvin format (e.g., 303 for ~30°C)
                            celsius = temp_raw - 273.15
                            temp_scaled = celsius * 9/5 + 32 if self.temp_unit == 'F' else celsius
                        else:  # Already in Celsius format
                            temp_scaled = temp_raw * 9/5 + 32 if self.temp_unit == 'F' else temp_raw
                        self.temperature2.append(temp_scaled)
                    
                    new_data = True
                    self.stats['record_count'] += 1
                
                # Update row count
                self.last_row_count += len(new_rows)
                
                return new_data
                
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return False
    
    def load_all_historical_data(self):
        """Load all data from CSV file for historical viewing"""
        if not self.csv_file.exists():
            print(f"Error: CSV file not found: {self.csv_file}")
            return
        
        print(f"Loading historical data from: {self.csv_file}")
        
        try:
            with open(self.csv_file, 'r', newline='') as f:
                reader = csv.reader(f)
                
                # Read header
                header = next(reader)
                self.header_map = {col: idx for idx, col in enumerate(header)}
                
                # Read all rows
                row_count = 0
                for row in reader:
                    if len(row) < len(self.header_map):
                        continue
                    
                    try:
                        # Parse timestamp - try with microseconds first, then without
                        try:
                            timestamp = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
                        except ValueError:
                            timestamp = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                        self.timestamps.append(timestamp)
                    except ValueError:
                        continue
                    
                    # Parse cell voltages (convert from mV to V)
                    for i in range(1, 9):
                        # Try new format first (afe_cell_volt1), then legacy format (Cell1_mV, Cell1_V)
                        col_name = f'afe_cell_volt{i}'
                        legacy_col_mv = f'Cell{i}_mV'
                        legacy_col_v = f'Cell{i}_V'
                        
                        if col_name in self.header_map:
                            value = float(row[self.header_map[col_name]]) / 1000.0
                            self.cell_voltages[f'cell_{i}'].append(value)
                        elif legacy_col_mv in self.header_map:
                            value = float(row[self.header_map[legacy_col_mv]]) / 1000.0
                            self.cell_voltages[f'cell_{i}'].append(value)
                        elif legacy_col_v in self.header_map:
                            # Legacy format might have values in mV despite column name
                            value = float(row[self.header_map[legacy_col_v]])
                            # Check if value needs conversion from mV to V
                            if value > 100:  # Likely in mV (e.g., 3206)
                                value = value / 1000.0
                            self.cell_voltages[f'cell_{i}'].append(value)
                    
                    # Parse other values
                    # Try new format first, then legacy
                    pack_col = None
                    if 'afe_pack_volt' in self.header_map:
                        pack_col = 'afe_pack_volt'
                    elif 'Pack_V' in self.header_map:
                        pack_col = 'Pack_V'
                    elif 'Pack_mV' in self.header_map:
                        pack_col = 'Pack_mV'
                    
                    if pack_col:
                        pack_v = float(row[self.header_map[pack_col]])
                        # If pack voltage seems too low (like 100 instead of 26600), it might need different scaling
                        if pack_v < 1000:  # Probably needs to be treated as already in V * 100
                            pack_v = pack_v / 100.0  # Convert from V*100 to V
                        else:
                            pack_v = pack_v / 1000.0  # Convert from mV to V
                        self.pack_voltage.append(pack_v)
                    
                    # Current - use fg_current (fuel gauge current) as primary source
                    current_col = None
                    if 'fg_current' in self.header_map:
                        current_col = 'fg_current'
                    elif 'afe_current' in self.header_map:
                        current_col = 'afe_current'
                    elif 'Current' in self.header_map:
                        current_col = 'Current'
                    
                    if current_col:
                        current = float(row[self.header_map[current_col]])
                        # Current values from standalone logger are already properly scaled
                        # Just convert to amperes if they appear to be in milliamps
                        if abs(current) > 100:
                            current = current / 1000.0
                        
                        # Apply current spike filtering
                        current = self.filter_current_spike(current)
                        
                        self.current.append(current)
                    
                    # Cell delta
                    delta_col = None
                    if 'afe_cell_volt_delta' in self.header_map:
                        delta_col = 'afe_cell_volt_delta'
                    elif 'Cell_Delta_V' in self.header_map:
                        delta_col = 'Cell_Delta_V'
                    elif 'Cell_Delta_mV' in self.header_map:
                        delta_col = 'Cell_Delta_mV'
                    
                    if delta_col:
                        delta = float(row[self.header_map[delta_col]])
                        # Keep in mV
                        if delta < 1.0:
                            delta = delta * 1000.0
                        self.cell_delta.append(delta)
                        
                        # Track peak delta and corresponding cell voltages
                        if delta > self.peak_delta_value:
                            self.peak_delta_value = delta
                            self.peak_delta_timestamp = timestamp
                            # Store current cell voltages at peak delta
                            for i in range(1, 9):
                                cell_key = f'cell_{i}'
                                if self.cell_voltages[cell_key]:
                                    self.peak_delta_cell_voltages[cell_key] = self.cell_voltages[cell_key][-1]
                    
                    # SOC
                    soc_col = None
                    if 'fg_state_of_charge' in self.header_map:
                        soc_col = 'fg_state_of_charge'
                    elif 'SOC' in self.header_map:
                        soc_col = 'SOC'
                    
                    if soc_col:
                        self.soc.append(float(row[self.header_map[soc_col]]))
                    
                    # Temperature
                    temp1_col = None
                    temp2_col = None
                    if 'afe_temp1' in self.header_map:
                        temp1_col = 'afe_temp1'
                    elif 'Temp1' in self.header_map:
                        temp1_col = 'Temp1'
                    
                    if 'afe_temp2' in self.header_map:
                        temp2_col = 'afe_temp2'
                    elif 'Temp2' in self.header_map:
                        temp2_col = 'Temp2'
                    
                    if temp1_col:
                        temp_raw = float(row[self.header_map[temp1_col]])
                        # Detect temperature format and convert appropriately
                        if temp_raw > 1000:  # Raw Kelvin×10 format (e.g., 3030 for ~30°C)
                            if SCALE_FUNCTIONS_AVAILABLE:
                                temp_scaled = scale_temperature(temp_raw, self.temp_unit)
                            else:
                                kelvin = temp_raw / 10.0
                                celsius = kelvin - 273.15
                                temp_scaled = celsius * 9/5 + 32 if self.temp_unit == 'F' else celsius
                        elif temp_raw > 200:  # Kelvin format (e.g., 303 for ~30°C)
                            celsius = temp_raw - 273.15
                            temp_scaled = celsius * 9/5 + 32 if self.temp_unit == 'F' else celsius
                        else:  # Already in Celsius format
                            temp_scaled = temp_raw * 9/5 + 32 if self.temp_unit == 'F' else temp_raw
                        self.temperature1.append(temp_scaled)
                    
                    if temp2_col:
                        temp_raw = float(row[self.header_map[temp2_col]])
                        # Detect temperature format and convert appropriately
                        if temp_raw > 1000:  # Raw Kelvin×10 format (e.g., 3030 for ~30°C)
                            if SCALE_FUNCTIONS_AVAILABLE:
                                temp_scaled = scale_temperature(temp_raw, self.temp_unit)
                            else:
                                kelvin = temp_raw / 10.0
                                celsius = kelvin - 273.15
                                temp_scaled = celsius * 9/5 + 32 if self.temp_unit == 'F' else celsius
                        elif temp_raw > 200:  # Kelvin format (e.g., 303 for ~30°C)
                            celsius = temp_raw - 273.15
                            temp_scaled = celsius * 9/5 + 32 if self.temp_unit == 'F' else celsius
                        else:  # Already in Celsius format
                            temp_scaled = temp_raw * 9/5 + 32 if self.temp_unit == 'F' else temp_raw
                        self.temperature2.append(temp_scaled)
                    
                    row_count += 1
                    self.stats['record_count'] = row_count
                
                self.last_row_count = row_count
                
                print(f"Loaded {row_count} records from historical data")
                
                # Update statistics
                self.update_statistics()
                
                # Plot all data
                self.plot_all_data()
                
        except Exception as e:
            print(f"Error loading historical data: {e}")
    
    def plot_all_data(self):
        """Plot all historical data at once"""
        if len(self.timestamps) < 2:
            print("Not enough data to plot")
            return
        
        time_data = list(self.timestamps)
        
        # Update cell voltage lines and text labels
        for i, (cell, line) in enumerate(self.cell_lines.items(), 1):
            if self.cell_voltages[cell]:
                line.set_data(time_data, list(self.cell_voltages[cell]))
                # Update text label with peak delta voltage if available, otherwise final voltage
                if self.peak_delta_cell_voltages[cell] > 0:
                    peak_voltage = self.peak_delta_cell_voltages[cell]
                    self.cell_texts[cell].set_text(f'Cell {i}: {peak_voltage:.3f}V (peak Δ)')
                else:
                    final_voltage = self.cell_voltages[cell][-1]
                    self.cell_texts[cell].set_text(f'Cell {i}: {final_voltage:.3f}V')
        
        # Update other lines
        if self.pack_voltage:
            self.pack_line.set_data(time_data, list(self.pack_voltage))
        if self.current:
            self.current_line.set_data(time_data, list(self.current))
        if self.cell_delta:
            self.delta_line.set_data(time_data, list(self.cell_delta))
        if self.soc:
            self.soc_line.set_data(time_data, list(self.soc))
        if self.temperature1:
            self.temp1_line.set_data(time_data, list(self.temperature1))
        if self.temperature2:
            self.temp2_line.set_data(time_data, list(self.temperature2))
        
        # Adjust axes limits
        for ax in [self.ax_cells, self.ax_pack, self.ax_current, 
                  self.ax_delta, self.ax_soc, self.ax_temp]:
            ax.relim()
            ax.autoscale_view()
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            # Apply 3 decimal place formatting for voltage plots
            if ax in [self.ax_cells, self.ax_pack]:
                from matplotlib.ticker import FormatStrFormatter
                ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
        
        # Update statistics text
        self.update_stats_display()
        
        # Redraw
        plt.draw()
    
    def update_statistics(self):
        """Update statistics from current data"""
        if len(self.timestamps) > 0:
            # Cell voltage statistics - get latest value from each cell
            current_cell_voltages = []
            for cell_data in self.cell_voltages.values():
                if cell_data:
                    current_cell_voltages.append(cell_data[-1])  # Get most recent value from each cell
            
            if current_cell_voltages:
                self.stats['min_cell_voltage'] = min(current_cell_voltages)
                self.stats['max_cell_voltage'] = max(current_cell_voltages)
                self.stats['avg_cell_voltage'] = sum(current_cell_voltages) / len(current_cell_voltages)
            
            # Current values
            if self.cell_delta:
                self.stats['cell_delta_current'] = self.cell_delta[-1]
            if self.pack_voltage:
                self.stats['pack_voltage_current'] = self.pack_voltage[-1]
            if self.current:
                self.stats['current_current'] = self.current[-1]
            if self.soc:
                self.stats['soc_current'] = self.soc[-1]
            if self.temperature1:
                self.stats['temp1_current'] = self.temperature1[-1]
            if self.temperature2:
                self.stats['temp2_current'] = self.temperature2[-1]
            
            # Duration
            if len(self.timestamps) > 1:
                self.stats['logging_duration'] = self.timestamps[-1] - self.timestamps[0]
    
    def update_stats_display(self):
        """Update the statistics display text"""
        # Build metadata info string
        metadata_info = ""
        if self.metadata:
            session = self.metadata.get('session', {})
            if session.get('baudrate'):
                metadata_info = f"Baudrate: {session['baudrate']} | "
            if self.metadata.get('logging', {}).get('interval'):
                metadata_info += f"Interval: {self.metadata['logging']['interval']}s | "
            if self.metadata.get('logging', {}).get('filter_enabled'):
                metadata_info += "Filter: ON"
            else:
                metadata_info += "Filter: OFF"
        
        # Update statistics text in horizontal layout
        stats_str = f"Port: {self.com_port} | Serial: {self.serial_number} | RMA: {self.rma_number}"
        
        # Add WebSocket connection status
        if self.websocket_url:
            connection_info = self.data_source_manager.get_connection_info()
            mode_display = connection_info['mode'].upper()
            if connection_info['mode'] == 'websocket':
                ws_info = connection_info.get('websocket_info', {})
                if ws_info.get('connected', False):
                    status_text = f"WebSocket CONNECTED"
                else:
                    reconnect_count = ws_info.get('reconnect_count', 0)
                    status_text = f"WebSocket RECONNECTING ({reconnect_count}/30)"
            elif connection_info['mode'] == 'fallback':
                status_text = "CSV FALLBACK MODE"
            else:
                status_text = "CSV MODE"
            
            stats_str += f" | {status_text}"
        
        if metadata_info:
            stats_str += f" | {metadata_info}"
            
        # Add peak delta info if available
        peak_info = ""
        if self.peak_delta_value > 0:
            peak_time_str = self.peak_delta_timestamp.strftime("%H:%M:%S") if self.peak_delta_timestamp else "Unknown"
            peak_info = f" | Peak Δ: {self.peak_delta_value:.1f}mV @ {peak_time_str}"
            
        stats_str += (
            f"\nRecords: {self.stats['record_count']:,} | Duration: {str(self.stats['logging_duration']).split('.')[0]} | "
            f"Pack V: {self.stats['pack_voltage_current']:.2f}V | Current: {self.stats['current_current']:.2f}A | "
            f"Cell Δ: {self.stats['cell_delta_current']:.1f}mV | SOC: {self.stats['soc_current']:.1f}%{peak_info}\n"
            f"Temp1: {self.stats['temp1_current']:.1f}°{self.temp_unit} | Temp2: {self.stats['temp2_current']:.1f}°{self.temp_unit} | "
            f"Min Cell: {self.stats['min_cell_voltage']:.3f}V | Max Cell: {self.stats['max_cell_voltage']:.3f}V | "
            f"Avg Cell: {self.stats['avg_cell_voltage']:.3f}V"
        )
        self.stats_text.set_text(stats_str)
        
        # Color code cell delta based on peak value
        peak_or_current = max(self.peak_delta_value, self.stats['cell_delta_current'])
        if peak_or_current > 50:
            self.ax_delta.set_facecolor('#3d1111')  # Dark red background
        elif peak_or_current > 30:
            self.ax_delta.set_facecolor('#3d3311')  # Dark yellow background
        else:
            self.ax_delta.set_facecolor('#1e1e1e')  # Normal background
    
    def update_plots(self, frame):
        """Update all plots with new data - optimized for performance"""
        # Read new data
        if not self.read_new_data():
            return
        
        # Update statistics
        self.update_statistics()
        
        # Increment update counter for optimization
        self._update_counter += 1
        
        # Convert timestamps for plotting
        if len(self.timestamps) > 1:
            time_data = list(self.timestamps)
            
            # Update cell voltage lines and text labels
            for i, (cell, line) in enumerate(self.cell_lines.items(), 1):
                if self.cell_voltages[cell]:
                    line.set_data(time_data, list(self.cell_voltages[cell]))
                    # Update text label with current voltage
                    current_voltage = self.cell_voltages[cell][-1]
                    self.cell_texts[cell].set_text(f'Cell {i}: {current_voltage:.3f}V')
            
            # Update other lines
            if self.pack_voltage:
                self.pack_line.set_data(time_data, list(self.pack_voltage))
            if self.current:
                self.current_line.set_data(time_data, list(self.current))
            if self.cell_delta:
                self.delta_line.set_data(time_data, list(self.cell_delta))
            if self.soc:
                self.soc_line.set_data(time_data, list(self.soc))
            if self.temperature1:
                self.temp1_line.set_data(time_data, list(self.temperature1))
            if self.temperature2:
                self.temp2_line.set_data(time_data, list(self.temperature2))
            
            # Optimize axis updates - only full update every N iterations
            if self._update_counter % self._plot_update_interval == 0:
                # Full axis update with formatting
                for ax in [self.ax_cells, self.ax_pack, self.ax_current, 
                          self.ax_delta, self.ax_soc, self.ax_temp]:
                    ax.relim()
                    ax.autoscale_view()
                    
                    # Format x-axis
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
                    
                    # Force 3 decimal places for voltage plots (replaces ticklabel_format)
                    if ax in [self.ax_cells, self.ax_pack]:
                        from matplotlib.ticker import FormatStrFormatter
                        ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
            else:
                # Quick update without formatting overhead
                for ax in [self.ax_cells, self.ax_pack, self.ax_current, 
                          self.ax_delta, self.ax_soc, self.ax_temp]:
                    try:
                        ax.relim()
                        ax.autoscale_view(tight=True)
                    except:
                        pass  # Skip if axis update fails
        
        # Update statistics display
        self.update_stats_display()
        
        # Force early auto-scaling after first few data points for immediate usability
        if len(self.timestamps) == 5:  # After 5 data points (~2.5 seconds)
            self.set_smart_axis_limits()
        
        # Force GUI refresh
        try:
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        except:
            pass
        
        # Check for peak cell delta and capture screenshot if enabled
        self.check_peak_delta_for_screenshot()
    
    def set_smart_axis_limits(self):
        """Set smart axis limits based on actual data with margins for edge cases"""
        try:
            if len(self.timestamps) < 2:
                return
                
            # Cell voltages - adjust based on actual data but keep safety margins
            if any(self.cell_voltages.values()):
                all_cell_values = [v for voltages in self.cell_voltages.values() for v in voltages if voltages]
                if all_cell_values:
                    min_v, max_v = min(all_cell_values), max(all_cell_values)
                    # Add 10% margin but keep within safety bounds (2.0V-4.2V)
                    margin = max((max_v - min_v) * 0.1, 0.05)  # Minimum 50mV margin
                    new_min = max(2.0, min_v - margin)  # Don't go below 2.0V
                    new_max = min(4.2, max_v + margin)  # Don't go above 4.2V
                    self.ax_cells.set_ylim(new_min, new_max)
            
            # Pack voltage - adjust based on actual data
            if self.pack_voltage:
                min_v, max_v = min(self.pack_voltage), max(self.pack_voltage)
                margin = max((max_v - min_v) * 0.1, 0.5)  # Minimum 0.5V margin
                new_min = max(22.0, min_v - margin)  # Don't go below 22V
                new_max = min(29.0, max_v + margin)  # Don't go above 29V
                self.ax_pack.set_ylim(new_min, new_max)
            
            # Current - adjust based on actual data
            if self.current:
                min_i, max_i = min(self.current), max(self.current)
                margin = max(abs(max_i - min_i) * 0.1, 1.0)  # Minimum 1A margin
                self.ax_current.set_ylim(min_i - margin, max_i + margin)
            
            # Cell delta - adjust based on actual data
            if self.cell_delta:
                max_delta = max(self.cell_delta)
                # Set upper limit to 110% of max delta or minimum 50mV
                new_max = max(max_delta * 1.1, 50)
                self.ax_delta.set_ylim(0, new_max)
            
            # Temperature - adjust based on actual data
            if self.temperature1 or self.temperature2:
                all_temps = []
                if self.temperature1:
                    all_temps.extend(self.temperature1)
                if self.temperature2:
                    all_temps.extend(self.temperature2)
                if all_temps:
                    min_t, max_t = min(all_temps), max(all_temps)
                    margin = max((max_t - min_t) * 0.1, 2.0)  # Minimum 2°C margin
                    self.ax_temp.set_ylim(min_t - margin, max_t + margin)
                    
        except Exception as e:
            # If smart scaling fails, keep the initial sensible ranges
            print(f"Smart axis scaling failed: {e}")
    
    def check_peak_delta_for_screenshot(self):
        """Check for peak cell delta and capture screenshot data"""
        if not self.screenshot_enabled or len(self.cell_delta) < 2:
            return
        
        current_delta = self.cell_delta[-1]
        current_current = self.current[-1] if self.current else 0
        
        with self.screenshot_lock:
            # Check for current cutoff event (BMS protection activation)
            if (self.detect_current_cutoff and self.previous_current is not None and 
                abs(self.previous_current) > self.current_cutoff_threshold and 
                abs(current_current) < self.current_cutoff_threshold):
                
                self.current_cutoff_detected = True
                current_direction = "Charge" if self.previous_current > 0 else "Discharge"
                print(f"\nCURRENT CUTOFF DETECTED ({current_direction}): {self.previous_current:.1f}A → {current_current:.1f}A")
                print(f"   Cell Delta at cutoff: {current_delta:.1f}mV")
                
                # If we weren't already tracking a peak, start now
                if not self.peak_detected:
                    self.peak_detected = True
                    self.peak_detection_time = datetime.now()
                    self.recovery_data = []
                    print(f"   Starting {self.recovery_time_seconds}-second recovery capture after current cutoff...")
            
            # Standard peak detection
            elif not self.peak_detected and current_delta >= self.peak_delta_threshold:
                # Peak detected!
                self.peak_detected = True
                self.peak_detection_time = datetime.now()
                self.recovery_data = []
                cutoff_msg = " (with current cutoff)" if self.current_cutoff_detected else ""
                print(f"\nPEAK CELL DELTA DETECTED: {current_delta:.1f}mV at {self.peak_detection_time.strftime('%H:%M:%S')}{cutoff_msg}")
                print(f"Starting {self.recovery_time_seconds}-second recovery capture...")
            
            # Collect recovery data if we're tracking a peak
            if self.peak_detected and self.peak_detection_time:
                time_since_peak = datetime.now() - self.peak_detection_time
                
                if time_since_peak.total_seconds() <= self.recovery_time_seconds:
                    # Still in recovery period - collect data
                    recovery_point = {
                        'timestamp': self.timestamps[-1] if self.timestamps else datetime.now(),
                        'cell_delta': current_delta,
                        'cell_voltages': {cell: deque(maxlen=1) for cell in self.cell_voltages},
                        'pack_voltage': self.pack_voltage[-1] if self.pack_voltage else 0,
                        'current': current_current,
                        'soc': self.soc[-1] if self.soc else 0,
                        'temperature1': self.temperature1[-1] if self.temperature1 else 0,
                        'temperature2': self.temperature2[-1] if self.temperature2 else 0,
                        'current_cutoff': self.current_cutoff_detected
                    }
                    
                    # Copy current cell voltages
                    for cell in self.cell_voltages:
                        if self.cell_voltages[cell]:
                            recovery_point['cell_voltages'][cell].append(self.cell_voltages[cell][-1])
                    
                    self.recovery_data.append(recovery_point)
                else:
                    # Recovery period complete - take screenshot
                    self.capture_peak_recovery_screenshot()
                    # Reset for next detection
                    self.peak_detected = False
                    self.peak_detection_time = None
                    self.recovery_data = []
                    self.current_cutoff_detected = False
        
        # Update previous current for next iteration
        self.previous_current = current_current
    
    def capture_peak_recovery_screenshot(self):
        """Capture screenshot showing peak cell delta and recovery period"""
        if not self.recovery_data:
            print("No recovery data available for screenshot")
            return
        
        try:
            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Get peak delta value
            peak_delta = max(point['cell_delta'] for point in self.recovery_data)
            
            # Determine screenshot directory based on existing structure
            screenshot_dir = self.get_screenshot_directory()
            
            # Create filename
            filename = f"peak_delta_screenshot_{timestamp}_{self.serial_number}_{self.rma_number}_peak{peak_delta:.0f}mV.png"
            screenshot_path = screenshot_dir / filename
            
            # Save current figure
            self.fig.savefig(screenshot_path, dpi=300, bbox_inches='tight', 
                           facecolor=self.fig.get_facecolor(), edgecolor='none')
            
            # Calculate recovery metrics
            start_delta = self.recovery_data[0]['cell_delta'] if self.recovery_data else peak_delta
            end_delta = self.recovery_data[-1]['cell_delta'] if self.recovery_data else peak_delta
            recovery_amount = start_delta - end_delta
            recovery_percent = (recovery_amount / start_delta * 100) if start_delta > 0 else 0
            
            # Check if current cutoff occurred
            current_cutoff_event = any(point.get('current_cutoff', False) for point in self.recovery_data)
            cutoff_info = " (BMS Protection Activated)" if current_cutoff_event else ""
            
            print(f"\nSCREENSHOT CAPTURED: {filename}")
            print(f"   Peak Delta: {peak_delta:.1f}mV{cutoff_info}")
            print(f"   Recovery: {recovery_amount:.1f}mV ({recovery_percent:.1f}%)")
            print(f"   Duration: {self.recovery_time_seconds}s")
            if current_cutoff_event:
                start_current = self.recovery_data[0]['current'] if self.recovery_data else 0
                end_current = self.recovery_data[-1]['current'] if self.recovery_data else 0
                current_type = "Charge" if start_current > 0 else "Discharge"
                print(f"   Current Change ({current_type}): {start_current:.1f}A → {end_current:.1f}A")
            print(f"   Saved to: {screenshot_path}")
            print(f"   Data points captured: {len(self.recovery_data)}\n")
            
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
    
    def enable_screenshot_feature(self, threshold_mv: float = 50.0, recovery_seconds: int = 10, detect_cutoff: bool = True):
        """Enable the screenshot feature with specified parameters"""
        self.screenshot_enabled = True
        self.peak_delta_threshold = threshold_mv
        self.recovery_time_seconds = recovery_seconds
        self.detect_current_cutoff = detect_cutoff
        screenshot_dir = self.get_screenshot_directory()
        print(f"\nScreenshot feature ENABLED")
        print(f"   Peak threshold: {threshold_mv}mV")
        print(f"   Recovery time: {recovery_seconds}s")
        print(f"   Current cutoff detection: {'ON' if detect_cutoff else 'OFF'}")
        print(f"   Screenshots will be saved to: {screenshot_dir}\n")
    
    def get_screenshot_directory(self) -> Path:
        """Determine the appropriate screenshot directory based on existing structure"""
        csv_path = self.csv_file_path
        
        # Check if we're in the P3E-Report/test-artifacts structure
        if 'P3E-Report' in str(csv_path) and 'test-artifacts' in str(csv_path):
            # Try to find the serial number directory
            path_parts = csv_path.parts
            if 'test-artifacts' in path_parts:
                artifacts_index = path_parts.index('test-artifacts')
                if artifacts_index + 1 < len(path_parts):
                    serial_dir = Path(*path_parts[:artifacts_index + 2])  # Include serial number folder
                    screenshot_dir = serial_dir / 'screenshots'
                    if screenshot_dir.exists():
                        return screenshot_dir
                    else:
                        # Create screenshots directory in serial number folder
                        screenshot_dir.mkdir(exist_ok=True)
                        return screenshot_dir
        
        # Check if we're in a session-based structure (data/sessions/session-xxx)
        if 'data' in str(csv_path) and 'sessions' in str(csv_path):
            # Look for session directory
            path_parts = csv_path.parts
            for i, part in enumerate(path_parts):
                if part.startswith('session-'):
                    session_dir = Path(*path_parts[:i + 1])
                    screenshot_dir = session_dir / 'screenshots'
                    screenshot_dir.mkdir(exist_ok=True)
                    return screenshot_dir
        
        # Default: create screenshots directory next to CSV file
        screenshot_dir = csv_path.parent / 'screenshots'
        screenshot_dir.mkdir(exist_ok=True)
        return screenshot_dir
    
    def disable_screenshot_feature(self):
        """Disable the screenshot feature"""
        self.screenshot_enabled = False
        self.peak_detected = False
        self.peak_detection_time = None
        self.recovery_data = []
        print("Screenshot feature DISABLED")
    
    def cleanup(self):
        """Clean up resources, including WebSocket connections"""
        try:
            if hasattr(self, 'data_source_manager') and self.data_source_manager:
                self.data_source_manager.stop()
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")
    
    def run(self):
        """Run the dashboard"""
        if self.historical_mode:
            if self.export_screenshot:
                print(f"Loading historical data from: {self.csv_file}")
                print(f"Exporting screenshot to: {self.export_screenshot}")
                
                # Set backend for headless operation if needed
                if self.headless:
                    import matplotlib
                    matplotlib.use('Agg')  # Non-interactive backend
                
                # Save the figure instead of showing it
                self.fig.savefig(self.export_screenshot, dpi=300, bbox_inches='tight', 
                               facecolor='white', edgecolor='none')
                print(f"✓ Screenshot exported successfully!")
                return
            else:
                print(f"Displaying historical data from: {self.csv_file}")
                
                # Show historical data plot
                print("Close window to exit...")
                try:
                    plt.show()
                except Exception as e:
                    print(f"GUI failed: {e}, saving plot instead...")
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    plot_file = f"dashboard_plot_{timestamp}.png"
                    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
                    print(f"Plot saved as: {plot_file}")
        else:
            print(f"Starting real-time dashboard for: {self.csv_file}")
            print("Press Ctrl+C to stop...")
            
            # Create animation for real-time updates with optimizations
            self.ani = animation.FuncAnimation(self.fig, self.update_plots, 
                                        interval=self.update_interval,
                                        blit=False, cache_frame_data=False,
                                        repeat=True, save_count=1)
            
            # Force initial draw
            self.fig.canvas.draw()
            
            try:
                # Show GUI dashboard
                print("Displaying GUI dashboard...")
                try:
                    plt.show()
                except Exception as e:
                    print(f"GUI failed: {e}")
                    print("Falling back to background mode...")
                    try:
                        while True:
                            time.sleep(1.0)
                    except KeyboardInterrupt:
                        print("\nStopping dashboard...")
            finally:
                # Clean up WebSocket connections
                self.cleanup()


def find_latest_csv(directory: Path, serial_number: str = None, rma_number: str = None) -> Optional[Path]:
    """Find the latest CSV file in directory"""
    csv_files = list(directory.glob("*.csv"))
    
    if serial_number and rma_number:
        # Filter by serial and RMA
        pattern = f"*-{serial_number}-{rma_number}.csv"
        csv_files = list(directory.glob(pattern))
    
    if not csv_files:
        return None
    
    # Return most recent file
    return max(csv_files, key=lambda f: f.stat().st_mtime)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Real-time Dashboard for Standalone Modbus Logger",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor specific CSV file (real-time)
  python modbus_dashboard.py data.csv
  
  # View historical CSV file (no real-time updates)
  python modbus_dashboard.py data.csv --historical
  
  # Monitor latest CSV in directory
  python modbus_dashboard.py --dir C:\\Data\\BMS_Logs
  
  # Monitor specific serial/RMA
  python modbus_dashboard.py --dir C:\\Data\\BMS_Logs --sn 0520 --rma 8765
  
  # Custom update interval
  python modbus_dashboard.py data.csv --interval 500
  
  # View historical data with metadata
  python modbus_dashboard.py historical_log.csv --historical --port COM3
  
  # View historical charge session data
  python modbus_dashboard.py charge_data.csv --historical --session-type charge
  
  # Monitor with WebSocket connection (real-time)
  python modbus_dashboard.py data.csv --websocket ws://localhost:8765
  
  # WebSocket with CSV fallback
  python modbus_dashboard.py data.csv --websocket ws://localhost:8765 --websocket-fallback
        """
    )
    
    parser.add_argument('csv_file', nargs='?', help='CSV file to monitor')
    parser.add_argument('--dir', help='Directory to search for latest CSV')
    parser.add_argument('--sn', '--serial-number', help='Serial number filter')
    parser.add_argument('--rma', '--rma-number', help='RMA number filter')
    parser.add_argument('--interval', type=int, default=1000, 
                       help='Update interval in milliseconds (default: 1000)')
    parser.add_argument('--port', help='COM port being used (e.g., COM3, /dev/ttyUSB0)')
    parser.add_argument('--historical', action='store_true', 
                       help='View historical data (no real-time updates)')
    parser.add_argument('--screenshot', action='store_true', 
                       help='Enable automatic screenshot capture on peak cell delta events')
    parser.add_argument('--peak-threshold', type=float, default=50.0,
                       help='Cell delta threshold in mV for peak detection (default: 50)')
    parser.add_argument('--recovery-time', type=int, default=10,
                       help='Recovery time in seconds to capture after peak (default: 10)')
    parser.add_argument('--no-cutoff-detection', action='store_true',
                       help='Disable automatic current cutoff detection (BMS protection events)')
    parser.add_argument('--fast-mode', action='store_true',
                       help='Enable fast mode with reduced visual updates for better performance')
    parser.add_argument('--max-points', type=int, default=300,
                       help='Maximum data points to display (default: 300, lower = faster)')
    parser.add_argument('--session-type', choices=['charge', 'discharge', 'root'], 
                       help='Session type for display in title (charge, discharge, or root)')
    parser.add_argument('--export-screenshot', help='Export screenshot to specified file path (requires --historical)')
    parser.add_argument('--no-gui', action='store_true', help='Run in headless mode for screenshot export')
    parser.add_argument('--no-current-filter', action='store_true', 
                       help='Disable current spike filtering')
    parser.add_argument('--current-spike-threshold', type=float, default=50.0,
                       help='Current spike threshold in amperes (default: 50.0)')
    parser.add_argument('--websocket', '--websocket-url', dest='websocket_url',
                       help='WebSocket server URL (e.g., ws://localhost:8765) for real-time data')
    parser.add_argument('--websocket-fallback', '--fallback-csv', dest='fallback_csv', action='store_true',
                       help='Enable CSV fallback when WebSocket connection fails (default behavior)')
    
    args = parser.parse_args()
    
    # Validate export screenshot arguments
    if args.export_screenshot and not args.historical:
        print("Error: --export-screenshot requires --historical mode")
        return 1
    
    # Check dependencies
    if not MATPLOTLIB_AVAILABLE:
        print("Error: matplotlib is required. Install with: pip install matplotlib")
        return 1
    
    if not NUMPY_AVAILABLE:
        print("Error: numpy is required. Install with: pip install numpy")
        return 1
    
    # Find CSV file
    csv_file = None
    
    if args.csv_file:
        csv_file = Path(args.csv_file)
    elif args.dir:
        directory = Path(args.dir)
        if not directory.exists():
            print(f"Error: Directory not found: {directory}")
            return 1
        
        csv_file = find_latest_csv(directory, args.sn, args.rma)
        if not csv_file:
            print(f"Error: No CSV files found in {directory}")
            if args.sn and args.rma:
                print(f"  Looking for pattern: *-{args.sn}-{args.rma}.csv")
            return 1
    else:
        print("Error: Specify either a CSV file or --dir option")
        return 1
    
    if not csv_file.exists():
        print(f"Error: CSV file not found: {csv_file}")
        return 1
    
    # Validate WebSocket availability
    websocket_url = args.websocket_url
    if websocket_url and not WEBSOCKET_AVAILABLE:
        print("Warning: WebSocket functionality requested but websockets library not available.")
        print("Install with: pip install websockets")
        print("Falling back to CSV-only mode.")
        websocket_url = None
    
    # Create and run dashboard
    try:
        dashboard = ModbusDashboard(str(csv_file), 
                                  update_interval=args.interval, 
                                  com_port=args.port,
                                  historical_mode=args.historical,
                                  session_type=args.session_type,
                                  export_screenshot=args.export_screenshot,
                                  headless=args.no_gui,
                                  websocket_url=websocket_url)
        
        # Apply performance optimizations
        if args.fast_mode:
            dashboard._plot_update_interval = 10  # Update plots less frequently
            print("Fast mode enabled - reduced visual updates for better performance")
        
        if args.max_points != 300:
            # Adjust deque maxlen for real-time mode
            if not dashboard.historical_mode:
                for cell in dashboard.cell_voltages:
                    dashboard.cell_voltages[cell] = deque(dashboard.cell_voltages[cell], maxlen=args.max_points)
                dashboard.pack_voltage = deque(dashboard.pack_voltage, maxlen=args.max_points)
                dashboard.current = deque(dashboard.current, maxlen=args.max_points)
                dashboard.cell_delta = deque(dashboard.cell_delta, maxlen=args.max_points)
                dashboard.soc = deque(dashboard.soc, maxlen=args.max_points)
                dashboard.temperature1 = deque(dashboard.temperature1, maxlen=args.max_points)
                dashboard.temperature2 = deque(dashboard.temperature2, maxlen=args.max_points)
                dashboard.timestamps = deque(dashboard.timestamps, maxlen=args.max_points)
                print(f"Display limited to {args.max_points} data points for better performance")
        
        # Configure current filtering
        if args.no_current_filter:
            dashboard.current_filter_enabled = False
            print("Current spike filtering DISABLED")
        else:
            dashboard.current_spike_threshold = args.current_spike_threshold
            print(f"Current spike filtering enabled (threshold: {args.current_spike_threshold}A)")
        
        # Enable screenshot feature if requested
        if args.screenshot:
            dashboard.enable_screenshot_feature(args.peak_threshold, args.recovery_time, 
                                               not args.no_cutoff_detection)
        
        dashboard.run()
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")
        try:
            dashboard.cleanup()
        except:
            pass
    except Exception as e:
        print(f"Error: {e}")
        try:
            dashboard.cleanup()
        except:
            pass
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())