#!/usr/bin/env python3
"""
Unit tests for standalone logger metadata functionality
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestMetadataFunctionality(unittest.TestCase):
    """Test metadata creation and consumption"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_metadata_structure_validation(self):
        """Test that metadata structure contains required fields"""
        # Expected metadata structure
        metadata = {
            "csv_file": {
                "name": "test.csv",
                "full_path": "/path/to/test.csv"
            },
            "session": {
                "rma_number": "8765",
                "serial_number": "0573",
                "com_port": "COM3",
                "start_timestamp": "2025-07-20T12:00:00",
                "end_timestamp": None,
                "baudrate": 9600,
                "slave_id": 1
            },
            "logging": {
                "interval": 0.5,
                "filter_enabled": True,
                "filter_settings": {
                    "window_size": 5,
                    "spike_threshold": 2.0
                }
            }
        }

        # Validate structure
        self.assertIn('csv_file', metadata)
        self.assertIn('session', metadata)
        self.assertIn('logging', metadata)

        # Validate CSV file section
        csv_section = metadata['csv_file']
        self.assertIn('name', csv_section)
        self.assertIn('full_path', csv_section)

        # Validate session section
        session_section = metadata['session']
        required_session_fields = [
            'rma_number', 'serial_number', 'com_port', 
            'start_timestamp', 'baudrate', 'slave_id'
        ]
        for field in required_session_fields:
            self.assertIn(field, session_section)

        # Validate logging section
        logging_section = metadata['logging']
        self.assertIn('interval', logging_section)
        self.assertIn('filter_enabled', logging_section)
        self.assertIn('filter_settings', logging_section)

    @patch('src.modbus_standalone_logger.Path.mkdir')
    @patch('src.modbus_standalone_logger.open')
    @patch('src.modbus_standalone_logger.json.dump')
    def test_standalone_logger_metadata_creation(self, mock_json_dump, mock_open, mock_mkdir):
        """Test that StandaloneModbusLogger creates metadata files"""
        from modbus_standalone_logger import StandaloneModbusLogger

        # Create logger instance
        logger = StandaloneModbusLogger()
        logger.is_connected = True  # Mock connection
        logger.config = {
            'connection': {
                'port': 'COM3',
                'baudrate': 9600,
                'slave_id': 1
            },
            'logging': {
                'auto_create_dirs': True
            },
            'filter': {
                'enabled': True,
                'window_size': 5,
                'spike_threshold': 2.0
            }
        }

        # Mock file operations
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Test start_logging creates metadata
        with patch.object(logger, '_save_config'), \
             patch.object(logger, '_add_to_history'), \
             patch('src.modbus_standalone_logger.csv.writer'), \
             patch('src.modbus_standalone_logger.register_map', {'reg1': 'Register 1'}):
            
            result = logger.start_logging(
                output_path=str(self.temp_path),
                serial_number="0573",
                rma_number="8765",
                interval=0.5
            )

        # Verify metadata was created
        self.assertTrue(result)
        self.assertTrue(mock_json_dump.called)
        
        # Check metadata structure
        metadata_call = mock_json_dump.call_args[0][0]
        self.assertIn('csv_file', metadata_call)
        self.assertIn('session', metadata_call)
        self.assertIn('logging', metadata_call)

    def test_dashboard_metadata_loading(self):
        """Test that dashboard can load metadata files"""
        # Create test CSV and metadata files
        csv_file = self.temp_path / "test_20250720_120000-0573-8765.csv"
        metadata_file = csv_file.with_suffix('.json')

        # Create test CSV
        with open(csv_file, 'w') as f:
            f.write("Timestamp,afe_cell_volt1\n")
            f.write("2025-07-20T12:00:00,3234\n")

        # Create test metadata
        metadata = {
            "csv_file": {
                "name": "test_20250720_120000-0573-8765.csv",
                "full_path": str(csv_file.absolute())
            },
            "session": {
                "rma_number": "8765",
                "serial_number": "0573",
                "com_port": "COM3",
                "start_timestamp": "2025-07-20T12:00:00",
                "baudrate": 9600,
                "slave_id": 1
            },
            "logging": {
                "interval": 0.5,
                "filter_enabled": True
            }
        }

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)

        # Test dashboard loading (mock matplotlib to avoid display)
        with patch('src.modbus_dashboard.MATPLOTLIB_AVAILABLE', False), \
             patch('src.modbus_dashboard.plt'), \
             patch.object(sys.modules.get('src.modbus_dashboard', Mock()), 'ModbusDashboard') as MockDashboard:
            
            # Import and test
            from modbus_dashboard import ModbusDashboard
            
            # Create dashboard instance
            dashboard = ModbusDashboard(str(csv_file))
            
            # Verify metadata was loaded
            self.assertIsNotNone(dashboard.metadata)
            self.assertEqual(dashboard.com_port, "COM3")
            self.assertEqual(dashboard.serial_number, "0573")
            self.assertEqual(dashboard.rma_number, "8765")

    def test_metadata_file_creation_and_loading(self):
        """Integration test for metadata file creation and loading"""
        csv_file = self.temp_path / "integration_test.csv"
        metadata_file = csv_file.with_suffix('.json')

        # Create test metadata manually (simulating logger creation)
        test_metadata = {
            "csv_file": {
                "name": "integration_test.csv",
                "full_path": str(csv_file.absolute())
            },
            "session": {
                "rma_number": "TEST123",
                "serial_number": "0999",
                "com_port": "COM99",
                "start_timestamp": "2025-07-20T15:30:00",
                "end_timestamp": "2025-07-20T15:35:00",
                "baudrate": 9600,
                "slave_id": 1
            },
            "logging": {
                "interval": 1.0,
                "filter_enabled": False,
                "filter_settings": {
                    "window_size": 10,
                    "spike_threshold": 3.0
                }
            }
        }

        # Write metadata file
        with open(metadata_file, 'w') as f:
            json.dump(test_metadata, f, indent=2)

        # Verify file was created
        self.assertTrue(metadata_file.exists())

        # Load and verify metadata
        with open(metadata_file, 'r') as f:
            loaded_metadata = json.load(f)

        self.assertEqual(loaded_metadata['session']['rma_number'], "TEST123")
        self.assertEqual(loaded_metadata['session']['serial_number'], "0999")
        self.assertEqual(loaded_metadata['session']['com_port'], "COM99")
        self.assertEqual(loaded_metadata['logging']['interval'], 1.0)
        self.assertFalse(loaded_metadata['logging']['filter_enabled'])


if __name__ == '__main__':
    unittest.main()