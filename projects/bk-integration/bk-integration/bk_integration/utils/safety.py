"""Safety monitoring utilities for BK-Integration."""

import logging
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety alert levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class SafetyError(Exception):
    """Safety-related error."""
    pass


@dataclass
class SafetyLimit:
    """Safety limit definition."""
    name: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    tolerance_percent: float = 0.0
    level: SafetyLevel = SafetyLevel.WARNING
    
    def check(self, value: float) -> bool:
        """Check if value is within safety limits."""
        tolerance = self.tolerance_percent / 100.0
        
        if self.min_value is not None:
            adjusted_min = self.min_value * (1 - tolerance)
            if value < adjusted_min:
                return False
        
        if self.max_value is not None:
            adjusted_max = self.max_value * (1 + tolerance)
            if value > adjusted_max:
                return False
        
        return True


@dataclass
class SafetyEvent:
    """Safety event record."""
    timestamp: float
    level: SafetyLevel
    device: str
    parameter: str
    value: float
    limit: SafetyLimit
    message: str
    acknowledged: bool = False


class SafetyMonitor:
    """Comprehensive safety monitoring system for BK devices."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize safety monitor.
        
        Args:
            config: Safety configuration dictionary
        """
        self.config = config or {}
        self.events: List[SafetyEvent] = []
        self.callbacks: Dict[SafetyLevel, List[Callable]] = {
            level: [] for level in SafetyLevel
        }
        
        # Initialize safety limits
        self.limits = self._create_default_limits()
        self._apply_config_limits()
        
        # Monitoring state
        self.monitoring_active = False
        self.emergency_stop_callback: Optional[Callable] = None
        
        logger.info("Safety monitor initialized")
    
    def _create_default_limits(self) -> Dict[str, Dict[str, SafetyLimit]]:
        """Create default safety limits for both devices."""
        limits = {
            'bk8520': {
                'voltage': SafetyLimit(
                    name='BK8520 Voltage',
                    min_value=0.0,
                    max_value=120.0,
                    tolerance_percent=5.0,
                    level=SafetyLevel.CRITICAL
                ),
                'current': SafetyLimit(
                    name='BK8520 Current',
                    min_value=0.0,
                    max_value=60.0,
                    tolerance_percent=10.0,
                    level=SafetyLevel.CRITICAL
                ),
                'power': SafetyLimit(
                    name='BK8520 Power',
                    min_value=0.0,
                    max_value=999.0,
                    tolerance_percent=5.0,
                    level=SafetyLevel.WARNING
                ),
                'temperature': SafetyLimit(
                    name='BK8520 Temperature',
                    min_value=-10.0,
                    max_value=85.0,
                    tolerance_percent=0.0,
                    level=SafetyLevel.EMERGENCY
                )
            },
            'bk9206b': {
                'voltage': SafetyLimit(
                    name='BK9206b Voltage',
                    min_value=0.0,
                    max_value=60.0,
                    tolerance_percent=5.0,
                    level=SafetyLevel.CRITICAL
                ),
                'current': SafetyLimit(
                    name='BK9206b Current',
                    min_value=0.0,
                    max_value=5.0,
                    tolerance_percent=10.0,
                    level=SafetyLevel.CRITICAL
                ),
                'power': SafetyLimit(
                    name='BK9206b Power',
                    min_value=0.0,
                    max_value=300.0,
                    tolerance_percent=5.0,
                    level=SafetyLevel.WARNING
                )
            }
        }
        
        return limits
    
    def _apply_config_limits(self) -> None:
        """Apply safety limits from configuration."""
        if not self.config:
            return
        
        # Apply device-specific overrides
        devices_config = self.config.get('devices', {})
        
        for device_name, device_config in devices_config.items():
            if device_name in self.limits:
                safety_limits = device_config.get('safety_limits', {})
                
                for param, limit_value in safety_limits.items():
                    if param in self.limits[device_name]:
                        # Update max value from config
                        self.limits[device_name][param].max_value = limit_value
                        logger.debug(f"Updated {device_name} {param} limit to {limit_value}")
        
        # Apply global safety overrides
        safety_config = self.config.get('safety', {})
        
        if 'voltage_tolerance_percent' in safety_config:
            tolerance = safety_config['voltage_tolerance_percent']
            for device in self.limits.values():
                if 'voltage' in device:
                    device['voltage'].tolerance_percent = tolerance
        
        if 'current_tolerance_percent' in safety_config:
            tolerance = safety_config['current_tolerance_percent']
            for device in self.limits.values():
                if 'current' in device:
                    device['current'].tolerance_percent = tolerance
    
    def check_reading_safety(self, device: str, readings: Dict[str, Any]) -> bool:
        """Check if device readings are within safety limits.
        
        Args:
            device: Device name ('bk8520' or 'bk9206b')
            readings: Device readings dictionary
            
        Returns:
            True if all readings are safe, False otherwise
        """
        if device not in self.limits:
            logger.warning(f"No safety limits defined for device: {device}")
            return True
        
        device_limits = self.limits[device]
        all_safe = True
        
        for param, value in readings.items():
            if param in device_limits and isinstance(value, (int, float)):
                limit = device_limits[param]
                
                if not limit.check(value):
                    self._record_safety_event(
                        device=device,
                        parameter=param,
                        value=value,
                        limit=limit,
                        message=f"{param} value {value} exceeds safety limit"
                    )
                    all_safe = False
        
        return all_safe
    
    def check_charging_safety(self, data: Dict[str, Any]) -> bool:
        """Check charging phase safety.
        
        Args:
            data: Charging data point
            
        Returns:
            True if charging is safe to continue
        """
        voltage = data.get('voltage_actual', 0)
        current = data.get('current_actual', 0)
        power = data.get('power_actual', 0)
        
        # Check against BK9206b limits
        readings = {
            'voltage': voltage,
            'current': current,
            'power': power
        }
        
        safe = self.check_reading_safety('bk9206b', readings)
        
        # Additional charging-specific checks
        if current < 0:
            self._record_safety_event(
                device='bk9206b',
                parameter='current',
                value=current,
                limit=SafetyLimit('Charging Current', min_value=0.0),
                message="Negative current detected during charging"
            )
            safe = False
        
        # Check for voltage runaway
        if voltage > 70.0:  # Well above normal battery voltage
            self._record_safety_event(
                device='bk9206b',
                parameter='voltage',
                value=voltage,
                limit=SafetyLimit('Charging Voltage Runaway', max_value=70.0),
                message="Voltage runaway detected during charging"
            )
            safe = False
        
        return safe
    
    def check_discharge_safety(self, data: Dict[str, Any]) -> bool:
        """Check discharge phase safety.
        
        Args:
            data: Discharge data point
            
        Returns:
            True if discharge is safe to continue
        """
        voltage = data.get('voltage', 0)
        current = data.get('current', 0)
        power = data.get('power', 0)
        
        # Check against BK8520 limits
        readings = {
            'voltage': voltage,
            'current': current,
            'power': power
        }
        
        safe = self.check_reading_safety('bk8520', readings)
        
        # Additional discharge-specific checks
        if voltage < 0:
            self._record_safety_event(
                device='bk8520',
                parameter='voltage',
                value=voltage,
                limit=SafetyLimit('Discharge Voltage', min_value=0.0),
                message="Negative voltage detected during discharge"
            )
            safe = False
        
        # Check for current spike
        if current > 65.0:  # Above normal maximum
            self._record_safety_event(
                device='bk8520',
                parameter='current',
                value=current,
                limit=SafetyLimit('Current Spike', max_value=65.0),
                message="Current spike detected during discharge"
            )
            safe = False
        
        return safe
    
    def _record_safety_event(self, device: str, parameter: str, value: float,
                           limit: SafetyLimit, message: str) -> None:
        """Record a safety event."""
        event = SafetyEvent(
            timestamp=time.time(),
            level=limit.level,
            device=device,
            parameter=parameter,
            value=value,
            limit=limit,
            message=message
        )
        
        self.events.append(event)
        
        # Log event
        log_methods = {
            SafetyLevel.INFO: logger.info,
            SafetyLevel.WARNING: logger.warning,
            SafetyLevel.CRITICAL: logger.error,
            SafetyLevel.EMERGENCY: logger.critical
        }
        
        log_method = log_methods.get(limit.level, logger.info)
        log_method(f"SAFETY [{limit.level.value.upper()}] {device}: {message}")
        
        # Execute callbacks
        for callback in self.callbacks.get(limit.level, []):
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Safety callback error: {e}")
        
        # Emergency stop for critical events
        if limit.level == SafetyLevel.EMERGENCY and self.emergency_stop_callback:
            logger.critical("EMERGENCY STOP triggered by safety event")
            try:
                self.emergency_stop_callback(event)
            except Exception as e:
                logger.error(f"Emergency stop callback error: {e}")
    
    def register_callback(self, level: SafetyLevel, callback: Callable) -> None:
        """Register callback for safety events of specified level.
        
        Args:
            level: Safety level to monitor
            callback: Callback function that receives SafetyEvent
        """
        if level not in self.callbacks:
            self.callbacks[level] = []
        
        self.callbacks[level].append(callback)
        logger.info(f"Registered safety callback for {level.value} events")
    
    def set_emergency_stop_callback(self, callback: Callable) -> None:
        """Set emergency stop callback for critical safety events.
        
        Args:
            callback: Emergency stop callback function
        """
        self.emergency_stop_callback = callback
        logger.info("Emergency stop callback registered")
    
    def get_recent_events(self, level: Optional[SafetyLevel] = None,
                         device: Optional[str] = None,
                         hours: float = 24.0) -> List[SafetyEvent]:
        """Get recent safety events matching criteria.
        
        Args:
            level: Filter by safety level
            device: Filter by device name
            hours: Hours to look back
            
        Returns:
            List of matching safety events
        """
        cutoff_time = time.time() - (hours * 3600)
        
        filtered_events = []
        for event in self.events:
            if event.timestamp < cutoff_time:
                continue
            
            if level and event.level != level:
                continue
            
            if device and event.device != device:
                continue
            
            filtered_events.append(event)
        
        return filtered_events
    
    def get_safety_summary(self) -> Dict[str, Any]:
        """Get safety monitoring summary.
        
        Returns:
            Safety summary dictionary
        """
        recent_events = self.get_recent_events(hours=24.0)
        
        event_counts = {level.value: 0 for level in SafetyLevel}
        for event in recent_events:
            event_counts[event.level.value] += 1
        
        return {
            'monitoring_active': self.monitoring_active,
            'total_events': len(self.events),
            'recent_events_24h': len(recent_events),
            'event_counts': event_counts,
            'emergency_stop_configured': self.emergency_stop_callback is not None,
            'devices_monitored': list(self.limits.keys())
        }
    
    def acknowledge_event(self, event_index: int) -> bool:
        """Acknowledge a safety event.
        
        Args:
            event_index: Index of event to acknowledge
            
        Returns:
            True if acknowledged successfully
        """
        if 0 <= event_index < len(self.events):
            self.events[event_index].acknowledged = True
            logger.info(f"Safety event {event_index} acknowledged")
            return True
        return False
    
    def clear_old_events(self, hours: float = 168.0) -> int:
        """Clear safety events older than specified hours.
        
        Args:
            hours: Age threshold in hours (default: 1 week)
            
        Returns:
            Number of events cleared
        """
        cutoff_time = time.time() - (hours * 3600)
        initial_count = len(self.events)
        
        self.events = [event for event in self.events if event.timestamp >= cutoff_time]
        
        cleared_count = initial_count - len(self.events)
        if cleared_count > 0:
            logger.info(f"Cleared {cleared_count} old safety events")
        
        return cleared_count
    
    def start_monitoring(self) -> None:
        """Start safety monitoring."""
        self.monitoring_active = True
        logger.info("Safety monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop safety monitoring."""
        self.monitoring_active = False
        logger.info("Safety monitoring stopped")
    
    def export_events(self, filename: str, format: str = 'csv') -> None:
        """Export safety events to file.
        
        Args:
            filename: Output filename
            format: Export format ('csv' or 'json')
        """
        import json
        import csv
        from datetime import datetime
        
        if format.lower() == 'json':
            events_data = []
            for event in self.events:
                events_data.append({
                    'timestamp': datetime.fromtimestamp(event.timestamp).isoformat(),
                    'level': event.level.value,
                    'device': event.device,
                    'parameter': event.parameter,
                    'value': event.value,
                    'limit_name': event.limit.name,
                    'message': event.message,
                    'acknowledged': event.acknowledged
                })
            
            with open(filename, 'w') as f:
                json.dump(events_data, f, indent=2)
        
        elif format.lower() == 'csv':
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Timestamp', 'Level', 'Device', 'Parameter', 
                    'Value', 'Limit', 'Message', 'Acknowledged'
                ])
                
                for event in self.events:
                    writer.writerow([
                        datetime.fromtimestamp(event.timestamp).isoformat(),
                        event.level.value,
                        event.device,
                        event.parameter,
                        event.value,
                        event.limit.name,
                        event.message,
                        event.acknowledged
                    ])
        
        logger.info(f"Exported {len(self.events)} safety events to {filename}")


def create_safety_monitor_from_config(config: Dict[str, Any]) -> SafetyMonitor:
    """Create safety monitor from configuration.
    
    Args:
        config: Application configuration
        
    Returns:
        Configured SafetyMonitor instance
    """
    return SafetyMonitor(config)