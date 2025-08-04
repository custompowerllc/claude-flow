#!/usr/bin/env python3
"""
Basic Logging Configuration for GA Modbus Simulator

This configuration provides standard console logging suitable for development
and basic troubleshooting.
"""

import logging
import sys

def setup_basic_logging(verbose=False):
    """
    Setup basic logging configuration
    
    Args:
        verbose (bool): Enable DEBUG level logging if True
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout
    )
    
    # Set specific component levels
    if not verbose:
        # Reduce noise from pymodbus in normal mode
        logging.getLogger('pymodbus').setLevel(logging.WARNING)
        logging.getLogger('pymodbus.transport').setLevel(logging.ERROR)
    
    return logging.getLogger('simulator')

def setup_minimal_logging():
    """
    Setup minimal logging for production use
    """
    logging.basicConfig(
        level=logging.WARNING,
        format='%(levelname)s: %(message)s',
        stream=sys.stdout
    )
    
    # Only show errors from external libraries
    logging.getLogger('pymodbus').setLevel(logging.ERROR)
    
    return logging.getLogger('simulator')

# Example usage
if __name__ == "__main__":
    # Test basic logging
    logger = setup_basic_logging(verbose=True)
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print("\n" + "="*50)
    print("Basic logging test complete")