#!/usr/bin/env python3
"""
Cell #6 Runaway Simulation Script

This script simulates a specific Cell #6 runaway scenario with the following parameters:
- Initial voltage: 3.2V per cell
- Initial delta: 8mV
- Final delta: 700mV (emergency threshold)
- Duration: 5 minutes (300 seconds)
- Discharge current: 20A
- Cell #6 degrades progressively during discharge

The simulation integrates with the standalone logger and runaway detection system.
"""

import sys
import os
import time
import threading
import signal
import json
from pathlib import Path
from datetime import datetime, timedelta
import math

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import simulator components
try:
    from src.core.modbus_server import ModbusSimulatorServer, ServerConfig
    from src.core.register_handler import RegisterHandler, BatteryScenario, BatteryState
    from src.algorithms.runaway_detection import RunawayDetector, RunawayThresholds
    from src.utils.log_manager import setup_logging, get_logger
    from src.utils.com_port_manager import ComPortManager
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Error importing simulator components: {e}")
    print("Please ensure the simulator is properly installed.")
    IMPORTS_AVAILABLE = False


class Cell6RunawaySimulator:
    """Custom Cell #6 runaway simulation"""
    
    def __init__(self, port: str = '/dev/ttyUSB0'):
        """Initialize the Cell #6 runaway simulator"""
        self.port = port
        self.running = False
        self.simulation_thread = None
        self.server = None
        self.runaway_detector = None
        
        # Simulation parameters
        self.simulation_duration = 300  # 5 minutes in seconds
        self.discharge_current = -20000  # -20A in mA
        self.initial_voltage = 3200  # 3.2V in mV
        self.initial_delta = 8  # 8mV initial delta
        self.final_delta = 700  # 700mV final delta (emergency threshold)
        
        # Cell voltage tracking
        self.cell_voltages = [3200] * 8  # Initialize all cells to 3.2V
        self.cell_voltages[5] = 3192  # Cell #6 (index 5) starts 8mV lower
        
        # Simulation state
        self.start_time = None
        self.current_time_seconds = 0
        self.soc = 70  # Start at 70% SOC
        
        # Setup logging
        self.setup_logging()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def setup_logging(self):
        """Setup logging system"""
        try:
            # Setup advanced logging
            config_path = project_root / 'config' / 'logging_config.json'
            self.log_manager = setup_logging(
                config_path=str(config_path) if config_path.exists() else None,
                level='INFO',
                console=True,
                json_format=False
            )
            self.logger = self.log_manager.get_logger(__name__, 'cell6_runaway')
            self.logger.info("Cell #6 runaway simulation logger initialized")
        except Exception as e:
            print(f"Warning: Failed to setup advanced logging: {e}")
            import logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger(__name__)
            self.log_manager = None
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received shutdown signal {signum}")
        print("\nShutting down Cell #6 runaway simulation...")
        self.stop_simulation()
        sys.exit(0)
    
    def calculate_cell6_degradation(self, progress_ratio: float) -> int:
        """Calculate Cell #6 voltage degradation over time
        
        Args:
            progress_ratio: 0.0 to 1.0 representing simulation progress
            
        Returns:
            Cell #6 voltage in mV
        """
        # Exponential degradation curve for Cell #6
        # Starts at 3192mV, degrades to create 700mV delta at end
        
        if progress_ratio <= 0.6:
            # First 60% of simulation: gradual degradation
            degradation = (self.initial_delta / 2) * progress_ratio / 0.6
            return int(self.initial_voltage - self.initial_delta - degradation)
        else:
            # Last 40% of simulation: rapid degradation
            rapid_progress = (progress_ratio - 0.6) / 0.4
            # Use exponential curve for rapid degradation
            exp_factor = math.exp(3 * rapid_progress) - 1
            max_exp = math.exp(3) - 1
            
            rapid_degradation = (self.final_delta - self.initial_delta) * exp_factor / max_exp
            return int(self.initial_voltage - self.initial_delta - rapid_degradation)
    
    def calculate_other_cells_voltage(self, progress_ratio: float, cell_id: int) -> int:
        """Calculate voltage for cells other than Cell #6
        
        Args:
            progress_ratio: 0.0 to 1.0 representing simulation progress
            cell_id: Cell ID (1-8)
            
        Returns:
            Cell voltage in mV
        """
        # Normal discharge curve for other cells
        # Slight variations between cells for realism
        base_discharge = 200 * progress_ratio  # 200mV total discharge over 5 minutes
        
        # Add small variations per cell
        cell_variations = {
            1: -2, 2: +3, 3: +1, 4: -1, 5: +2, 7: -3, 8: +1
        }
        variation = cell_variations.get(cell_id, 0)
        
        return int(self.initial_voltage - base_discharge + variation)
    
    def update_simulation_state(self):
        """Update simulation state based on elapsed time"""
        if not self.start_time:
            return
            
        elapsed = time.time() - self.start_time
        self.current_time_seconds = elapsed
        progress_ratio = min(elapsed / self.simulation_duration, 1.0)
        
        # Update Cell #6 (index 5) with degradation
        self.cell_voltages[5] = self.calculate_cell6_degradation(progress_ratio)
        
        # Update other cells with normal discharge
        for i in range(8):
            if i != 5:  # Skip Cell #6
                cell_id = i + 1
                self.cell_voltages[i] = self.calculate_other_cells_voltage(progress_ratio, cell_id)
        
        # Update SOC (discharge from 70% to ~40%)
        self.soc = int(70 - (30 * progress_ratio))
        
        # Calculate current delta
        current_delta = max(self.cell_voltages) - min(self.cell_voltages)
        
        # Log progress every 10 seconds
        if int(elapsed) % 10 == 0 and int(elapsed) != getattr(self, '_last_log_time', -1):
            self._last_log_time = int(elapsed)
            self.logger.info(f"Simulation Progress: {progress_ratio:.1%} | "
                           f"Time: {int(elapsed)}s | Delta: {current_delta}mV | "
                           f"Cell #6: {self.cell_voltages[5]}mV | SOC: {self.soc}%")
    
    def start_modbus_server(self):
        """Start the Modbus server"""
        try:
            # Create server configuration
            config = ServerConfig(
                port=self.port,
                baudrate=9600,
                parity='E',
                stopbits=1,
                bytesize=8,
                slave_id=1
            )
            
            # Create and start server
            self.server = ModbusSimulatorServer(config)
            
            if self.server.start():
                self.logger.info(f"Modbus server started on {self.port}")
                return True
            else:
                self.logger.error("Failed to start Modbus server")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting Modbus server: {e}")
            return False
    
    def start_runaway_detection(self):
        """Start the runaway detection system"""
        try:
            # Create custom thresholds for this simulation
            thresholds = RunawayThresholds(
                early_warning_mv=50,    # Lower threshold for early detection
                high_risk_mv=200,       # Enhanced sensitivity
                critical_mv=400,        # Earlier critical detection
                emergency_mv=600,       # Just before our 700mV target
                catastrophic_mv=700     # Our target threshold
            )
            
            self.runaway_detector = RunawayDetector(cell_count=8, thresholds=thresholds)
            self.runaway_detector.start_monitoring()
            
            self.logger.info("Runaway detection system started with custom thresholds")
            self.logger.info(f"Emergency threshold: {thresholds.emergency_mv}mV")
            self.logger.info(f"Catastrophic threshold: {thresholds.catastrophic_mv}mV")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting runaway detection: {e}")
            return False
    
    def update_system_data(self):
        """Update both Modbus server and runaway detector with current data"""
        try:
            # Update Modbus server registers
            if self.server and self.server.register_handler:
                handler = self.server.register_handler
                
                # Update cell voltages (registers 1-8)
                for i, voltage in enumerate(self.cell_voltages):
                    handler.set_register(i + 1, voltage)
                
                # Update pack current (register 9)
                handler.set_register(9, self.discharge_current)
                
                # Update SOC (register 10)
                handler.set_register(10, self.soc)
                
                # Update temperatures (registers 11-18) - simulate heating
                base_temp = 250 + int(self.current_time_seconds * 0.5)  # Gradual heating
                for i in range(8):
                    temp = base_temp + (20 if i == 5 else 0)  # Cell #6 runs hotter
                    handler.set_register(11 + i, temp)
            
            # Update runaway detector
            if self.runaway_detector:
                for i, voltage in enumerate(self.cell_voltages):
                    cell_id = i + 1
                    temp_dc = 250 + int(self.current_time_seconds * 0.5) + (20 if i == 5 else 0)
                    
                    self.runaway_detector.update_cell_data(
                        cell_id=cell_id,
                        voltage_mv=voltage,
                        temperature_dc=temp_dc,
                        current_ma=self.discharge_current,
                        soc_percent=self.soc
                    )
        
        except Exception as e:
            self.logger.error(f"Error updating system data: {e}")
    
    def check_runaway_alerts(self):
        """Check for runaway detection alerts"""
        if not self.runaway_detector:
            return
        
        try:
            alert = self.runaway_detector.get_next_alert(timeout=0.1)
            if alert:
                self.logger.warning(f"RUNAWAY ALERT: {alert.event_type.value} - {alert.risk_level.value}")
                self.logger.warning(f"  Delta: {alert.delta_mv}mV | Affected Cells: {alert.affected_cells}")
                self.logger.warning(f"  Temperature: {alert.temperature_c:.1f}°C | Current: {alert.current_ma}mA")
                self.logger.warning(f"  P3E Correlation: {alert.p3e_correlation}")
                self.logger.warning(f"  Recommended Action: {alert.recommended_action}")
                
                # Check for emergency shutdown
                if alert.risk_level.value in ['emergency', 'catastrophic']:
                    self.logger.critical(f"EMERGENCY LEVEL REACHED: {alert.risk_level.value}")
                    self.logger.critical("Target 700mV delta threshold reached!")
                    
        except Exception as e:
            self.logger.error(f"Error checking runaway alerts: {e}")
    
    def simulation_loop(self):
        """Main simulation loop"""
        self.logger.info("Starting Cell #6 runaway simulation loop")
        self.start_time = time.time()
        
        try:
            while self.running and self.current_time_seconds < self.simulation_duration:
                # Update simulation state
                self.update_simulation_state()
                
                # Update system data
                self.update_system_data()
                
                # Check for runaway alerts
                self.check_runaway_alerts()
                
                # Sleep for 1 second
                time.sleep(1.0)
            
            # Simulation completed
            if self.current_time_seconds >= self.simulation_duration:
                self.logger.info("Cell #6 runaway simulation completed successfully")
                self.logger.info(f"Final delta: {max(self.cell_voltages) - min(self.cell_voltages)}mV")
                self.logger.info(f"Cell #6 final voltage: {self.cell_voltages[5]}mV")
                
                # Generate final report
                self.generate_final_report()
            
        except Exception as e:
            self.logger.error(f"Error in simulation loop: {e}")
        finally:
            self.logger.info("Simulation loop ended")
    
    def generate_final_report(self):
        """Generate final simulation report"""
        try:
            current_delta = max(self.cell_voltages) - min(self.cell_voltages)
            
            report = {
                "simulation_type": "Cell #6 Runaway",
                "duration_seconds": self.simulation_duration,
                "actual_duration": self.current_time_seconds,
                "parameters": {
                    "initial_voltage_mv": self.initial_voltage,
                    "initial_delta_mv": self.initial_delta,
                    "target_delta_mv": self.final_delta,
                    "discharge_current_ma": self.discharge_current
                },
                "results": {
                    "final_delta_mv": current_delta,
                    "target_reached": current_delta >= self.final_delta,
                    "cell_voltages_mv": self.cell_voltages,
                    "final_soc_percent": self.soc,
                    "cell6_degradation_mv": self.initial_voltage - 8 - self.cell_voltages[5]
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Save report
            report_path = project_root / 'cell6_runaway_report.json'
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Final report saved to: {report_path}")
            
            # Print summary
            print("\n" + "="*60)
            print("CELL #6 RUNAWAY SIMULATION SUMMARY")
            print("="*60)
            print(f"Duration: {self.current_time_seconds:.1f} seconds")
            print(f"Initial Delta: {self.initial_delta}mV")
            print(f"Final Delta: {current_delta}mV")
            print(f"Target Reached: {'YES' if current_delta >= self.final_delta else 'NO'}")
            print(f"Cell #6 Final Voltage: {self.cell_voltages[5]}mV")
            print(f"Total Degradation: {self.initial_voltage - 8 - self.cell_voltages[5]}mV")
            print(f"Final SOC: {self.soc}%")
            print("="*60)
            
        except Exception as e:
            self.logger.error(f"Error generating final report: {e}")
    
    def start_simulation(self):
        """Start the complete simulation"""
        self.logger.info("Starting Cell #6 runaway simulation")
        self.logger.info(f"Parameters: 5 minutes, 20A discharge, {self.initial_delta}mV -> {self.final_delta}mV")
        
        try:
            # Start Modbus server
            if not self.start_modbus_server():
                self.logger.error("Failed to start Modbus server")
                return False
            
            # Start runaway detection
            if not self.start_runaway_detection():
                self.logger.error("Failed to start runaway detection")
                return False
            
            # Start simulation thread
            self.running = True
            self.simulation_thread = threading.Thread(target=self.simulation_loop)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()
            
            self.logger.info("Cell #6 runaway simulation started successfully")
            print(f"Simulation running on port {self.port}")
            print("Press Ctrl+C to stop the simulation")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting simulation: {e}")
            return False
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.logger.info("Stopping Cell #6 runaway simulation")
        
        self.running = False
        
        # Stop runaway detector
        if self.runaway_detector:
            self.runaway_detector.stop_monitoring()
        
        # Stop Modbus server
        if self.server:
            self.server.stop()
        
        # Wait for simulation thread
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=5.0)
        
        self.logger.info("Cell #6 runaway simulation stopped")
    
    def run_interactive(self):
        """Run simulation in interactive mode"""
        try:
            while self.running and self.simulation_thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
        finally:
            self.stop_simulation()


def main():
    """Main entry point"""
    if not IMPORTS_AVAILABLE:
        print("Required imports not available. Please check the simulator installation.")
        return
    
    # Get port from command line or use default
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    
    print("Cell #6 Runaway Simulation")
    print("="*50)
    print(f"Port: {port}")
    print("Duration: 5 minutes (300 seconds)")
    print("Initial voltage: 3.2V per cell")
    print("Initial delta: 8mV")
    print("Target delta: 700mV (emergency threshold)")
    print("Discharge current: 20A")
    print("="*50)
    
    # Create and start simulation
    simulator = Cell6RunawaySimulator(port)
    
    if simulator.start_simulation():
        # Run interactive mode
        simulator.run_interactive()
    else:
        print("Failed to start simulation")
        return


if __name__ == "__main__":
    main()