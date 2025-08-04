"""
GA Modbus BMS Simulator

A Modbus RTU server that simulates GA BMS device responses for testing
and development purposes. This simulator is 100% compatible with the
existing GA Modbus applications.

Main Components:
- ModbusSimulatorServer: Core Modbus RTU server
- RegisterHandler: Manages BMS register values and simulation
- ComPortManager: Handles serial port detection and management

Usage:
    from simulator.src.core.modbus_server import ModbusSimulatorServer
    from simulator.src.core.register_handler import BatteryScenario
    
    server = ModbusSimulatorServer()
    server.start()
"""

__version__ = "1.0.0"
__author__ = "GA Technologies"
__email__ = "support@ga-tech.com"

# Import main classes for easy access
try:
    from .src.core.modbus_server import ModbusSimulatorServer, ServerConfig
    from .src.core.register_handler import RegisterHandler, BatteryScenario, BatteryState
    from .src.utils.com_port_manager import ComPortManager, PortInfo, PortStatus
    
    __all__ = [
        'ModbusSimulatorServer',
        'ServerConfig', 
        'RegisterHandler',
        'BatteryScenario',
        'BatteryState',
        'ComPortManager',
        'PortInfo',
        'PortStatus'
    ]
    
except ImportError as e:
    # Handle import errors gracefully during development
    print(f"Warning: Could not import all simulator components: {e}")
    __all__ = []