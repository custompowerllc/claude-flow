"""BK8520 Electronic Load API Client with safety validation."""

import httpx
import time
import logging
from typing import Dict, Any, Optional, Callable
from ..utils.validation import validate_range, ValidationError

logger = logging.getLogger(__name__)


class BK8520Error(Exception):
    """BK8520-specific error."""
    pass


class BK8520Client:
    """BK8520 Electronic Load API Client with comprehensive safety validation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize BK8520 client.
        
        Args:
            config: Device configuration dictionary
        """
        self.base_url = config['device_url']
        self.serial_port = config.get('serial_port', '/dev/ttyUSB0')
        self.name = config.get('name', 'BK8520')
        
        # Device specifications
        defaults = config.get('defaults', {})
        self.max_current = defaults.get('max_current', 60.0)
        self.max_voltage = defaults.get('max_voltage', 120.0)
        self.max_power = defaults.get('max_power', 999.0)
        
        # Safety limits
        safety = config.get('safety_limits', {})
        self.max_temperature = safety.get('max_temperature', 85.0)
        self.max_current_spike = safety.get('max_current_spike', 65.0)
        self.comm_timeout = safety.get('communication_timeout', 5.0)
        
        # HTTP client configuration
        timeout = httpx.Timeout(config.get('timeout', 30.0))
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={'User-Agent': 'BK-Integration/1.0'}
        )
        
        self._connected = False
        self._last_readings = {}
        self._consecutive_failures = 0
        self._max_failures = 5
        
        logger.info(f"Initialized BK8520 client for {self.base_url}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connected:
            self.disconnect()
        self.client.close()
    
    def _handle_request_error(self, operation: str, error: Exception) -> Dict[str, Any]:
        """Handle HTTP request errors with retry logic."""
        self._consecutive_failures += 1
        error_msg = f"{operation} failed: {error}"
        
        if self._consecutive_failures >= self._max_failures:
            logger.error(f"Max consecutive failures reached for {operation}")
            self._connected = False
        
        logger.error(error_msg)
        return {"success": False, "message": error_msg}
    
    def _handle_success(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful response and reset failure counter."""
        self._consecutive_failures = 0
        return response_data
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health and connectivity."""
        try:
            response = self.client.get("/api/health")
            response.raise_for_status()
            result = response.json()
            logger.debug("Health check successful")
            return self._handle_success(result)
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Health check", e)
    
    def connect(self, port: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Connect to BK8520 device with safety protocols.
        
        Args:
            port: Serial port path (optional)
            **kwargs: Additional connection parameters
            
        Returns:
            Connection result dictionary
        """
        connect_data = {
            "port": port or self.serial_port,
            "baudrate": kwargs.get('baudrate', 9600),
            "timeout": kwargs.get('timeout', 3.0),
            "reset_input_on_connect": kwargs.get('reset_input_on_connect', True)
        }
        
        logger.info(f"Connecting to {self.name} on {connect_data['port']}")
        
        try:
            response = self.client.post("/api/device/connect", json=connect_data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                self._connected = True
                logger.info(f"Successfully connected to {self.name}")
                
                # Verify connection with device info
                info_result = self.get_device_info()
                if info_result.get('success'):
                    logger.info(f"Device info: {info_result.get('data', {})}")
            else:
                logger.error(f"Connection failed: {result.get('message')}")
            
            return self._handle_success(result)
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Connection", e)
    
    def disconnect(self) -> Dict[str, Any]:
        """Safely disconnect from device with emergency stop."""
        logger.info(f"Disconnecting from {self.name}")
        
        try:
            # Emergency stop before disconnect
            self.disable_input()
            
            response = self.client.post("/api/device/disconnect")
            response.raise_for_status()
            result = response.json()
            
            self._connected = False
            logger.info(f"Disconnected from {self.name}")
            return self._handle_success(result)
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            # Force disconnection even if API call fails
            self._connected = False
            return self._handle_request_error("Disconnection", e)
    
    def get_status(self) -> Dict[str, Any]:
        """Get device connection and operational status."""
        try:
            response = self.client.get("/api/device/status")
            response.raise_for_status()
            result = response.json()
            
            # Update internal connection state
            if result.get('success') and result.get('data'):
                self._connected = result['data'].get('connected', False)
            
            return self._handle_success(result)
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Status check", e)
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get detailed device information."""
        try:
            response = self.client.get("/api/device/info")
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Device info retrieved: {result.get('data', {})}")
            return self._handle_success(result)
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Device info", e)
    
    def get_readings(self) -> Dict[str, Any]:
        """Get real-time voltage, current, and power measurements."""
        try:
            response = self.client.get("/api/device/readings")
            response.raise_for_status()
            result = response.json()
            
            if result.get('success') and result.get('data'):
                readings = result['data']
                self._last_readings = readings
                
                # Basic safety check on readings
                if self._check_reading_safety(readings):
                    logger.debug(f"Readings: V={readings.get('voltage', 0):.3f}V, "
                               f"I={readings.get('current', 0):.3f}A, "
                               f"P={readings.get('power', 0):.3f}W")
                    return readings
                else:
                    logger.warning("Safety limits exceeded in readings")
                    return {"voltage": 0, "current": 0, "power": 0, 
                           "error": "Safety limits exceeded"}
            
            return result.get('data', {})
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            error_msg = f"Readings failed: {e}"
            logger.error(error_msg)
            return {"voltage": 0, "current": 0, "power": 0, "error": error_msg}
    
    def _check_reading_safety(self, readings: Dict[str, Any]) -> bool:
        """Check if readings are within safety limits."""
        voltage = readings.get('voltage', 0)
        current = readings.get('current', 0)
        power = readings.get('power', 0)
        
        if voltage > self.max_voltage * 1.1:  # 10% tolerance
            logger.warning(f"Voltage {voltage}V exceeds safety limit {self.max_voltage}V")
            return False
        
        if current > self.max_current_spike:
            logger.warning(f"Current {current}A exceeds spike limit {self.max_current_spike}A")
            return False
        
        if power > self.max_power * 1.1:  # 10% tolerance
            logger.warning(f"Power {power}W exceeds safety limit {self.max_power}W")
            return False
        
        return True
    
    def set_current(self, current: float) -> Dict[str, Any]:
        """Set discharge current with safety validation.
        
        Args:
            current: Discharge current in amperes
            
        Returns:
            Operation result dictionary
        """
        try:
            validate_range(current, 0.0, self.max_current, "discharge current")
            logger.info(f"Setting discharge current to {current}A")
            
            response = self.client.post("/api/device/current", json={"current": current})
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info(f"Discharge current set to {current}A")
            
            return self._handle_success(result)
            
        except ValidationError as e:
            error_msg = f"Current validation failed: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Set current", e)
    
    def set_voltage(self, voltage: float) -> Dict[str, Any]:
        """Set cutoff voltage with safety validation.
        
        Args:
            voltage: Cutoff voltage in volts
            
        Returns:
            Operation result dictionary
        """
        try:
            validate_range(voltage, 0.0, self.max_voltage, "cutoff voltage")
            logger.info(f"Setting cutoff voltage to {voltage}V")
            
            response = self.client.post("/api/device/voltage", json={"voltage": voltage})
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info(f"Cutoff voltage set to {voltage}V")
            
            return self._handle_success(result)
            
        except ValidationError as e:
            error_msg = f"Voltage validation failed: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Set voltage", e)
    
    def set_mode(self, mode: str) -> Dict[str, Any]:
        """Set operation mode.
        
        Args:
            mode: Operation mode ('CC', 'CV', 'CW', 'CR')
            
        Returns:
            Operation result dictionary
        """
        mode_map = {"CC": 0, "CV": 1, "CW": 2, "CR": 3}
        
        if mode not in mode_map:
            available = list(mode_map.keys())
            error_msg = f"Invalid mode '{mode}'. Available: {available}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
        
        logger.info(f"Setting operation mode to {mode}")
        
        try:
            response = self.client.post("/api/device/mode", json={"mode": mode_map[mode]})
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info(f"Operation mode set to {mode}")
            
            return self._handle_success(result)
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Set mode", e)
    
    def enable_input(self) -> Dict[str, Any]:
        """Enable input with safety checks."""
        if not self._connected:
            error_msg = "Device not connected"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
        
        logger.info("Enabling load input")
        
        try:
            response = self.client.post("/api/device/input", json={"enabled": True})
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info("Load input enabled")
            
            return self._handle_success(result)
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Enable input", e)
    
    def disable_input(self) -> Dict[str, Any]:
        """Disable input (emergency stop capability)."""
        logger.info("Disabling load input")
        
        try:
            response = self.client.post("/api/device/input", json={"enabled": False})
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info("Load input disabled")
            
            return self._handle_success(result)
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            # Log error but don't fail - emergency stop should always succeed
            logger.error(f"Disable input API call failed: {e}")
            return {"success": True, "message": "Emergency stop - input disabled locally"}
    
    def setup_discharge(self, current: float, cutoff_voltage: float, 
                       mode: str = "CC") -> Dict[str, Any]:
        """Configure complete discharge setup with validation.
        
        Args:
            current: Discharge current in amperes
            cutoff_voltage: Cutoff voltage in volts
            mode: Operation mode (default: "CC")
            
        Returns:
            Setup result dictionary
        """
        logger.info(f"Setting up discharge: {current}A, {cutoff_voltage}V cutoff, {mode} mode")
        
        try:
            validate_range(current, 0.0, self.max_current, "discharge current")
            validate_range(cutoff_voltage, 0.0, self.max_voltage, "cutoff voltage")
            
            # Configure discharge parameters step by step
            mode_result = self.set_mode(mode)
            if not mode_result.get('success'):
                return mode_result
            
            # Small delay between commands for device stability
            time.sleep(0.1)
            
            current_result = self.set_current(current)
            if not current_result.get('success'):
                return current_result
            
            time.sleep(0.1)
            
            voltage_result = self.set_voltage(cutoff_voltage)
            if not voltage_result.get('success'):
                return voltage_result
            
            logger.info("Discharge setup completed successfully")
            return {"success": True, "message": "Discharge setup completed"}
            
        except ValidationError as e:
            error_msg = f"Setup validation failed: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    def start_battery_test(self, discharge_current: float, cutoff_voltage: float,
                          max_time_hours: float = 24.0) -> Dict[str, Any]:
        """Start automated battery capacity test.
        
        Args:
            discharge_current: Discharge current in amperes
            cutoff_voltage: Minimum voltage to stop test
            max_time_hours: Maximum test duration in hours
            
        Returns:
            Test start result dictionary
        """
        logger.info(f"Starting battery test: {discharge_current}A discharge, "
                   f"{cutoff_voltage}V cutoff, {max_time_hours}h max")
        
        test_data = {
            "discharge_current": discharge_current,
            "cutoff_voltage": cutoff_voltage,
            "max_time_hours": max_time_hours
        }
        
        try:
            response = self.client.post("/api/battery-test/start", json=test_data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info("Battery test started")
            
            return self._handle_success(result)
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Start battery test", e)
    
    def stop_battery_test(self) -> Dict[str, Any]:
        """Stop currently running battery test."""
        logger.info("Stopping battery test")
        
        try:
            response = self.client.post("/api/battery-test/stop")
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info("Battery test stopped")
            
            return self._handle_success(result)
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Stop battery test", e)
    
    def get_battery_test_status(self) -> Dict[str, Any]:
        """Get current battery test status."""
        try:
            response = self.client.get("/api/battery-test/status")
            response.raise_for_status()
            result = response.json()
            
            return self._handle_success(result)
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Get test status", e)
    
    def get_battery_test_results(self) -> Dict[str, Any]:
        """Get complete battery test results."""
        try:
            response = self.client.get("/api/battery-test/results")
            response.raise_for_status()
            result = response.json()
            
            return self._handle_success(result)
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Get test results", e)
    
    def monitor_discharge(self, callback: Optional[Callable] = None,
                         interval: float = 1.0) -> Dict[str, Any]:
        """Monitor discharge process with optional callback.
        
        Args:
            callback: Optional callback function for readings
            interval: Monitoring interval in seconds
            
        Returns:
            Monitoring result dictionary
        """
        logger.info(f"Starting discharge monitoring (interval: {interval}s)")
        
        monitoring_data = []
        start_time = time.time()
        
        try:
            while True:
                readings = self.get_readings()
                
                if 'error' in readings:
                    logger.error(f"Monitoring error: {readings['error']}")
                    break
                
                # Add timestamp to readings
                readings['timestamp'] = time.time()
                readings['elapsed_time'] = readings['timestamp'] - start_time
                
                monitoring_data.append(readings)
                
                if callback:
                    callback(readings)
                
                # Check if discharge stopped (very low current)
                if readings.get('current', 0) < 0.001:
                    logger.info("Discharge appears to have stopped")
                    break
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        
        return {
            "success": True,
            "message": f"Monitoring completed, {len(monitoring_data)} readings collected",
            "data": monitoring_data
        }
    
    @property
    def connected(self) -> bool:
        """Check if device is connected."""
        return self._connected
    
    @property
    def last_readings(self) -> Dict[str, Any]:
        """Get last readings from device."""
        return self._last_readings.copy()
    
    @property
    def device_limits(self) -> Dict[str, float]:
        """Get device specification limits."""
        return {
            "max_voltage": self.max_voltage,
            "max_current": self.max_current,
            "max_power": self.max_power
        }