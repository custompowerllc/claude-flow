#!/usr/bin/env python3
"""
COM Port Manager - Handles serial port detection and management for simulator

This module provides utilities for managing COM/serial ports, detecting
available ports, and handling port conflicts between the simulator and
real devices.

Key Features:
- Detect available serial ports
- Check for port conflicts
- Suggest alternative ports for simulator
- Validate port configurations
- Handle port cleanup and release
"""

import logging
import platform
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Import logging system
try:
    from .log_manager import get_logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

# Import serial port libraries
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    print("PySerial not available. Install with: pip install pyserial")
    SERIAL_AVAILABLE = False


class PortStatus(Enum):
    """Port availability status"""
    AVAILABLE = "available"
    IN_USE = "in_use"
    NOT_FOUND = "not_found"
    ERROR = "error"


@dataclass
class PortInfo:
    """Information about a serial port"""
    device: str
    description: str
    hwid: str
    manufacturer: Optional[str]
    status: PortStatus
    is_ga_device: bool = False
    is_virtual: bool = False


class ComPortManager:
    """
    Manages COM/serial ports for the Modbus simulator
    
    This class helps detect available ports, identify potential conflicts,
    and suggest appropriate ports for the simulator to use.
    """
    
    def __init__(self):
        """Initialize the COM port manager"""
        if LOGGING_AVAILABLE:
            self.logger = get_logger(__name__, 'com_port')
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
        
        # Platform-specific settings
        self.platform = platform.system().lower()
        self._setup_platform_defaults()
        
        self.logger.info(f"ComPortManager initialized for {self.platform}")
    
    def _setup_platform_defaults(self):
        """Setup platform-specific default settings"""
        if self.platform == "windows":
            self.default_ports = ["COM3", "COM4", "COM5", "COM6"]
            self.virtual_port_patterns = ["USB", "FTDI", "Prolific", "CH340"]
        elif self.platform == "linux":
            self.default_ports = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyACM1"]
            self.virtual_port_patterns = ["USB", "ACM", "FTDI", "ttyUSB"]
        elif self.platform == "darwin":  # macOS
            self.default_ports = ["/dev/tty.usbserial", "/dev/tty.usbmodem", "/dev/cu.usbserial"]
            self.virtual_port_patterns = ["usbserial", "usbmodem", "FTDI"]
        else:
            self.default_ports = []
            self.virtual_port_patterns = []
    
    def get_available_ports(self) -> List[PortInfo]:
        """Get list of all available serial ports with detailed information"""
        if not SERIAL_AVAILABLE:
            self.logger.error("PySerial not available")
            return []
        
        ports = []
        
        try:
            for port in serial.tools.list_ports.comports():
                # Determine if this is likely a virtual/USB port
                is_virtual = any(pattern.lower() in (port.description or "").lower() 
                                for pattern in self.virtual_port_patterns)
                
                # Check if this might be a GA device based on description
                is_ga_device = self._is_likely_ga_device(port)
                
                # Check port status
                status = self._check_port_status(port.device)
                
                port_info = PortInfo(
                    device=port.device,
                    description=port.description or "Unknown",
                    hwid=port.hwid or "Unknown",
                    manufacturer=getattr(port, 'manufacturer', None),
                    status=status,
                    is_ga_device=is_ga_device,
                    is_virtual=is_virtual
                )
                
                ports.append(port_info)
            
            self.logger.info(f"Found {len(ports)} serial ports")
            return ports
            
        except Exception as e:
            self.logger.error(f"Error getting available ports: {e}")
            return []
    
    def _is_likely_ga_device(self, port) -> bool:
        """Check if a port is likely connected to a GA device"""
        # Look for GA-specific identifiers in port description
        ga_indicators = [
            "ga", "bms", "battery", "fuel gauge", "texas instruments",
            "ti", "cc2640", "cc2650"  # Common GA BMS chips
        ]
        
        description = (port.description or "").lower()
        hwid = (port.hwid or "").lower()
        
        return any(indicator in description or indicator in hwid 
                  for indicator in ga_indicators)
    
    def _check_port_status(self, port_device: str) -> PortStatus:
        """Check if a port is available for use"""
        try:
            # Try to open the port briefly
            test_port = serial.Serial(
                port=port_device,
                baudrate=9600,
                timeout=0.1
            )
            test_port.close()
            return PortStatus.AVAILABLE
            
        except serial.SerialException as e:
            if "permission" in str(e).lower() or "access" in str(e).lower():
                return PortStatus.IN_USE
            else:
                return PortStatus.ERROR
        except Exception:
            return PortStatus.ERROR
    
    def suggest_simulator_port(self, avoid_ports: Optional[List[str]] = None) -> Optional[str]:
        """
        Suggest an appropriate port for the simulator
        
        Args:
            avoid_ports: List of ports to avoid (e.g., ports with real devices)
            
        Returns:
            Suggested port device string, or None if no suitable port found
        """
        avoid_ports = avoid_ports or []
        available_ports = self.get_available_ports()
        
        # Filter out ports to avoid
        suitable_ports = [
            port for port in available_ports
            if port.device not in avoid_ports and 
               port.status == PortStatus.AVAILABLE and
               not port.is_ga_device  # Avoid ports that might have real GA devices
        ]
        
        if not suitable_ports:
            self.logger.warning("No suitable ports found for simulator")
            return None
        
        # Prefer virtual/USB ports for simulator
        virtual_ports = [port for port in suitable_ports if port.is_virtual]
        if virtual_ports:
            suggested = virtual_ports[0].device
            self.logger.info(f"Suggested virtual port for simulator: {suggested}")
            return suggested
        
        # Fall back to any available port
        suggested = suitable_ports[0].device
        self.logger.info(f"Suggested port for simulator: {suggested}")
        return suggested
    
    def detect_ga_devices(self) -> List[PortInfo]:
        """Detect ports that likely have GA devices connected"""
        all_ports = self.get_available_ports()
        ga_ports = [port for port in all_ports if port.is_ga_device]
        
        self.logger.info(f"Detected {len(ga_ports)} potential GA device ports")
        return ga_ports
    
    def validate_port_config(self, port: str, baudrate: int = 9600, 
                           parity: str = 'E', stopbits: int = 1, 
                           bytesize: int = 8) -> Tuple[bool, str]:
        """
        Validate a port configuration
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not SERIAL_AVAILABLE:
            return False, "PySerial not available"
        
        try:
            # Check if port exists
            available_ports = [p.device for p in self.get_available_ports()]
            if port not in available_ports:
                return False, f"Port {port} not found. Available: {available_ports}"
            
            # Try to open with specified configuration
            test_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize,
                timeout=0.1
            )
            test_port.close()
            
            return True, "Port configuration valid"
            
        except serial.SerialException as e:
            return False, f"Serial error: {e}"
        except Exception as e:
            return False, f"Configuration error: {e}"
    
    def cleanup_port(self, port: str) -> bool:
        """
        Attempt to cleanup and release a port
        
        This can help if a port is stuck in use.
        """
        try:
            # Try to open and immediately close the port
            cleanup_port = serial.Serial(port, timeout=0.1)
            cleanup_port.close()
            self.logger.info(f"Cleaned up port {port}")
            return True
            
        except Exception as e:
            self.logger.warning(f"Could not cleanup port {port}: {e}")
            return False
    
    def get_port_recommendations(self) -> Dict[str, Any]:
        """
        Get port recommendations for simulator deployment
        
        Returns a dictionary with recommendations for different scenarios
        """
        all_ports = self.get_available_ports()
        ga_ports = self.detect_ga_devices()
        
        # Suggest ports to avoid (those with potential real devices)
        avoid_ports = [port.device for port in ga_ports]
        
        # Suggest simulator port
        simulator_port = self.suggest_simulator_port(avoid_ports)
        
        recommendations = {
            'total_ports_found': len(all_ports),
            'available_ports': [port.device for port in all_ports if port.status == PortStatus.AVAILABLE],
            'ga_device_ports': [port.device for port in ga_ports],
            'suggested_simulator_port': simulator_port,
            'avoid_ports': avoid_ports,
            'platform': self.platform,
            'recommendations': []
        }
        
        # Add specific recommendations
        if ga_ports:
            recommendations['recommendations'].append(
                f"Found {len(ga_ports)} potential GA device(s) on: {[p.device for p in ga_ports]}"
            )
            recommendations['recommendations'].append(
                "Avoid these ports for simulator to prevent conflicts"
            )
        
        if simulator_port:
            recommendations['recommendations'].append(
                f"Use {simulator_port} for simulator (avoids conflicts)"
            )
        else:
            recommendations['recommendations'].append(
                "No suitable port found for simulator - check connections"
            )
        
        if len(all_ports) < 2:
            recommendations['recommendations'].append(
                "Consider using USB-to-Serial adapters for more ports"
            )
        
        return recommendations
    
    def monitor_port_changes(self, callback=None) -> List[PortInfo]:
        """
        Monitor for port changes (simple polling-based approach)
        
        This is a basic implementation - for real-time monitoring,
        platform-specific solutions would be better.
        """
        # This is a simple implementation for demonstration
        # In production, you might want to use platform-specific
        # port change notifications
        return self.get_available_ports()
    
    def format_port_table(self, ports: Optional[List[PortInfo]] = None) -> str:
        """Format port information as a readable table"""
        if ports is None:
            ports = self.get_available_ports()
        
        if not ports:
            return "No serial ports found"
        
        # Calculate column widths
        max_device = max(len(port.device) for port in ports)
        max_desc = max(len(port.description) for port in ports)
        max_status = max(len(port.status.value) for port in ports)
        
        # Create header
        header = f"{'Device':<{max_device}} | {'Description':<{max_desc}} | {'Status':<{max_status}} | GA Device | Virtual"
        separator = "-" * len(header)
        
        # Create rows
        rows = [header, separator]
        for port in ports:
            ga_flag = "Yes" if port.is_ga_device else "No"
            virtual_flag = "Yes" if port.is_virtual else "No"
            
            row = f"{port.device:<{max_device}} | {port.description:<{max_desc}} | {port.status.value:<{max_status}} | {ga_flag:^9} | {virtual_flag:^7}"
            rows.append(row)
        
        return "\n".join(rows)


def main():
    """Test function for the COM port manager"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create port manager
    manager = ComPortManager()
    
    print("COM Port Manager Test")
    print("=" * 50)
    
    # Get port information
    ports = manager.get_available_ports()
    print(f"\nFound {len(ports)} serial ports:")
    print(manager.format_port_table(ports))
    
    # Detect GA devices
    ga_ports = manager.detect_ga_devices()
    if ga_ports:
        print(f"\nDetected GA devices on:")
        for port in ga_ports:
            print(f"  {port.device}: {port.description}")
    
    # Get recommendations
    recommendations = manager.get_port_recommendations()
    print(f"\nPort Recommendations:")
    print(f"  Platform: {recommendations['platform']}")
    print(f"  Total ports: {recommendations['total_ports_found']}")
    print(f"  Available: {recommendations['available_ports']}")
    print(f"  GA devices: {recommendations['ga_device_ports']}")
    print(f"  Suggested simulator port: {recommendations['suggested_simulator_port']}")
    
    for rec in recommendations['recommendations']:
        print(f"  - {rec}")
    
    # Test port validation
    if recommendations['suggested_simulator_port']:
        port = recommendations['suggested_simulator_port']
        valid, message = manager.validate_port_config(port)
        print(f"\nPort validation for {port}: {valid} - {message}")


if __name__ == "__main__":
    main()