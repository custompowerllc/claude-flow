"""Configuration management for BK-Integration application."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DeviceConfig:
    """Device configuration container."""
    name: str
    device_url: str
    port: int
    defaults: Dict[str, Any]
    safety_limits: Dict[str, Any]


@dataclass
class TestProfile:
    """Battery test profile configuration."""
    name: str
    description: str
    charge_voltage: float
    charge_current: float
    discharge_current: float
    cutoff_voltage: float
    rest_time: int
    taper_threshold: float
    taper_duration: int
    max_charge_time_hours: float
    max_discharge_time_hours: float


class ConfigurationError(Exception):
    """Configuration-related error."""
    pass


class ConfigManager:
    """Manages application configuration with validation and environment overrides."""
    
    def __init__(self, config_path: Path = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. Defaults to 'config.json'
        """
        self.config_path = config_path or Path("config.json")
        self._config = {}
        self._load_config()
        self._apply_environment_overrides()
        self._validate_config()
    
    def _load_config(self) -> None:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                self._config = json.load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error reading config file: {e}")
    
    def _apply_environment_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        # Device URL overrides
        load_url = os.getenv('BK_LOAD_URL')
        if load_url:
            self._config.setdefault('devices', {}).setdefault('load_tester', {})['device_url'] = load_url
            logger.info(f"Override load tester URL from environment: {load_url}")
        
        power_url = os.getenv('BK_POWER_URL')
        if power_url:
            self._config.setdefault('devices', {}).setdefault('power_supply', {})['device_url'] = power_url
            logger.info(f"Override power supply URL from environment: {power_url}")
        
        # Serial port override
        load_port = os.getenv('BK_LOAD_PORT')
        if load_port:
            self._config.setdefault('devices', {}).setdefault('load_tester', {})['serial_port'] = load_port
            logger.info(f"Override load tester serial port from environment: {load_port}")
        
        # Logging level override
        log_level = os.getenv('BK_LOG_LEVEL')
        if log_level:
            self._config.setdefault('logging', {})['level'] = log_level
            logger.info(f"Override log level from environment: {log_level}")
    
    def _validate_config(self) -> None:
        """Validate configuration structure and values."""
        required_sections = ['devices', 'test_profiles']
        for section in required_sections:
            if section not in self._config:
                raise ConfigurationError(f"Missing required configuration section: {section}")
        
        # Validate devices section
        devices = self._config['devices']
        required_devices = ['load_tester', 'power_supply']
        for device in required_devices:
            if device not in devices:
                raise ConfigurationError(f"Missing device configuration: {device}")
            
            device_config = devices[device]
            required_fields = ['device_url', 'port']
            for field in required_fields:
                if field not in device_config:
                    raise ConfigurationError(f"Missing {field} in {device} configuration")
        
        # Validate test profiles
        profiles = self._config['test_profiles']
        if not profiles:
            raise ConfigurationError("No test profiles defined")
        
        for profile_name, profile in profiles.items():
            self._validate_test_profile(profile_name, profile)
        
        logger.info("Configuration validation passed")
    
    def _validate_test_profile(self, name: str, profile: Dict[str, Any]) -> None:
        """Validate a single test profile."""
        required_fields = [
            'charge_voltage', 'charge_current', 'discharge_current',
            'cutoff_voltage', 'rest_time'
        ]
        
        for field in required_fields:
            if field not in profile:
                raise ConfigurationError(f"Missing {field} in test profile '{name}'")
        
        # Validate numeric ranges
        if profile['charge_voltage'] <= 0 or profile['charge_voltage'] > 60:
            raise ConfigurationError(f"Invalid charge_voltage in profile '{name}': must be 0-60V")
        
        if profile['charge_current'] <= 0 or profile['charge_current'] > 5:
            raise ConfigurationError(f"Invalid charge_current in profile '{name}': must be 0-5A")
        
        if profile['discharge_current'] <= 0 or profile['discharge_current'] > 60:
            raise ConfigurationError(f"Invalid discharge_current in profile '{name}': must be 0-60A")
        
        if profile['cutoff_voltage'] <= 0 or profile['cutoff_voltage'] > 120:
            raise ConfigurationError(f"Invalid cutoff_voltage in profile '{name}': must be 0-120V")
        
        if profile['rest_time'] < 0 or profile['rest_time'] > 3600:
            raise ConfigurationError(f"Invalid rest_time in profile '{name}': must be 0-3600s")
    
    def get_load_config(self) -> Dict[str, Any]:
        """Get load tester configuration."""
        return self._config['devices']['load_tester'].copy()
    
    def get_power_config(self) -> Dict[str, Any]:
        """Get power supply configuration."""
        return self._config['devices']['power_supply'].copy()
    
    def get_test_profile(self, name: str) -> Dict[str, Any]:
        """Get test profile by name.
        
        Args:
            name: Profile name
            
        Returns:
            Test profile dictionary
            
        Raises:
            ConfigurationError: If profile not found
        """
        profiles = self._config.get('test_profiles', {})
        if name not in profiles:
            available = list(profiles.keys())
            raise ConfigurationError(f"Test profile '{name}' not found. Available: {available}")
        
        return profiles[name].copy()
    
    def list_test_profiles(self) -> Dict[str, str]:
        """List available test profiles with descriptions.
        
        Returns:
            Dict mapping profile names to descriptions
        """
        profiles = self._config.get('test_profiles', {})
        return {
            name: profile.get('description', f'{name} profile') 
            for name, profile in profiles.items()
        }
    
    def validate_test_profile(self, profile: Dict[str, Any]) -> bool:
        """Validate test profile parameters against device limits.
        
        Args:
            profile: Test profile dictionary
            
        Returns:
            True if valid
            
        Raises:
            ConfigurationError: If validation fails
        """
        try:
            self._validate_test_profile("validation", profile)
            
            # Additional validation against device limits
            load_config = self.get_load_config()
            power_config = self.get_power_config()
            
            load_limits = load_config.get('defaults', {})
            power_limits = power_config.get('safety_limits', {})
            
            if profile['discharge_current'] > load_limits.get('max_current', 60):
                raise ConfigurationError("Discharge current exceeds load tester maximum")
            
            if profile['charge_voltage'] > power_limits.get('max_voltage', 60):
                raise ConfigurationError("Charge voltage exceeds power supply maximum")
            
            if profile['charge_current'] > power_limits.get('max_current', 5):
                raise ConfigurationError("Charge current exceeds power supply maximum")
            
            return True
            
        except ConfigurationError:
            return False
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        defaults = {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': 'bk_integration.log'
        }
        return {**defaults, **self._config.get('logging', {})}
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration."""
        defaults = {
            'timeout': 30,
            'retry_count': 3,
            'retry_delay': 1.0
        }
        return {**defaults, **self._config.get('api', {})}
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        defaults = {
            'data_collection_interval': 1.0,
            'status_update_interval': 0.1,
            'safety_check_interval': 0.5
        }
        return {**defaults, **self._config.get('monitoring', {})}
    
    def get_safety_config(self) -> Dict[str, Any]:
        """Get safety configuration."""
        defaults = {
            'enable_emergency_stop': True,
            'auto_disconnect_on_error': True,
            'max_consecutive_failures': 5
        }
        return {**defaults, **self._config.get('safety', {})}
    
    def create_device_config(self, device_type: str) -> DeviceConfig:
        """Create a DeviceConfig object for the specified device type.
        
        Args:
            device_type: 'load_tester' or 'power_supply'
            
        Returns:
            DeviceConfig object
        """
        if device_type == 'load_tester':
            config = self.get_load_config()
        elif device_type == 'power_supply':
            config = self.get_power_config()
        else:
            raise ConfigurationError(f"Unknown device type: {device_type}")
        
        return DeviceConfig(
            name=config['name'],
            device_url=config['device_url'],
            port=config['port'],
            defaults=config.get('defaults', {}),
            safety_limits=config.get('safety_limits', {})
        )
    
    def create_test_profile_obj(self, name: str) -> TestProfile:
        """Create a TestProfile object for the specified profile.
        
        Args:
            name: Profile name
            
        Returns:
            TestProfile object
        """
        profile = self.get_test_profile(name)
        
        return TestProfile(
            name=name,
            description=profile.get('description', f'{name} profile'),
            charge_voltage=profile['charge_voltage'],
            charge_current=profile['charge_current'],
            discharge_current=profile['discharge_current'],
            cutoff_voltage=profile['cutoff_voltage'],
            rest_time=profile['rest_time'],
            taper_threshold=profile.get('taper_threshold', 0.1),
            taper_duration=profile.get('taper_duration', 60),
            max_charge_time_hours=profile.get('max_charge_time_hours', 12),
            max_discharge_time_hours=profile.get('max_discharge_time_hours', 24)
        )
    
    def save_config(self, backup: bool = True) -> None:
        """Save current configuration to file.
        
        Args:
            backup: Whether to create a backup of the existing file
        """
        if backup and self.config_path.exists():
            backup_path = self.config_path.with_suffix('.json.bak')
            self.config_path.rename(backup_path)
            logger.info(f"Created config backup: {backup_path}")
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            raise ConfigurationError(f"Error saving config: {e}")
    
    def update_test_profile(self, name: str, profile: Dict[str, Any]) -> None:
        """Update or create a test profile.
        
        Args:
            name: Profile name
            profile: Profile configuration
        """
        self._validate_test_profile(name, profile)
        self._config.setdefault('test_profiles', {})[name] = profile
        logger.info(f"Updated test profile: {name}")
    
    def remove_test_profile(self, name: str) -> None:
        """Remove a test profile.
        
        Args:
            name: Profile name
        """
        profiles = self._config.get('test_profiles', {})
        if name not in profiles:
            raise ConfigurationError(f"Test profile '{name}' not found")
        
        del profiles[name]
        logger.info(f"Removed test profile: {name}")
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get read-only copy of configuration."""
        return self._config.copy()