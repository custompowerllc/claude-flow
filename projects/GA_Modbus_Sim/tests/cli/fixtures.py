"""
Test fixtures and mock objects for CLI testing
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import tempfile
import os
import sys
from typing import Dict, Any, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.session_manager import Session, SessionManager
from communication.modbus_worker import ModbusWorker
from core.auto_start_stop_manager import AutoStartStopManager
from core.cell_runaway_analyzer import CellRunawayAnalyzer
from core.plugin_system import PluginManager, AppContext
from utils.config_manager import ConfigManager


class MockModbusWorker:
    """Mock Modbus worker for testing"""
    
    def __init__(self):
        self.is_connected = False
        self.port = None
        self.baudrate = 9600
        self.slave_id = 1
        self.last_data = None
        self.connection_attempts = 0
        
    def connect(self, port: str, baudrate: int = 9600, slave_id: int = 1) -> bool:
        self.port = port
        self.baudrate = baudrate
        self.slave_id = slave_id
        self.connection_attempts += 1
        self.is_connected = True
        return True
        
    def disconnect(self):
        self.is_connected = False
        self.port = None
        
    def read_data(self) -> Optional[Dict[str, Any]]:
        """Return mock battery data"""
        if not self.is_connected:
            return None
            
        mock_data = {
            'timestamp': '2024-01-01 12:00:00',
            'cell_1': 3.25,
            'cell_2': 3.26,
            'cell_3': 3.24,
            'cell_4': 3.27,
            'cell_5': 3.25,
            'cell_6': 3.26,
            'cell_7': 3.24,
            'cell_8': 3.25,
            'cell_9': 3.26,
            'cell_10': 3.25,
            'cell_11': 3.24,
            'cell_12': 3.26,
            'cell_13': 3.25,
            'cell_14': 3.27,
            'cell_15': 3.24,
            'cell_16': 3.25,
            'pack_voltage': 52.1,
            'pack_current': 2.5,
            'soc': 75.5,
            'temperature_1': 25.2,
            'temperature_2': 25.8,
            'temperature_3': 24.9,
            'temperature_4': 25.1,
            'fet_temp': 26.3,
            'balance_status': 0x0000,
            'protection_status': 0x0000,
            'fault_status': 0x0000,
            'remaining_capacity': 18.5,
            'full_capacity': 24.5,
            'cycle_count': 125,
            'design_capacity': 25.0,
            'manufacture_date': '2023-06-15',
            'serial_number': '12345678'
        }
        
        self.last_data = mock_data
        return mock_data


class MockSessionManager:
    """Mock session manager for testing"""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.current_session: Optional[Session] = None
        
    def create_session(self, name: str, battery_id: str = "TEST") -> Session:
        """Create a mock session"""
        session = Mock(spec=Session)
        session.session_id = f"session-{len(self.sessions)}"
        session.name = name
        session.battery_id = battery_id
        session.created_at = "2024-01-01 12:00:00"
        session.status = "active"
        session.data_points = 0
        session.start_time = "2024-01-01 12:00:00"
        session.end_time = None
        session.csv_file = f"data/sessions/{session.session_id}/data.csv"
        
        self.sessions[session.session_id] = session
        return session
        
    def get_session(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)
        
    def list_sessions(self) -> List[Session]:
        return list(self.sessions.values())
        
    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
        
    def set_current_session(self, session: Session):
        self.current_session = session
        
    def get_current_session(self) -> Optional[Session]:
        return self.current_session


class MockConfigManager:
    """Mock configuration manager for testing"""
    
    def __init__(self):
        self.config = {
            'modbus': {
                'port': 'COM1',
                'baudrate': 9600,
                'slave_id': 1,
                'timeout': 3.0
            },
            'logging': {
                'interval': 1.0,
                'output_dir': 'log',
                'auto_start': False
            },
            'plugins': {
                'enabled': True,
                'load_builtin': True
            }
        }
        
    def get(self, key: str, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default
        
    def set(self, key: str, value: Any):
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        
    def save(self):
        pass


class MockPluginManager:
    """Mock plugin manager for testing"""
    
    def __init__(self):
        self.plugins = {
            'battery_analyzer': {
                'name': 'Battery Analyzer',
                'version': '1.0.0',
                'commands': ['analyze_battery', 'cell_balance']
            },
            'csv_exporter': {
                'name': 'CSV Exporter',
                'version': '1.0.0',
                'commands': ['export_csv', 'format_data']
            }
        }
        self.loaded_plugins = set()
        
    def load_plugins(self):
        self.loaded_plugins.update(self.plugins.keys())
        
    def get_loaded_plugins(self) -> List[str]:
        return list(self.loaded_plugins)
        
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        return self.plugins.get(plugin_name)
        
    def execute_plugin_command(self, plugin_name: str, command: str, *args, **kwargs):
        if plugin_name in self.loaded_plugins:
            return f"Executed {command} on {plugin_name}"
        return None


@pytest.fixture
def mock_modbus_worker():
    """Fixture providing mock Modbus worker"""
    return MockModbusWorker()


@pytest.fixture
def mock_session_manager():
    """Fixture providing mock session manager"""
    return MockSessionManager()


@pytest.fixture
def mock_config_manager():
    """Fixture providing mock configuration manager"""
    return MockConfigManager()


@pytest.fixture
def mock_plugin_manager():
    """Fixture providing mock plugin manager"""
    return MockPluginManager()


@pytest.fixture
def temp_data_dir():
    """Fixture providing temporary directory for test data"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create subdirectories
        os.makedirs(f"{tmpdir}/sessions")
        os.makedirs(f"{tmpdir}/csv")
        os.makedirs(f"{tmpdir}/log")
        yield tmpdir


@pytest.fixture
def mock_rich_console():
    """Fixture providing mock Rich console"""
    console = Mock()
    console.print = Mock()
    return console


@pytest.fixture
def sample_session_data():
    """Fixture providing sample session data"""
    return {
        'session_id': 'test-session-001',
        'name': 'Test Session',
        'battery_id': 'TEST001',
        'created_at': '2024-01-01 12:00:00',
        'status': 'active',
        'data_points': 100,
        'start_time': '2024-01-01 12:00:00',
        'end_time': None,
        'csv_file': 'data/sessions/test-session-001/data.csv'
    }


@pytest.fixture
def sample_battery_data():
    """Fixture providing sample battery data"""
    return {
        'timestamp': '2024-01-01 12:00:00',
        'cell_1': 3.25,
        'cell_2': 3.26,
        'cell_3': 3.24,
        'cell_4': 3.27,
        'cell_5': 3.25,
        'cell_6': 3.26,
        'cell_7': 3.24,
        'cell_8': 3.25,
        'cell_9': 3.26,
        'cell_10': 3.25,
        'cell_11': 3.24,
        'cell_12': 3.26,
        'cell_13': 3.25,
        'cell_14': 3.27,
        'cell_15': 3.24,
        'cell_16': 3.25,
        'pack_voltage': 52.1,
        'pack_current': 2.5,
        'soc': 75.5,
        'temperature_1': 25.2,
        'temperature_2': 25.8,
        'temperature_3': 24.9,
        'temperature_4': 25.1,
        'fet_temp': 26.3,
        'balance_status': 0x0000,
        'protection_status': 0x0000,
        'fault_status': 0x0000,
        'remaining_capacity': 18.5,
        'full_capacity': 24.5,
        'cycle_count': 125,
        'design_capacity': 25.0,
        'manufacture_date': '2023-06-15',
        'serial_number': '12345678'
    }


class MockSerial:
    """Mock serial connection for testing"""
    
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.is_open = True
        
    def close(self):
        self.is_open = False
        
    def read(self, size):
        return b'\x01\x03\x04\x00\x01\x00\x02'
        
    def write(self, data):
        return len(data)


@pytest.fixture
def mock_serial():
    """Fixture providing mock serial connection"""
    return MockSerial


@pytest.fixture
def cli_input_patcher():
    """Fixture for patching CLI input methods"""
    with patch('builtins.input') as mock_input:
        yield mock_input


@pytest.fixture
def mock_file_system():
    """Fixture providing mock file system operations"""
    with patch('os.path.exists') as mock_exists, \
         patch('os.makedirs') as mock_makedirs, \
         patch('builtins.open', create=True) as mock_open:
        
        mock_exists.return_value = True
        mock_makedirs.return_value = None
        mock_open.return_value.__enter__.return_value.write.return_value = None
        
        yield {
            'exists': mock_exists,
            'makedirs': mock_makedirs,
            'open': mock_open
        }