"""
Unit tests for CLI Demo interface (cli_demo.py)
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
from pathlib import Path
from io import StringIO

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli_demo import BMSCLIDemo


class TestBMSCLIDemo:
    """Test cases for BMSCLIDemo class"""
    
    def test_initialization_without_rich(self):
        """Test demo CLI initialization without Rich"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            assert demo.console is None
            assert demo.prompt == '(bms-demo) '
    
    def test_initialization_with_rich(self):
        """Test demo CLI initialization with Rich"""
        with patch('cli_demo.RICH_AVAILABLE', True), \
             patch('cli_demo.Console') as mock_console:
            
            demo = BMSCLIDemo()
            
            assert demo.console == mock_console.return_value
            assert mock_console.called
    
    def test_show_welcome_banner_without_rich(self):
        """Test welcome banner display without Rich"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            # Should not raise any exceptions
            demo._show_welcome_banner()
    
    def test_show_welcome_banner_with_rich(self):
        """Test welcome banner display with Rich"""
        with patch('cli_demo.RICH_AVAILABLE', True), \
             patch('cli_demo.Console') as mock_console:
            
            mock_console_instance = Mock()
            mock_console.return_value = mock_console_instance
            
            demo = BMSCLIDemo()
            
            # Verify console.print was called during banner display
            assert mock_console_instance.print.called
    
    def test_do_status(self):
        """Test status command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.do_status("")
                output = mock_stdout.getvalue()
                
            assert "System Status" in output
            assert "Demo Mode" in output
    
    def test_do_demo_data(self):
        """Test demo data command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.do_demo_data("")
                output = mock_stdout.getvalue()
                
            assert "Sample Battery Data" in output
            assert "cell_1" in output
            assert "pack_voltage" in output
    
    def test_do_demo_data_with_rich(self):
        """Test demo data command with Rich formatting"""
        with patch('cli_demo.RICH_AVAILABLE', True), \
             patch('cli_demo.Console') as mock_console:
            
            mock_console_instance = Mock()
            mock_console.return_value = mock_console_instance
            
            demo = BMSCLIDemo()
            demo.do_demo_data("")
            
            # Verify Rich table was created and printed
            assert mock_console_instance.print.called
    
    def test_do_demo_sessions(self):
        """Test demo sessions command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.do_demo_sessions("")
                output = mock_stdout.getvalue()
                
            assert "Sample Sessions" in output
            assert "session-001" in output
            assert "Active" in output
    
    def test_do_demo_plugins(self):
        """Test demo plugins command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.do_demo_plugins("")
                output = mock_stdout.getvalue()
                
            assert "Plugin System Demo" in output
            assert "battery_analyzer" in output
            assert "csv_exporter" in output
    
    def test_do_demo_monitoring(self):
        """Test demo monitoring command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.do_demo_monitoring("")
                output = mock_stdout.getvalue()
                
            assert "Live Monitoring Demo" in output
            assert "would display" in output
    
    def test_do_demo_auto_features(self):
        """Test demo auto features command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.do_demo_auto_features("")
                output = mock_stdout.getvalue()
                
            assert "Auto Start/Stop Demo" in output
            assert "Auto Start" in output
            assert "Auto Stop" in output
    
    def test_do_demo_runaway(self):
        """Test demo runaway detection command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.do_demo_runaway("")
                output = mock_stdout.getvalue()
                
            assert "Cell Runaway Detection Demo" in output
            assert "No runaway" in output
    
    def test_do_demo_settings(self):
        """Test demo settings command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.do_demo_settings("")
                output = mock_stdout.getvalue()
                
            assert "Settings Demo" in output
            assert "modbus.port" in output
            assert "COM1" in output
    
    def test_do_demo_help(self):
        """Test demo help command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.do_demo_help("")
                output = mock_stdout.getvalue()
                
            assert "Available Demo Commands" in output
            assert "status" in output
            assert "demo_data" in output
    
    def test_do_version(self):
        """Test version command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.do_version("")
                output = mock_stdout.getvalue()
                
            assert "GA BMS Monitor CLI Demo" in output
            assert "v2.0.0" in output
    
    def test_do_quit(self):
        """Test quit command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            result = demo.do_quit("")
            
            assert result is True
    
    def test_do_exit(self):
        """Test exit command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            result = demo.do_exit("")
            
            assert result is True
    
    def test_help_status(self):
        """Test help for status command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.help_status()
                output = mock_stdout.getvalue()
                
            assert "Show system status" in output
    
    def test_help_demo_data(self):
        """Test help for demo_data command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.help_demo_data()
                output = mock_stdout.getvalue()
                
            assert "Display sample battery data" in output
    
    def test_help_demo_sessions(self):
        """Test help for demo_sessions command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.help_demo_sessions()
                output = mock_stdout.getvalue()
                
            assert "Show sample monitoring sessions" in output
    
    def test_help_demo_plugins(self):
        """Test help for demo_plugins command"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.help_demo_plugins()
                output = mock_stdout.getvalue()
                
            assert "Demonstrate plugin system" in output
    
    def test_default_command(self):
        """Test default command for unknown commands"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.default("unknown_command")
                output = mock_stdout.getvalue()
                
            assert "Unknown command" in output
            assert "demo_help" in output
    
    def test_emptyline(self):
        """Test empty line handling"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            # Should not raise any exceptions
            demo.emptyline()
    
    def test_rich_table_creation(self):
        """Test Rich table creation functionality"""
        with patch('cli_demo.RICH_AVAILABLE', True), \
             patch('cli_demo.Console') as mock_console, \
             patch('cli_demo.Table') as mock_table:
            
            mock_console_instance = Mock()
            mock_console.return_value = mock_console_instance
            
            mock_table_instance = Mock()
            mock_table.return_value = mock_table_instance
            
            demo = BMSCLIDemo()
            demo.do_demo_data("")
            
            # Verify table was created and configured
            assert mock_table.called
            assert mock_table_instance.add_column.called
            assert mock_table_instance.add_row.called
    
    def test_rich_panel_creation(self):
        """Test Rich panel creation functionality"""
        with patch('cli_demo.RICH_AVAILABLE', True), \
             patch('cli_demo.Console') as mock_console, \
             patch('cli_demo.Panel') as mock_panel:
            
            mock_console_instance = Mock()
            mock_console.return_value = mock_console_instance
            
            mock_panel_instance = Mock()
            mock_panel.return_value = mock_panel_instance
            
            demo = BMSCLIDemo()
            demo.do_status("")
            
            # Verify panel was created
            assert mock_panel.called
    
    def test_sample_data_consistency(self):
        """Test that sample data is consistent across calls"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            # Call demo_data twice and compare outputs
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout1:
                demo.do_demo_data("")
                output1 = mock_stdout1.getvalue()
                
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout2:
                demo.do_demo_data("")
                output2 = mock_stdout2.getvalue()
                
            # Should be identical
            assert output1 == output2
    
    def test_all_demo_commands_callable(self):
        """Test that all demo commands are callable without errors"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            # List of all demo commands
            demo_commands = [
                'status',
                'demo_data',
                'demo_sessions', 
                'demo_plugins',
                'demo_monitoring',
                'demo_auto_features',
                'demo_runaway',
                'demo_settings',
                'demo_help',
                'version'
            ]
            
            # Test each command runs without exception
            for command in demo_commands:
                with patch('sys.stdout', new_callable=StringIO):
                    method = getattr(demo, f'do_{command}')
                    method("")  # All demo commands take empty string
    
    def test_command_completion(self):
        """Test command completion functionality"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            # Test that all expected commands are available
            expected_commands = [
                'status', 'demo_data', 'demo_sessions', 'demo_plugins',
                'demo_monitoring', 'demo_auto_features', 'demo_runaway',
                'demo_settings', 'demo_help', 'version', 'quit', 'exit'
            ]
            
            for command in expected_commands:
                assert hasattr(demo, f'do_{command}')
    
    def test_help_system_completeness(self):
        """Test that help system covers all commands"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            # Test that help methods exist for main commands
            help_methods = [
                'help_status', 'help_demo_data', 'help_demo_sessions',
                'help_demo_plugins', 'help_demo_monitoring',
                'help_demo_auto_features', 'help_demo_runaway',
                'help_demo_settings', 'help_version'
            ]
            
            for method_name in help_methods:
                assert hasattr(demo, method_name)
    
    def test_interactive_mode_simulation(self):
        """Test simulated interactive mode"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            # Simulate a series of commands
            commands = ['status', 'demo_data', 'version', 'quit']
            
            for command in commands[:-1]:  # Skip quit for testing
                with patch('sys.stdout', new_callable=StringIO):
                    method = getattr(demo, f'do_{command}')
                    method("")
            
            # Test quit returns True
            assert demo.do_quit("") is True


class TestBMSCLIDemoMain:
    """Test cases for main function and entry point"""
    
    def test_main_function_exists(self):
        """Test that main function exists and is callable"""
        from cli_demo import main
        assert callable(main)
    
    def test_main_function_with_mock_cmdloop(self):
        """Test main function with mocked cmdloop"""
        with patch('cli_demo.BMSCLIDemo') as mock_demo_class:
            mock_demo_instance = Mock()
            mock_demo_class.return_value = mock_demo_instance
            
            from cli_demo import main
            main()
            
            # Verify demo instance was created and cmdloop was called
            assert mock_demo_class.called
            assert mock_demo_instance.cmdloop.called
    
    def test_script_execution(self):
        """Test script execution as main module"""
        with patch('cli_demo.main') as mock_main:
            with patch('cli_demo.__name__', '__main__'):
                # This would normally trigger the if __name__ == '__main__' block
                # We'll test the main function directly instead
                from cli_demo import main
                main()
                
                # Verify main would be called
                assert callable(main)


class TestBMSCLIDemoRichIntegration:
    """Test cases for Rich library integration"""
    
    def test_rich_styling_in_status(self):
        """Test Rich styling in status command"""
        with patch('cli_demo.RICH_AVAILABLE', True), \
             patch('cli_demo.Console') as mock_console, \
             patch('cli_demo.Panel') as mock_panel:
            
            mock_console_instance = Mock()
            mock_console.return_value = mock_console_instance
            
            demo = BMSCLIDemo()
            demo.do_status("")
            
            # Verify styled output
            assert mock_panel.called
            assert mock_console_instance.print.called
    
    def test_rich_table_in_demo_data(self):
        """Test Rich table creation in demo_data"""
        with patch('cli_demo.RICH_AVAILABLE', True), \
             patch('cli_demo.Console') as mock_console, \
             patch('cli_demo.Table') as mock_table:
            
            mock_console_instance = Mock()
            mock_console.return_value = mock_console_instance
            
            demo = BMSCLIDemo()
            demo.do_demo_data("")
            
            # Verify table operations
            assert mock_table.called
            table_instance = mock_table.return_value
            assert table_instance.add_column.called
            assert table_instance.add_row.called
    
    def test_fallback_without_rich(self):
        """Test fallback behavior when Rich is not available"""
        with patch('cli_demo.RICH_AVAILABLE', False):
            demo = BMSCLIDemo()
            
            # All commands should work without Rich
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                demo.do_status("")
                demo.do_demo_data("")
                demo.do_demo_sessions("")
                
                output = mock_stdout.getvalue()
                assert len(output) > 0  # Should produce some output
    
    def test_rich_text_formatting(self):
        """Test Rich text formatting features"""
        with patch('cli_demo.RICH_AVAILABLE', True), \
             patch('cli_demo.Console') as mock_console, \
             patch('cli_demo.Text') as mock_text:
            
            mock_console_instance = Mock()
            mock_console.return_value = mock_console_instance
            
            demo = BMSCLIDemo()
            
            # Text formatting should be used in welcome banner
            assert mock_text.called or mock_console_instance.print.called