#!/usr/bin/env python3
"""
Simple Python WebSocket client for testing Modbus data streaming
"""

import asyncio
import websockets
import json
import argparse
from datetime import datetime

async def websocket_client(uri, duration=None):
    """Connect to WebSocket server and receive data"""
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✓ Connected successfully!")
            print("Waiting for data... (Press Ctrl+C to stop)")
            print("-" * 60)
            
            message_count = 0
            start_time = datetime.now()
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_count += 1
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    if data.get('type') == 'connection':
                        print(f"[{timestamp}] Server: {data.get('message', 'Connected')}")
                    
                    elif data.get('type') == 'data':
                        # Extract session info
                        session = data.get('data', {}).get('session', {})
                        modbus_data = data.get('data', {}).get('modbus_data', {})
                        
                        print(f"[{timestamp}] Data #{message_count}")
                        print(f"  Serial: {session.get('serial_number', 'N/A')}")
                        print(f"  Records: {session.get('record_count', 'N/A')}")
                        
                        # Display key Modbus parameters
                        key_params = [
                            'afe_pack_volt', 'afe_pack_current', 'afe_soc',
                            'afe_cell_volt_max', 'afe_cell_volt_min', 'afe_cell_volt_delta',
                            'afe_temp_max', 'afe_temp_min'
                        ]
                        
                        for param in key_params:
                            if param in modbus_data:
                                value = modbus_data[param]
                                unit = get_unit(param)
                                print(f"  {param.replace('_', ' ').title()}: {value} {unit}")
                        
                        print("-" * 60)
                    
                    else:
                        print(f"[{timestamp}] Unknown message type: {data.get('type')}")
                    
                    # Check duration limit
                    if duration:
                        elapsed = (datetime.now() - start_time).total_seconds()
                        if elapsed >= duration:
                            print(f"\nDuration limit reached ({duration}s). Disconnecting...")
                            break
                            
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
                    print(f"Raw message: {message}")
                except Exception as e:
                    print(f"Error processing message: {e}")
    
    except websockets.exceptions.ConnectionRefused:
        print("✗ Connection refused. Is the WebSocket server running?")
    except websockets.exceptions.InvalidURI:
        print("✗ Invalid WebSocket URI")
    except KeyboardInterrupt:
        print("\n\nDisconnected by user")
    except Exception as e:
        print(f"✗ Connection error: {e}")

def get_unit(param):
    """Get appropriate unit for parameter"""
    units = {
        'afe_cell_volt_delta': 'mV',
        'afe_cell_volt_max': 'mV',
        'afe_cell_volt_min': 'mV',
        'afe_cell_volt_avg': 'mV',
        'afe_pack_volt': 'mV',
        'afe_pack_current': 'mA',
        'afe_soc': '%',
        'afe_temp_max': '°C',
        'afe_temp_min': '°C',
        'afe_temp_avg': '°C'
    }
    return units.get(param, '')

def main():
    parser = argparse.ArgumentParser(description='WebSocket client for Modbus data streaming')
    parser.add_argument('--host', default='localhost', help='WebSocket server host')
    parser.add_argument('--port', type=int, default=8765, help='WebSocket server port')
    parser.add_argument('--duration', type=int, help='Connection duration in seconds')
    
    args = parser.parse_args()
    
    uri = f"ws://{args.host}:{args.port}"
    
    print("🔋 Modbus WebSocket Python Client")
    print("=" * 40)
    print(f"Server: {uri}")
    if args.duration:
        print(f"Duration: {args.duration} seconds")
    print()
    
    # Run the client
    asyncio.run(websocket_client(uri, args.duration))

if __name__ == "__main__":
    main()