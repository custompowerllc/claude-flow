"""Tests for ConfigManager class."""

import pytest
import json
import tempfile
import os
from pathlib import Path
from gehc_phtc_test.src.config.config_manager import ConfigManager, ConfigError


class TestConfigManager:
    """Test cases for ConfigManager class."""

    @pytest.fixture
    def sample_config_data(self):
        """Sample configuration data for tests."""
        return {
            "serial": {
                "port": "/dev/ttyUSB0",
                "baudrate": 9600,
                "bytesize": 8,
                "parity": "N",
                "stopbits": 1,
                "timeout": 1.0
            },
            "timing": {
                "command_delay": 0.1,
                "response_timeout": 2.0,
                "retry_count": 3
            }
        }

    @pytest.fixture
    def sample_commands_data(self):
        """Sample commands data for tests."""
        return {
            "protocol_version": "1.0",
            "test_profiles": {
                "quick_test": [
                    "GET_SYSTEM_STATUS",
                    "GET_TEMPERATURE"
                ],
                "full_implemented": [
                    "GET_SYSTEM_STATUS",
                    "GET_TEMPERATURE",
                    "GET_PRESSURE"
                ],
                "development_test": [
                    "GET_SYSTEM_STATUS",
                    "GET_TEMPERATURE",
                    "GET_PRESSURE",
                    "GET_DEBUG_INFO"
                ]
            },
            "commands": {
                "GET_SYSTEM_STATUS": {
                    "code": 0x01,
                    "description": "Get system status",
                    "implemented": True,
                    "enabled": True,
                    "data_type": "UNSIGNED_INT_16",
                    "scaling": {
                        "granularity": 1.0,
                        "unit": "",
                        "offset": 0
                    },
                    "validation": {
                        "min_value": 0,
                        "max_value": 65535
                    }
                },
                "GET_TEMPERATURE": {
                    "code": 0x02,
                    "description": "Get temperature",
                    "implemented": True,
                    "enabled": True,
                    "data_type": "SIGNED_INT_16",
                    "scaling": {
                        "granularity": 0.1,
                        "unit": "°C",
                        "offset": -40.0
                    },
                    "validation": {
                        "min_value": -40.0,
                        "max_value": 85.0
                    }
                },
                "GET_PRESSURE": {
                    "code": 0x03,
                    "description": "Get pressure",
                    "implemented": False,
                    "enabled": False,
                    "data_type": "UNSIGNED_INT_16",
                    "scaling": {
                        "granularity": 0.01,
                        "unit": "kPa",
                        "offset": 0
                    }
                },
                "GET_DEBUG_INFO": {
                    "code": 0x04,
                    "description": "Get debug information",
                    "implemented": True,
                    "enabled": False,
                    "data_type": "STRING",
                    "scaling": {
                        "granularity": 1.0,
                        "unit": "",
                        "offset": 0
                    }
                }
            }
        }

    @pytest.fixture
    def temp_config_file(self, sample_config_data):
        """Create temporary config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_config_data, f)
            temp_file = f.name
        yield temp_file
        os.unlink(temp_file)

    @pytest.fixture
    def temp_commands_file(self, sample_commands_data):
        """Create temporary commands file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_commands_data, f)
            temp_file = f.name
        yield temp_file
        os.unlink(temp_file)

    def test_load_valid_config(self, temp_config_file):
        """Test loading valid configuration file."""
        manager = ConfigManager()
        config = manager.load_config(temp_config_file)
        
        assert config["serial"]["port"] == "/dev/ttyUSB0"
        assert config["serial"]["baudrate"] == 9600
        assert config["timing"]["command_delay"] == 0.1

    def test_load_nonexistent_config(self):
        """Test loading nonexistent configuration file."""
        manager = ConfigManager()
        
        with pytest.raises(ConfigError, match="Configuration file not found"):
            manager.load_config("nonexistent.json")

    def test_load_invalid_json(self):
        """Test loading invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_file = f.name
        
        try:
            manager = ConfigManager()
            with pytest.raises(ConfigError, match="Invalid JSON format"):
                manager.load_config(temp_file)
        finally:
            os.unlink(temp_file)

    def test_validate_config_valid(self, sample_config_data):
        """Test validation of valid configuration."""
        manager = ConfigManager()
        
        # Should not raise exception
        is_valid = manager.validate_config(sample_config_data)
        assert is_valid == True

    def test_validate_config_missing_section(self):
        """Test validation of config with missing required section."""
        manager = ConfigManager()
        invalid_config = {
            "serial": {
                "port": "/dev/ttyUSB0",
                "baudrate": 9600
            }
            # Missing timing section
        }
        
        is_valid = manager.validate_config(invalid_config)
        assert is_valid == False

    def test_validate_config_missing_field(self):
        """Test validation of config with missing required field."""
        manager = ConfigManager()
        invalid_config = {
            "serial": {
                "port": "/dev/ttyUSB0"
                # Missing baudrate
            },
            "timing": {
                "command_delay": 0.1
            }
        }
        
        is_valid = manager.validate_config(invalid_config)
        assert is_valid == False

    def test_load_commands_valid(self, temp_commands_file):
        """Test loading valid commands file."""
        manager = ConfigManager()
        commands = manager.load_commands(temp_commands_file)
        
        assert "commands" in commands
        assert "test_profiles" in commands
        assert "GET_SYSTEM_STATUS" in commands["commands"]
        assert commands["commands"]["GET_SYSTEM_STATUS"]["code"] == 0x01

    def test_get_test_profile_quick(self, temp_commands_file):
        """Test getting quick test profile."""
        manager = ConfigManager()
        commands = manager.load_commands(temp_commands_file)
        
        profile_commands = manager.get_test_profile(commands, "quick_test")
        
        assert len(profile_commands) == 2
        assert "GET_SYSTEM_STATUS" in profile_commands
        assert "GET_TEMPERATURE" in profile_commands

    def test_get_test_profile_nonexistent(self, temp_commands_file):
        """Test getting nonexistent test profile."""
        manager = ConfigManager()
        commands = manager.load_commands(temp_commands_file)
        
        with pytest.raises(ConfigError, match="Test profile .* not found"):
            manager.get_test_profile(commands, "nonexistent_profile")

    def test_filter_enabled_commands(self, temp_commands_file):
        """Test filtering enabled commands only."""
        manager = ConfigManager()
        commands = manager.load_commands(temp_commands_file)
        
        enabled_commands = manager.filter_commands(commands["commands"], enabled_only=True)
        
        # Only GET_SYSTEM_STATUS and GET_TEMPERATURE are enabled
        assert len(enabled_commands) == 2
        assert "GET_SYSTEM_STATUS" in enabled_commands
        assert "GET_TEMPERATURE" in enabled_commands
        assert "GET_PRESSURE" not in enabled_commands
        assert "GET_DEBUG_INFO" not in enabled_commands

    def test_filter_implemented_commands(self, temp_commands_file):
        """Test filtering implemented commands only."""
        manager = ConfigManager()
        commands = manager.load_commands(temp_commands_file)
        
        implemented_commands = manager.filter_commands(commands["commands"], implemented_only=True)
        
        # GET_SYSTEM_STATUS, GET_TEMPERATURE, and GET_DEBUG_INFO are implemented
        assert len(implemented_commands) == 3
        assert "GET_SYSTEM_STATUS" in implemented_commands
        assert "GET_TEMPERATURE" in implemented_commands
        assert "GET_DEBUG_INFO" in implemented_commands
        assert "GET_PRESSURE" not in implemented_commands

    def test_filter_enabled_and_implemented_commands(self, temp_commands_file):
        """Test filtering both enabled and implemented commands."""
        manager = ConfigManager()
        commands = manager.load_commands(temp_commands_file)
        
        filtered_commands = manager.filter_commands(
            commands["commands"], 
            enabled_only=True, 
            implemented_only=True
        )
        
        # Only GET_SYSTEM_STATUS and GET_TEMPERATURE are both enabled and implemented
        assert len(filtered_commands) == 2
        assert "GET_SYSTEM_STATUS" in filtered_commands
        assert "GET_TEMPERATURE" in filtered_commands

    def test_get_command_config(self, temp_commands_file):
        """Test getting specific command configuration."""
        manager = ConfigManager()
        commands = manager.load_commands(temp_commands_file)
        
        cmd_config = manager.get_command_config(commands["commands"], "GET_TEMPERATURE")
        
        assert cmd_config["code"] == 0x02
        assert cmd_config["data_type"] == "SIGNED_INT_16"
        assert cmd_config["scaling"]["unit"] == "°C"
        assert cmd_config["scaling"]["granularity"] == 0.1

    def test_get_nonexistent_command_config(self, temp_commands_file):
        """Test getting configuration for nonexistent command."""
        manager = ConfigManager()
        commands = manager.load_commands(temp_commands_file)
        
        with pytest.raises(ConfigError, match="Command .* not found"):
            manager.get_command_config(commands["commands"], "NONEXISTENT_COMMAND")

    def test_validate_commands_integrity_valid(self, temp_commands_file):
        """Test validation of commands with good integrity."""
        manager = ConfigManager()
        commands = manager.load_commands(temp_commands_file)
        
        is_valid = manager.validate_commands_integrity(commands)
        assert is_valid == True

    def test_validate_commands_integrity_duplicate_codes(self):
        """Test validation with duplicate command codes."""
        manager = ConfigManager()
        invalid_commands = {
            "commands": {
                "CMD1": {"code": 0x01, "implemented": True, "enabled": True},
                "CMD2": {"code": 0x01, "implemented": True, "enabled": True}  # Duplicate code
            }
        }
        
        is_valid = manager.validate_commands_integrity(invalid_commands)
        assert is_valid == False

    def test_get_serial_config(self, temp_config_file):
        """Test getting serial configuration."""
        manager = ConfigManager()
        config = manager.load_config(temp_config_file)
        
        serial_config = manager.get_serial_config(config)
        
        assert serial_config["port"] == "/dev/ttyUSB0"
        assert serial_config["baudrate"] == 9600
        assert serial_config["timeout"] == 1.0

    def test_get_timing_config(self, temp_config_file):
        """Test getting timing configuration."""
        manager = ConfigManager()
        config = manager.load_config(temp_config_file)
        
        timing_config = manager.get_timing_config(config)
        
        assert timing_config["command_delay"] == 0.1
        assert timing_config["response_timeout"] == 2.0
        assert timing_config["retry_count"] == 3

    def test_update_command_status(self, temp_commands_file):
        """Test updating command enable/disable status."""
        manager = ConfigManager()
        commands = manager.load_commands(temp_commands_file)
        
        # Initially GET_DEBUG_INFO is disabled
        assert commands["commands"]["GET_DEBUG_INFO"]["enabled"] == False
        
        # Update status
        updated_commands = manager.update_command_status(
            commands["commands"], 
            "GET_DEBUG_INFO", 
            enabled=True
        )
        
        assert updated_commands["GET_DEBUG_INFO"]["enabled"] == True