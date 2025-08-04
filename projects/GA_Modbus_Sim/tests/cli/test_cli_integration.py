"""
Integration tests for complete CLI workflows
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
import tempfile
import threading
import time
from pathlib import Path
from io import StringIO

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fixtures import (
    mock_modbus_worker, mock_session_manager, mock_config_manager,
    mock_plugin_manager, temp_data_dir, sample_session_data, sample_battery_data
)


class TestCLIIntegrationWorkflows:
    """Integration tests for complete CLI workflows"""
    
    def test_complete_monitoring_workflow(self, mock_modbus_worker, mock_session_manager, 
                                        mock_config_manager, sample_session_data, sample_battery_data):
        """Test complete monitoring workflow: connect -> create session -> start logging -> stop logging -> disconnect"""
        with patch('cli.bms_cli.ModbusWorker', return_value=mock_modbus_worker), \
             patch('cli.bms_cli.SessionManager', return_value=mock_session_manager), \
             patch('cli.bms_cli.ConfigManager', return_value=mock_config_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            from cli.bms_cli import BMSCLIShell
            shell = BMSCLIShell()
            
            # Step 1: Connect to device
            mock_modbus_worker.connect.return_value = True
            shell.do_connect("COM1 9600 1")
            assert shell.is_connected is True
            
            # Step 2: Create session
            mock_session = Mock()
            mock_session.session_id = sample_session_data['session_id']
            mock_session.name = sample_session_data['name']
            mock_session_manager.create_session.return_value = mock_session
            shell.do_session_create("test_session TEST001")
            assert shell.current_session == mock_session
            
            # Step 3: Start logging
            mock_modbus_worker.read_data.return_value = sample_battery_data
            with patch('threading.Thread') as mock_thread:
                shell.do_start_logging("")
                assert shell.is_logging is True
                assert mock_thread.called
            
            # Step 4: Stop logging
            shell.do_stop_logging("")
            assert shell.is_logging is False
            
            # Step 5: Disconnect
            shell.do_disconnect("")
            assert shell.is_connected is False
    
    def test_session_management_workflow(self, mock_session_manager, sample_session_data):
        """Test session management workflow: create -> list -> load -> delete"""
        with patch('cli.bms_cli.SessionManager', return_value=mock_session_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            from cli.bms_cli import BMSCLIShell
            shell = BMSCLIShell()
            
            # Step 1: Create multiple sessions
            sessions = []
            for i in range(3):
                mock_session = Mock()
                mock_session.session_id = f"session-{i}"
                mock_session.name = f"Test Session {i}"
                mock_session.status = "active"
                sessions.append(mock_session)
                
                mock_session_manager.create_session.return_value = mock_session
                shell.do_session_create(f"test_session_{i} TEST00{i}")
            
            # Step 2: List sessions
            mock_session_manager.list_sessions.return_value = sessions
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                shell.do_session_list("")
                output = mock_stdout.getvalue()
                assert "session-0" in output
                assert "session-1" in output
                assert "session-2" in output
            
            # Step 3: Load specific session
            mock_session_manager.get_session.return_value = sessions[1]
            shell.do_session_load("session-1")
            assert shell.current_session == sessions[1]
            
            # Step 4: Delete session
            mock_session_manager.delete_session.return_value = True
            with patch('builtins.input', return_value='y'):
                shell.do_session_delete("session-0")
                assert mock_session_manager.delete_session.called
    
    def test_plugin_system_workflow(self, mock_plugin_manager):
        """Test plugin system workflow: load -> list -> info -> execute"""
        with patch('cli.bms_cli.PluginManager', return_value=mock_plugin_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            from cli.bms_cli import BMSCLIShell
            shell = BMSCLIShell()
            
            # Step 1: Load plugins (automatic during init)
            mock_plugin_manager.load_plugins.return_value = None
            
            # Step 2: List loaded plugins
            mock_plugin_manager.get_loaded_plugins.return_value = ['battery_analyzer', 'csv_exporter']
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                shell.do_plugin_list("")
                output = mock_stdout.getvalue()
                assert "battery_analyzer" in output
                assert "csv_exporter" in output
            
            # Step 3: Get plugin info
            mock_plugin_info = {
                'name': 'Battery Analyzer',
                'version': '1.0.0',
                'description': 'Analyzes battery data',
                'commands': ['analyze_battery', 'cell_balance']
            }
            mock_plugin_manager.get_plugin_info.return_value = mock_plugin_info
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                shell.do_plugin_info("battery_analyzer")
                output = mock_stdout.getvalue()
                assert "Battery Analyzer" in output
                assert "1.0.0" in output
            
            # Step 4: Execute plugin command
            mock_plugin_manager.execute_plugin_command.return_value = "Analysis complete"
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                shell.do_plugin_exec("battery_analyzer analyze_battery")
                output = mock_stdout.getvalue()
                assert "Analysis complete" in output
    
    def test_configuration_workflow(self, mock_config_manager):
        """Test configuration workflow: get -> set -> save"""
        with patch('cli.bms_cli.ConfigManager', return_value=mock_config_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            from cli.bms_cli import BMSCLIShell
            shell = BMSCLIShell()
            
            # Step 1: Get current settings
            mock_config_manager.get.return_value = "COM1"
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                shell.do_settings_get("modbus.port")
                output = mock_stdout.getvalue()
                assert "COM1" in output
            
            # Step 2: Set new value
            shell.do_settings_set("modbus.port COM2")
            assert mock_config_manager.set.called
            assert mock_config_manager.save.called
            
            # Step 3: Verify change
            mock_config_manager.get.return_value = "COM2"
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                shell.do_settings_get("modbus.port")
                output = mock_stdout.getvalue()
                assert "COM2" in output
    
    def test_auto_features_workflow(self, mock_modbus_worker, mock_session_manager):
        """Test auto start/stop and runaway detection workflow"""
        with patch('cli.bms_cli.ModbusWorker', return_value=mock_modbus_worker), \
             patch('cli.bms_cli.SessionManager', return_value=mock_session_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            from cli.bms_cli import BMSCLIShell
            shell = BMSCLIShell()
            
            # Step 1: Configure auto start
            shell.do_auto_start_enable("3.0 2.8")
            assert shell.auto_start_stop_manager.configure_auto_start.called
            
            # Step 2: Configure auto stop
            shell.do_auto_stop_enable("4.2 0.1")
            assert shell.auto_start_stop_manager.configure_auto_stop.called
            
            # Step 3: Enable runaway detection
            shell.do_runaway_enable("0.1 5.0")
            assert shell.cell_runaway_analyzer.enable.called
            
            # Step 4: Check auto start/stop status
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                shell.do_auto_start_status("")
                output = mock_stdout.getvalue()
                assert "Auto Start" in output
            
            # Step 5: Disable runaway detection
            shell.do_runaway_disable("")
            assert shell.cell_runaway_analyzer.disable.called
    
    def test_error_recovery_workflow(self, mock_modbus_worker, mock_session_manager):
        """Test error recovery workflow"""
        with patch('cli.bms_cli.ModbusWorker', return_value=mock_modbus_worker), \
             patch('cli.bms_cli.SessionManager', return_value=mock_session_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            from cli.bms_cli import BMSCLIShell
            shell = BMSCLIShell()
            
            # Step 1: Attempt failed connection
            mock_modbus_worker.connect.return_value = False
            shell.do_connect("COM1 9600 1")
            assert shell.is_connected is False
            
            # Step 2: Retry with successful connection
            mock_modbus_worker.connect.return_value = True
            shell.do_connect("COM2 9600 1")
            assert shell.is_connected is True
            
            # Step 3: Simulate connection loss during monitoring
            mock_modbus_worker.read_data.return_value = None
            with patch('threading.Thread') as mock_thread:
                shell.do_start_logging("")
                assert shell.is_logging is True
            
            # Step 4: Handle graceful shutdown
            shell.do_stop_logging("")
            assert shell.is_logging is False
    
    def test_multi_threaded_workflow(self, mock_modbus_worker, mock_session_manager, sample_battery_data):
        """Test multi-threaded operations workflow"""
        with patch('cli.bms_cli.ModbusWorker', return_value=mock_modbus_worker), \
             patch('cli.bms_cli.SessionManager', return_value=mock_session_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            from cli.bms_cli import BMSCLIShell
            shell = BMSCLIShell()
            
            # Setup connection and session
            mock_modbus_worker.connect.return_value = True
            shell.do_connect("COM1 9600 1")
            
            mock_session = Mock()
            mock_session_manager.create_session.return_value = mock_session
            shell.do_session_create("test_session TEST001")
            
            # Test concurrent operations
            mock_modbus_worker.read_data.return_value = sample_battery_data
            
            # Start logging in background
            with patch('threading.Thread') as mock_thread:
                shell.do_start_logging("")
                assert shell.is_logging is True
                
                # Simulate concurrent status checks
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    shell.do_status("")
                    output = mock_stdout.getvalue()
                    assert "Logging: Active" in output
                
                # Stop logging
                shell.do_stop_logging("")
                assert shell.is_logging is False
    
    def test_script_execution_workflow(self, mock_modbus_worker, mock_session_manager):
        """Test script execution workflow"""
        with patch('cli.bms_cli.ModbusWorker', return_value=mock_modbus_worker), \
             patch('cli.bms_cli.SessionManager', return_value=mock_session_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            from cli.bms_cli import BMSCLIShell
            shell = BMSCLIShell()
            
            # Create a script sequence
            commands = [
                "connect COM1 9600 1",
                "session_create test_session TEST001",
                "start_logging",
                "stop_logging",
                "disconnect"
            ]
            
            # Setup mocks
            mock_modbus_worker.connect.return_value = True
            mock_session = Mock()
            mock_session_manager.create_session.return_value = mock_session
            
            # Execute commands sequentially
            for command in commands:
                with patch('threading.Thread') as mock_thread:
                    shell.onecmd(command)
            
            # Verify final state
            assert shell.is_connected is False
            assert shell.is_logging is False
    
    def test_data_export_workflow(self, mock_modbus_worker, mock_session_manager, 
                                 mock_plugin_manager, sample_battery_data):
        """Test data export workflow"""
        with patch('cli.bms_cli.ModbusWorker', return_value=mock_modbus_worker), \
             patch('cli.bms_cli.SessionManager', return_value=mock_session_manager), \
             patch('cli.bms_cli.PluginManager', return_value=mock_plugin_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            from cli.bms_cli import BMSCLIShell
            shell = BMSCLIShell()
            
            # Setup monitoring session
            mock_modbus_worker.connect.return_value = True
            shell.do_connect("COM1 9600 1")
            
            mock_session = Mock()
            mock_session_manager.create_session.return_value = mock_session
            shell.do_session_create("export_test TEST001")
            
            # Collect some data
            mock_modbus_worker.read_data.return_value = sample_battery_data
            with patch('threading.Thread') as mock_thread:
                shell.do_start_logging("")
                time.sleep(0.1)  # Brief logging
                shell.do_stop_logging("")
            
            # Export data using plugin
            mock_plugin_manager.execute_plugin_command.return_value = "Export completed"
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                shell.do_plugin_exec("csv_exporter export_session export_test")
                output = mock_stdout.getvalue()
                assert "Export completed" in output


class TestCLIIntegrationErrorHandling:
    """Integration tests for error handling scenarios"""
    
    def test_connection_failure_recovery(self, mock_modbus_worker):
        """Test connection failure and recovery scenarios"""
        with patch('cli.bms_cli.ModbusWorker', return_value=mock_modbus_worker), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            from cli.bms_cli import BMSCLIShell
            shell = BMSCLIShell()
            
            # Test multiple connection attempts
            for attempt in range(3):
                if attempt < 2:
                    mock_modbus_worker.connect.return_value = False
                else:
                    mock_modbus_worker.connect.return_value = True
                
                shell.do_connect("COM1 9600 1")
                
                if attempt < 2:
                    assert shell.is_connected is False
                else:
                    assert shell.is_connected is True
    
    def test_session_corruption_handling(self, mock_session_manager):
        """Test handling of corrupted session data"""
        with patch('cli.bms_cli.SessionManager', return_value=mock_session_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            from cli.bms_cli import BMSCLIShell
            shell = BMSCLIShell()
            
            # Test session creation failure
            mock_session_manager.create_session.side_effect = Exception("Session creation failed")
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                shell.do_session_create("corrupted_session TEST001")
                output = mock_stdout.getvalue()
                assert "Error" in output or "Failed" in output
    
    def test_plugin_execution_errors(self, mock_plugin_manager):
        """Test plugin execution error handling"""
        with patch('cli.bms_cli.PluginManager', return_value=mock_plugin_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            from cli.bms_cli import BMSCLIShell
            shell = BMSCLIShell()
            
            # Test plugin execution failure
            mock_plugin_manager.execute_plugin_command.side_effect = Exception("Plugin error")
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                shell.do_plugin_exec("battery_analyzer analyze_battery")
                output = mock_stdout.getvalue()
                assert "Error" in output or "Failed" in output
    
    def test_monitoring_interruption_handling(self, mock_modbus_worker, mock_session_manager):
        """Test monitoring interruption scenarios"""
        with patch('cli.bms_cli.ModbusWorker', return_value=mock_modbus_worker), \
             patch('cli.bms_cli.SessionManager', return_value=mock_session_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            from cli.bms_cli import BMSCLIShell
            shell = BMSCLIShell()
            
            # Setup monitoring
            mock_modbus_worker.connect.return_value = True
            shell.do_connect("COM1 9600 1")
            
            mock_session = Mock()
            mock_session_manager.create_session.return_value = mock_session
            shell.do_session_create("interrupt_test TEST001")
            
            # Start monitoring
            with patch('threading.Thread') as mock_thread:
                shell.do_start_logging("")
                assert shell.is_logging is True
                
                # Simulate interruption
                shell.is_logging = False
                
                # Verify graceful handling
                shell.do_stop_logging("")
                assert shell.is_logging is False


class TestCLIIntegrationPerformance:
    """Performance integration tests"""
    
    def test_rapid_command_execution(self, mock_modbus_worker, mock_session_manager):
        """Test rapid command execution performance"""
        with patch('cli.bms_cli.ModbusWorker', return_value=mock_modbus_worker), \
             patch('cli.bms_cli.SessionManager', return_value=mock_session_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            from cli.bms_cli import BMSCLIShell
            shell = BMSCLIShell()
            
            # Setup mocks
            mock_modbus_worker.connect.return_value = True
            mock_session = Mock()
            mock_session_manager.create_session.return_value = mock_session
            
            # Execute rapid commands
            start_time = time.time()
            for i in range(100):
                shell.do_status("")
            execution_time = time.time() - start_time
            
            # Should complete within reasonable time
            assert execution_time < 5.0  # 5 seconds for 100 status commands
    
    def test_memory_usage_monitoring(self, mock_modbus_worker, mock_session_manager):
        """Test memory usage during extended monitoring"""
        with patch('cli.bms_cli.ModbusWorker', return_value=mock_modbus_worker), \
             patch('cli.bms_cli.SessionManager', return_value=mock_session_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            from cli.bms_cli import BMSCLIShell
            shell = BMSCLIShell()
            
            # Setup monitoring
            mock_modbus_worker.connect.return_value = True
            shell.do_connect("COM1 9600 1")
            
            mock_session = Mock()
            mock_session_manager.create_session.return_value = mock_session
            shell.do_session_create("memory_test TEST001")
            
            # Simulate data collection
            mock_modbus_worker.read_data.return_value = {'cell_1': 3.25}
            
            # Start and stop monitoring multiple times
            for i in range(10):
                with patch('threading.Thread') as mock_thread:
                    shell.do_start_logging("")
                    time.sleep(0.01)  # Brief monitoring
                    shell.do_stop_logging("")
            
            # Verify shell is still responsive
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                shell.do_status("")
                output = mock_stdout.getvalue()
                assert "System Status" in output