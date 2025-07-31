"""
Configuration management for serial communication.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum

from .exceptions import ConfigurationError


class Parity(Enum):
    """Serial parity options."""
    NONE = 'N'
    EVEN = 'E' 
    ODD = 'O'
    MARK = 'M'
    SPACE = 'S'


class StopBits(Enum):
    """Serial stop bits options."""
    ONE = 1
    ONE_POINT_FIVE = 1.5
    TWO = 2


class FlowControl(Enum):
    """Flow control options for RS422."""
    NONE = 'none'
    RTS_CTS = 'rts_cts'
    XON_XOFF = 'xon_xoff'


@dataclass
class SerialConfig:
    """Configuration for serial communication parameters."""
    
    # Basic serial parameters
    baudrate: int = 115200
    bytesize: int = 8
    parity: Parity = Parity.NONE
    stopbits: StopBits = StopBits.ONE
    
    # RS422 specific parameters
    flow_control: FlowControl = FlowControl.RTS_CTS
    rs485_mode: bool = False  # Enable for RS485/RS422 adapters
    
    # Timeout settings
    timeout: float = 1.0
    write_timeout: float = 1.0
    inter_byte_timeout: Optional[float] = None
    
    # Connection management
    reconnect_attempts: int = 3
    reconnect_delay: float = 1.0
    connection_check_interval: float = 5.0
    
    # Buffer settings
    read_buffer_size: int = 4096
    write_buffer_size: int = 4096
    
    # Protocol settings
    message_timeout: float = 2.0
    max_message_size: int = 1024
    enable_checksum: bool = True
    
    # Logging
    log_level: int = logging.INFO
    log_raw_data: bool = False
    
    # Advanced settings
    exclusive: bool = True
    dsrdtr: bool = False
    rtscts: bool = False
    xonxoff: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.baudrate <= 0:
            raise ConfigurationError("Baudrate must be positive")
        
        if self.bytesize not in [5, 6, 7, 8]:
            raise ConfigurationError("Bytesize must be 5, 6, 7, or 8")
        
        if self.timeout < 0:
            raise ConfigurationError("Timeout must be non-negative")
        
        if self.write_timeout < 0:
            raise ConfigurationError("Write timeout must be non-negative")
        
        if self.reconnect_attempts < 0:
            raise ConfigurationError("Reconnect attempts must be non-negative")
        
        if self.reconnect_delay < 0:
            raise ConfigurationError("Reconnect delay must be non-negative")
        
        if self.read_buffer_size <= 0:
            raise ConfigurationError("Read buffer size must be positive")
        
        if self.write_buffer_size <= 0:
            raise ConfigurationError("Write buffer size must be positive")
        
        if self.max_message_size <= 0:
            raise ConfigurationError("Max message size must be positive")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'baudrate': self.baudrate,
            'bytesize': self.bytesize,
            'parity': self.parity.value,
            'stopbits': self.stopbits.value,
            'timeout': self.timeout,
            'write_timeout': self.write_timeout,
            'inter_byte_timeout': self.inter_byte_timeout,
            'xonxoff': self.xonxoff,
            'rtscts': self.rtscts,
            'dsrdtr': self.dsrdtr,
            'exclusive': self.exclusive
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SerialConfig':
        """Create configuration from dictionary."""
        config = cls()
        
        # Update basic parameters
        for key, value in data.items():
            if hasattr(config, key):
                if key == 'parity' and isinstance(value, str):
                    setattr(config, key, Parity(value))
                elif key == 'stopbits' and isinstance(value, (int, float)):
                    setattr(config, key, StopBits(value))
                elif key == 'flow_control' and isinstance(value, str):
                    setattr(config, key, FlowControl(value))
                else:
                    setattr(config, key, value)
        
        config.validate()
        return config
    
    @classmethod
    def rs422_default(cls) -> 'SerialConfig':
        """Create default RS422 configuration."""
        return cls(
            baudrate=115200,
            bytesize=8,
            parity=Parity.NONE,
            stopbits=StopBits.ONE,
            flow_control=FlowControl.RTS_CTS,
            rs485_mode=True,
            timeout=1.0,
            write_timeout=1.0
        )
    
    @classmethod  
    def high_speed_rs422(cls) -> 'SerialConfig':
        """Create high-speed RS422 configuration."""
        return cls(
            baudrate=921600,
            bytesize=8,
            parity=Parity.NONE,
            stopbits=StopBits.ONE,
            flow_control=FlowControl.RTS_CTS,
            rs485_mode=True,
            timeout=0.5,
            write_timeout=0.5,
            message_timeout=1.0
        )