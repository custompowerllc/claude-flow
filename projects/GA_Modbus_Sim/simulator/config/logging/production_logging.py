#!/usr/bin/env python3
"""
Production Logging Configuration for GA Modbus Simulator

This configuration is optimized for production environments with:
- Minimal performance impact
- Structured logging for monitoring systems
- Error-focused logging
- JSON output for log aggregation
"""

import logging
import logging.handlers
import json
import sys
import os
from datetime import datetime
from pathlib import Path

class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in JSON format for easy parsing
    by log aggregation systems like ELK stack, Splunk, etc.
    """
    
    def __init__(self, include_extra=True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record):
        log_entry = {
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
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if configured
        if self.include_extra:
            # Add any custom fields from the log record
            for key, value in record.__dict__.items():
                if key not in ('name', 'msg', 'args', 'levelname', 'levelno', 
                              'pathname', 'filename', 'module', 'lineno', 
                              'funcName', 'created', 'msecs', 'relativeCreated',
                              'thread', 'threadName', 'processName', 'process',
                              'message', 'exc_info', 'exc_text', 'stack_info'):
                    log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)

class PerformanceFilter(logging.Filter):
    """
    Filter that limits high-frequency DEBUG messages to reduce performance impact
    """
    
    def __init__(self, max_debug_per_second=10):
        super().__init__()
        self.max_debug_per_second = max_debug_per_second
        self.debug_count = 0
        self.last_reset = datetime.now()
    
    def filter(self, record):
        now = datetime.now()
        
        # Reset counter every second
        if (now - self.last_reset).seconds >= 1:
            self.debug_count = 0
            self.last_reset = now
        
        # Limit DEBUG messages
        if record.levelno == logging.DEBUG:
            if self.debug_count >= self.max_debug_per_second:
                return False
            self.debug_count += 1
        
        return True

def setup_production_logging(log_dir="logs", service_name="ga-modbus-simulator"):
    """
    Setup production-grade logging configuration
    
    Args:
        log_dir (str): Directory for log files
        service_name (str): Service name for structured logging
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Configure root logger for WARNING and above only
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    root_logger.handlers.clear()
    
    # JSON formatter for structured logging
    json_formatter = JSONFormatter()
    
    # Standard formatter for console
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 1. Error log file (JSON format for monitoring)
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_path / f"{service_name}_errors.json",
        maxBytes=50*1024*1024,  # 50MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    root_logger.addHandler(error_handler)
    
    # 2. Application events log (JSON format)
    app_handler = logging.handlers.RotatingFileHandler(
        filename=log_path / f"{service_name}_events.json",
        maxBytes=100*1024*1024,  # 100MB
        backupCount=5,
        encoding='utf-8'
    )
    app_handler.setLevel(logging.WARNING)
    app_handler.setFormatter(json_formatter)
    root_logger.addHandler(app_handler)
    
    # 3. Console output for immediate visibility
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 4. Separate operational log for INFO messages from simulator components
    simulator_logger = logging.getLogger('simulator')
    simulator_logger.setLevel(logging.INFO)
    simulator_logger.propagate = True  # Allow propagation to root handlers
    
    ops_handler = logging.handlers.RotatingFileHandler(
        filename=log_path / f"{service_name}_operations.log",
        maxBytes=50*1024*1024,  # 50MB
        backupCount=3,
        encoding='utf-8'
    )
    ops_handler.setLevel(logging.INFO)
    ops_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    # Add performance filter to prevent log flooding
    ops_handler.addFilter(PerformanceFilter(max_debug_per_second=5))
    simulator_logger.addHandler(ops_handler)
    
    # Suppress verbose external library logging
    logging.getLogger('pymodbus').setLevel(logging.ERROR)
    logging.getLogger('pymodbus.transport').setLevel(logging.CRITICAL)
    logging.getLogger('serial').setLevel(logging.ERROR)
    
    # Configure simulator component loggers
    logging.getLogger('simulator.src.core.modbus_server').setLevel(logging.INFO)
    logging.getLogger('simulator.src.core.register_handler').setLevel(logging.INFO)
    logging.getLogger('simulator.src.utils.com_port_manager').setLevel(logging.INFO)
    
    # Log startup information
    startup_logger = logging.getLogger('simulator.startup')
    startup_logger.info(f"Production logging initialized", extra={
        'service_name': service_name,
        'log_directory': str(log_path.absolute()),
        'log_level': 'WARNING',
        'json_logging': True
    })
    
    return logging.getLogger('simulator')

def setup_monitoring_logging(log_dir="logs", metrics_interval=60):
    """
    Setup logging with metrics collection for monitoring systems
    
    Args:
        log_dir (str): Directory for log files
        metrics_interval (int): Interval in seconds for metrics logging
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Setup basic production logging first
    logger = setup_production_logging(log_dir)
    
    # Add metrics logger
    metrics_logger = logging.getLogger('simulator.metrics')
    metrics_logger.setLevel(logging.INFO)
    metrics_logger.propagate = False
    
    # Metrics file handler (JSON format)
    metrics_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_path / "simulator_metrics.json",
        when='H',  # Hourly rotation
        interval=1,
        backupCount=24,  # Keep 24 hours
        encoding='utf-8'
    )
    metrics_handler.setLevel(logging.INFO)
    metrics_handler.setFormatter(JSONFormatter())
    metrics_logger.addHandler(metrics_handler)
    
    return logger, metrics_logger

def setup_docker_logging():
    """
    Setup logging optimized for Docker containers
    - Logs to stdout/stderr for Docker log drivers
    - JSON format for structured logging
    - Minimal file I/O
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    
    # JSON formatter for structured output
    json_formatter = JSONFormatter()
    
    # Stdout handler for general logs
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(json_formatter)
    
    # Filter to exclude ERROR and CRITICAL from stdout
    class InfoWarningFilter(logging.Filter):
        def filter(self, record):
            return record.levelno < logging.ERROR
    
    stdout_handler.addFilter(InfoWarningFilter())
    root_logger.addHandler(stdout_handler)
    
    # Stderr handler for errors
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(json_formatter)
    root_logger.addHandler(stderr_handler)
    
    # Suppress external library noise
    logging.getLogger('pymodbus').setLevel(logging.ERROR)
    
    # Configure environment-based log level
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    logger = logging.getLogger('simulator')
    logger.info("Docker logging configured", extra={
        'log_level': log_level,
        'output': 'stdout/stderr',
        'format': 'json'
    })
    
    return logger

# Health check and monitoring functions
def log_system_health(logger, extra_info=None):
    """
    Log system health information for monitoring
    """
    import psutil
    import platform
    
    health_info = {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'platform': platform.system(),
        'python_version': platform.python_version()
    }
    
    if extra_info:
        health_info.update(extra_info)
    
    logger.info("System health check", extra=health_info)

def log_application_metrics(logger, server_state=None, active_connections=0, 
                          requests_processed=0, errors_count=0):
    """
    Log application-specific metrics
    """
    metrics = {
        'server_state': server_state,
        'active_connections': active_connections,
        'requests_processed': requests_processed,
        'errors_count': errors_count,
        'metric_type': 'application'
    }
    
    logger.info("Application metrics", extra=metrics)

# Example usage and testing
if __name__ == "__main__":
    print("Testing production logging configurations...\n")
    
    # Test production logging
    print("1. Testing production logging:")
    logger = setup_production_logging()
    
    logger.info("Production logging test - INFO message")
    logger.warning("Production logging test - WARNING message")
    logger.error("Production logging test - ERROR message")
    
    # Test with extra fields
    logger.info("Test with extra fields", extra={
        'user_id': 'test_user',
        'session_id': 'abc123',
        'operation': 'start_server'
    })
    
    print("   Check logs/ directory for JSON log files\n")
    
    # Test Docker logging
    print("2. Testing Docker logging:")
    docker_logger = setup_docker_logging()
    docker_logger.info("Docker logging test")
    docker_logger.error("Docker error test")
    print("   Docker logs sent to stdout/stderr\n")
    
    # Test monitoring
    print("3. Testing monitoring logging:")
    monitor_logger, metrics_logger = setup_monitoring_logging()
    
    # Log some metrics
    log_system_health(metrics_logger)
    log_application_metrics(metrics_logger, 
                          server_state="running", 
                          active_connections=3,
                          requests_processed=150)
    
    print("   Check logs/ directory for metrics files")
    
    print("\nProduction logging tests complete!")