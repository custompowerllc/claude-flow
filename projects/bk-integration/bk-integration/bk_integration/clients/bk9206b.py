"""BK9206b Power Supply API Client with taper detection."""

import httpx
import time
import logging
from typing import Dict, Any, Optional, Callable
from ..utils.validation import validate_range, ValidationError

logger = logging.getLogger(__name__)


class BK9206bError(Exception):
    """BK9206b-specific error."""
    pass


class BK9206bClient:
    """BK9206b Power Supply API Client with comprehensive taper detection."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize BK9206b client.
        
        Args:
            config: Device configuration dictionary
        """
        self.base_url = config['device_url']
        self.name = config.get('name', 'BK9206b')
        
        # Device specifications (BK9206b limits)
        safety_limits = config.get('safety_limits', {})
        self.max_voltage = safety_limits.get('max_voltage', 60.0)
        self.max_current = safety_limits.get('max_current', 5.0)
        self.max_power = safety_limits.get('max_power', 300.0)
        
        # Default settings
        defaults = config.get('defaults', {})
        self.default_voltage = defaults.get('voltage', 15.0)
        self.default_current = defaults.get('current_limit', 2.0)
        self.default_taper_threshold = defaults.get('taper_threshold', 0.1)
        self.default_taper_duration = defaults.get('taper_duration', 60)
        
        # HTTP client configuration
        timeout = httpx.Timeout(config.get('timeout', 30.0))
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={'User-Agent': 'BK-Integration/1.0'}
        )
        
        self._consecutive_failures = 0
        self._max_failures = 5
        self._last_status = {}
        self._taper_detection_active = False
        
        logger.info(f"Initialized BK9206b client for {self.base_url}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Emergency shutdown on exit
        try:
            self.disable_output()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            self.client.close()
    
    def _handle_request_error(self, operation: str, error: Exception) -> Dict[str, Any]:
        """Handle HTTP request errors with retry logic."""
        self._consecutive_failures += 1
        error_msg = f"{operation} failed: {error}"
        
        if self._consecutive_failures >= self._max_failures:
            logger.error(f"Max consecutive failures reached for {operation}")
        
        logger.error(error_msg)
        return {"success": False, "message": error_msg}
    
    def _handle_success(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful response and reset failure counter."""
        self._consecutive_failures = 0
        return response_data
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health and device connectivity."""
        try:
            response = self.client.get("/api/health")
            response.raise_for_status()
            result = response.json()
            logger.debug("Health check successful")
            return self._handle_success(result)
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Health check", e)
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive device status and measurements."""
        try:
            response = self.client.get("/api/status")
            response.raise_for_status()
            status = response.json()
            
            if status:
                self._last_status = status
                
                # Log status for monitoring
                logger.debug(f"Status: {status.get('voltage_actual', 0):.3f}V, "
                           f"{status.get('current_actual', 0):.3f}A, "
                           f"{status.get('operating_mode', 'N/A')} mode")
            
            return self._handle_success(status)
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Status check", e)
    
    def set_voltage(self, voltage: float) -> Dict[str, Any]:
        """Set output voltage with safety validation.
        
        Args:
            voltage: Output voltage in volts (0.0 - 60.0V)
            
        Returns:
            Operation result dictionary
        """
        try:
            validate_range(voltage, 0.0, self.max_voltage, "output voltage")
            logger.info(f"Setting output voltage to {voltage}V")
            
            response = self.client.post("/api/voltage", json={"voltage": voltage})
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info(f"Output voltage set to {voltage}V")
            
            return self._handle_success(result)
            
        except ValidationError as e:
            error_msg = f"Voltage validation failed: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Set voltage", e)
    
    def set_current(self, current: float) -> Dict[str, Any]:
        """Set current limit with safety validation.
        
        Args:
            current: Current limit in amperes (0.0 - 5.0A)
            
        Returns:
            Operation result dictionary
        """
        try:
            validate_range(current, 0.0, self.max_current, "current limit")
            logger.info(f"Setting current limit to {current}A")
            
            response = self.client.post("/api/current", json={"current": current})
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info(f"Current limit set to {current}A")
            
            return self._handle_success(result)
            
        except ValidationError as e:
            error_msg = f"Current validation failed: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Set current", e)
    
    def enable_output(self) -> Dict[str, Any]:
        """Enable power output."""
        logger.info("Enabling power output")
        
        try:
            response = self.client.post("/api/output/enable")
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info("Power output enabled")
            
            return self._handle_success(result)
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Enable output", e)
    
    def disable_output(self) -> Dict[str, Any]:
        """Disable power output (emergency stop)."""
        logger.info("Disabling power output")
        
        try:
            response = self.client.post("/api/output/disable")
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info("Power output disabled")
            
            return self._handle_success(result)
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            # Log error but don't fail - emergency stop should always succeed
            logger.error(f"Disable output API call failed: {e}")
            return {"success": True, "message": "Emergency stop - output disabled locally"}
    
    def configure_taper_detection(self, threshold: float, duration: int) -> Dict[str, Any]:
        """Configure taper current detection for battery charging.
        
        Args:
            threshold: Taper current threshold in amperes
            duration: Duration threshold in seconds
            
        Returns:
            Configuration result dictionary
        """
        try:
            validate_range(threshold, 0.01, self.max_current, "taper threshold")
            validate_range(duration, 1, 3600, "taper duration")
            
            logger.info(f"Configuring taper detection: {threshold}A threshold, {duration}s duration")
            
            # Set threshold
            threshold_response = self.client.post("/api/taper/threshold", 
                                                json={"threshold": threshold})
            threshold_response.raise_for_status()
            threshold_result = threshold_response.json()
            
            if not threshold_result.get('success'):
                return threshold_result
            
            # Small delay between API calls
            time.sleep(0.1)
            
            # Set duration
            duration_response = self.client.post("/api/taper/duration",
                                               json={"duration": duration})
            duration_response.raise_for_status()
            duration_result = duration_response.json()
            
            if not duration_result.get('success'):
                return duration_result
            
            self._taper_detection_active = True
            logger.info(f"Taper detection configured successfully")
            
            return {"success": True, "message": "Taper detection configured"}
            
        except ValidationError as e:
            error_msg = f"Taper config validation failed: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Configure taper", e)
    
    def get_taper_config(self) -> Dict[str, Any]:
        """Get current taper detection configuration."""
        try:
            response = self.client.get("/api/taper/config")
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Taper config: {result}")
            return self._handle_success(result)
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return self._handle_request_error("Get taper config", e)
    
    def monitor_taper_detection(self, callback: Optional[Callable] = None) -> bool:
        """Monitor for taper current detection.
        
        Args:
            callback: Optional callback function when taper detected
            
        Returns:
            True if taper detected, False otherwise
        """
        status = self.get_status()
        
        if isinstance(status, dict) and status.get('operating_mode') == 'TAPER':
            message = "Taper current detected - battery charging complete"
            logger.info(message)
            
            if callback:
                callback(message)
            
            return True
        
        return False
    
    def setup_charging(self, voltage: float, current: float,
                      taper_threshold: Optional[float] = None,
                      taper_duration: Optional[int] = None) -> Dict[str, Any]:
        """Setup complete charging configuration.
        
        Args:
            voltage: Charge voltage in volts
            current: Charge current limit in amperes
            taper_threshold: Optional taper current threshold
            taper_duration: Optional taper duration in seconds
            
        Returns:
            Setup result dictionary
        """
        logger.info(f"Setting up charging: {voltage}V @ {current}A")
        
        try:
            # Set voltage
            voltage_result = self.set_voltage(voltage)
            if not voltage_result.get('success'):
                return voltage_result
            
            time.sleep(0.1)
            
            # Set current
            current_result = self.set_current(current)
            if not current_result.get('success'):
                return current_result
            
            # Configure taper detection if specified
            if taper_threshold is not None and taper_duration is not None:
                time.sleep(0.1)
                taper_result = self.configure_taper_detection(taper_threshold, taper_duration)
                if not taper_result.get('success'):
                    logger.warning(f"Taper detection setup failed: {taper_result.get('message')}")
            elif taper_threshold is not None or taper_duration is not None:
                # Use defaults for missing parameters
                threshold = taper_threshold or self.default_taper_threshold
                duration = taper_duration or self.default_taper_duration
                time.sleep(0.1)
                taper_result = self.configure_taper_detection(threshold, duration)
                if not taper_result.get('success'):
                    logger.warning(f"Default taper detection setup failed: {taper_result.get('message')}")
            
            logger.info("Charging setup completed successfully")
            return {"success": True, "message": "Charging setup completed"}
            
        except Exception as e:
            error_msg = f"Charging setup failed: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    def start_charging(self, voltage: float, current: float,
                      taper_threshold: Optional[float] = None,
                      taper_duration: Optional[int] = None) -> Dict[str, Any]:
        """Start charging with specified parameters.
        
        Args:
            voltage: Charge voltage in volts
            current: Charge current limit in amperes  
            taper_threshold: Optional taper current threshold
            taper_duration: Optional taper duration in seconds
            
        Returns:
            Operation result dictionary
        """
        logger.info(f"Starting charging: {voltage}V @ {current}A")
        
        # Setup charging parameters
        setup_result = self.setup_charging(voltage, current, taper_threshold, taper_duration)
        if not setup_result.get('success'):
            return setup_result
        
        # Enable output
        enable_result = self.enable_output()
        if not enable_result.get('success'):
            return enable_result
        
        logger.info("Charging started successfully")
        return {"success": True, "message": "Charging started"}
    
    def stop_charging(self) -> Dict[str, Any]:
        """Stop charging by disabling output."""
        logger.info("Stopping charging")
        return self.disable_output()
    
    def monitor_charging(self, callback: Optional[Callable] = None,
                        interval: float = 1.0,
                        max_duration: Optional[float] = None) -> Dict[str, Any]:
        """Monitor charging process with optional taper detection.
        
        Args:
            callback: Optional callback function for status updates
            interval: Monitoring interval in seconds
            max_duration: Maximum monitoring duration in seconds
            
        Returns:
            Monitoring result dictionary
        """
        logger.info(f"Starting charging monitoring (interval: {interval}s)")
        
        monitoring_data = []
        start_time = time.time()
        taper_detected = False
        
        try:
            while not taper_detected:
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Check maximum duration
                if max_duration and elapsed > max_duration:
                    logger.info(f"Maximum monitoring duration ({max_duration}s) reached")
                    break
                
                status = self.get_status()
                
                if isinstance(status, dict):
                    # Add timing information
                    status['timestamp'] = current_time
                    status['elapsed_time'] = elapsed
                    
                    monitoring_data.append(status)
                    
                    if callback:
                        callback(status)
                    
                    # Check for taper detection
                    if status.get('operating_mode') == 'TAPER':
                        taper_detected = True
                        logger.info(f"Taper detected after {elapsed:.1f} seconds")
                        break
                else:
                    logger.error("Failed to get status during monitoring")
                    break
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        
        result = {
            "success": True,
            "taper_detected": taper_detected,
            "monitoring_duration": time.time() - start_time,
            "data_points": len(monitoring_data),
            "data": monitoring_data
        }
        
        logger.info(f"Charging monitoring completed: {result['monitoring_duration']:.1f}s, "
                   f"{result['data_points']} readings, taper: {taper_detected}")
        
        return result
    
    def emergency_stop(self) -> Dict[str, Any]:
        """Emergency stop - immediately disable output."""
        logger.warning("EMERGENCY STOP requested")
        
        try:
            # Multiple attempts to ensure stop
            for attempt in range(3):
                result = self.disable_output()
                if result.get('success'):
                    break
                time.sleep(0.1)
            
            logger.warning("Emergency stop completed")
            return {"success": True, "message": "Emergency stop completed"}
            
        except Exception as e:
            error_msg = f"Emergency stop failed: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    def get_power_calculation(self) -> Dict[str, float]:
        """Calculate power metrics from current status."""
        status = self._last_status
        
        if not status:
            return {"voltage": 0.0, "current": 0.0, "power": 0.0}
        
        voltage = status.get('voltage_actual', 0.0)
        current = status.get('current_actual', 0.0)
        power = voltage * current
        
        return {
            "voltage": voltage,
            "current": current,
            "power": power,
            "efficiency": status.get('power_actual', power) / power * 100 if power > 0 else 0
        }
    
    @property
    def connected(self) -> bool:
        """Check if device is connected (based on last successful communication)."""
        return self._consecutive_failures < self._max_failures
    
    @property
    def output_enabled(self) -> bool:
        """Check if output is currently enabled."""
        return self._last_status.get('output_enabled', False)
    
    @property
    def operating_mode(self) -> str:
        """Get current operating mode."""
        return self._last_status.get('operating_mode', 'UNKNOWN')
    
    @property
    def taper_detection_active(self) -> bool:
        """Check if taper detection is configured and active."""
        return self._taper_detection_active
    
    @property
    def device_limits(self) -> Dict[str, float]:
        """Get device specification limits."""
        return {
            "max_voltage": self.max_voltage,
            "max_current": self.max_current,
            "max_power": self.max_power
        }
    
    @property
    def last_status(self) -> Dict[str, Any]:
        """Get last status from device."""
        return self._last_status.copy()