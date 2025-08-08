"""
BK-Integration: Unified control interface for BK8520 and BK9206b devices.

This package provides a comprehensive CLI and API for controlling BK Precision
test equipment including the BK8520 Electronic Load and BK9206b Power Supply,
with specialized battery testing workflows.
"""

__version__ = "1.0.0"
__author__ = "SuperClaude Implementation"
__email__ = "dev@example.com"

# Core imports for external usage
from .config import ConfigManager
from .clients import BK8520Client, BK9206bClient

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "ConfigManager",
    "BK8520Client",
    "BK9206bClient",
]