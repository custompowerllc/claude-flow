"""Configuration management for GEHC PHTC RS422 test application."""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from copy import deepcopy


class ConfigError(Exception):
    """Exception raised for configuration-related errors."""
    pass


class ConfigManager:
    """Manager for application configuration and command definitions."""

    def __init__(self):
        """Initialize the configuration manager."""
        self._required_config_sections = ['serial', 'timing']
        self._required_serial_fields = ['port', 'baudrate']
        self._required_timing_fields = ['command_delay']
        self._required_command_fields = ['code', 'description', 'implemented', 'enabled', 'data_type']

    def load_config(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            ConfigError: If file not found or invalid JSON
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise ConfigError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON format in {config_path}: {e}")
        except IOError as e:
            raise ConfigError(f"Error reading configuration file {config_path}: {e}")

    def load_commands(self, commands_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load command definitions from JSON file.
        
        Args:
            commands_path: Path to commands file
            
        Returns:
            Dictionary containing command definitions
            
        Raises:
            ConfigError: If file not found or invalid JSON
        """
        return self.load_config(commands_path)  # Same loading logic

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration structure and required fields.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required sections
            for section in self._required_config_sections:
                if section not in config:
                    return False
            
            # Validate serial section
            serial_config = config.get('serial', {})
            for field in self._required_serial_fields:
                if field not in serial_config:
                    return False
            
            # Validate timing section
            timing_config = config.get('timing', {})
            for field in self._required_timing_fields:
                if field not in timing_config:
                    return False
            
            return True
        except Exception:
            return False

    def validate_commands_integrity(self, commands: Dict[str, Any]) -> bool:
        """
        Validate command definitions for integrity and consistency.
        
        Args:
            commands: Commands dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if 'commands' not in commands:
                return False
            
            command_defs = commands['commands']
            used_codes = set()
            
            for cmd_name, cmd_config in command_defs.items():
                # Check required fields
                for field in self._required_command_fields:
                    if field not in cmd_config:
                        return False
                
                # Check for duplicate command codes
                code = cmd_config['code']
                if code in used_codes:
                    return False
                used_codes.add(code)
            
            return True
        except Exception:
            return False

    def get_test_profile(self, commands: Dict[str, Any], profile_name: str) -> List[str]:
        """
        Get list of commands for a specific test profile.
        
        Args:
            commands: Commands configuration dictionary
            profile_name: Name of test profile
            
        Returns:
            List of command names in the profile
            
        Raises:
            ConfigError: If profile not found
        """
        if 'test_profiles' not in commands:
            raise ConfigError("No test profiles found in commands configuration")
        
        test_profiles = commands['test_profiles']
        if profile_name not in test_profiles:
            raise ConfigError(f"Test profile '{profile_name}' not found")
        
        return test_profiles[profile_name]

    def filter_commands(
        self, 
        commands: Dict[str, Any], 
        enabled_only: bool = False, 
        implemented_only: bool = False
    ) -> Dict[str, Any]:
        """
        Filter commands based on enabled/implemented status.
        
        Args:
            commands: Command definitions dictionary
            enabled_only: If True, only return enabled commands
            implemented_only: If True, only return implemented commands
            
        Returns:
            Filtered command definitions
        """
        filtered = {}
        
        for cmd_name, cmd_config in commands.items():
            # Check enabled filter
            if enabled_only and not cmd_config.get('enabled', False):
                continue
            
            # Check implemented filter
            if implemented_only and not cmd_config.get('implemented', False):
                continue
            
            filtered[cmd_name] = cmd_config
        
        return filtered

    def get_command_config(self, commands: Dict[str, Any], command_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific command.
        
        Args:
            commands: Command definitions dictionary
            command_name: Name of command to get config for
            
        Returns:
            Command configuration dictionary
            
        Raises:
            ConfigError: If command not found
        """
        if command_name not in commands:
            raise ConfigError(f"Command '{command_name}' not found")
        
        return deepcopy(commands[command_name])

    def get_serial_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get serial port configuration.
        
        Args:
            config: Main configuration dictionary
            
        Returns:
            Serial configuration dictionary
        """
        return config.get('serial', {})

    def get_timing_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get timing configuration.
        
        Args:
            config: Main configuration dictionary
            
        Returns:
            Timing configuration dictionary
        """
        return config.get('timing', {})

    def update_command_status(
        self, 
        commands: Dict[str, Any], 
        command_name: str, 
        enabled: Optional[bool] = None,
        implemented: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update enable/implemented status of a command.
        
        Args:
            commands: Command definitions dictionary
            command_name: Name of command to update
            enabled: New enabled status (if provided)
            implemented: New implemented status (if provided)
            
        Returns:
            Updated commands dictionary
            
        Raises:
            ConfigError: If command not found
        """
        if command_name not in commands:
            raise ConfigError(f"Command '{command_name}' not found")
        
        updated_commands = deepcopy(commands)
        
        if enabled is not None:
            updated_commands[command_name]['enabled'] = enabled
        
        if implemented is not None:
            updated_commands[command_name]['implemented'] = implemented
        
        return updated_commands

    def save_config(self, config: Dict[str, Any], config_path: Union[str, Path]) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            config: Configuration dictionary to save
            config_path: Path to save configuration file
            
        Raises:
            ConfigError: If unable to save file
        """
        config_path = Path(config_path)
        
        try:
            # Ensure parent directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise ConfigError(f"Error saving configuration file {config_path}: {e}")

    def get_commands_by_group(self, commands: Dict[str, Any], group: str) -> Dict[str, Any]:
        """
        Get commands filtered by group.
        
        Args:
            commands: Command definitions dictionary
            group: Group name to filter by
            
        Returns:
            Commands in the specified group
        """
        grouped_commands = {}
        
        for cmd_name, cmd_config in commands.items():
            if cmd_config.get('group') == group:
                grouped_commands[cmd_name] = cmd_config
        
        return grouped_commands

    def get_command_groups(self, commands: Dict[str, Any]) -> List[str]:
        """
        Get list of all command groups.
        
        Args:
            commands: Command definitions dictionary
            
        Returns:
            List of unique group names
        """
        groups = set()
        
        for cmd_config in commands.values():
            group = cmd_config.get('group')
            if group:
                groups.add(group)
        
        return sorted(list(groups))