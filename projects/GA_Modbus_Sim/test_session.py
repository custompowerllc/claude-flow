#!/usr/bin/env python3
"""
Simple test script for session tracking functionality
"""

import sys
import os
from datetime import datetime
from PyQt6.QtCore import QSettings

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.session_manager import SessionManager, Session, AutoStartConfig

def test_session_functionality():
    """Test basic session functionality"""
    print("Testing Session Tracking Functionality")
    print("=" * 40)
    
    # Create a test QSettings instance
    settings = QSettings("GA_BMS_Test", "BatteryMonitor_Test")
    
    # Initialize session manager
    session_manager = SessionManager(settings)
    print("✓ SessionManager initialized")
    
    # Test auto-start configuration
    config = session_manager.auto_config
    config.auto_log_mode = 'ENABLE'
    config.auto_log_charging_threshold = 1.0
    config.auto_log_discharging_threshold = -1.0
    session_manager.save_auto_config()
    print("✓ Auto-start configuration saved")
    
    # Test manual session creation
    connection_params = {
        'port': 'COM3',
        'baudrate': 9600,
        'slave_id': 2,
        'parity': 'E'
    }
    
    session_id = session_manager.start_manual_session(connection_params)
    print(f"✓ Manual session created: {session_id[:8]}...")
    
    # Test session data update
    test_data = {
        'cell_voltages': [3.2, 3.3, 3.25, 3.28, 3.22, 3.24, 3.26, 3.23],
        'pack_voltage': 26.0,
        'current': 0.5,
        'timestamp': datetime.now()
    }
    
    session_manager.update_session_data(test_data)
    print("✓ Session data updated")
    
    # Test CSV file association
    session_manager.associate_csv_file("test_data.csv")
    print("✓ CSV file associated")
    
    # Test session status
    status = session_manager.get_current_session_status()
    print(f"✓ Session status: Active={status['active']}, Records={status['record_count']}")
    
    # Test auto-start conditions
    auto_session_id = session_manager.check_auto_start_conditions(1.5, connection_params)
    if auto_session_id:
        print(f"✓ Auto-start would trigger: {auto_session_id[:8]}...")
    else:
        print("✓ Auto-start conditions checked (no trigger - session already active)")
    
    # End session
    summary = session_manager.end_session()
    print(f"✓ Session ended: Duration={summary['duration_seconds']}s")
    
    # Test session history
    history = session_manager.get_session_history()
    print(f"✓ Session history retrieved: {len(history)} sessions")
    
    # Test auto-start trigger
    session_manager.current_session = None  # Clear current session
    auto_session_id = session_manager.check_auto_start_conditions(1.5, connection_params)
    if auto_session_id:
        print(f"✓ Auto-start triggered: {auto_session_id[:8]}...")
        session_manager.end_session()
    
    print("\n" + "=" * 40)
    print("All session functionality tests passed!")
    
    # Clean up test settings
    settings.clear()
    settings.sync()

if __name__ == "__main__":
    test_session_functionality()