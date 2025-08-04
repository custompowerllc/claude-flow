#!/usr/bin/env python3
"""
WebSocket Integration Test Script

This script provides comprehensive testing for the WebSocket integration between
the Modbus standalone logger and dashboard.

Author: Alan Hu
Company: Custom Power LLC
Date: August 4, 2025
"""

import asyncio
import websockets
import json
import time
import sys
import argparse
from datetime import datetime
from pathlib import Path
import threading
import queue
import signal
from typing import Dict, Any, List, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None


class WebSocketTester:
    """Comprehensive WebSocket integration tester"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.websocket = None
        self.connected = False
        self.message_count = 0
        self.error_count = 0
        self.test_results = []
        self.received_messages = queue.Queue()
        self.start_time = None
        self.running = False
        
        # Test statistics
        self.stats = {
            'connection_attempts': 0,
            'successful_connections': 0,
            'messages_received': 0,
            'data_messages': 0,
            'connection_messages': 0,
            'errors': 0,
            'disconnections': 0,
            'reconnections': 0,
            'last_message_time': None,
            'test_duration': 0
        }
        
        # Message validation
        self.expected_fields = {
            'data': ['type', 'timestamp', 'data'],
            'connection': ['type', 'status', 'message', 'timestamp']
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self._print_info("Test interrupted by user")
        self.stop_test()
        sys.exit(0)
    
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
    
    async def connect_to_server(self, url: str, timeout: float = 10.0) -> bool:
        """Connect to WebSocket server with timeout"""
        self.stats['connection_attempts'] += 1
        
        try:
            self._print_info(f"Connecting to {url}...")
            
            # Connect with timeout
            self.websocket = await asyncio.wait_for(
                websockets.connect(url, ping_interval=20, ping_timeout=10),
                timeout=timeout
            )
            
            self.connected = True
            self.stats['successful_connections'] += 1
            self._print_success(f"Connected to WebSocket server at {url}")
            return True
            
        except asyncio.TimeoutError:
            self._print_error(f"Connection timeout after {timeout}s")
            self.stats['errors'] += 1
            return False
        except Exception as e:
            self._print_error(f"Connection failed: {e}")
            self.stats['errors'] += 1
            return False
    
    async def listen_for_messages(self, duration: Optional[float] = None):
        """Listen for messages from the WebSocket server"""
        if not self.connected or not self.websocket:
            self._print_error("Not connected to WebSocket server")
            return
        
        self.running = True
        self.start_time = datetime.now()
        end_time = self.start_time.timestamp() + duration if duration else None
        
        self._print_info(f"Listening for messages{'...' if not duration else f' for {duration}s...'}")
        
        try:
            async for message in self.websocket:
                if not self.running:
                    break
                
                # Check duration limit
                if end_time and time.time() > end_time:
                    self._print_info(f"Test duration of {duration}s completed")
                    break
                
                await self.process_message(message)
                
        except websockets.exceptions.ConnectionClosed:
            self._print_warning("WebSocket connection closed by server")
            self.stats['disconnections'] += 1
        except Exception as e:
            self._print_error(f"Error receiving messages: {e}")
            self.stats['errors'] += 1
        finally:
            self.connected = False
            if self.start_time:
                self.stats['test_duration'] = (datetime.now() - self.start_time).total_seconds()
    
    async def process_message(self, message: str):
        """Process received WebSocket message"""
        try:
            # Parse JSON message
            data = json.loads(message)
            self.stats['messages_received'] += 1
            self.stats['last_message_time'] = datetime.now()
            
            # Validate message structure
            validation_result = self.validate_message(data)
            
            # Store message for analysis
            self.received_messages.put({
                'timestamp': datetime.now(),
                'message': data,
                'validation': validation_result
            })
            
            # Count message types
            msg_type = data.get('type', 'unknown')
            if msg_type == 'data':
                self.stats['data_messages'] += 1
            elif msg_type == 'connection':
                self.stats['connection_messages'] += 1
            
            # Print message summary
            if validation_result['valid']:
                self._print_success(f"Received {msg_type} message")
            else:
                self._print_error(f"Invalid {msg_type} message: {validation_result['errors']}")
                self.stats['errors'] += 1
            
            # Detailed logging for data messages
            if msg_type == 'data' and 'data' in data:
                modbus_data = data['data']
                if isinstance(modbus_data, dict) and 'modbus_data' in modbus_data:
                    registers = modbus_data['modbus_data']
                    self._print_info(f"  Modbus data: {len(registers)} registers received")
                    
                    # Sample key values for verification
                    if 'afe_pack_volt' in registers:
                        pack_volt = registers['afe_pack_volt']
                        self._print_info(f"  Pack voltage: {pack_volt}mV ({pack_volt/1000:.2f}V)")
                    
                    if 'afe_cell_volt_delta' in registers:
                        cell_delta = registers['afe_cell_volt_delta']
                        self._print_info(f"  Cell delta: {cell_delta}mV")
            
        except json.JSONDecodeError as e:
            self._print_error(f"Invalid JSON message: {e}")
            self.stats['errors'] += 1
        except Exception as e:
            self._print_error(f"Error processing message: {e}")
            self.stats['errors'] += 1
    
    def validate_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Validate WebSocket message structure"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check message type
        msg_type = message.get('type')
        if not msg_type:
            result['valid'] = False
            result['errors'].append("Missing 'type' field")
            return result
        
        # Validate based on message type
        if msg_type in self.expected_fields:
            expected = self.expected_fields[msg_type]
            for field in expected:
                if field not in message:
                    result['valid'] = False
                    result['errors'].append(f"Missing required field: {field}")
        
        # Additional validation for data messages
        if msg_type == 'data':
            if 'data' in message:
                data_payload = message['data']
                if isinstance(data_payload, dict):
                    # Check for expected modbus data structure
                    if 'modbus_data' in data_payload:
                        modbus_data = data_payload['modbus_data']
                        if not isinstance(modbus_data, dict):
                            result['warnings'].append("modbus_data is not a dictionary")
                        elif len(modbus_data) == 0:
                            result['warnings'].append("modbus_data is empty")
                    else:
                        result['warnings'].append("No modbus_data found in data payload")
                else:
                    result['warnings'].append("Data payload is not a dictionary")
        
        # Validate timestamp format
        if 'timestamp' in message:
            try:
                datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00'))
            except ValueError:
                result['warnings'].append("Invalid timestamp format")
        
        return result
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        if not self.start_time:
            return "No test data available"
        
        duration = self.stats['test_duration']
        success_rate = (self.stats['successful_connections'] / max(1, self.stats['connection_attempts'])) * 100
        
        report = f"""
WebSocket Integration Test Report
{'=' * 50}

Connection Statistics:
- Connection attempts: {self.stats['connection_attempts']}
- Successful connections: {self.stats['successful_connections']}
- Success rate: {success_rate:.1f}%
- Disconnections: {self.stats['disconnections']}

Message Statistics:
- Total messages received: {self.stats['messages_received']}
- Data messages: {self.stats['data_messages']}
- Connection messages: {self.stats['connection_messages']}
- Errors: {self.stats['errors']}

Performance Metrics:
- Test duration: {duration:.1f}s
- Messages per second: {(self.stats['messages_received'] / max(1, duration)):.2f}
- Last message received: {self.stats['last_message_time'].strftime('%H:%M:%S') if self.stats['last_message_time'] else 'None'}

Test Results:
"""
        
        # Add individual test results
        for i, result in enumerate(self.test_results, 1):
            status = "PASS" if result['success'] else "FAIL"
            report += f"- Test {i}: {result['name']} - {status}\n"
            if not result['success']:
                report += f"  Error: {result.get('error', 'Unknown error')}\n"
        
        return report
    
    def stop_test(self):
        """Stop the test gracefully"""
        self.running = False
        if self.websocket:
            asyncio.create_task(self.websocket.close())
    
    async def run_comprehensive_test(self, url: str, duration: float = 30.0):
        """Run comprehensive WebSocket integration test"""
        self._print_info("Starting comprehensive WebSocket integration test")
        
        if self.console:
            test_panel = Panel(
                f"WebSocket Integration Test\n"
                f"Server: {url}\n"
                f"Duration: {duration}s\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                title="🧪 Test Configuration",
                border_style="blue"
            )
            self.console.print(test_panel)
        
        # Test 1: Connection Test
        self._print_info("\n=== Test 1: Connection Test ===")
        connection_success = await self.connect_to_server(url)
        self.test_results.append({
            'name': 'Connection Test',
            'success': connection_success,
            'error': None if connection_success else 'Failed to establish connection'
        })
        
        if not connection_success:
            self._print_error("Connection test failed. Cannot proceed with further tests.")
            return self.generate_test_report()
        
        # Test 2: Message Reception Test
        self._print_info("\n=== Test 2: Message Reception Test ===")
        try:
            await self.listen_for_messages(duration)
            
            message_test_success = self.stats['messages_received'] > 0
            self.test_results.append({
                'name': 'Message Reception Test',
                'success': message_test_success,
                'error': None if message_test_success else 'No messages received'
            })
            
            if message_test_success:
                self._print_success(f"Received {self.stats['messages_received']} messages")
            else:
                self._print_error("No messages received during test period")
            
        except Exception as e:
            self.test_results.append({
                'name': 'Message Reception Test',
                'success': False,
                'error': str(e)
            })
        
        # Test 3: Data Validation Test
        self._print_info("\n=== Test 3: Data Validation Test ===")
        valid_messages = 0
        total_messages = 0
        
        # Process received messages
        while not self.received_messages.empty():
            try:
                msg_data = self.received_messages.get_nowait()
                total_messages += 1
                if msg_data['validation']['valid']:
                    valid_messages += 1
            except queue.Empty:
                break
        
        validation_success = total_messages > 0 and (valid_messages / total_messages) >= 0.8
        self.test_results.append({
            'name': 'Data Validation Test',
            'success': validation_success,
            'error': None if validation_success else f'Only {valid_messages}/{total_messages} messages were valid'
        })
        
        if validation_success:
            self._print_success(f"Data validation: {valid_messages}/{total_messages} messages valid")
        else:
            self._print_error(f"Data validation failed: {valid_messages}/{total_messages} messages valid")
        
        # Generate and return final report
        return self.generate_test_report()


class WebSocketLoadTester:
    """Load testing for WebSocket connections"""
    
    def __init__(self, url: str, num_clients: int = 5):
        self.url = url
        self.num_clients = num_clients
        self.clients = []
        self.stats = {
            'total_connections': 0,
            'successful_connections': 0,
            'total_messages': 0,
            'connection_errors': 0,
            'message_errors': 0
        }
    
    async def create_client(self, client_id: int, duration: float = 30.0):
        """Create a single test client"""
        try:
            async with websockets.connect(self.url) as websocket:
                self.stats['successful_connections'] += 1
                print(f"Client {client_id}: Connected")
                
                start_time = time.time()
                message_count = 0
                
                async for message in websocket:
                    if time.time() - start_time > duration:
                        break
                    
                    message_count += 1
                    self.stats['total_messages'] += 1
                    
                    if message_count % 10 == 0:
                        print(f"Client {client_id}: Received {message_count} messages")
                
                print(f"Client {client_id}: Disconnected after receiving {message_count} messages")
                
        except Exception as e:
            self.stats['connection_errors'] += 1
            print(f"Client {client_id}: Error - {e}")
    
    async def run_load_test(self, duration: float = 30.0):
        """Run load test with multiple clients"""
        print(f"Starting load test with {self.num_clients} clients for {duration}s")
        
        self.stats['total_connections'] = self.num_clients
        
        # Create tasks for all clients
        tasks = [
            self.create_client(i, duration) 
            for i in range(self.num_clients)
        ]
        
        # Run all clients concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Print results
        print(f"\nLoad Test Results:")
        print(f"- Total clients: {self.num_clients}")
        print(f"- Successful connections: {self.stats['successful_connections']}")
        print(f"- Connection errors: {self.stats['connection_errors']}")
        print(f"- Total messages received: {self.stats['total_messages']}")
        print(f"- Average messages per client: {self.stats['total_messages'] / max(1, self.stats['successful_connections']):.1f}")


async def main():
    """Main test function"""
    parser = argparse.ArgumentParser(
        description="WebSocket Integration Tester",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic connection test
  python test_websocket_integration.py --url ws://localhost:8765
  
  # Extended test with custom duration
  python test_websocket_integration.py --url ws://localhost:8765 --duration 60
  
  # Load test with multiple clients
  python test_websocket_integration.py --url ws://localhost:8765 --load-test --clients 10
  
  # Quick connection test only
  python test_websocket_integration.py --url ws://localhost:8765 --quick
        """
    )
    
    parser.add_argument('--url', default='ws://localhost:8765',
                       help='WebSocket server URL (default: ws://localhost:8765)')
    parser.add_argument('--duration', type=float, default=30.0,
                       help='Test duration in seconds (default: 30)')
    parser.add_argument('--load-test', action='store_true',
                       help='Run load test with multiple clients')
    parser.add_argument('--clients', type=int, default=5,
                       help='Number of clients for load test (default: 5)')
    parser.add_argument('--quick', action='store_true',
                       help='Quick connection test only')
    
    args = parser.parse_args()
    
    if args.load_test:
        # Run load test
        load_tester = WebSocketLoadTester(args.url, args.clients)
        await load_tester.run_load_test(args.duration)
    elif args.quick:
        # Quick connection test
        tester = WebSocketTester()
        success = await tester.connect_to_server(args.url)
        if success:
            print("✓ Quick connection test PASSED")
            await tester.websocket.close()
        else:
            print("✗ Quick connection test FAILED")
    else:
        # Comprehensive test
        tester = WebSocketTester()
        report = await tester.run_comprehensive_test(args.url, args.duration)
        
        print("\n" + "="*60)
        print(report)
        print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)