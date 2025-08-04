#!/usr/bin/env python3
"""
File Logging Configuration for GA Modbus Simulator

This configuration saves logs to files with rotation and provides
both console and file output for production environments.
"""

import logging
import logging.handlers
import os
from pathlib import Path

def setup_file_logging(log_dir="logs", max_bytes=10*1024*1024, backup_count=5, verbose=False):
    """
    Setup file-based logging with rotation
    
    Args:
        log_dir (str): Directory for log files
        max_bytes (int): Maximum log file size before rotation
        backup_count (int): Number of backup files to keep
        verbose (bool): Enable DEBUG level logging
    """
    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Configure root logger
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # File handler for all logs (with rotation)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_path / "simulator.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler for errors only
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_path / "simulator_errors.log",
        maxBytes=max_bytes // 2,
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Console handler for important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO if not verbose else logging.DEBUG)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # Set specific component levels
    if not verbose:
        logging.getLogger('pymodbus').setLevel(logging.WARNING)
        logging.getLogger('pymodbus.transport').setLevel(logging.ERROR)
    
    # Log the configuration
    logger = logging.getLogger('simulator.config')
    logger.info(f"File logging configured:")
    logger.info(f"  - Log directory: {log_path.absolute()}")
    logger.info(f"  - Max file size: {max_bytes / (1024*1024):.1f}MB")
    logger.info(f"  - Backup files: {backup_count}")
    logger.info(f"  - Level: {'DEBUG' if verbose else 'INFO'}")
    
    return logging.getLogger('simulator')

def setup_daily_logging(log_dir="logs", days_to_keep=7, verbose=False):
    """
    Setup daily log rotation
    
    Args:
        log_dir (str): Directory for log files
        days_to_keep (int): Number of daily log files to keep
        verbose (bool): Enable DEBUG level logging
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    level = logging.DEBUG if verbose else logging.INFO
    
    # Formatter with date
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    
    # Daily rotating file handler
    daily_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_path / "simulator.log",
        when='midnight',
        interval=1,
        backupCount=days_to_keep,
        encoding='utf-8'
    )
    daily_handler.setLevel(level)
    daily_handler.setFormatter(formatter)
    daily_handler.suffix = '%Y-%m-%d'  # Add date suffix to rotated files
    root_logger.addHandler(daily_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    root_logger.addHandler(console_handler)
    
    logger = logging.getLogger('simulator.config')
    logger.info(f"Daily logging configured: {log_path.absolute()}")
    
    return logging.getLogger('simulator')

def setup_component_logging(log_dir="logs", verbose=False):
    """
    Setup separate log files for different components
    
    Args:
        log_dir (str): Directory for log files
        verbose (bool): Enable DEBUG level logging
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    level = logging.DEBUG if verbose else logging.INFO
    
    # Detailed formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure individual component loggers
    components = [
        ('simulator.src.core.modbus_server', 'server.log'),
        ('simulator.src.core.register_handler', 'registers.log'),
        ('simulator.src.utils.com_port_manager', 'ports.log'),
        ('pymodbus', 'modbus.log')
    ]
    
    for component_name, filename in components:
        logger = logging.getLogger(component_name)
        logger.setLevel(level)
        
        # Remove existing handlers
        logger.handlers.clear()
        logger.propagate = False  # Don't propagate to root logger
        
        # File handler for this component
        handler = logging.handlers.RotatingFileHandler(
            filename=log_path / filename,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # General console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    logger = logging.getLogger('simulator.config')
    logger.info(f"Component logging configured in: {log_path.absolute()}")
    
    return logging.getLogger('simulator')

# Example usage and testing
if __name__ == "__main__":
    import sys
    import time
    
    print("Testing file logging configurations...\n")
    
    # Test basic file logging
    print("1. Testing basic file logging:")
    logger1 = setup_file_logging(verbose=True)
    logger1.info("File logging test message")
    logger1.error("File logging test error")
    print("   Check logs/ directory for simulator.log and simulator_errors.log\n")
    
    # Test daily logging
    print("2. Testing daily logging:")
    logger2 = setup_daily_logging(log_dir="logs_daily", verbose=False)
    logger2.info("Daily logging test message")
    print("   Check logs_daily/ directory for simulator.log\n")
    
    # Test component logging
    print("3. Testing component logging:")
    logger3 = setup_component_logging(log_dir="logs_components", verbose=True)
    
    # Test different components
    server_logger = logging.getLogger('simulator.src.core.modbus_server')
    register_logger = logging.getLogger('simulator.src.core.register_handler')
    
    server_logger.info("Server component test message")
    register_logger.debug("Register component test message")
    
    print("   Check logs_components/ directory for separate component logs")
    
    print("\nFile logging tests complete!")