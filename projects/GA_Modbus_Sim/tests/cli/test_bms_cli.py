"""
Unit tests for BMS CLI interface (bms_cli.py)
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
from pathlib import Path
import threading
import time
from io import StringIO

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cli.bms_cli import BMSCLIShell
from fixtures import (
    mock_modbus_worker, mock_session_manager, mock_config_manager,
    mock_plugin_manager, temp_data_dir, mock_rich_console,
    sample_session_data, sample_battery_data, cli_input_patcher
)


class TestBMSCLIShell:
    """Test cases for BMSCLIShell class"""
    
    def test_initialization(self, mock_config_manager, mock_session_manager):
        """Test CLI shell initialization"""
        with patch('cli.bms_cli.ConfigManager', return_value=mock_config_manager), \
             patch('cli.bms_cli.SessionManager', return_value=mock_session_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', False):
            
            shell = BMSCLIShell()
            
            assert shell.config_manager == mock_config_manager
            assert shell.session_manager == mock_session_manager
            assert shell.console is None  # Rich not available
            assert shell.is_connected is False
            assert shell.is_monitoring is False
            assert shell.is_logging is False
            assert shell.current_session is None
            assert shell.modbus_worker is None
    
    def test_initialization_with_rich(self, mock_config_manager, mock_session_manager):
        """Test CLI shell initialization with Rich available"""
        with patch('cli.bms_cli.ConfigManager', return_value=mock_config_manager), \
             patch('cli.bms_cli.SessionManager', return_value=mock_session_manager), \
             patch('cli.bms_cli.RICH_AVAILABLE', True), \
             patch('cli.bms_cli.Console') as mock_console:
            
            shell = BMSCLIShell()
            
            assert shell.console == mock_console.return_value
    
    def test_do_connect_success(self, mock_modbus_worker):
        """Test successful connection command"""
        with patch('cli.bms_cli.ModbusWorker', return_value=mock_modbus_worker):
            shell = BMSCLIShell()
            
            # Mock successful connection
            mock_modbus_worker.connect.return_value = True
            
            # Capture output
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                shell.do_connect("COM1 9600 1")
                
            assert shell.is_connected is True
            assert shell.modbus_worker == mock_modbus_worker
            assert mock_modbus_worker.connect.called
    
    def test_do_connect_failure(self, mock_modbus_worker):
        """Test failed connection command"""
        with patch('cli.bms_cli.ModbusWorker', return_value=mock_modbus_worker):
            shell = BMSCLIShell()
            
            # Mock failed connection
            mock_modbus_worker.connect.return_value = False
            
            shell.do_connect("COM1 9600 1")
            
            assert shell.is_connected is False
            assert mock_modbus_worker.connect.called
    
    def test_do_disconnect(self, mock_modbus_worker):
        """Test disconnect command"""
        with patch('cli.bms_cli.ModbusWorker', return_value=mock_modbus_worker):
            shell = BMSCLIShell()
            shell.modbus_worker = mock_modbus_worker
            shell.is_connected = True
            
            shell.do_disconnect("")
            
            assert shell.is_connected is False
            assert mock_modbus_worker.disconnect.called
    
    def test_do_status_disconnected(self):
        """Test status command when disconnected"""
        shell = BMSCLIShell()
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            shell.do_status("")
            output = mock_stdout.getvalue()
            
        assert "Connection: Not connected" in output
        assert "Monitoring: Stopped" in output
        assert "Logging: Stopped" in output
    
    def test_do_status_connected(self, mock_modbus_worker):
        """Test status command when connected"""
        shell = BMSCLIShell()
        shell.modbus_worker = mock_modbus_worker
        shell.is_connected = True
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            shell.do_status("")
            output = mock_stdout.getvalue()
            
        assert "Connection: Connected" in output
    
    def test_do_session_create(self, mock_session_manager, sample_session_data):
        """Test session creation command"""
        shell = BMSCLIShell()
        shell.session_manager = mock_session_manager
        
        # Mock session creation
        mock_session = Mock()
        mock_session.session_id = sample_session_data['session_id']
        mock_session.name = sample_session_data['name']
        mock_session_manager.create_session.return_value = mock_session
        
        shell.do_session_create("test_session TEST001")
        
        assert mock_session_manager.create_session.called
        assert shell.current_session == mock_session
    
    def test_do_session_list(self, mock_session_manager):
        """Test session list command"""
        shell = BMSCLIShell()
        shell.session_manager = mock_session_manager
        
        # Mock session list
        mock_sessions = [Mock(session_id="test1", name="Test 1", status="active")]
        mock_session_manager.list_sessions.return_value = mock_sessions
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            shell.do_session_list("")
            output = mock_stdout.getvalue()
            
        assert "test1" in output
        assert "Test 1" in output
        assert mock_session_manager.list_sessions.called
    
    def test_do_session_load(self, mock_session_manager, sample_session_data):
        """Test session load command"""
        shell = BMSCLIShell()
        shell.session_manager = mock_session_manager
        
        # Mock session retrieval
        mock_session = Mock()
        mock_session.session_id = sample_session_data['session_id']
        mock_session_manager.get_session.return_value = mock_session
        
        shell.do_session_load("test-session-001")
        
        assert mock_session_manager.get_session.called
        assert shell.current_session == mock_session
    
    def test_do_session_delete(self, mock_session_manager):
        """Test session delete command"""
        shell = BMSCLIShell()
        shell.session_manager = mock_session_manager
        
        # Mock deletion success
        mock_session_manager.delete_session.return_value = True
        
        with patch('builtins.input', return_value='y'):
            shell.do_session_delete("test-session-001")
            
        assert mock_session_manager.delete_session.called
    
    def test_do_start_logging_without_session(self):
        """Test start logging command without active session"""
        shell = BMSCLIShell()
        shell.current_session = None
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            shell.do_start_logging("")
            output = mock_stdout.getvalue()
            
        assert "No active session" in output
        assert shell.is_logging is False
    
    def test_do_start_logging_with_session(self, mock_modbus_worker, sample_session_data):
        """Test start logging command with active session"""
        shell = BMSCLIShell()
        shell.modbus_worker = mock_modbus_worker
        shell.is_connected = True
        shell.current_session = Mock()
        shell.current_session.session_id = sample_session_data['session_id']
        
        with patch('threading.Thread') as mock_thread:
            shell.do_start_logging("")
            
        assert shell.is_logging is True
        assert mock_thread.called
    
    def test_do_stop_logging(self):
        """Test stop logging command"""
        shell = BMSCLIShell()
        shell.is_logging = True
        shell.monitoring_thread = Mock()
        
        shell.do_stop_logging("")
        
        assert shell.is_logging is False
    
    def test_do_read_data_not_connected(self):
        """Test read data command when not connected"""
        shell = BMSCLIShell()
        shell.is_connected = False
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            shell.do_read_data("")
            output = mock_stdout.getvalue()
            
        assert "Not connected" in output
    
    def test_do_read_data_connected(self, mock_modbus_worker, sample_battery_data):
        """Test read data command when connected"""
        shell = BMSCLIShell()
        shell.modbus_worker = mock_modbus_worker
        shell.is_connected = True
        
        # Mock data reading
        mock_modbus_worker.read_data.return_value = sample_battery_data
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            shell.do_read_data("")
            output = mock_stdout.getvalue()
            
        assert "cell_1" in output
        assert "3.25" in output
        assert mock_modbus_worker.read_data.called
    
    def test_do_list_ports(self):
        """Test list ports command"""
        shell = BMSCLIShell()
        
        with patch('serial.tools.list_ports.comports') as mock_comports:
            mock_comports.return_value = [
                Mock(device='COM1', description='USB Serial Port')
            ]
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                shell.do_list_ports("")
                output = mock_stdout.getvalue()
                
            assert "COM1" in output
            assert "USB Serial Port" in output
    
    def test_do_plugin_list(self, mock_plugin_manager):
        """Test plugin list command"""
        shell = BMSCLIShell()
        shell.plugin_manager = mock_plugin_manager
        
        # Mock plugin list
        mock_plugin_manager.get_loaded_plugins.return_value = ['battery_analyzer', 'csv_exporter']
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            shell.do_plugin_list("")
            output = mock_stdout.getvalue()
            
        assert "battery_analyzer" in output
        assert "csv_exporter" in output
    
    def test_do_plugin_info(self, mock_plugin_manager):
        """Test plugin info command"""
        shell = BMSCLIShell()
        shell.plugin_manager = mock_plugin_manager
        
        # Mock plugin info
        mock_info = {
            'name': 'Battery Analyzer',
            'version': '1.0.0',
            'commands': ['analyze_battery', 'cell_balance']
        }
        mock_plugin_manager.get_plugin_info.return_value = mock_info
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            shell.do_plugin_info("battery_analyzer")
            output = mock_stdout.getvalue()
            
        assert "Battery Analyzer" in output
        assert "1.0.0" in output
        assert "analyze_battery" in output
    
    def test_do_plugin_exec(self, mock_plugin_manager):
        """Test plugin execute command"""
        shell = BMSCLIShell()
        shell.plugin_manager = mock_plugin_manager
        
        # Mock plugin execution
        mock_plugin_manager.execute_plugin_command.return_value = "Plugin executed successfully"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            shell.do_plugin_exec("battery_analyzer analyze_battery")
            output = mock_stdout.getvalue()
            
        assert "Plugin executed successfully" in output
        assert mock_plugin_manager.execute_plugin_command.called
    
    def test_do_settings_get(self, mock_config_manager):
        """Test settings get command"""
        shell = BMSCLIShell()
        shell.config_manager = mock_config_manager
        
        # Mock config get
        mock_config_manager.get.return_value = 'COM1'
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            shell.do_settings_get("modbus.port")
            output = mock_stdout.getvalue()
            
        assert "COM1" in output
        assert mock_config_manager.get.called
    
    def test_do_settings_set(self, mock_config_manager):
        """Test settings set command"""
        shell = BMSCLIShell()
        shell.config_manager = mock_config_manager
        
        shell.do_settings_set("modbus.port COM2")
        
        assert mock_config_manager.set.called
        assert mock_config_manager.save.called
    
    def test_do_auto_start_enable(self):
        """Test auto start enable command"""
        shell = BMSCLIShell()
        shell.auto_start_stop_manager = Mock()
        
        shell.do_auto_start_enable("3.0 2.8")
        
        assert shell.auto_start_stop_manager.configure_auto_start.called
    
    def test_do_auto_stop_enable(self):
        """Test auto stop enable command"""
        shell = BMSCLIShell()
        shell.auto_start_stop_manager = Mock()
        
        shell.do_auto_stop_enable("4.2 0.1")
        
        assert shell.auto_start_stop_manager.configure_auto_stop.called
    
    def test_do_runaway_enable(self):
        """Test runaway detection enable command"""
        shell = BMSCLIShell()
        shell.cell_runaway_analyzer = Mock()
        
        shell.do_runaway_enable("0.1 5.0")
        
        assert shell.cell_runaway_analyzer.enable.called
    
    def test_do_runaway_disable(self):
        """Test runaway detection disable command"""
        shell = BMSCLIShell()
        shell.cell_runaway_analyzer = Mock()
        
        shell.do_runaway_disable("")
        
        assert shell.cell_runaway_analyzer.disable.called
    
    def test_do_version(self):
        """Test version command"""
        shell = BMSCLIShell()
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            shell.do_version("")
            output = mock_stdout.getvalue()
            
        assert "GA BMS CLI" in output
    
    def test_do_quit(self):
        """Test quit command"""
        shell = BMSCLIShell()
        
        result = shell.do_quit("")
        
        assert result is True
    
    def test_do_exit(self):
        """Test exit command"""
        shell = BMSCLIShell()
        
        result = shell.do_exit("")
        
        assert result is True
    
    def test_help_commands(self):
        """Test help commands are available"""
        shell = BMSCLIShell()
        
        # Test that help methods exist for major commands
        assert hasattr(shell, 'help_connect')
        assert hasattr(shell, 'help_disconnect')
        assert hasattr(shell, 'help_status')
        assert hasattr(shell, 'help_session_create')
        assert hasattr(shell, 'help_start_logging')
        assert hasattr(shell, 'help_stop_logging')
    
    def test_error_handling_invalid_command(self):
        """Test error handling for invalid commands"""
        shell = BMSCLIShell()
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            shell.default("invalid_command")
            output = mock_stdout.getvalue()
            
        assert "Unknown command" in output
    
    def test_monitoring_thread_lifecycle(self, mock_modbus_worker):
        """Test monitoring thread lifecycle"""
        shell = BMSCLIShell()
        shell.modbus_worker = mock_modbus_worker
        shell.is_connected = True
        shell.current_session = Mock()
        
        # Mock data reading
        mock_modbus_worker.read_data.return_value = {'cell_1': 3.25}
        
        with patch('threading.Thread') as mock_thread:
            shell.do_start_logging("")
            
            # Verify thread was created and started
            assert mock_thread.called
            assert mock_thread.return_value.start.called
    
    def test_signal_handling(self):
        """Test signal handling for graceful shutdown"""
        shell = BMSCLIShell()
        shell.is_logging = True
        shell.monitoring_thread = Mock()
        
        # Test signal handler
        shell._signal_handler(None, None)
        
        assert shell.is_logging is False
    
    def test_cleanup_on_exit(self, mock_modbus_worker):
        """Test cleanup operations on exit"""
        shell = BMSCLIShell()
        shell.modbus_worker = mock_modbus_worker
        shell.is_connected = True
        shell.is_logging = True
        shell.monitoring_thread = Mock()
        
        # Mock cleanup method
        with patch.object(shell, '_cleanup') as mock_cleanup:
            shell.do_quit("")
            
            # Cleanup should be called
            mock_cleanup.assert_called_once()


class TestBMSCLIArguments:
    """Test cases for CLI argument parsing"""
    
    def test_argument_parsing_help(self):
        """Test help argument parsing"""
        with patch('sys.argv', ['bms_cli.py', '--help']):
            with pytest.raises(SystemExit):
                from cli.bms_cli import main
                main()
    
    def test_argument_parsing_version(self):
        """Test version argument parsing"""
        with patch('sys.argv', ['bms_cli.py', '--version']):
            with pytest.raises(SystemExit):
                from cli.bms_cli import main
                main()
    
    def test_argument_parsing_command(self):
        """Test single command execution"""
        with patch('sys.argv', ['bms_cli.py', '--command', 'status']):
            with patch('cli.bms_cli.BMSCLIShell') as mock_shell:
                mock_shell_instance = Mock()
                mock_shell.return_value = mock_shell_instance
                
                from cli.bms_cli import main
                main()
                
                assert mock_shell_instance.onecmd.called
    
    def test_argument_parsing_script(self):
        """Test script file execution"""
        with patch('sys.argv', ['bms_cli.py', '--script', 'test_script.txt']):
            with patch('builtins.open', mock_open(read_data='status\nquit\n')):
                with patch('cli.bms_cli.BMSCLIShell') as mock_shell:
                    mock_shell_instance = Mock()
                    mock_shell.return_value = mock_shell_instance
                    
                    from cli.bms_cli import main
                    main()
                    
                    assert mock_shell_instance.onecmd.called


class TestBMSCLIIntegration:
    """Integration tests for CLI operations"""
    
    def test_full_workflow_session_and_logging(self, mock_modbus_worker, mock_session_manager):
        """Test complete workflow: connect, create session, start logging, stop logging"""
        with patch('cli.bms_cli.ModbusWorker', return_value=mock_modbus_worker), \
             patch('cli.bms_cli.SessionManager', return_value=mock_session_manager):
            
            shell = BMSCLIShell()
            
            # Connect
            mock_modbus_worker.connect.return_value = True
            shell.do_connect("COM1 9600 1")
            assert shell.is_connected is True
            
            # Create session
            mock_session = Mock()
            mock_session_manager.create_session.return_value = mock_session
            shell.do_session_create("test_session TEST001")
            assert shell.current_session == mock_session
            
            # Start logging
            with patch('threading.Thread') as mock_thread:
                shell.do_start_logging("")
                assert shell.is_logging is True
                assert mock_thread.called
            
            # Stop logging
            shell.do_stop_logging("")
            assert shell.is_logging is False
            
            # Disconnect
            shell.do_disconnect("")
            assert shell.is_connected is False
    
    def test_plugin_workflow(self, mock_plugin_manager):
        """Test plugin loading and execution workflow"""
        with patch('cli.bms_cli.PluginManager', return_value=mock_plugin_manager):
            shell = BMSCLIShell()
            
            # List plugins
            mock_plugin_manager.get_loaded_plugins.return_value = ['battery_analyzer']
            shell.do_plugin_list("")
            
            # Get plugin info
            mock_info = {'name': 'Battery Analyzer', 'version': '1.0.0'}
            mock_plugin_manager.get_plugin_info.return_value = mock_info
            shell.do_plugin_info("battery_analyzer")
            
            # Execute plugin command
            mock_plugin_manager.execute_plugin_command.return_value = "Success"
            shell.do_plugin_exec("battery_analyzer analyze_battery")
            
            assert mock_plugin_manager.execute_plugin_command.called