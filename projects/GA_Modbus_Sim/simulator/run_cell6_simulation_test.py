#!/usr/bin/env python3
"""
Cell #6 Runaway Simulation Test (No Serial Port Required)

This script runs the Cell #6 runaway simulation in test mode without requiring
a physical serial port. It focuses on the runaway detection algorithm and
logging functionality.
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
    from src.algorithms.runaway_detection import RunawayDetector, RunawayThresholds, RunawayRiskLevel
    from src.utils.log_manager import setup_logging, get_logger
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Error importing simulator components: {e}")
    IMPORTS_AVAILABLE = False


class Cell6RunawayTest:
    """Cell #6 runaway simulation test without Modbus server"""
    
    def __init__(self):
        """Initialize the Cell #6 runaway test"""
        self.running = False
        self.simulation_thread = None
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
        self.alerts_detected = []
        
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
            self.logger = self.log_manager.get_logger(__name__, 'cell6_runaway_test')
            self.logger.info("Cell #6 runaway test logger initialized")
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
        print("\nShutting down Cell #6 runaway test...")
        self.stop_simulation()
        sys.exit(0)
    
    def calculate_cell6_degradation(self, progress_ratio: float) -> int:
        """Calculate Cell #6 voltage degradation over time"""
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
        """Calculate voltage for cells other than Cell #6"""
        # Normal discharge curve for other cells
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
            self.logger.info(f"Progress: {progress_ratio:.1%} | "
                           f"Time: {int(elapsed)}s/{self.simulation_duration}s | "
                           f"Delta: {current_delta}mV | "
                           f"Cell #6: {self.cell_voltages[5]}mV | "
                           f"SOC: {self.soc}% | "
                           f"Current: {self.discharge_current/1000:.1f}A")
            
            # Also log all cell voltages
            voltage_str = " | ".join([f"C{i+1}: {v}mV" for i, v in enumerate(self.cell_voltages)])
            self.logger.debug(f"Cell voltages: {voltage_str}")
    
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
            self.logger.info(f"Thresholds - Warning: {thresholds.early_warning_mv}mV, "
                           f"High Risk: {thresholds.high_risk_mv}mV, "
                           f"Critical: {thresholds.critical_mv}mV, "
                           f"Emergency: {thresholds.emergency_mv}mV, "
                           f"Catastrophic: {thresholds.catastrophic_mv}mV")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting runaway detection: {e}")
            return False
    
    def update_runaway_detector(self):
        """Update runaway detector with current data"""
        try:
            if not self.runaway_detector:
                return
                
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
            self.logger.error(f"Error updating runaway detector: {e}")
    
    def check_runaway_alerts(self):
        """Check for runaway detection alerts"""
        if not self.runaway_detector:
            return
        
        try:
            alert = self.runaway_detector.get_next_alert(timeout=0.1)
            if alert:
                # Store alert
                alert_data = {
                    'timestamp': alert.timestamp.isoformat(),
                    'time_seconds': self.current_time_seconds,
                    'event_type': alert.event_type.value,
                    'risk_level': alert.risk_level.value,
                    'delta_mv': alert.delta_mv,
                    'affected_cells': alert.affected_cells,
                    'temperature_c': alert.temperature_c,
                    'current_ma': alert.current_ma,
                    'p3e_correlation': alert.p3e_correlation,
                    'recommended_action': alert.recommended_action
                }
                self.alerts_detected.append(alert_data)
                
                # Log alert
                self.logger.warning(f"🚨 RUNAWAY ALERT #{len(self.alerts_detected)}: {alert.event_type.value} - {alert.risk_level.value}")
                self.logger.warning(f"   Time: {self.current_time_seconds:.1f}s | Delta: {alert.delta_mv}mV | Cells: {alert.affected_cells}")
                self.logger.warning(f"   Temperature: {alert.temperature_c:.1f}°C | Current: {alert.current_ma/1000:.1f}A")
                self.logger.warning(f"   P3E Correlation: {alert.p3e_correlation}")
                self.logger.warning(f"   Action: {alert.recommended_action}")
                
                # Check for emergency shutdown
                if alert.risk_level in [RunawayRiskLevel.EMERGENCY, RunawayRiskLevel.CATASTROPHIC]:
                    self.logger.critical(f"🔥 EMERGENCY LEVEL REACHED: {alert.risk_level.value}")
                    if alert.delta_mv >= self.final_delta:
                        self.logger.critical(f"🎯 TARGET 700mV DELTA THRESHOLD REACHED! ({alert.delta_mv}mV)")
                    
        except Exception as e:
            self.logger.error(f"Error checking runaway alerts: {e}")
    
    def simulation_loop(self):
        """Main simulation loop"""
        self.logger.info("Starting Cell #6 runaway simulation loop")
        self.logger.info(f"Target: {self.initial_delta}mV -> {self.final_delta}mV delta over {self.simulation_duration}s")
        self.start_time = time.time()
        
        try:
            while self.running and self.current_time_seconds < self.simulation_duration:
                # Update simulation state
                self.update_simulation_state()
                
                # Update runaway detector
                self.update_runaway_detector()
                
                # Check for runaway alerts
                self.check_runaway_alerts()
                
                # Sleep for 1 second
                time.sleep(1.0)
            
            # Simulation completed
            if self.current_time_seconds >= self.simulation_duration:
                self.logger.info("✅ Cell #6 runaway simulation completed successfully")
                current_delta = max(self.cell_voltages) - min(self.cell_voltages)
                self.logger.info(f"Final results - Delta: {current_delta}mV | Cell #6: {self.cell_voltages[5]}mV")
                
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
                "simulation_type": "Cell #6 Runaway Test",
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
                    "cell6_degradation_mv": self.initial_voltage - 8 - self.cell_voltages[5],
                    "total_alerts": len(self.alerts_detected)
                },
                "alerts": self.alerts_detected,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save report
            report_path = project_root / 'cell6_runaway_test_report.json'
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"📊 Final report saved to: {report_path}")
            
            # Print summary
            print("\n" + "="*70)
            print("CELL #6 RUNAWAY SIMULATION TEST RESULTS")
            print("="*70)
            print(f"Duration: {self.current_time_seconds:.1f}s / {self.simulation_duration}s")
            print(f"Initial Delta: {self.initial_delta}mV")
            print(f"Final Delta: {current_delta}mV")
            print(f"Target Delta: {self.final_delta}mV")
            print(f"Target Reached: {'✅ YES' if current_delta >= self.final_delta else '❌ NO'}")
            print(f"Cell #6 Final Voltage: {self.cell_voltages[5]}mV")
            print(f"Total Degradation: {self.initial_voltage - 8 - self.cell_voltages[5]}mV")
            print(f"Final SOC: {self.soc}%")
            print(f"Discharge Current: {self.discharge_current/1000:.1f}A")
            print(f"Total Alerts: {len(self.alerts_detected)}")
            print("="*70)
            
            # Show alert summary
            if self.alerts_detected:
                print("\nALERT SUMMARY:")
                risk_counts = {}
                for alert in self.alerts_detected:
                    risk = alert['risk_level']
                    risk_counts[risk] = risk_counts.get(risk, 0) + 1
                
                for risk_level, count in risk_counts.items():
                    print(f"  {risk_level.upper()}: {count} alerts")
                
                # Show first and last alerts
                if len(self.alerts_detected) > 0:
                    first = self.alerts_detected[0]
                    last = self.alerts_detected[-1]
                    print(f"\nFirst Alert: {first['time_seconds']:.1f}s - {first['risk_level']} ({first['delta_mv']}mV)")
                    print(f"Last Alert:  {last['time_seconds']:.1f}s - {last['risk_level']} ({last['delta_mv']}mV)")
            
            print("="*70)
            
        except Exception as e:
            self.logger.error(f"Error generating final report: {e}")
    
    def start_simulation(self):
        """Start the complete simulation"""
        self.logger.info("🚀 Starting Cell #6 runaway simulation test")
        self.logger.info(f"Parameters: {self.simulation_duration/60:.1f} minutes, {abs(self.discharge_current/1000):.0f}A discharge, {self.initial_delta}mV -> {self.final_delta}mV")
        
        try:
            # Start runaway detection
            if not self.start_runaway_detection():
                self.logger.error("Failed to start runaway detection")
                return False
            
            # Start simulation thread
            self.running = True
            self.simulation_thread = threading.Thread(target=self.simulation_loop)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()
            
            self.logger.info("✅ Cell #6 runaway simulation test started successfully")
            print("Cell #6 Runaway Simulation Test Running...")
            print("Press Ctrl+C to stop the simulation early")
            print("-" * 50)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting simulation: {e}")
            return False
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.logger.info("Stopping Cell #6 runaway simulation test")
        
        self.running = False
        
        # Stop runaway detector
        if self.runaway_detector:
            self.runaway_detector.stop_monitoring()
        
        # Wait for simulation thread
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=5.0)
        
        self.logger.info("Cell #6 runaway simulation test stopped")
    
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
    
    print("Cell #6 Runaway Simulation Test")
    print("="*50)
    print("Duration: 5 minutes (300 seconds)")
    print("Initial voltage: 3.2V per cell")
    print("Initial delta: 8mV")
    print("Target delta: 700mV (emergency threshold)")
    print("Discharge current: 20A")
    print("Test mode: No serial port required")
    print("="*50)
    
    # Create and start simulation
    simulator = Cell6RunawayTest()
    
    if simulator.start_simulation():
        # Run interactive mode
        simulator.run_interactive()
    else:
        print("Failed to start simulation")
        return


if __name__ == "__main__":
    main()