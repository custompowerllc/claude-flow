#!/usr/bin/env python3
"""
GA Modbus BMS Simulator - Command Line Interface

This script provides a simple command-line interface for running the
Modbus BMS simulator. It's designed to be 100% compatible with the
existing GA Modbus applications.

Usage:
    python run_simulator.py --port COM4 --scenario charging
    python run_simulator.py --list-ports
    python run_simulator.py --list-scenarios
"""

import sys
import os
import argparse
import time
import signal
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import logging system
try:
    from simulator.src.utils.log_manager import setup_logging, get_logger
    LOGGING_AVAILABLE = True
except ImportError as e:
    print("Warning: Advanced logging not available: {}".format(e))
    LOGGING_AVAILABLE = False

# Import simulator components
try:
    from simulator.src.core.modbus_server import ModbusSimulatorServer, ServerConfig
    from simulator.src.core.register_handler import RegisterHandler, BatteryScenario, BatteryState
    from simulator.src.utils.com_port_manager import ComPortManager
    SIMULATOR_AVAILABLE = True
except ImportError as e:
    print("Error importing simulator: {}".format(e))
    print("Please ensure the simulator is properly installed.")
    sys.exit(1)


class SimulatorCLI:
    """Command-line interface for the Modbus BMS simulator"""
    
    def __init__(self, log_manager=None):
        """Initialize the CLI"""
        self.server = None
        self.port_manager = ComPortManager()
        self.running = False
        self.log_manager = log_manager
        
        # Setup logger
        if LOGGING_AVAILABLE and log_manager:
            self.logger = log_manager.get_logger(__name__, 'cli')
        else:
            self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info("Received shutdown signal {}".format(signum))
        print("\nShutting down simulator...")
        self.stop_server()
        sys.exit(0)
    
    def list_ports(self):
        """List available serial ports"""
        print("Available Serial Ports:")
        print("=" * 50)
        
        ports = self.port_manager.get_available_ports()
        if not ports:
            print("No serial ports found.")
            return
        
        print(self.port_manager.format_port_table(ports))
        
        # Show recommendations
        print("\nRecommendations:")
        recommendations = self.port_manager.get_port_recommendations()
        for rec in recommendations['recommendations']:
            print("  • {}".format(rec))
    
    def list_scenarios(self):
        """List available battery scenarios"""
        print("Available Battery Scenarios:")
        print("=" * 50)
        
        handler = RegisterHandler()
        scenarios = handler.get_predefined_scenarios()
        
        for i, scenario in enumerate(scenarios, 1):
            print("{}. {}".format(i, scenario.name))
            print("   State: {}".format(scenario.state.value))
            print("   Voltage: {}V".format(scenario.base_voltage))
            print("   Current: {}A".format(scenario.current))
            print("   SOC: {}%".format(scenario.soc))
            print("   Cell Delta: {:.1f}mV".format(scenario.cell_delta * 1000))
            print()
    
    def start_server(self, port: str, scenario_name: str = None, 
                     baudrate: int = 9600, parity: str = 'E',
                     stopbits: int = 1, bytesize: int = 8, slave_id: int = 1):
        """Start the Modbus simulator server"""
        self.logger.info("Starting server on port {} with scenario '{}'".format(port, scenario_name))
        try:
            # Validate port
            valid, message = self.port_manager.validate_port_config(
                port, baudrate, parity, stopbits, bytesize
            )
            
            if not valid:
                self.logger.error("Port validation failed: {}".format(message))
                print("Port validation failed: {}".format(message))
                return False
            
            # Create server configuration
            config = ServerConfig(
                port=port,
                baudrate=baudrate,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize,
                slave_id=slave_id
            )
            
            # Create server
            self.server = ModbusSimulatorServer(config)
            
            # Set scenario if specified
            if scenario_name:
                if not self._set_scenario(scenario_name):
                    print("Warning: Could not set scenario '{}', using default".format(scenario_name))
            
            # Start server
            print("Starting Modbus simulator on {}...".format(port))
            self.logger.info("Attempting to start Modbus server")
            if self.server.start():
                self.logger.info("Simulator started successfully on {}".format(port))
                print("✅ Simulator started successfully!")
                print("   Port: {}".format(port))
                print("   Baudrate: {}".format(baudrate))
                print("   Slave ID: {}".format(slave_id))
                print("   Scenario: {}".format(scenario_name or 'Default'))
                print()
                print("The simulator is now responding to Modbus queries.")
                print("You can test it with the GA Modbus application.")
                print("Press Ctrl+C to stop the simulator.")
                
                self.running = True
                return True
            else:
                self.logger.error("Failed to start simulator")
                print("❌ Failed to start simulator")
                return False
                
        except Exception as e:
            self.logger.error("Error starting server: {}".format(e))
            print("Error starting server: {}".format(e))
            return False
    
    def _set_scenario(self, scenario_name: str) -> bool:
        """Set the battery scenario"""
        if not self.server:
            return False
        
        try:
            # Get available scenarios
            handler = RegisterHandler()
            scenarios = handler.get_predefined_scenarios()
            
            # Find matching scenario
            scenario = None
            for s in scenarios:
                if s.name.lower() == scenario_name.lower():
                    scenario = s
                    break
                elif scenario_name.lower() in s.name.lower():
                    scenario = s
                    break
            
            if not scenario:
                print("Scenario '{}' not found".format(scenario_name))
                return False
            
            # Set scenario in server
            self.server.register_handler.set_scenario(scenario)
            print("Set scenario to: {}".format(scenario.name))
            return True
            
        except Exception as e:
            print("Error setting scenario: {}".format(e))
            return False
    
    def stop_server(self):
        """Stop the simulator server"""
        self.logger.info("Stopping simulator server")
        if self.server:
            self.server.stop()
            self.server = None
        self.running = False
        self.logger.info("Simulator server stopped")
    
    def run_interactive(self):
        """Run the simulator in interactive mode"""
        while self.running:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
        
        self.stop_server()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="GA Modbus BMS Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available ports
  python run_simulator.py --list-ports
  
  # List available scenarios  
  python run_simulator.py --list-scenarios
  
  # Start simulator on COM4 with default scenario
  python run_simulator.py --port COM4
  
  # Start simulator with charging scenario
  python run_simulator.py --port COM4 --scenario charging
  
  # Start with custom settings
  python run_simulator.py --port COM4 --baudrate 19200 --slave-id 2
        """
    )
    
    # Utility commands
    parser.add_argument('--list-ports', action='store_true',
                       help='List available serial ports')
    parser.add_argument('--list-scenarios', action='store_true',
                       help='List available battery scenarios')
    
    # Server configuration
    parser.add_argument('--port', help='Serial port (e.g., COM4, /dev/ttyUSB0)')
    parser.add_argument('--baudrate', type=int, default=9600,
                       help='Baud rate (default: 9600)')
    parser.add_argument('--parity', choices=['N', 'E', 'O'], default='E',
                       help='Parity (default: E)')
    parser.add_argument('--stopbits', type=int, default=1,
                       help='Stop bits (default: 1)')
    parser.add_argument('--bytesize', type=int, default=8,
                       help='Data bits (default: 8)')
    parser.add_argument('--slave-id', type=int, default=1,
                       help='Modbus slave ID (default: 1)')
    
    # Simulation settings
    parser.add_argument('--scenario', help='Battery scenario name')
    
    # Logging options
    logging_group = parser.add_argument_group('Logging Options')
    logging_group.add_argument('--verbose', '-v', action='store_true',
                             help='Enable verbose logging (DEBUG level)')
    logging_group.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                             help='Set log level (overrides --verbose)')
    logging_group.add_argument('--log-config', metavar='PATH',
                             help='Path to logging configuration file')
    logging_group.add_argument('--log-dir', metavar='PATH',
                             help='Directory for log files')
    logging_group.add_argument('--no-console-log', action='store_true',
                             help='Disable console logging')
    logging_group.add_argument('--no-file-log', action='store_true',
                             help='Disable file logging')
    logging_group.add_argument('--json-logs', action='store_true',
                             help='Use JSON format for logs')
    logging_group.add_argument('--log-rotation-size', metavar='SIZE', default='10MB',
                             help='Log file rotation size (default: 10MB)')
    logging_group.add_argument('--log-backup-count', type=int, default=5,
                             help='Number of backup log files to keep (default: 5)')
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Setup logging
    log_manager = None
    if LOGGING_AVAILABLE:
        try:
            # Determine log level
            if args.log_level:
                log_level = args.log_level
            elif args.verbose:
                log_level = 'DEBUG'
            else:
                log_level = 'INFO'
            
            # Determine config path
            config_path = args.log_config
            if not config_path:
                # Try default config location
                default_config = Path(__file__).parent / 'config' / 'logging_config.json'
                if default_config.exists():
                    config_path = str(default_config)
            
            # Setup advanced logging
            log_manager = setup_logging(
                config_path=config_path,
                level=log_level,
                console=not args.no_console_log,
                json_format=args.json_logs
            )
            
            # Apply CLI overrides
            config_updates = {}
            if args.log_dir:
                config_updates['log_dir'] = args.log_dir
            if args.no_file_log:
                config_updates['file_output'] = False
            if args.log_rotation_size != '10MB':
                config_updates['rotation'] = {
                    **log_manager.config.get('rotation', {}),
                    'max_file_size': args.log_rotation_size
                }
            if args.log_backup_count != 5:
                if 'rotation' not in config_updates:
                    config_updates['rotation'] = log_manager.config.get('rotation', {})
                config_updates['rotation']['backup_count'] = args.log_backup_count
            
            if config_updates:
                log_manager.update_config(config_updates)
            
            logger = log_manager.get_logger(__name__, 'cli')
            logger.info("Advanced logging initialized")
            
        except Exception as e:
            print("Warning: Failed to setup advanced logging: {}".format(e))
            print("Falling back to basic logging")
            log_manager = None
    
    # Fallback to basic logging if advanced logging failed
    if not log_manager:
        log_level = logging.DEBUG if args.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
        logger.info("Basic logging initialized")
    
    # Create CLI
    cli = SimulatorCLI(log_manager)
    
    # Handle utility commands
    if args.list_ports:
        cli.list_ports()
        return
    
    if args.list_scenarios:
        cli.list_scenarios()
        return
    
    # Validate required arguments for server mode
    if not args.port:
        print("Error: --port is required to start the simulator")
        print("Use --list-ports to see available ports")
        return
    
    # Start server
    success = cli.start_server(
        port=args.port,
        scenario_name=args.scenario,
        baudrate=args.baudrate,
        parity=args.parity,
        stopbits=args.stopbits,
        bytesize=args.bytesize,
        slave_id=args.slave_id
    )
    
    if success:
        # Run interactive mode
        cli.run_interactive()
    else:
        print("Failed to start simulator")
        sys.exit(1)


if __name__ == "__main__":
    main()