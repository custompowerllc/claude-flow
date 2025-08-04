#!/usr/bin/env python3
"""
ModbusSimulatorServer - Core Modbus RTU server for BMS simulation

This server simulates a GA BMS device by responding to Modbus RTU queries
exactly as a real device would. It's designed to be 100% compatible with
the standalone logger and modbus_query_test.py applications.

Key Features:
- Responds to read_input_registers queries at address 9 with count 36
- Returns register values compatible with register_map from modbus_query_test.py
- Supports both simulated and realistic battery data
- Compatible with existing GA app queries
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Import pymodbus server components
try:
    from pymodbus.server import StartSerialServer
    from pymodbus.device import ModbusDeviceIdentification
    from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
    from pymodbus.datastore import ModbusSequentialDataBlock
    from pymodbus.constants import Endian
    import serial
    import serial.tools.list_ports
    MODBUS_AVAILABLE = True
except ImportError as e:
    print("Error importing pymodbus: {}".format(e))
    print("Install with: pip install pymodbus pyserial")
    MODBUS_AVAILABLE = False

# Import register handler
from .register_handler import RegisterHandler

# Import logging system
try:
    from ..utils.log_manager import get_logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False


class SimulatorState(Enum):
    """Simulator operating states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ServerConfig:
    """Configuration for the Modbus server"""
    port: str = "COM4"  # Default to COM4 to avoid conflict with real device on COM3
    baudrate: int = 9600
    parity: str = 'E'
    stopbits: int = 1
    bytesize: int = 8
    timeout: float = 1.0
    slave_id: int = 1
    start_address: int = 9  # Address for read_input_registers (data starts at register 10)
    register_count: int = 36  # Number of registers to serve


class ModbusSimulatorServer:
    """
    Modbus RTU server that simulates GA BMS device responses
    
    This server is designed to be a drop-in replacement for a real BMS device,
    responding to the exact same Modbus queries that the GA app sends.
    """
    
    def __init__(self, config: Optional[ServerConfig] = None):
        """Initialize the Modbus simulator server"""
        self.config = config or ServerConfig()
        self.state = SimulatorState.STOPPED
        self.server_thread: Optional[threading.Thread] = None
        self.server_context: Optional[ModbusServerContext] = None
        self.register_handler = RegisterHandler()
        
        # Setup logging
        if LOGGING_AVAILABLE:
            self.logger = get_logger(__name__, 'server')
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
        
        # Server control
        self._stop_event = threading.Event()
        self._server_instance = None
        
        self.logger.info("ModbusSimulatorServer initialized for {}".format(self.config.port))
    
    def _setup_server_context(self) -> ModbusServerContext:
        """Setup the Modbus server context with register data"""
        try:
            # Get initial register values from the register handler
            register_values = self.register_handler.get_all_registers()
            
            # Create data block for input registers
            # Input registers start at address 1, but we want our data at register 10
            # So we need to create a block that can handle addresses 10-45 (36 registers)
            input_registers = ModbusSequentialDataBlock(1, [0] * 100)  # Create larger block
            
            # Populate the registers starting at address 10 (index 9 for 0-based)
            for i, value in enumerate(register_values):
                input_registers.setValues(10 + i, [value])
            
            # Create slave context with the register blocks
            slave_context = ModbusSlaveContext(
                di=None,  # Discrete inputs
                co=None,  # Coils
                hr=None,  # Holding registers
                ir=input_registers  # Input registers
            )
            
            # Create server context with single slave
            server_context = ModbusServerContext(
                slaves={self.config.slave_id: slave_context},
                single=False
            )
            
            self.logger.info("Server context created with {} registers".format(len(register_values)))
            return server_context
            
        except Exception as e:
            self.logger.error("Error setting up server context: {}".format(e))
            raise
    
    def _setup_device_identification(self) -> ModbusDeviceIdentification:
        """Setup device identification for Modbus server"""
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'GA Technologies'
        identity.ProductCode = 'BMS Simulator'
        identity.VendorUrl = 'https://github.com/ga-technologies'
        identity.ProductName = 'Modbus BMS Simulator'
        identity.ModelName = 'GA-BMS-SIM-v1.0'
        identity.MajorMinorRevision = '1.0.0'
        
        return identity
    
    def _update_registers(self):
        """Background task to update register values periodically"""
        while not self._stop_event.is_set():
            try:
                if self.server_context and self.state == SimulatorState.RUNNING:
                    # Get updated register values
                    register_values = self.register_handler.get_all_registers()
                    
                    # Update the input registers in the server context
                    slave_context = self.server_context[self.config.slave_id]
                    for i, value in enumerate(register_values):
                        slave_context.setValues(4, 10 + i, [value])  # 4 = input registers
                    
                    self.logger.debug("Updated {} registers".format(len(register_values)))
                
                # Wait before next update
                self._stop_event.wait(1.0)  # Update every second
                
            except Exception as e:
                self.logger.error("Error updating registers: {}".format(e))
                self._stop_event.wait(5.0)  # Wait longer on error
    
    def _check_port_availability(self) -> bool:
        """Check if the configured port is available"""
        try:
            # List available ports
            available_ports = [port.device for port in serial.tools.list_ports.comports()]
            
            if self.config.port not in available_ports:
                self.logger.warning("Port {} not found. Available: {}".format(self.config.port, available_ports))
                return False
            
            # Try to open the port briefly to check if it's free
            test_port = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baudrate,
                parity=self.config.parity,
                stopbits=self.config.stopbits,
                bytesize=self.config.bytesize,
                timeout=0.1
            )
            test_port.close()
            
            self.logger.info("Port {} is available".format(self.config.port))
            return True
            
        except serial.SerialException as e:
            self.logger.error("Port {} is not available: {}".format(self.config.port, e))
            return False
        except Exception as e:
            self.logger.error("Error checking port availability: {}".format(e))
            return False
    
    def start(self) -> bool:
        """Start the Modbus server"""
        if not MODBUS_AVAILABLE:
            self.logger.error("PyModbus not available. Cannot start server.")
            return False
        
        if self.state != SimulatorState.STOPPED:
            self.logger.warning("Server already running or starting (state: {})".format(self.state))
            return False
        
        try:
            self.state = SimulatorState.STARTING
            self.logger.info("Starting Modbus server on {}".format(self.config.port))
            
            # Check port availability
            if not self._check_port_availability():
                self.state = SimulatorState.ERROR
                return False
            
            # Setup server context and device identification
            self.server_context = self._setup_server_context()
            device_identity = self._setup_device_identification()
            
            # Clear stop event
            self._stop_event.clear()
            
            # Start register update thread
            update_thread = threading.Thread(target=self._update_registers, daemon=True)
            update_thread.start()
            
            # Start the server in a separate thread
            def run_server():
                try:
                    self.logger.info("Starting Modbus RTU server on {}".format(self.config.port))
                    self.state = SimulatorState.RUNNING
                    
                    # Start the serial server
                    StartSerialServer(
                        context=self.server_context,
                        identity=device_identity,
                        port=self.config.port,
                        baudrate=self.config.baudrate,
                        parity=self.config.parity,
                        stopbits=self.config.stopbits,
                        bytesize=self.config.bytesize,
                        timeout=self.config.timeout,
                        ignore_missing_slaves=True
                    )
                    
                except Exception as e:
                    self.logger.error("Server error: {}".format(e))
                    self.state = SimulatorState.ERROR
                finally:
                    if self.state == SimulatorState.RUNNING:
                        self.state = SimulatorState.STOPPED
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            # Wait a moment for server to start
            time.sleep(2.0)
            
            if self.state == SimulatorState.RUNNING:
                self.logger.info("Modbus server started successfully")
                return True
            else:
                self.logger.error("Failed to start Modbus server")
                return False
                
        except Exception as e:
            self.logger.error("Error starting server: {}".format(e))
            self.state = SimulatorState.ERROR
            return False
    
    def stop(self) -> bool:
        """Stop the Modbus server"""
        if self.state == SimulatorState.STOPPED:
            self.logger.info("Server already stopped")
            return True
        
        try:
            self.state = SimulatorState.STOPPING
            self.logger.info("Stopping Modbus server...")
            
            # Signal threads to stop
            self._stop_event.set()
            
            # Wait for server thread to finish
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5.0)
            
            self.state = SimulatorState.STOPPED
            self.logger.info("Modbus server stopped")
            return True
            
        except Exception as e:
            self.logger.error("Error stopping server: {}".format(e))
            self.state = SimulatorState.ERROR
            return False
    
    def is_running(self) -> bool:
        """Check if the server is running"""
        return self.state == SimulatorState.RUNNING
    
    def get_status(self) -> Dict[str, Any]:
        """Get server status information"""
        return {
            'state': self.state.value,
            'port': self.config.port,
            'baudrate': self.config.baudrate,
            'slave_id': self.config.slave_id,
            'register_count': self.config.register_count,
            'thread_alive': self.server_thread.is_alive() if self.server_thread else False
        }
    
    def update_register(self, register_name: str, value: int) -> bool:
        """Update a specific register value"""
        try:
            return self.register_handler.update_register(register_name, value)
        except Exception as e:
            self.logger.error("Error updating register {}: {}".format(register_name, e))
            return False
    
    def get_register_values(self) -> Dict[str, int]:
        """Get current register values"""
        try:
            return self.register_handler.get_register_dict()
        except Exception as e:
            self.logger.error("Error getting register values: {}".format(e))
            return {}


def main():
    """Test function for the Modbus server"""
    # Setup logging
    if LOGGING_AVAILABLE:
        from ..utils.log_manager import setup_logging
        setup_logging(level='INFO')
        logger = get_logger(__name__, 'server')
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
    
    # Create and start server
    config = ServerConfig(port="COM4")  # Use COM4 to avoid conflict with real device
    server = ModbusSimulatorServer(config)
    
    try:
        if server.start():
            print("Server started. Press Ctrl+C to stop...")
            while server.is_running():
                time.sleep(1)
        else:
            print("Failed to start server")
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.stop()


if __name__ == "__main__":
    main()