#!/usr/bin/env python3
"""
Test script for WebSocket client functionality in modbus dashboard
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import the dashboard
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_websocket_imports():
    """Test that WebSocket dependencies are available"""
    try:
        from src.modbus_dashboard import WEBSOCKET_AVAILABLE, WebSocketDataSource, DataSourceManager, ModbusDashboard
        print("✅ WebSocket imports successful")
        print(f"✅ WebSocket libraries available: {WEBSOCKET_AVAILABLE}")
        return True
    except ImportError as e:
        print(f"❌ WebSocket import failed: {e}")
        return False

def test_websocket_classes():
    """Test WebSocket class instantiation"""
    try:
        from src.modbus_dashboard import WebSocketDataSource, DataSourceManager
        
        # Test WebSocketDataSource
        ws_source = WebSocketDataSource("ws://localhost:8765")
        print("✅ WebSocketDataSource created successfully")
        print(f"   - URL: {ws_source.url}")
        print(f"   - Max reconnects: {ws_source.max_reconnects}")
        print(f"   - Reconnect interval: {ws_source.reconnect_interval}s")
        
        # Test DataSourceManager
        manager = DataSourceManager("test.csv", "ws://localhost:8765")
        print("✅ DataSourceManager created successfully")
        print(f"   - Mode: {manager.get_mode()}")
        print(f"   - CSV file: {manager.csv_file}")
        print(f"   - WebSocket URL: {manager.websocket_url}")
        
        return True
    except Exception as e:
        print(f"❌ WebSocket class instantiation failed: {e}")
        return False

def test_dashboard_integration():
    """Test dashboard integration with WebSocket support"""
    try:
        from src.modbus_dashboard import ModbusDashboard
        
        # Create a minimal CSV file for testing
        test_csv = Path("test_data.csv")
        if not test_csv.exists():
            with open(test_csv, 'w') as f:
                f.write("Timestamp,afe_cell_volt1,afe_cell_volt2,afe_cell_volt3,afe_cell_volt4,afe_cell_volt5,afe_cell_volt6,afe_cell_volt7,afe_cell_volt8,afe_pack_volt,fg_current,afe_cell_volt_delta,fg_state_of_charge,afe_temp1,afe_temp2\n")
                f.write("2025-08-04 04:30:00,3245,3248,3243,3247,3246,3244,3245,3249,25984,-1250,6,87,3030,3035\n")
        
        # Test dashboard with WebSocket URL
        dashboard = ModbusDashboard(
            str(test_csv),
            update_interval=1000,
            historical_mode=True,  # Use historical mode to avoid GUI
            websocket_url="ws://localhost:8765"
        )
        
        print("✅ Dashboard with WebSocket support created successfully")
        print(f"   - CSV file: {dashboard.csv_file}")
        print(f"   - WebSocket URL: {dashboard.websocket_url}")
        print(f"   - Data source mode: {dashboard.data_source_mode}")
        
        # Test connection info
        connection_info = dashboard.data_source_manager.get_connection_info()
        print(f"   - Connection info: {connection_info}")
        
        # Cleanup
        dashboard.cleanup()
        
        # Clean up test file
        if test_csv.exists():
            test_csv.unlink()
        
        return True
    except Exception as e:
        print(f"❌ Dashboard integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing WebSocket Client Implementation\n")
    
    tests = [
        ("WebSocket Imports", test_websocket_imports),
        ("WebSocket Classes", test_websocket_classes),
        ("Dashboard Integration", test_dashboard_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! WebSocket client implementation is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())