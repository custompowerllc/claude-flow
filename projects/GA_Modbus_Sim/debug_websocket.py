#!/usr/bin/env python3
"""
WebSocket Debug Script - More detailed diagnostics
"""

import asyncio
import websockets
import json
import time
from datetime import datetime

async def debug_websocket_connection():
    """Debug WebSocket connection with detailed logging"""
    url = "ws://localhost:8765"
    
    print(f"🔍 DEBUG: Attempting to connect to {url}")
    
    try:
        # Connect with extended timeout and detailed logging
        print(f"🔍 DEBUG: Creating WebSocket connection...")
        
        async with websockets.connect(
            url, 
            ping_interval=None,  # Disable ping for debugging
            ping_timeout=None,   # Disable ping timeout
            close_timeout=10,    # 10 second close timeout
            max_size=2**20,      # 1MB max message size
            max_queue=32         # Max queue size
        ) as websocket:
            
            print(f"✅ DEBUG: WebSocket connected successfully!")
            print(f"🔍 DEBUG: WebSocket state: {websocket.state}")
            print(f"🔍 DEBUG: WebSocket remote address: {websocket.remote_address}")
            print(f"🔍 DEBUG: WebSocket local address: {websocket.local_address}")
            
            # Wait for welcome message
            print(f"🔍 DEBUG: Waiting for welcome message...")
            
            try:
                # Wait for the first message with timeout
                welcome_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"✅ DEBUG: Received welcome message: {welcome_message}")
                
                try:
                    welcome_data = json.loads(welcome_message)
                    print(f"🔍 DEBUG: Welcome message type: {welcome_data.get('type')}")
                    print(f"🔍 DEBUG: Welcome message content: {welcome_data}")
                except json.JSONDecodeError as e:
                    print(f"⚠️ DEBUG: Welcome message is not valid JSON: {e}")
                
                # Now listen for more messages
                print(f"🔍 DEBUG: Listening for data messages for 10 seconds...")
                
                message_count = 0
                start_time = time.time()
                
                while time.time() - start_time < 10.0:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        message_count += 1
                        
                        print(f"✅ DEBUG: Message {message_count} received at {datetime.now().strftime('%H:%M:%S')}")
                        
                        try:
                            data = json.loads(message)
                            msg_type = data.get('type', 'unknown')
                            print(f"🔍 DEBUG: Message type: {msg_type}")
                            
                            if msg_type == 'data':
                                # Print some key data points
                                payload = data.get('data', {})
                                if 'modbus_data' in payload:
                                    modbus_data = payload['modbus_data']
                                    pack_volt = modbus_data.get('afe_pack_volt', 'N/A')
                                    cell_delta = modbus_data.get('afe_cell_volt_delta', 'N/A')
                                    print(f"🔍 DEBUG: Pack voltage: {pack_volt}, Cell delta: {cell_delta}")
                            
                        except json.JSONDecodeError:
                            print(f"⚠️ DEBUG: Message {message_count} is not valid JSON")
                            
                    except asyncio.TimeoutError:
                        print(f"⏱️ DEBUG: No message received in the last second...")
                        continue
                    except websockets.exceptions.ConnectionClosed as e:
                        print(f"❌ DEBUG: Connection closed during message listening: {e}")
                        break
                
                print(f"🔍 DEBUG: Finished listening. Total messages received: {message_count}")
                
            except asyncio.TimeoutError:
                print(f"⏱️ DEBUG: Timeout waiting for welcome message")
                print(f"🔍 DEBUG: WebSocket state after timeout: {websocket.state}")
                
            except websockets.exceptions.ConnectionClosed as e:
                print(f"❌ DEBUG: Connection closed while waiting for welcome message: {e}")
                print(f"🔍 DEBUG: Close code: {e.code}, Close reason: {e.reason}")
                
    except websockets.exceptions.InvalidURI as e:
        print(f"❌ DEBUG: Invalid WebSocket URI: {e}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ DEBUG: Connection closed during initial connection: {e}")
        print(f"🔍 DEBUG: Close code: {e.code}, Close reason: {e.reason}")
    except OSError as e:
        print(f"❌ DEBUG: OS Error (server not running?): {e}")
    except Exception as e:
        print(f"❌ DEBUG: Unexpected error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("🔍 Starting WebSocket Debug Session")
    print("="*60)
    
    try:
        asyncio.run(debug_websocket_connection())
    except KeyboardInterrupt:
        print("🔍 DEBUG: Debug session interrupted by user")
    except Exception as e:
        print(f"❌ DEBUG: Fatal error: {e}")
    
    print("="*60)
    print("🔍 Debug session complete")