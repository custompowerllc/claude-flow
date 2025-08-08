"""Battery test orchestration workflows with multi-device coordination."""

import time
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional
from enum import Enum
from dataclasses import dataclass, field
import csv
import json

logger = logging.getLogger(__name__)


class TestPhase(Enum):
    """Battery test phases with state management."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    CHARGING = "charging"
    REST_AFTER_CHARGE = "rest_after_charge"
    DISCHARGING = "discharging"
    REST_AFTER_DISCHARGE = "rest_after_discharge"
    RECHARGING = "recharging"
    COMPLETE = "complete"
    ERROR = "error"
    STOPPED = "stopped"
    EMERGENCY_STOPPED = "emergency_stopped"


@dataclass
class TestResults:
    """Battery test results container with comprehensive metrics."""
    test_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    profile: Dict[str, Any] = field(default_factory=dict)
    cycles_completed: int = 0
    total_cycles: int = 1
    
    # Performance metrics
    capacity_ah: float = 0.0
    energy_wh: float = 0.0
    efficiency_percent: float = 0.0
    
    # Data collections
    charge_data: List[Dict] = field(default_factory=list)
    discharge_data: List[Dict] = field(default_factory=list)
    recharge_data: List[Dict] = field(default_factory=list)
    
    # Test state
    status: TestPhase = TestPhase.IDLE
    error_message: Optional[str] = None
    
    # Additional metrics
    peak_charge_current: float = 0.0
    peak_discharge_current: float = 0.0
    charge_time_seconds: float = 0.0
    discharge_time_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary for serialization."""
        return {
            'test_id': self.test_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'profile': self.profile,
            'cycles_completed': self.cycles_completed,
            'total_cycles': self.total_cycles,
            'capacity_ah': self.capacity_ah,
            'energy_wh': self.energy_wh,
            'efficiency_percent': self.efficiency_percent,
            'status': self.status.value,
            'error_message': self.error_message,
            'peak_charge_current': self.peak_charge_current,
            'peak_discharge_current': self.peak_discharge_current,
            'charge_time_seconds': self.charge_time_seconds,
            'discharge_time_seconds': self.discharge_time_seconds,
            'data_points': {
                'charge': len(self.charge_data),
                'discharge': len(self.discharge_data),
                'recharge': len(self.recharge_data)
            }
        }


class BatteryTestOrchestrator:
    """Orchestrates comprehensive battery testing workflows with safety monitoring."""
    
    def __init__(self, power_client, load_client, safety_monitor, console=None):
        """Initialize battery test orchestrator.
        
        Args:
            power_client: BK9206b power supply client
            load_client: BK8520 load tester client
            safety_monitor: Safety monitoring system
            console: Rich console for output (optional)
        """
        self.power_client = power_client
        self.load_client = load_client
        self.safety_monitor = safety_monitor
        self.console = console
        
        # Test state
        self.current_phase = TestPhase.IDLE
        self.test_active = False
        self.emergency_stop_requested = False
        self.current_results: Optional[TestResults] = None
        
        # Monitoring
        self.phase_start_time = 0.0
        self.data_collection_interval = 1.0  # seconds
        
        logger.info("Battery test orchestrator initialized")
    
    def run_battery_test(self, test_profile: Dict[str, Any], cycles: int = 1) -> TestResults:
        """Run complete battery test with specified profile and cycles.
        
        Args:
            test_profile: Test configuration parameters
            cycles: Number of charge/discharge cycles
            
        Returns:
            TestResults object with comprehensive test data
            
        Raises:
            Exception: If test fails or is aborted
        """
        # Initialize test results
        test_id = f"test_{int(time.time())}"
        self.current_results = TestResults(
            test_id=test_id,
            start_time=datetime.now(),
            profile=test_profile.copy(),
            total_cycles=cycles,
            status=TestPhase.INITIALIZING
        )
        
        try:
            self.test_active = True
            self.emergency_stop_requested = False
            
            self._log_test_start(test_profile, cycles)
            
            # Pre-test device verification
            if not self._verify_devices():
                raise Exception("Device verification failed")
            
            self.current_results.status = TestPhase.CHARGING
            
            # Execute test cycles
            for cycle in range(1, cycles + 1):
                if self.emergency_stop_requested:
                    self.current_results.status = TestPhase.EMERGENCY_STOPPED
                    break
                
                self._log_cycle_start(cycle, cycles)
                
                # Phase 1: Charging
                charge_data = self._execute_charge_phase(test_profile, f"Cycle {cycle} - Initial Charge")
                self.current_results.charge_data.extend(charge_data)
                
                if self.emergency_stop_requested:
                    break
                
                # Phase 2: Rest after charge
                self._execute_rest_phase(
                    test_profile['rest_time'], 
                    f"Cycle {cycle} - Post-Charge Rest"
                )
                
                if self.emergency_stop_requested:
                    break
                
                # Phase 3: Discharge capacity test
                discharge_data = self._execute_discharge_phase(test_profile, f"Cycle {cycle} - Capacity Test")
                self.current_results.discharge_data.extend(discharge_data)
                
                if self.emergency_stop_requested:
                    break
                
                # Phase 4: Rest after discharge
                self._execute_rest_phase(
                    test_profile['rest_time'],
                    f"Cycle {cycle} - Post-Discharge Rest"
                )
                
                if self.emergency_stop_requested:
                    break
                
                # Phase 5: Recharge (except last cycle)
                if cycle < cycles:
                    recharge_data = self._execute_charge_phase(
                        test_profile, 
                        f"Cycle {cycle} - Recharge",
                        is_recharge=True
                    )
                    self.current_results.recharge_data.extend(recharge_data)
                
                # Calculate cycle results
                self._calculate_cycle_metrics(discharge_data, charge_data)
                self.current_results.cycles_completed = cycle
                
                self._log_cycle_complete(cycle, discharge_data, charge_data)
            
            # Calculate final results
            self._calculate_final_metrics()
            
            self.current_results.end_time = datetime.now()
            
            if self.emergency_stop_requested:
                self.current_results.status = TestPhase.EMERGENCY_STOPPED
            else:
                self.current_results.status = TestPhase.COMPLETE
            
            self._log_test_complete()
            
            return self.current_results
            
        except Exception as e:
            self.current_results.status = TestPhase.ERROR
            self.current_results.error_message = str(e)
            logger.error(f"Battery test failed: {e}")
            raise
        finally:
            self.test_active = False
            self.emergency_stop()  # Ensure all outputs are disabled
    
    def _verify_devices(self) -> bool:
        """Verify both devices are connected and ready."""
        self._log_status("Verifying device connections...")
        
        # Check BK8520 connection
        load_status = self.load_client.get_status()
        if not load_status.get('success') or not load_status.get('data', {}).get('connected'):
            self._log_error("BK8520 Load Tester not connected")
            return False
        
        # Check BK9206b connection
        power_health = self.power_client.health_check()
        if not power_health.get('success') and power_health.get('server_status') != 'healthy':
            self._log_error("BK9206b Power Supply not connected")
            return False
        
        self._log_success("Device verification completed")
        return True
    
    def _execute_charge_phase(self, profile: Dict[str, Any], phase_name: str,
                            is_recharge: bool = False) -> List[Dict]:
        """Execute charging phase with comprehensive monitoring.
        
        Args:
            profile: Test profile parameters
            phase_name: Human-readable phase name
            is_recharge: Whether this is a recharge phase
            
        Returns:
            List of charge data points
        """
        self.current_phase = TestPhase.CHARGING
        self.phase_start_time = time.time()
        
        self._log_phase_start(phase_name)
        
        # Configure power supply
        setup_result = self.power_client.setup_charging(
            voltage=profile['charge_voltage'],
            current=profile['charge_current'],
            taper_threshold=profile.get('taper_threshold', 0.1),
            taper_duration=profile.get('taper_duration', 60)
        )
        
        if not setup_result.get('success'):
            raise Exception(f"Failed to setup charging: {setup_result.get('message')}")
        
        # Start charging
        enable_result = self.power_client.enable_output()
        if not enable_result.get('success'):
            raise Exception(f"Failed to enable power output: {enable_result.get('message')}")
        
        # Monitor charging with data collection
        charge_data = []
        start_time = time.time()
        taper_detected = False
        max_charge_time = profile.get('max_charge_time_hours', 12) * 3600
        
        self._update_status_display(f"{phase_name} in progress...")
        
        while not taper_detected and not self.emergency_stop_requested:
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Timeout check
            if elapsed > max_charge_time:
                self._log_warning(f"Maximum charge time ({max_charge_time/3600:.1f}h) reached")
                break
            
            # Get power supply status
            try:
                power_status = self.power_client.get_status()
                if not isinstance(power_status, dict):
                    self._log_error("Failed to get power supply status")
                    break
            except Exception as e:
                self._log_error(f"Power supply communication error: {e}")
                break
            
            # Create data point
            data_point = {
                'timestamp': current_time,
                'elapsed_time': elapsed,
                'phase': phase_name,
                'voltage_set': power_status.get('voltage_set', 0),
                'voltage_actual': power_status.get('voltage_actual', 0),
                'current_set': power_status.get('current_set', 0),
                'current_actual': power_status.get('current_actual', 0),
                'power_actual': power_status.get('power_actual', 0),
                'operating_mode': power_status.get('operating_mode', 'N/A')
            }
            
            charge_data.append(data_point)
            
            # Update peak current tracking
            current_actual = data_point['current_actual']
            if current_actual > self.current_results.peak_charge_current:
                self.current_results.peak_charge_current = current_actual
            
            # Update status display
            self._update_phase_status(phase_name, elapsed, data_point)
            
            # Safety monitoring
            if not self.safety_monitor.check_charging_safety(data_point):
                self._log_error("Safety limits exceeded during charging")
                break
            
            # Check for taper detection
            if power_status.get('operating_mode') == 'TAPER':
                taper_detected = True
                self._log_success(f"Taper current detected after {elapsed/60:.1f} minutes")
            
            time.sleep(self.data_collection_interval)
        
        # Stop charging
        self.power_client.disable_output()
        
        # Update timing metrics
        charge_time = time.time() - start_time
        self.current_results.charge_time_seconds += charge_time
        
        self._log_phase_complete(phase_name, len(charge_data), charge_time)
        
        return charge_data
    
    def _execute_discharge_phase(self, profile: Dict[str, Any], phase_name: str) -> List[Dict]:
        """Execute discharge phase with capacity measurement.
        
        Args:
            profile: Test profile parameters
            phase_name: Human-readable phase name
            
        Returns:
            List of discharge data points
        """
        self.current_phase = TestPhase.DISCHARGING
        self.phase_start_time = time.time()
        
        self._log_phase_start(phase_name)
        
        # Configure load tester
        setup_result = self.load_client.setup_discharge(
            current=profile['discharge_current'],
            cutoff_voltage=profile['cutoff_voltage'],
            mode="CC"
        )
        
        if not setup_result.get('success'):
            raise Exception(f"Failed to setup discharge: {setup_result.get('message')}")
        
        # Start discharge
        enable_result = self.load_client.enable_input()
        if not enable_result.get('success'):
            raise Exception(f"Failed to enable load input: {enable_result.get('message')}")
        
        # Monitor discharge with data collection
        discharge_data = []
        start_time = time.time()
        cutoff_reached = False
        max_discharge_time = profile.get('max_discharge_time_hours', 24) * 3600
        
        self._update_status_display(f"{phase_name} in progress...")
        
        while not cutoff_reached and not self.emergency_stop_requested:
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Timeout check
            if elapsed > max_discharge_time:
                self._log_warning(f"Maximum discharge time ({max_discharge_time/3600:.1f}h) reached")
                break
            
            # Get load tester readings
            try:
                readings = self.load_client.get_readings()
                if 'error' in readings:
                    self._log_error(f"Load tester communication error: {readings['error']}")
                    break
            except Exception as e:
                self._log_error(f"Load tester communication error: {e}")
                break
            
            # Create data point
            data_point = {
                'timestamp': current_time,
                'elapsed_time': elapsed,
                'phase': phase_name,
                'voltage': readings.get('voltage', 0),
                'current': readings.get('current', 0),
                'power': readings.get('power', 0)
            }
            
            discharge_data.append(data_point)
            
            # Update peak current tracking
            current_actual = data_point['current']
            if current_actual > self.current_results.peak_discharge_current:
                self.current_results.peak_discharge_current = current_actual
            
            # Update status display
            self._update_phase_status(phase_name, elapsed, data_point)
            
            # Safety monitoring
            if not self.safety_monitor.check_discharge_safety(data_point):
                self._log_error("Safety limits exceeded during discharge")
                break
            
            # Check for cutoff voltage
            if data_point['voltage'] <= profile['cutoff_voltage']:
                cutoff_reached = True
                self._log_success(f"Cutoff voltage reached after {elapsed/60:.1f} minutes")
            
            time.sleep(self.data_collection_interval)
        
        # Stop discharge
        self.load_client.disable_input()
        
        # Update timing metrics
        discharge_time = time.time() - start_time
        self.current_results.discharge_time_seconds += discharge_time
        
        self._log_phase_complete(phase_name, len(discharge_data), discharge_time)
        
        return discharge_data
    
    def _execute_rest_phase(self, rest_time_seconds: int, phase_name: str) -> None:
        """Execute rest phase with countdown display.
        
        Args:
            rest_time_seconds: Duration of rest period
            phase_name: Human-readable phase name
        """
        if rest_time_seconds <= 0:
            return
        
        self.current_phase = TestPhase.REST_AFTER_CHARGE if "Charge" in phase_name else TestPhase.REST_AFTER_DISCHARGE
        
        self._log_phase_start(f"{phase_name} - {rest_time_seconds}s")
        
        self._update_status_display(f"{phase_name} in progress...")
        
        for remaining in range(rest_time_seconds, 0, -1):
            if self.emergency_stop_requested:
                break
            
            # Update countdown display
            self._update_rest_status(phase_name, remaining)
            time.sleep(1)
        
        if not self.emergency_stop_requested:
            self._log_phase_complete(phase_name, 0, rest_time_seconds)
    
    def _calculate_cycle_metrics(self, discharge_data: List[Dict], charge_data: List[Dict]) -> None:
        """Calculate metrics for completed cycle."""
        if discharge_data:
            cycle_capacity = self._calculate_capacity(discharge_data)
            cycle_energy = self._calculate_energy(discharge_data)
            
            # Add to running totals (will be averaged later)
            self.current_results.capacity_ah += cycle_capacity
            self.current_results.energy_wh += cycle_energy
    
    def _calculate_final_metrics(self) -> None:
        """Calculate final test metrics."""
        cycles = max(self.current_results.cycles_completed, 1)
        
        # Average capacity and energy over cycles
        self.current_results.capacity_ah /= cycles
        self.current_results.energy_wh /= cycles
        
        # Calculate efficiency if we have both charge and discharge data
        self.current_results.efficiency_percent = self._calculate_efficiency()
    
    def _calculate_capacity(self, discharge_data: List[Dict]) -> float:
        """Calculate battery capacity in Ah from discharge data."""
        if len(discharge_data) < 2:
            return 0.0
        
        total_ah = 0.0
        for i in range(1, len(discharge_data)):
            dt = discharge_data[i]['elapsed_time'] - discharge_data[i-1]['elapsed_time']
            current = discharge_data[i]['current']
            total_ah += current * (dt / 3600)  # Convert seconds to hours
        
        return total_ah
    
    def _calculate_energy(self, data: List[Dict]) -> float:
        """Calculate energy in Wh from data points."""
        if len(data) < 2:
            return 0.0
        
        total_wh = 0.0
        for i in range(1, len(data)):
            dt = data[i]['elapsed_time'] - data[i-1]['elapsed_time']
            power = data[i].get('power', 0)
            total_wh += power * (dt / 3600)  # Convert seconds to hours
        
        return total_wh
    
    def _calculate_efficiency(self) -> float:
        """Calculate round-trip efficiency percentage."""
        if not self.current_results.charge_data or not self.current_results.discharge_data:
            return 0.0
        
        charge_energy = self._calculate_energy(self.current_results.charge_data)
        discharge_energy = self.current_results.energy_wh
        
        if charge_energy <= 0:
            return 0.0
        
        return (discharge_energy / charge_energy) * 100
    
    def emergency_stop(self) -> None:
        """Emergency stop - disable all outputs immediately."""
        self.emergency_stop_requested = True
        
        try:
            # Disable both devices
            self.power_client.disable_output()
            self.load_client.disable_input()
            
            self._log_error("EMERGENCY STOP: All outputs disabled")
            
        except Exception as e:
            logger.error(f"Emergency stop error: {e}")
        
        if self.current_results:
            self.current_results.status = TestPhase.EMERGENCY_STOPPED
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current test status for monitoring."""
        if not self.current_results:
            return {"test_active": False, "phase": TestPhase.IDLE.value}
        
        elapsed = 0
        if self.current_results.start_time:
            elapsed = (datetime.now() - self.current_results.start_time).total_seconds()
        
        return {
            "test_active": self.test_active,
            "phase": self.current_phase.value,
            "test_id": self.current_results.test_id,
            "cycles_completed": self.current_results.cycles_completed,
            "total_cycles": self.current_results.total_cycles,
            "elapsed_time": elapsed,
            "current_capacity_ah": self.current_results.capacity_ah,
            "current_energy_wh": self.current_results.energy_wh,
            "efficiency_percent": self.current_results.efficiency_percent
        }
    
    def export_results(self, filename: str, format: str = 'csv') -> None:
        """Export test results to file.
        
        Args:
            filename: Output filename
            format: Export format ('csv', 'json', 'detailed_csv')
        """
        if not self.current_results:
            raise ValueError("No test results available")
        
        if format.lower() == 'json':
            self._export_json(filename)
        elif format.lower() == 'detailed_csv':
            self._export_detailed_csv(filename)
        else:
            self._export_csv(filename)
        
        logger.info(f"Test results exported to {filename} ({format} format)")
    
    def _export_json(self, filename: str) -> None:
        """Export complete results as JSON."""
        results_dict = self.current_results.to_dict()
        
        # Add raw data
        results_dict['raw_data'] = {
            'charge_data': self.current_results.charge_data,
            'discharge_data': self.current_results.discharge_data,
            'recharge_data': self.current_results.recharge_data
        }
        
        with open(filename, 'w') as f:
            json.dump(results_dict, f, indent=2)
    
    def _export_csv(self, filename: str) -> None:
        """Export summary results as CSV."""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Test ID', 'Profile', 'Cycles', 'Capacity (Ah)', 
                           'Energy (Wh)', 'Efficiency (%)', 'Status', 'Duration (s)'])
            
            # Data
            duration = 0
            if self.current_results.end_time and self.current_results.start_time:
                duration = (self.current_results.end_time - self.current_results.start_time).total_seconds()
            
            writer.writerow([
                self.current_results.test_id,
                self.current_results.profile.get('name', 'Unknown'),
                self.current_results.cycles_completed,
                f"{self.current_results.capacity_ah:.3f}",
                f"{self.current_results.energy_wh:.3f}",
                f"{self.current_results.efficiency_percent:.1f}",
                self.current_results.status.value,
                duration
            ])
    
    def _export_detailed_csv(self, filename: str) -> None:
        """Export detailed time-series data as CSV."""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Combined data with phase identification
            all_data = []
            
            # Add charge data
            for point in self.current_results.charge_data:
                point['data_type'] = 'charge'
                all_data.append(point)
            
            # Add discharge data
            for point in self.current_results.discharge_data:
                point['data_type'] = 'discharge'
                all_data.append(point)
            
            # Add recharge data
            for point in self.current_results.recharge_data:
                point['data_type'] = 'recharge'
                all_data.append(point)
            
            # Sort by timestamp
            all_data.sort(key=lambda x: x.get('timestamp', 0))
            
            if all_data:
                # Write header
                headers = list(all_data[0].keys())
                writer.writerow(headers)
                
                # Write data
                for point in all_data:
                    row = [point.get(header, '') for header in headers]
                    writer.writerow(row)
    
    # Logging and display helper methods
    def _log_test_start(self, profile: Dict[str, Any], cycles: int) -> None:
        """Log test start information."""
        logger.info(f"Starting battery test: {cycles} cycles, profile: {profile.get('name', 'custom')}")
        if self.console:
            self.console.print(f"[bold green]Starting battery test: {cycles} cycles[/bold green]")
    
    def _log_cycle_start(self, cycle: int, total: int) -> None:
        """Log cycle start."""
        logger.info(f"Starting cycle {cycle}/{total}")
        if self.console:
            self.console.rule(f"[bold]Cycle {cycle}/{total}[/bold]")
    
    def _log_phase_start(self, phase_name: str) -> None:
        """Log phase start."""
        logger.info(f"Starting phase: {phase_name}")
        if self.console:
            self.console.print(f"[bold blue]Phase: {phase_name}[/bold blue]")
    
    def _log_phase_complete(self, phase_name: str, data_points: int, duration: float) -> None:
        """Log phase completion."""
        logger.info(f"Phase complete: {phase_name} ({data_points} data points, {duration:.1f}s)")
    
    def _log_cycle_complete(self, cycle: int, discharge_data: List[Dict], charge_data: List[Dict]) -> None:
        """Log cycle completion with metrics."""
        capacity = self._calculate_capacity(discharge_data)
        energy = self._calculate_energy(discharge_data)
        
        logger.info(f"Cycle {cycle} complete: {capacity:.3f}Ah, {energy:.3f}Wh")
        
        if self.console:
            self.console.print(f"[bold green]Cycle {cycle} complete![/bold green]")
            self.console.print(f"  Capacity: [blue]{capacity:.3f} Ah[/blue]")
            self.console.print(f"  Energy: [magenta]{energy:.3f} Wh[/magenta]")
    
    def _log_test_complete(self) -> None:
        """Log test completion."""
        logger.info("Battery test completed successfully")
        if self.console:
            self.console.print("[bold green]✓ Test completed successfully![/bold green]")
    
    def _log_success(self, message: str) -> None:
        """Log success message."""
        logger.info(message)
        if self.console:
            self.console.print(f"[green]{message}[/green]")
    
    def _log_warning(self, message: str) -> None:
        """Log warning message."""
        logger.warning(message)
        if self.console:
            self.console.print(f"[yellow]Warning: {message}[/yellow]")
    
    def _log_error(self, message: str) -> None:
        """Log error message."""
        logger.error(message)
        if self.console:
            self.console.print(f"[red]Error: {message}[/red]")
    
    def _log_status(self, message: str) -> None:
        """Log status message."""
        logger.info(message)
        if self.console:
            self.console.print(f"[dim]{message}[/dim]")
    
    def _update_status_display(self, status: str) -> None:
        """Update status display."""
        # This would be used by live monitoring displays
        pass
    
    def _update_phase_status(self, phase_name: str, elapsed: float, data_point: Dict) -> None:
        """Update phase status display with current data."""
        # Implementation for live monitoring updates
        pass
    
    def _update_rest_status(self, phase_name: str, remaining: int) -> None:
        """Update rest phase countdown display."""
        # Implementation for rest countdown display
        pass