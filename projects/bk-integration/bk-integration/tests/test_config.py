"""Tests for configuration management."""

import pytest
import json
import tempfile
from pathlib import Path

from bk_integration.config import ConfigManager, ConfigurationError


class TestConfigManager:
    """Test configuration manager functionality."""
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing."""
        return {
            "devices": {
                "load_tester": {
                    "name": "BK8520",
                    "device_url": "http://localhost:8000",
                    "port": 8000,
                    "serial_port": "/dev/ttyUSB0",
                    "defaults": {
                        "max_current": 60.0,
                        "max_voltage": 120.0,
                        "max_power": 999.0
                    },
                    "safety_limits": {
                        "max_temperature": 85.0
                    }
                },
                "power_supply": {
                    "name": "BK9206b",
                    "device_url": "http://localhost:5300",
                    "port": 5300,
                    "defaults": {
                        "voltage": 15.0,
                        "current_limit": 2.0
                    },
                    "safety_limits": {
                        "max_voltage": 60.0,
                        "max_current": 5.0
                    }
                }
            },
            "test_profiles": {
                "default": {
                    "name": "Default Test",
                    "charge_voltage": 16.8,
                    "charge_current": 2.0,
                    "discharge_current": 5.0,
                    "cutoff_voltage": 10.0,
                    "rest_time": 60
                },
                "high_current": {
                    "name": "High Current Test",
                    "charge_voltage": 16.8,
                    "charge_current": 4.0,
                    "discharge_current": 10.0,
                    "cutoff_voltage": 10.0,
                    "rest_time": 120
                }
            },
            "logging": {
                "level": "INFO",
                "file": "test.log"
            },
            "api": {
                "timeout": 30,
                "retry_count": 3
            }
        }
    
    @pytest.fixture
    def temp_config_file(self, sample_config):
        """Create temporary configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_config, f)
            config_path = Path(f.name)
        
        yield config_path
        
        # Cleanup
        config_path.unlink()
    
    def test_config_loading(self, temp_config_file):
        """Test configuration file loading."""
        config = ConfigManager(temp_config_file)
        
        assert config.config is not None
        assert 'devices' in config.config
        assert 'test_profiles' in config.config
    
    def test_missing_config_file(self):
        """Test error handling for missing config file."""
        with pytest.raises(ConfigurationError):
            ConfigManager(Path("nonexistent.json"))
    
    def test_invalid_json_config(self):
        """Test error handling for invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            invalid_config_path = Path(f.name)
        
        try:
            with pytest.raises(ConfigurationError):
                ConfigManager(invalid_config_path)
        finally:
            invalid_config_path.unlink()
    
    def test_get_device_configs(self, temp_config_file):
        """Test device configuration retrieval."""
        config = ConfigManager(temp_config_file)
        
        load_config = config.get_load_config()
        assert load_config['name'] == 'BK8520'
        assert load_config['device_url'] == 'http://localhost:8000'
        
        power_config = config.get_power_config()
        assert power_config['name'] == 'BK9206b'
        assert power_config['device_url'] == 'http://localhost:5300'
    
    def test_get_test_profiles(self, temp_config_file):
        """Test test profile retrieval."""
        config = ConfigManager(temp_config_file)
        
        # Get existing profile
        default_profile = config.get_test_profile('default')
        assert default_profile['charge_voltage'] == 16.8
        assert default_profile['charge_current'] == 2.0
        
        # Test nonexistent profile
        with pytest.raises(ConfigurationError):
            config.get_test_profile('nonexistent')
    
    def test_list_test_profiles(self, temp_config_file):
        """Test test profile listing."""
        config = ConfigManager(temp_config_file)
        
        profiles = config.list_test_profiles()
        assert 'default' in profiles
        assert 'high_current' in profiles
        assert len(profiles) == 2
    
    def test_validate_test_profile_valid(self, temp_config_file):
        """Test validation of valid test profile."""
        config = ConfigManager(temp_config_file)
        
        valid_profile = {
            'charge_voltage': 15.0,
            'charge_current': 2.0,
            'discharge_current': 5.0,
            'cutoff_voltage': 10.0,
            'rest_time': 60
        }
        
        assert config.validate_test_profile(valid_profile) == True
    
    def test_validate_test_profile_invalid(self, temp_config_file):
        """Test validation of invalid test profile."""
        config = ConfigManager(temp_config_file)
        
        # Invalid voltage
        invalid_profile = {
            'charge_voltage': 70.0,  # Exceeds BK9206b max
            'charge_current': 2.0,
            'discharge_current': 5.0,
            'cutoff_voltage': 10.0,
            'rest_time': 60
        }
        
        assert config.validate_test_profile(invalid_profile) == False
        
        # Cutoff voltage higher than charge voltage
        invalid_profile2 = {
            'charge_voltage': 15.0,
            'charge_current': 2.0,
            'discharge_current': 5.0,
            'cutoff_voltage': 20.0,  # Higher than charge voltage
            'rest_time': 60
        }
        
        assert config.validate_test_profile(invalid_profile2) == False
    
    def test_environment_overrides(self, temp_config_file, monkeypatch):
        """Test environment variable overrides."""
        monkeypatch.setenv('BK_LOAD_URL', 'http://override:8000')
        monkeypatch.setenv('BK_LOG_LEVEL', 'DEBUG')
        
        config = ConfigManager(temp_config_file)
        
        load_config = config.get_load_config()
        assert load_config['device_url'] == 'http://override:8000'
        
        log_config = config.get_logging_config()
        assert log_config['level'] == 'DEBUG'
    
    def test_get_configuration_sections(self, temp_config_file):
        """Test retrieval of different configuration sections."""
        config = ConfigManager(temp_config_file)
        
        # Logging config
        log_config = config.get_logging_config()
        assert log_config['level'] == 'INFO'
        assert log_config['file'] == 'test.log'
        assert 'format' in log_config  # Should include default
        
        # API config
        api_config = config.get_api_config()
        assert api_config['timeout'] == 30
        assert api_config['retry_count'] == 3
        assert 'retry_delay' in api_config  # Should include default
        
        # Monitoring config (with defaults)
        monitor_config = config.get_monitoring_config()
        assert 'data_collection_interval' in monitor_config
        assert 'status_update_interval' in monitor_config
        
        # Safety config (with defaults)
        safety_config = config.get_safety_config()
        assert 'enable_emergency_stop' in safety_config
        assert safety_config['enable_emergency_stop'] == True
    
    def test_create_device_config_objects(self, temp_config_file):
        """Test creation of device configuration objects."""
        config = ConfigManager(temp_config_file)
        
        # Load tester device config
        load_device_config = config.create_device_config('load_tester')
        assert load_device_config.name == 'BK8520'
        assert load_device_config.device_url == 'http://localhost:8000'
        assert load_device_config.port == 8000
        
        # Power supply device config
        power_device_config = config.create_device_config('power_supply')
        assert power_device_config.name == 'BK9206b'
        assert power_device_config.device_url == 'http://localhost:5300'
        
        # Invalid device type
        with pytest.raises(ConfigurationError):
            config.create_device_config('invalid_device')
    
    def test_create_test_profile_objects(self, temp_config_file):
        """Test creation of test profile objects."""
        config = ConfigManager(temp_config_file)
        
        profile_obj = config.create_test_profile_obj('default')
        assert profile_obj.name == 'default'
        assert profile_obj.charge_voltage == 16.8
        assert profile_obj.charge_current == 2.0
        assert profile_obj.discharge_current == 5.0
        assert profile_obj.cutoff_voltage == 10.0
        assert profile_obj.rest_time == 60
    
    def test_update_test_profile(self, temp_config_file):
        """Test updating and creating test profiles."""
        config = ConfigManager(temp_config_file)
        
        # Create new profile
        new_profile = {
            'name': 'custom',
            'charge_voltage': 14.4,
            'charge_current': 1.5,
            'discharge_current': 3.0,
            'cutoff_voltage': 9.0,
            'rest_time': 30
        }
        
        config.update_test_profile('custom', new_profile)
        
        # Verify it was added
        retrieved_profile = config.get_test_profile('custom')
        assert retrieved_profile['charge_voltage'] == 14.4
        
        # Update existing profile
        updated_profile = new_profile.copy()
        updated_profile['charge_current'] = 2.5
        
        config.update_test_profile('custom', updated_profile)
        retrieved_profile = config.get_test_profile('custom')
        assert retrieved_profile['charge_current'] == 2.5
    
    def test_remove_test_profile(self, temp_config_file):
        """Test removing test profiles."""
        config = ConfigManager(temp_config_file)
        
        # Remove existing profile
        config.remove_test_profile('default')
        
        with pytest.raises(ConfigurationError):
            config.get_test_profile('default')
        
        # Try to remove nonexistent profile
        with pytest.raises(ConfigurationError):
            config.remove_test_profile('nonexistent')
    
    def test_config_validation_missing_sections(self, sample_config):
        """Test configuration validation with missing sections."""
        # Remove required section
        del sample_config['devices']
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_config, f)
            config_path = Path(f.name)
        
        try:
            with pytest.raises(ConfigurationError):
                ConfigManager(config_path)
        finally:
            config_path.unlink()
    
    def test_config_validation_missing_device(self, sample_config):
        """Test configuration validation with missing device."""
        # Remove required device
        del sample_config['devices']['load_tester']
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_config, f)
            config_path = Path(f.name)
        
        try:
            with pytest.raises(ConfigurationError):
                ConfigManager(config_path)
        finally:
            config_path.unlink()
    
    def test_config_save(self, temp_config_file):
        """Test configuration saving."""
        config = ConfigManager(temp_config_file)
        
        # Modify configuration
        config.update_test_profile('test_save', {
            'name': 'Save Test',
            'charge_voltage': 12.0,
            'charge_current': 1.0,
            'discharge_current': 2.0,
            'cutoff_voltage': 8.0,
            'rest_time': 30
        })
        
        # Save configuration
        config.save_config()
        
        # Load new instance and verify changes
        config2 = ConfigManager(temp_config_file)
        profiles = config2.list_test_profiles()
        assert 'test_save' in profiles