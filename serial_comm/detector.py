"""
Serial port detection and enumeration functionality.
"""

import asyncio
import logging
import platform
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

try:
    import serial.tools.list_ports
    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False

from .exceptions import DeviceNotFoundError, SerialCommError


@dataclass
class PortInfo:
    """Information about a detected serial port."""
    device: str
    description: str
    manufacturer: Optional[str] = None
    product: Optional[str] = None
    vid: Optional[int] = None
    pid: Optional[int] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    interface: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of port info."""
        parts = [f"{self.device}"]
        if self.description:
            parts.append(f"({self.description})")
        if self.manufacturer:
            parts.append(f"- {self.manufacturer}")
        if self.product:
            parts.append(f"{self.product}")
        return " ".join(parts)
    
    @property
    def is_usb(self) -> bool:
        """Check if this is a USB serial device."""
        return self.vid is not None and self.pid is not None
    
    @property
    def is_rs422_compatible(self) -> bool:
        """Check if device appears to be RS422 compatible."""
        # Common RS422/RS485 adapter indicators
        rs422_indicators = [
            'rs422', 'rs485', '422', '485',
            'ftdi', 'prolific', 'cp210', 'ch340'
        ]
        
        search_text = f"{self.description} {self.manufacturer} {self.product}".lower()
        return any(indicator in search_text for indicator in rs422_indicators)


class PortDetector:
    """Detect and enumerate serial ports with RS422 support."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize port detector."""
        self.logger = logger or logging.getLogger(__name__)
        
        if not PYSERIAL_AVAILABLE:
            raise SerialCommError("pyserial library is required for port detection")
    
    async def list_ports(self, include_links: bool = True) -> List[PortInfo]:
        """
        List all available serial ports.
        
        Args:
            include_links: Include symbolic links to devices
            
        Returns:
            List of PortInfo objects for detected ports
        """
        self.logger.debug("Scanning for serial ports...")
        
        ports = []
        
        try:
            # Use pyserial's list_ports for cross-platform detection
            for port_info in serial.tools.list_ports.comports(include_links=include_links):
                port = PortInfo(
                    device=port_info.device,
                    description=port_info.description or "Unknown",
                    manufacturer=port_info.manufacturer,
                    product=port_info.product,
                    vid=port_info.vid,
                    pid=port_info.pid,
                    serial_number=port_info.serial_number,
                    location=port_info.location,
                    interface=getattr(port_info, 'interface', None)
                )
                ports.append(port)
                
        except Exception as e:
            self.logger.error(f"Error listing ports: {e}")
            # Fallback to manual detection
            ports.extend(await self._manual_port_detection())
        
        self.logger.info(f"Found {len(ports)} serial ports")
        for port in ports:
            self.logger.debug(f"  {port}")
        
        return ports
    
    async def find_rs422_ports(self) -> List[PortInfo]:
        """Find ports that appear to be RS422 compatible."""
        all_ports = await self.list_ports()
        rs422_ports = [port for port in all_ports if port.is_rs422_compatible]
        
        self.logger.info(f"Found {len(rs422_ports)} potential RS422 ports")
        return rs422_ports
    
    async def find_port_by_description(self, description_pattern: str) -> Optional[PortInfo]:
        """
        Find port by description pattern.
        
        Args:
            description_pattern: Regex pattern to match against port description
            
        Returns:
            First matching PortInfo or None
        """
        ports = await self.list_ports()
        pattern = re.compile(description_pattern, re.IGNORECASE)
        
        for port in ports:
            if pattern.search(port.description):
                self.logger.debug(f"Found port matching '{description_pattern}': {port}")
                return port
        
        return None
    
    async def find_port_by_vid_pid(self, vid: int, pid: int) -> Optional[PortInfo]:
        """
        Find port by USB Vendor ID and Product ID.
        
        Args:
            vid: USB Vendor ID
            pid: USB Product ID
            
        Returns:
            First matching PortInfo or None
        """
        ports = await self.list_ports()
        
        for port in ports:
            if port.vid == vid and port.pid == pid:
                self.logger.debug(f"Found port with VID:PID {vid:04X}:{pid:04X}: {port}")
                return port
        
        return None
    
    async def find_port_by_serial_number(self, serial_number: str) -> Optional[PortInfo]:
        """
        Find port by serial number.
        
        Args:
            serial_number: Device serial number
            
        Returns:
            First matching PortInfo or None
        """
        ports = await self.list_ports()
        
        for port in ports:
            if port.serial_number == serial_number:
                self.logger.debug(f"Found port with serial {serial_number}: {port}")
                return port
        
        return None
    
    async def verify_port_exists(self, device_path: str) -> bool:
        """
        Verify that a port device exists and is accessible.
        
        Args:
            device_path: Path to serial device
            
        Returns:
            True if port exists and is accessible
        """
        try:
            path = Path(device_path)
            
            # Check if device file exists
            if not path.exists():
                self.logger.debug(f"Device {device_path} does not exist")
                return False
            
            # On Unix systems, check if it's a character device
            if platform.system() != 'Windows':
                if not path.is_char_device():
                    self.logger.debug(f"Device {device_path} is not a character device")
                    return False
            
            # Try to access the device (basic permission check)
            try:
                path.stat()
                self.logger.debug(f"Device {device_path} is accessible")
                return True
            except PermissionError:
                self.logger.debug(f"Permission denied accessing {device_path}")
                return False
                
        except Exception as e:
            self.logger.debug(f"Error verifying port {device_path}: {e}")
            return False
    
    async def get_port_info(self, device_path: str) -> Optional[PortInfo]:
        """
        Get detailed information about a specific port.
        
        Args:
            device_path: Path to serial device
            
        Returns:
            PortInfo object or None if not found
        """
        ports = await self.list_ports()
        
        for port in ports:
            if port.device == device_path:
                return port
        
        # If not found in list_ports, create basic info if device exists
        if await self.verify_port_exists(device_path):
            return PortInfo(
                device=device_path,
                description="Manual device",
                manufacturer=None
            )
        
        return None
    
    async def _manual_port_detection(self) -> List[PortInfo]:
        """Manual port detection as fallback."""
        ports = []
        system = platform.system()
        
        try:
            if system == "Linux":
                ports.extend(await self._detect_linux_ports())
            elif system == "Windows":
                ports.extend(await self._detect_windows_ports()) 
            elif system == "Darwin":  # macOS
                ports.extend(await self._detect_macos_ports())
                
        except Exception as e:
            self.logger.error(f"Manual port detection failed: {e}")
        
        return ports
    
    async def _detect_linux_ports(self) -> List[PortInfo]:
        """Detect serial ports on Linux."""
        ports = []
        
        # Common Linux serial device patterns
        patterns = [
            '/dev/ttyUSB*',
            '/dev/ttyACM*', 
            '/dev/ttyS*',
            '/dev/ttyAMA*',
            '/dev/serial/by-id/*'
        ]
        
        for pattern in patterns:
            try:
                from glob import glob
                devices = glob(pattern)
                
                for device in devices:
                    if await self.verify_port_exists(device):
                        ports.append(PortInfo(
                            device=device,
                            description=f"Linux serial device ({Path(device).name})"
                        ))
            except Exception as e:
                self.logger.debug(f"Error checking pattern {pattern}: {e}")
        
        return ports
    
    async def _detect_windows_ports(self) -> List[PortInfo]:
        """Detect serial ports on Windows."""
        ports = []
        
        # Windows COM port detection
        for i in range(1, 256):
            device = f"COM{i}"
            try:
                # Try to open the port briefly to check if it exists
                import serial
                with serial.Serial(device, timeout=0) as ser:
                    ports.append(PortInfo(
                        device=device,
                        description=f"Windows COM port {i}"
                    ))
            except (serial.SerialException, FileNotFoundError):
                # Port doesn't exist or is in use
                continue
            except Exception as e:
                self.logger.debug(f"Error checking {device}: {e}")
        
        return ports
    
    async def _detect_macos_ports(self) -> List[PortInfo]:
        """Detect serial ports on macOS."""
        ports = []
        
        # Common macOS serial device patterns
        patterns = [
            '/dev/tty.usb*',
            '/dev/cu.usb*',
            '/dev/tty.SLAB*',
            '/dev/cu.SLAB*'
        ]
        
        for pattern in patterns:
            try:
                from glob import glob
                devices = glob(pattern)
                
                for device in devices:
                    if await self.verify_port_exists(device):
                        ports.append(PortInfo(
                            device=device,
                            description=f"macOS serial device ({Path(device).name})"
                        ))
            except Exception as e:
                self.logger.debug(f"Error checking pattern {pattern}: {e}")
        
        return ports