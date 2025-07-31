"""
Serial connection manager with persistence and recovery.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, AsyncIterator, Callable
from dataclasses import dataclass, field

try:
    import serial_asyncio
    import serial
    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False

from .config import SerialConfig
from .detector import PortDetector, PortInfo
from .exceptions import (
    ConnectionError, DeviceNotFoundError, 
    PermissionError, ConfigurationError,
    SerialCommError
)


@dataclass
class ConnectionStats:
    """Statistics for serial connection."""
    connect_time: float = field(default_factory=time.time)
    bytes_sent: int = 0
    bytes_received: int = 0
    reconnect_count: int = 0
    last_activity: float = field(default_factory=time.time)
    errors: int = 0
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = time.time()
    
    def add_sent(self, bytes_count: int):
        """Add sent bytes to statistics."""
        self.bytes_sent += bytes_count
        self.update_activity()
    
    def add_received(self, bytes_count: int):
        """Add received bytes to statistics."""
        self.bytes_received += bytes_count
        self.update_activity()
    
    def add_error(self):
        """Increment error count."""
        self.errors += 1
    
    def add_reconnect(self):
        """Increment reconnect count."""
        self.reconnect_count += 1


class SerialConnection:
    """Async serial connection wrapper with health monitoring."""
    
    def __init__(self, 
                 reader: asyncio.StreamReader,
                 writer: asyncio.StreamWriter, 
                 serial_instance: serial.Serial,
                 config: SerialConfig,
                 device_path: str,
                 logger: logging.Logger):
        """Initialize serial connection."""
        self.reader = reader
        self.writer = writer
        self.serial = serial_instance
        self.config = config
        self.device_path = device_path
        self.logger = logger
        self.stats = ConnectionStats()
        self._closed = False
        self._health_check_task: Optional[asyncio.Task] = None
        
        # Start health monitoring
        if config.connection_check_interval > 0:
            self._health_check_task = asyncio.create_task(self._health_monitor())
    
    async def read(self, size: int = -1) -> bytes:
        """Read data from serial connection."""
        if self._closed:
            raise ConnectionError("Connection is closed")
        
        try:
            if size == -1:
                data = await self.reader.read(self.config.read_buffer_size)
            else:
                data = await self.reader.read(size)
            
            if data:
                self.stats.add_received(len(data))
                if self.config.log_raw_data:
                    self.logger.debug(f"Received: {data.hex()}")
            
            return data
            
        except Exception as e:
            self.stats.add_error()
            self.logger.error(f"Read error: {e}")
            raise ConnectionError(f"Read failed: {e}")
    
    async def readline(self) -> bytes:
        """Read a line from serial connection."""
        if self._closed:
            raise ConnectionError("Connection is closed")
        
        try:
            data = await self.reader.readline()
            if data:
                self.stats.add_received(len(data))
                if self.config.log_raw_data:
                    self.logger.debug(f"Received line: {data.hex()}")
            return data
            
        except Exception as e:
            self.stats.add_error()
            self.logger.error(f"Readline error: {e}")
            raise ConnectionError(f"Readline failed: {e}")
    
    async def read_until(self, separator: bytes = b'\n') -> bytes:
        """Read until separator is found."""
        if self._closed:
            raise ConnectionError("Connection is closed")
        
        try:
            data = await self.reader.readuntil(separator)
            if data:
                self.stats.add_received(len(data))
                if self.config.log_raw_data:
                    self.logger.debug(f"Received until '{separator.hex()}': {data.hex()}")
            return data
            
        except Exception as e:
            self.stats.add_error()
            self.logger.error(f"Read until error: {e}")
            raise ConnectionError(f"Read until failed: {e}")
    
    async def write(self, data: bytes) -> None:
        """Write data to serial connection."""
        if self._closed:
            raise ConnectionError("Connection is closed")
        
        try:
            self.writer.write(data)
            await self.writer.drain()
            
            self.stats.add_sent(len(data))
            if self.config.log_raw_data:
                self.logger.debug(f"Sent: {data.hex()}")
                
        except Exception as e:
            self.stats.add_error()
            self.logger.error(f"Write error: {e}")
            raise ConnectionError(f"Write failed: {e}")
    
    async def flush(self) -> None:
        """Flush write buffer."""
        if not self._closed:
            try:
                await self.writer.drain()
            except Exception as e:
                self.logger.warning(f"Flush error: {e}")
    
    def is_open(self) -> bool:
        """Check if connection is open."""
        return not self._closed and self.serial.is_open
    
    async def close(self) -> None:
        """Close serial connection."""
        if self._closed:
            return
        
        self._closed = True
        
        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Close writer
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception as e:
                self.logger.debug(f"Error closing writer: {e}")
        
        # Close serial port
        if self.serial and self.serial.is_open:
            try:
                self.serial.close()
            except Exception as e:
                self.logger.debug(f"Error closing serial port: {e}")
        
        self.logger.info(f"Connection to {self.device_path} closed")
    
    async def _health_monitor(self) -> None:
        """Monitor connection health."""
        while not self._closed:
            try:
                await asyncio.sleep(self.config.connection_check_interval)
                
                if self._closed:
                    break
                
                # Check if serial port is still open
                if not self.serial.is_open:
                    self.logger.warning("Serial port closed unexpectedly")
                    break
                
                # Check for timeout since last activity
                inactive_time = time.time() - self.stats.last_activity
                if inactive_time > self.config.connection_check_interval * 3:
                    self.logger.debug(f"Connection inactive for {inactive_time:.1f}s")
                
            except Exception as e:
                self.logger.error(f"Health monitor error: {e}")
                break
    
    def __str__(self) -> str:
        """String representation of connection."""
        status = "open" if self.is_open() else "closed"
        return f"SerialConnection({self.device_path}, {status})"


class SerialManager:
    """Manages serial connections with auto-discovery and recovery."""
    
    def __init__(self, config: Optional[SerialConfig] = None, logger: Optional[logging.Logger] = None):
        """Initialize serial manager."""
        if not PYSERIAL_AVAILABLE:
            raise SerialCommError("pyserial and pyserial-asyncio are required")
        
        self.config = config or SerialConfig()
        self.logger = logger or logging.getLogger(__name__)
        self.detector = PortDetector(self.logger)
        self._connections: Dict[str, SerialConnection] = {}
        
        # Setup logging
        if self.logger.level == logging.NOTSET:
            self.logger.setLevel(self.config.log_level)
    
    async def list_ports(self) -> List[PortInfo]:
        """List all available serial ports."""
        return await self.detector.list_ports()
    
    async def find_rs422_ports(self) -> List[PortInfo]:
        """Find RS422 compatible ports."""
        return await self.detector.find_rs422_ports()
    
    async def auto_connect(self, 
                          vid_pid: Optional[tuple] = None,
                          description_pattern: Optional[str] = None,
                          serial_number: Optional[str] = None) -> SerialConnection:
        """
        Automatically connect to a device based on criteria.
        
        Args:
            vid_pid: Tuple of (vendor_id, product_id)
            description_pattern: Regex pattern for device description
            serial_number: Device serial number
            
        Returns:
            SerialConnection object
        """
        port_info = None
        
        if vid_pid:
            vid, pid = vid_pid
            port_info = await self.detector.find_port_by_vid_pid(vid, pid)
        elif description_pattern:
            port_info = await self.detector.find_port_by_description(description_pattern)
        elif serial_number:
            port_info = await self.detector.find_port_by_serial_number(serial_number)
        else:
            # Try to find any RS422 compatible port
            rs422_ports = await self.find_rs422_ports()
            if rs422_ports:
                port_info = rs422_ports[0]
        
        if not port_info:
            raise DeviceNotFoundError("No suitable device found for auto-connection")
        
        self.logger.info(f"Auto-connecting to: {port_info}")
        return await self.connect(port_info.device)
    
    async def connect(self, device_path: str, config: Optional[SerialConfig] = None) -> SerialConnection:
        """
        Connect to a serial device.
        
        Args:
            device_path: Path to serial device
            config: Optional custom configuration
            
        Returns:
            SerialConnection object
        """
        use_config = config or self.config
        
        # Check if already connected
        if device_path in self._connections:
            connection = self._connections[device_path]
            if connection.is_open():
                self.logger.debug(f"Reusing existing connection to {device_path}")
                return connection
            else:
                # Remove stale connection
                await connection.close()
                del self._connections[device_path]
        
        # Verify device exists
        if not await self.detector.verify_port_exists(device_path):
            raise DeviceNotFoundError(f"Device {device_path} not found")
        
        # Attempt connection with retries
        last_error = None
        for attempt in range(use_config.reconnect_attempts + 1):
            try:
                connection = await self._create_connection(device_path, use_config)
                self._connections[device_path] = connection
                
                self.logger.info(f"Connected to {device_path} on attempt {attempt + 1}")
                if attempt > 0:
                    connection.stats.add_reconnect()
                
                return connection
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                
                if attempt < use_config.reconnect_attempts:
                    await asyncio.sleep(use_config.reconnect_delay)
        
        raise ConnectionError(f"Failed to connect to {device_path} after {use_config.reconnect_attempts + 1} attempts: {last_error}")
    
    async def _create_connection(self, device_path: str, config: SerialConfig) -> SerialConnection:
        """Create a new serial connection."""
        try:
            # Create serial instance
            serial_kwargs = config.to_dict()
            serial_instance = serial.Serial(device_path, **serial_kwargs)
            
            # Configure RS485/RS422 mode if enabled
            if config.rs485_mode and hasattr(serial_instance, 'rs485_mode'):
                serial_instance.rs485_mode = serial.rs485.RS485Settings()
            
            # Create async streams
            reader, writer = await serial_asyncio.open_serial_connection(
                url=device_path,
                **serial_kwargs
            )
            
            connection = SerialConnection(
                reader=reader,
                writer=writer,
                serial_instance=serial_instance,
                config=config,
                device_path=device_path,
                logger=self.logger
            )
            
            self.logger.debug(f"Created connection to {device_path}")
            return connection
            
        except serial.SerialException as e:
            if "permission denied" in str(e).lower():
                raise PermissionError(f"Permission denied accessing {device_path}")
            elif "device not found" in str(e).lower():
                raise DeviceNotFoundError(f"Device {device_path} not found")
            else:
                raise ConnectionError(f"Serial connection failed: {e}")
        except Exception as e:
            raise ConnectionError(f"Failed to create connection: {e}")
    
    @asynccontextmanager
    async def connect_context(self, device_path: str, 
                             config: Optional[SerialConfig] = None) -> AsyncIterator[SerialConnection]:
        """
        Context manager for automatic connection cleanup.
        
        Usage:
            async with manager.connect_context('/dev/ttyUSB0') as conn:
                await conn.write(b'hello')
                response = await conn.read()
        """
        connection = await self.connect(device_path, config)
        try:
            yield connection
        finally:
            await self.disconnect(device_path)
    
    async def disconnect(self, device_path: str) -> None:
        """Disconnect from a device."""
        if device_path in self._connections:
            connection = self._connections[device_path]
            await connection.close()
            del self._connections[device_path]
            self.logger.info(f"Disconnected from {device_path}")
    
    async def disconnect_all(self) -> None:
        """Disconnect from all devices."""
        for device_path in list(self._connections.keys()):
            await self.disconnect(device_path)
    
    def get_connection(self, device_path: str) -> Optional[SerialConnection]:
        """Get existing connection to device."""
        return self._connections.get(device_path)
    
    def get_active_connections(self) -> Dict[str, SerialConnection]:
        """Get all active connections."""
        return {path: conn for path, conn in self._connections.items() if conn.is_open()}
    
    async def reconnect(self, device_path: str) -> SerialConnection:
        """Reconnect to a device."""
        await self.disconnect(device_path)
        return await self.connect(device_path)
    
    async def close(self) -> None:
        """Close manager and all connections."""
        await self.disconnect_all()
        self.logger.info("Serial manager closed")