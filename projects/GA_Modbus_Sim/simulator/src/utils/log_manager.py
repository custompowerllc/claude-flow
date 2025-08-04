#!/usr/bin/env python3
"""
LogManager - Centralized logging management for GA Modbus BMS Simulator

This module provides a centralized logging system with support for:
- Multiple rotating file handlers (size and time-based)
- Structured logging with JSON format option
- Component-specific loggers with configurable levels
- Path resolution (relative, absolute, environment variables)
- Console and file output with different formatters
"""

import logging
import logging.handlers
import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union, Any
from enum import Enum


class LogLevel(Enum):
    """Available log levels"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogFormat(Enum):
    """Available log formats"""
    STANDARD = "standard"
    DETAILED = "detailed"
    JSON = "json"
    MINIMAL = "minimal"


class LogManager:
    """
    Centralized logging manager for the GA Modbus BMS Simulator
    
    Provides structured logging with multiple handlers, formatters, and
    configurable output destinations.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the log manager
        
        Args:
            config_path: Path to logging configuration file
        """
        self.config_path = config_path
        self.config = {}
        self.loggers: Dict[str, logging.Logger] = {}
        self.handlers: Dict[str, logging.Handler] = {}
        self.formatters: Dict[str, logging.Formatter] = {}
        
        # Load configuration
        self._load_config()
        
        # Setup formatters
        self._setup_formatters()
        
        # Setup handlers
        self._setup_handlers()
        
        # Initialize root logger
        self._setup_root_logger()
    
    def _load_config(self):
        """Load logging configuration from file or use defaults"""
        default_config = {
            "version": "1.0",
            "log_dir": "logs",
            "default_level": "INFO",
            "console_output": True,
            "file_output": True,
            "json_format": False,
            "rotation": {
                "max_file_size": "10MB",
                "backup_count": 5,
                "time_rotation": False,
                "rotation_interval": "daily"
            },
            "components": {
                "server": {
                    "level": "INFO",
                    "file": "modbus_server.log"
                },
                "register_handler": {
                    "level": "INFO", 
                    "file": "register_handler.log"
                },
                "cli": {
                    "level": "INFO",
                    "file": "cli.log"
                },
                "simulator": {
                    "level": "INFO",
                    "file": "simulator.log"
                },
                "com_port": {
                    "level": "INFO",
                    "file": "com_port.log"
                }
            },
            "formatters": {
                "standard": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "detailed": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s",
                "minimal": "%(levelname)s - %(message)s",
                "json": None  # Will be handled by JSONFormatter
            }
        }
        
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                    # Merge with defaults
                    self.config = {**default_config, **file_config}
            except Exception as e:
                print(f"Warning: Failed to load config from {self.config_path}: {e}")
                self.config = default_config
        else:
            self.config = default_config
    
    def _resolve_path(self, path: str) -> Path:
        """
        Resolve path with support for relative, absolute, and environment variables
        
        Args:
            path: Path string to resolve
            
        Returns:
            Resolved Path object
        """
        # Expand environment variables
        expanded_path = os.path.expandvars(path)
        
        # Convert to Path object
        path_obj = Path(expanded_path)
        
        # If relative, make relative to project root
        if not path_obj.is_absolute():
            # Find project root (directory containing run_simulator.py)
            project_root = Path(__file__).parent.parent.parent
            path_obj = project_root / path_obj
        
        return path_obj.resolve()
    
    def _parse_file_size(self, size_str: str) -> int:
        """
        Parse file size string (e.g., '10MB', '500KB') to bytes
        
        Args:
            size_str: Size string to parse
            
        Returns:
            Size in bytes
        """
        size_str = size_str.upper().strip()
        
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            # Assume bytes
            return int(size_str)
    
    def _setup_formatters(self):
        """Setup log formatters"""
        # Standard formatter
        self.formatters['standard'] = logging.Formatter(
            self.config['formatters']['standard']
        )
        
        # Detailed formatter
        self.formatters['detailed'] = logging.Formatter(
            self.config['formatters']['detailed']
        )
        
        # Minimal formatter
        self.formatters['minimal'] = logging.Formatter(
            self.config['formatters']['minimal']
        )
        
        # JSON formatter
        self.formatters['json'] = JSONFormatter()
    
    def _setup_handlers(self):
        """Setup log handlers"""
        # Console handler
        if self.config['console_output']:
            console_handler = logging.StreamHandler(sys.stdout)
            formatter_name = 'json' if self.config['json_format'] else 'standard'
            console_handler.setFormatter(self.formatters[formatter_name])
            console_handler.setLevel(getattr(logging, self.config['default_level']))
            self.handlers['console'] = console_handler
        
        # File handlers
        if self.config['file_output']:
            self._setup_file_handlers()
    
    def _setup_file_handlers(self):
        """Setup file handlers with rotation"""
        log_dir = self._resolve_path(self.config['log_dir'])
        log_dir.mkdir(parents=True, exist_ok=True)
        
        rotation_config = self.config['rotation']
        max_bytes = self._parse_file_size(rotation_config['max_file_size'])
        backup_count = rotation_config['backup_count']
        
        # Main log file handler
        main_log_file = log_dir / "simulator.log"
        
        if rotation_config.get('time_rotation', False):
            # Time-based rotation
            interval = rotation_config.get('rotation_interval', 'daily')
            if interval == 'daily':
                when = 'D'
                interval_count = 1
            elif interval == 'hourly':
                when = 'H'
                interval_count = 1
            elif interval == 'weekly':
                when = 'W0'  # Monday
                interval_count = 1
            else:
                when = 'D'
                interval_count = 1
            
            main_handler = logging.handlers.TimedRotatingFileHandler(
                filename=str(main_log_file),
                when=when,
                interval=interval_count,
                backupCount=backup_count,
                encoding='utf-8'
            )
        else:
            # Size-based rotation
            main_handler = logging.handlers.RotatingFileHandler(
                filename=str(main_log_file),
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
        
        formatter_name = 'json' if self.config['json_format'] else 'detailed'
        main_handler.setFormatter(self.formatters[formatter_name])
        main_handler.setLevel(getattr(logging, self.config['default_level']))
        self.handlers['main_file'] = main_handler
        
        # Component-specific file handlers
        for component, comp_config in self.config['components'].items():
            if 'file' in comp_config:
                comp_log_file = log_dir / comp_config['file']
                
                if rotation_config.get('time_rotation', False):
                    comp_handler = logging.handlers.TimedRotatingFileHandler(
                        filename=str(comp_log_file),
                        when=when,
                        interval=interval_count,
                        backupCount=backup_count,
                        encoding='utf-8'
                    )
                else:
                    comp_handler = logging.handlers.RotatingFileHandler(
                        filename=str(comp_log_file),
                        maxBytes=max_bytes,
                        backupCount=backup_count,
                        encoding='utf-8'
                    )
                
                comp_handler.setFormatter(self.formatters[formatter_name])
                comp_level = comp_config.get('level', self.config['default_level'])
                comp_handler.setLevel(getattr(logging, comp_level))
                self.handlers[f'{component}_file'] = comp_handler
    
    def _setup_root_logger(self):
        """Setup root logger"""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers will filter
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Add our handlers
        for handler in self.handlers.values():
            root_logger.addHandler(handler)
    
    def get_logger(self, name: str, component: Optional[str] = None) -> logging.Logger:
        """
        Get a logger instance for a specific component
        
        Args:
            name: Logger name (usually module name)
            component: Component name for specific configuration
            
        Returns:
            Configured logger instance
        """
        # Use component name if provided, otherwise extract from name
        if not component:
            # Try to extract component from name
            name_parts = name.split('.')
            if len(name_parts) > 1:
                component = name_parts[-1]
            else:
                component = 'simulator'  # Default component
        
        logger_key = f"{name}_{component}"
        
        if logger_key not in self.loggers:
            logger = logging.getLogger(name)
            
            # Set component-specific level if configured
            if component in self.config['components']:
                comp_config = self.config['components'][component]
                level = comp_config.get('level', self.config['default_level'])
                logger.setLevel(getattr(logging, level))
                
                # Add component-specific file handler if exists
                comp_handler_key = f'{component}_file'
                if comp_handler_key in self.handlers:
                    # Create a filter to only log this component's messages to its file
                    comp_filter = ComponentFilter(component)
                    comp_handler = self.handlers[comp_handler_key]
                    comp_handler.addFilter(comp_filter)
            else:
                logger.setLevel(getattr(logging, self.config['default_level']))
            
            self.loggers[logger_key] = logger
        
        return self.loggers[logger_key]
    
    def update_config(self, config_updates: Dict[str, Any]):
        """
        Update logging configuration at runtime
        
        Args:
            config_updates: Dictionary of configuration updates
        """
        # Merge updates with current config
        self.config = {**self.config, **config_updates}
        
        # Re-setup formatters and handlers
        self._setup_formatters()
        self._setup_handlers()
        self._setup_root_logger()
        
        # Update existing loggers
        for logger in self.loggers.values():
            logger.handlers.clear()
            for handler in self.handlers.values():
                logger.addHandler(handler)
    
    def set_log_level(self, level: Union[str, LogLevel], component: Optional[str] = None):
        """
        Set log level for a component or globally
        
        Args:
            level: Log level to set
            component: Specific component, or None for global
        """
        if isinstance(level, LogLevel):
            level_value = level.value
            level_name = level.name
        else:
            level_name = level.upper()
            level_value = getattr(logging, level_name)
        
        if component:
            # Update specific component
            if component in self.config['components']:
                self.config['components'][component]['level'] = level_name
            
            # Update component loggers
            for logger_key, logger in self.loggers.items():
                if logger_key.endswith(f"_{component}"):
                    logger.setLevel(level_value)
            
            # Update component handlers
            comp_handler_key = f'{component}_file'
            if comp_handler_key in self.handlers:
                self.handlers[comp_handler_key].setLevel(level_value)
        else:
            # Update global level
            self.config['default_level'] = level_name
            
            # Update all handlers
            for handler in self.handlers.values():
                handler.setLevel(level_value)
    
    def add_custom_handler(self, name: str, handler: logging.Handler):
        """
        Add a custom log handler
        
        Args:
            name: Handler name
            handler: Handler instance
        """
        self.handlers[name] = handler
        
        # Add to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        
        # Add to existing component loggers
        for logger in self.loggers.values():
            logger.addHandler(handler)
    
    def get_log_files(self) -> Dict[str, Path]:
        """
        Get paths to all log files
        
        Returns:
            Dictionary mapping component names to log file paths
        """
        log_files = {}
        log_dir = self._resolve_path(self.config['log_dir'])
        
        # Main log file
        log_files['main'] = log_dir / "simulator.log"
        
        # Component log files
        for component, comp_config in self.config['components'].items():
            if 'file' in comp_config:
                log_files[component] = log_dir / comp_config['file']
        
        return log_files
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Clean up old log files
        
        Args:
            days_to_keep: Number of days of logs to keep
        """
        log_dir = self._resolve_path(self.config['log_dir'])
        if not log_dir.exists():
            return
        
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        for log_file in log_dir.glob("*.log*"):
            try:
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    print(f"Cleaned up old log file: {log_file}")
            except Exception as e:
                print(f"Error cleaning up log file {log_file}: {e}")


class JSONFormatter(logging.Formatter):
    """JSON log formatter"""
    
    def format(self, record):
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info']:
                log_data[key] = value
        
        return json.dumps(log_data, default=str, separators=(',', ':'))


class ComponentFilter(logging.Filter):
    """Filter to only allow specific component logs"""
    
    def __init__(self, component_name: str):
        super().__init__()
        self.component_name = component_name
    
    def filter(self, record):
        """Filter records based on component name"""
        # Check if record name contains component name
        return self.component_name in record.name.lower()


# Global log manager instance
_log_manager: Optional[LogManager] = None


def get_log_manager(config_path: Optional[str] = None) -> LogManager:
    """
    Get the global log manager instance
    
    Args:
        config_path: Path to logging configuration file
        
    Returns:
        LogManager instance
    """
    global _log_manager
    
    if _log_manager is None:
        _log_manager = LogManager(config_path)
    
    return _log_manager


def get_logger(name: str, component: Optional[str] = None) -> logging.Logger:
    """
    Convenience function to get a logger
    
    Args:
        name: Logger name
        component: Component name
        
    Returns:
        Logger instance
    """
    log_manager = get_log_manager()
    return log_manager.get_logger(name, component)


def setup_logging(config_path: Optional[str] = None, 
                  level: Optional[str] = None,
                  console: Optional[bool] = None,
                  json_format: Optional[bool] = None) -> LogManager:
    """
    Setup logging with optional overrides
    
    Args:
        config_path: Path to logging configuration file
        level: Override default log level
        console: Override console output setting
        json_format: Override JSON format setting
        
    Returns:
        LogManager instance
    """
    global _log_manager
    
    _log_manager = LogManager(config_path)
    
    # Apply overrides
    config_updates = {}
    if level:
        config_updates['default_level'] = level.upper()
    if console is not None:
        config_updates['console_output'] = console
    if json_format is not None:
        config_updates['json_format'] = json_format
    
    if config_updates:
        _log_manager.update_config(config_updates)
    
    return _log_manager