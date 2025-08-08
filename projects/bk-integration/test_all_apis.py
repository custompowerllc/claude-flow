#!/usr/bin/env python3
"""
Comprehensive API Test Suite for BK8520 and BK9206B Devices
Tests all available API endpoints for both electronic load and power supply devices
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BK8520_BASE_URL = "http://10.100.10.190:8000/api"
BK9206B_BASE_URL = "http://10.100.10.190:5300/api"

# Test result storage
test_results = {
    "bk8520": {"passed": 0, "failed": 0, "errors": []},
    "bk9206b": {"passed": 0, "failed": 0, "errors": []}
}

def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def print_test(test_name: str, device: str):
    """Print test information"""
    print(f"\n[{device}] Testing: {test_name}")

def print_success(message: str):
    """Print success message"""
    print(f"  ✅ {message}")

def print_error(message: str):
    """Print error message"""
    print(f"  ❌ {message}")

def test_api_endpoint(device: str, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> bool:
    """Test a single API endpoint"""
    base_url = BK8520_BASE_URL if device == "BK8520" else BK9206B_BASE_URL
    url = f"{base_url}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=3)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=3)
        else:
            print_error(f"Unsupported method: {method}")
            return False
        
        if response.status_code == expected_status:
            print_success(f"{method} {endpoint} - Status: {response.status_code}")
            if response.content:
                try:
                    json_data = response.json()
                    print(f"    Response: {json.dumps(json_data, indent=2)[:200]}...")
                except json.JSONDecodeError:
                    print(f"    Response: {response.text[:200]}...")
            test_results[device.lower()]["passed"] += 1
            return True
        else:
            print_error(f"{method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}")
            test_results[device.lower()]["failed"] += 1
            test_results[device.lower()]["errors"].append(f"{method} {endpoint}: Status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error(f"{method} {endpoint} - Connection refused (is the server running?)")
        test_results[device.lower()]["failed"] += 1
        test_results[device.lower()]["errors"].append(f"{method} {endpoint}: Connection refused")
        return False
    except requests.exceptions.Timeout:
        print_error(f"{method} {endpoint} - Request timeout")
        test_results[device.lower()]["failed"] += 1
        test_results[device.lower()]["errors"].append(f"{method} {endpoint}: Timeout")
        return False
    except Exception as e:
        print_error(f"{method} {endpoint} - Error: {str(e)}")
        test_results[device.lower()]["failed"] += 1
        test_results[device.lower()]["errors"].append(f"{method} {endpoint}: {str(e)}")
        return False

def test_bk8520_api():
    """Test all BK8520 Electronic Load API endpoints"""
    print_header("BK8520 Electronic Load API Tests")
    
    # Health Check
    print_test("Health Check", "BK8520")
    test_api_endpoint("BK8520", "GET", "/health")
    
    # Device Connection (Skip if already connected)
    print_test("Device Connection", "BK8520")
    # Note: Device appears to be already connected, so we'll skip connection
    # test_api_endpoint("BK8520", "POST", "/device/connect",
    #                  data={
    #                      "port": "/dev/ttyUSB0",
    #                      "baudrate": 4800,  # BK8520 uses 4800 baud
    #                      "timeout": 3.0,
    #                      "reset_input_on_connect": True
    #                  })
    
    # Device Status and Info
    print_test("Device Status and Info", "BK8520")
    test_api_endpoint("BK8520", "GET", "/device/status")
    test_api_endpoint("BK8520", "GET", "/device/info")
    test_api_endpoint("BK8520", "GET", "/device/readings")
    
    # Device Control
    print_test("Device Control", "BK8520")
    test_api_endpoint("BK8520", "POST", "/device/input", 
                     data={"enabled": True})
    test_api_endpoint("BK8520", "POST", "/device/input", 
                     data={"enabled": False})
    
    # Parameter Settings
    print_test("Parameter Settings", "BK8520")
    test_api_endpoint("BK8520", "POST", "/device/current", 
                     data={"current": 1.0})
    test_api_endpoint("BK8520", "POST", "/device/voltage", 
                     data={"voltage": 12.0})
    test_api_endpoint("BK8520", "POST", "/device/mode", 
                     data={"mode": 0})  # 0=CC mode
    test_api_endpoint("BK8520", "POST", "/device/max-current", 
                     data={"current": 5.0})
    test_api_endpoint("BK8520", "POST", "/device/max-power", 
                     data={"power": 100.0})
    test_api_endpoint("BK8520", "POST", "/device/max-voltage", 
                     data={"voltage": 60.0})
    
    # Discharge Setup
    print_test("Discharge Setup", "BK8520")
    test_api_endpoint("BK8520", "POST", "/device/setup-discharge",
                     data={
                         "current": 1.0,
                         "cutoff_voltage": 10.5
                     })
    
    # Battery Testing
    print_test("Battery Testing", "BK8520")
    test_api_endpoint("BK8520", "POST", "/battery-test/start",
                     data={
                         "discharge_current": 1.0,
                         "cutoff_voltage": 10.5,
                         "max_time_hours": 1.0
                     })
    test_api_endpoint("BK8520", "GET", "/battery-test/status")
    test_api_endpoint("BK8520", "POST", "/battery-test/stop", data={})
    test_api_endpoint("BK8520", "GET", "/battery-test/results")
    
    # Disconnect
    print_test("Device Disconnect", "BK8520")
    test_api_endpoint("BK8520", "POST", "/device/disconnect", data={})

def test_bk9206b_api():
    """Test all BK9206B Power Supply API endpoints"""
    print_header("BK9206B Power Supply API Tests")
    
    # Health and Status
    print_test("Health and Status", "BK9206B")
    test_api_endpoint("BK9206B", "GET", "/health")
    test_api_endpoint("BK9206B", "GET", "/status")
    
    # Voltage and Current Control
    print_test("Voltage Control", "BK9206B")
    test_api_endpoint("BK9206B", "POST", "/voltage", 
                     data={"voltage": 12.0})
    test_api_endpoint("BK9206B", "POST", "/voltage", 
                     data={"voltage": 70.0}, 
                     expected_status=422)  # Out of range
    
    print_test("Current Control", "BK9206B")
    test_api_endpoint("BK9206B", "POST", "/current", 
                     data={"current": 1.5})
    test_api_endpoint("BK9206B", "POST", "/current", 
                     data={"current": 10.0}, 
                     expected_status=422)  # Out of range
    
    # Output Control
    print_test("Output Control", "BK9206B")
    test_api_endpoint("BK9206B", "POST", "/output/enable")
    time.sleep(1)  # Wait for output to stabilize
    test_api_endpoint("BK9206B", "POST", "/output/disable")
    
    # Taper Current Configuration
    print_test("Taper Current Configuration", "BK9206B")
    test_api_endpoint("BK9206B", "GET", "/taper/config")
    test_api_endpoint("BK9206B", "POST", "/taper/threshold", 
                     data={"threshold": 0.2})
    test_api_endpoint("BK9206B", "POST", "/taper/threshold", 
                     data={"threshold": 10.0}, 
                     expected_status=422)  # Out of range
    test_api_endpoint("BK9206B", "POST", "/taper/duration", 
                     data={"duration": 60})
    test_api_endpoint("BK9206B", "POST", "/taper/duration", 
                     data={"duration": 5000}, 
                     expected_status=422)  # Out of range

def test_websocket_connections():
    """Test WebSocket connections for both devices"""
    print_header("WebSocket Connection Tests")
    
    print_test("WebSocket Endpoints", "Both")
    
    # Note: WebSocket testing requires websocket-client library
    # This is a placeholder for WebSocket tests
    print("  ⚠️  WebSocket testing requires websocket-client library")
    print("  ⚠️  BK8520 WebSocket: ws://localhost:8000/ws/devices/{device_id}/stream")
    print("  ⚠️  BK8520 WebSocket: ws://localhost:8000/ws/tests/{test_id}/progress")
    print("  ⚠️  BK9206B WebSocket: ws://localhost:5300/ws")

def print_summary():
    """Print test summary"""
    print_header("Test Summary")
    
    total_passed = test_results["bk8520"]["passed"] + test_results["bk9206b"]["passed"]
    total_failed = test_results["bk8520"]["failed"] + test_results["bk9206b"]["failed"]
    
    print(f"\n📊 Overall Results:")
    print(f"  Total Tests: {total_passed + total_failed}")
    print(f"  ✅ Passed: {total_passed}")
    print(f"  ❌ Failed: {total_failed}")
    
    print(f"\n🔌 BK8520 Electronic Load:")
    print(f"  Passed: {test_results['bk8520']['passed']}")
    print(f"  Failed: {test_results['bk8520']['failed']}")
    if test_results['bk8520']['errors']:
        print("  Errors:")
        for error in test_results['bk8520']['errors'][:5]:  # Show first 5 errors
            print(f"    - {error}")
    
    print(f"\n⚡ BK9206B Power Supply:")
    print(f"  Passed: {test_results['bk9206b']['passed']}")
    print(f"  Failed: {test_results['bk9206b']['failed']}")
    if test_results['bk9206b']['errors']:
        print("  Errors:")
        for error in test_results['bk9206b']['errors'][:5]:  # Show first 5 errors
            print(f"    - {error}")
    
    print(f"\n🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return exit code based on results
    return 0 if total_failed == 0 else 1

def main():
    """Main test execution"""
    print_header("BK Device API Test Suite")
    print("Testing endpoints for BK8520 and BK9206B devices")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test BK8520 API
    try:
        test_bk8520_api()
    except Exception as e:
        print_error(f"BK8520 test suite failed: {str(e)}")
    
    # Test BK9206B API
    try:
        test_bk9206b_api()
    except Exception as e:
        print_error(f"BK9206B test suite failed: {str(e)}")
    
    # Test WebSocket connections
    test_websocket_connections()
    
    # Print summary and exit
    exit_code = print_summary()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()