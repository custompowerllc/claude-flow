"""Main CLI interface for BK-Integration application."""

import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any

import click
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import track

from .config import ConfigManager, ConfigurationError
from .clients import BK8520Client, BK9206bClient
from .utils.display import (
    create_device_table, 
    create_status_table, 
    create_test_progress_display,
    create_monitoring_layout,
    create_test_results_table,
    create_error_panel,
    format_time
)
from .utils.safety import SafetyMonitor
from .workflows.battery_test import BatteryTestOrchestrator

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(level: str, log_file: str) -> None:
    """Setup logging configuration."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


@click.group()
@click.option('--config', '-c', default='config.json', 
              help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose logging')
@click.pass_context
def cli(ctx, config, verbose):
    """BK-Integration: Unified control for BK8520 and BK9206b devices.
    
    A comprehensive CLI for controlling B&K Precision test equipment,
    featuring battery testing workflows, real-time monitoring,
    and external API integration.
    """
    ctx.ensure_object(dict)
    
    # Initialize configuration
    config_path = Path(config)
    
    try:
        ctx.obj['config'] = ConfigManager(config_path)
        config_data = ctx.obj['config']
        
        # Setup logging
        log_config = config_data.get_logging_config()
        log_level = 'DEBUG' if verbose else log_config['level']
        setup_logging(log_level, log_config['file'])
        
        ctx.obj['verbose'] = verbose
        
        # Initialize device clients
        ctx.obj['load_client'] = BK8520Client(config_data.get_load_config())
        ctx.obj['power_client'] = BK9206bClient(config_data.get_power_config())
        
        # Initialize safety monitor
        ctx.obj['safety_monitor'] = SafetyMonitor(config_data.config)
        ctx.obj['safety_monitor'].start_monitoring()
        
        logger.info(f"BK-Integration initialized with config: {config_path}")
        
    except ConfigurationError as e:
        console.print(create_error_panel(
            f"Configuration error: {e}",
            f"Check your configuration file: {config_path}"
        ))
        ctx.exit(1)
    except Exception as e:
        console.print(create_error_panel(
            f"Initialization error: {e}",
            "Check device connections and configuration"
        ))
        ctx.exit(1)


# Device management commands
@cli.group()
def device():
    """Device management commands."""
    pass


@device.command()
@click.pass_context
def status(ctx):
    """Show comprehensive status of both devices."""
    with console.status("[bold green]Checking device status..."):
        try:
            load_status = ctx.obj['load_client'].get_status()
            power_status = ctx.obj['power_client'].get_status()
            
            # Add device info if available
            if ctx.obj['verbose']:
                load_info = ctx.obj['load_client'].get_device_info()
                if load_info.get('success'):
                    load_status.update(load_info.get('data', {}))
        
        except Exception as e:
            console.print(create_error_panel(
                f"Error getting device status: {e}",
                "Verify device connections and API availability"
            ))
            return
    
    # Create and display status table
    table = create_device_table(load_status, power_status)
    console.print(table)
    
    # Show safety summary if verbose
    if ctx.obj['verbose']:
        safety_summary = ctx.obj['safety_monitor'].get_safety_summary()
        console.print(f"\n[dim]Safety Events (24h): {safety_summary['recent_events_24h']}[/dim]")


@device.command()
@click.pass_context
def connect(ctx):
    """Connect to both devices with safety validation."""
    console.print("[bold blue]Connecting to devices...[/bold blue]")
    
    # Connect BK8520 with progress indication
    with console.status("[green]Connecting BK8520..."):
        load_config = ctx.obj['config'].get_load_config()
        load_result = ctx.obj['load_client'].connect(
            port=load_config.get('serial_port', '/dev/ttyUSB0'),
            reset_input_on_connect=True
        )
    
    if load_result.get('success'):
        console.print("[green]✓[/green] BK8520 Load Tester connected")
        
        # Get device info for confirmation
        info_result = ctx.obj['load_client'].get_device_info()
        if info_result.get('success') and ctx.obj['verbose']:
            device_info = info_result.get('data', {})
            console.print(f"  Model: {device_info.get('model', 'Unknown')}")
            console.print(f"  Firmware: {device_info.get('firmware', 'Unknown')}")
    else:
        console.print(f"[red]✗[/red] BK8520 connection failed: {load_result.get('message')}")
    
    # Check BK9206b connection
    with console.status("[green]Verifying BK9206b..."):
        power_result = ctx.obj['power_client'].health_check()
    
    if power_result.get('success') or power_result.get('server_status') == 'healthy':
        console.print("[green]✓[/green] BK9206b Power Supply connected")
        
        # Get status for confirmation
        if ctx.obj['verbose']:
            status_result = ctx.obj['power_client'].get_status()
            if isinstance(status_result, dict):
                device_id = status_result.get('device_id', 'Unknown')
                console.print(f"  Device: {device_id}")
    else:
        console.print(f"[red]✗[/red] BK9206b connection failed: {power_result.get('message')}")


@device.command()
@click.pass_context  
def disconnect(ctx):
    """Safely disconnect from both devices."""
    console.print("[bold yellow]Disconnecting devices...[/bold yellow]")
    
    # Disconnect BK8520
    load_result = ctx.obj['load_client'].disconnect()
    if load_result.get('success'):
        console.print("[green]✓[/green] BK8520 Load Tester disconnected")
    else:
        console.print(f"[yellow]⚠[/yellow] BK8520 disconnect: {load_result.get('message')}")
    
    # BK9206b - ensure output is disabled
    power_result = ctx.obj['power_client'].disable_output()
    if power_result.get('success'):
        console.print("[green]✓[/green] BK9206b Power Supply output disabled")
    else:
        console.print(f"[yellow]⚠[/yellow] BK9206b shutdown: {power_result.get('message')}")


@device.command()
@click.pass_context
def info(ctx):
    """Show detailed device information and specifications."""
    with console.status("[bold green]Getting device information..."):
        load_info = ctx.obj['load_client'].get_device_info()
        power_status = ctx.obj['power_client'].get_status()
    
    # BK8520 Information
    if load_info.get('success') and load_info.get('data'):
        info_data = load_info['data']
        load_table = create_status_table("BK8520 Electronic Load Information", info_data)
        console.print(load_table)
    
    # BK9206b Information
    if isinstance(power_status, dict):
        power_table = create_status_table("BK9206b Power Supply Information", power_status)
        console.print(power_table)
    
    # Device limits
    console.print("\n[bold]Device Specifications:[/bold]")
    limits_table = Table(show_header=True, header_style="bold cyan")
    limits_table.add_column("Device", style="cyan")
    limits_table.add_column("Parameter", style="blue")
    limits_table.add_column("Maximum", style="green")
    
    load_limits = ctx.obj['load_client'].device_limits
    for param, value in load_limits.items():
        limits_table.add_row("BK8520", param.replace('max_', '').title(), f"{value}")
    
    power_limits = ctx.obj['power_client'].device_limits
    for param, value in power_limits.items():
        limits_table.add_row("BK9206b", param.replace('max_', '').title(), f"{value}")
    
    console.print(limits_table)


# Battery testing commands
@cli.group()
def test():
    """Battery testing commands with safety protocols."""
    pass


@test.command()
@click.option('--profile', '-p', default='default', 
              help='Test profile to use')
@click.option('--cycles', '-n', default=1, type=int,
              help='Number of charge/discharge cycles')
@click.option('--dry-run', is_flag=True,
              help='Validate configuration without running test')
@click.pass_context
def battery(ctx, profile, cycles, dry_run):
    """Run complete battery test cycle with safety monitoring."""
    config = ctx.obj['config']
    
    # Validate test profile
    try:
        test_profile = config.get_test_profile(profile)
    except Exception as e:
        console.print(create_error_panel(
            f"Test profile error: {e}",
            f"Available profiles: {list(config.list_test_profiles().keys())}"
        ))
        return
    
    if not config.validate_test_profile(test_profile):
        console.print(create_error_panel(
            "Invalid test profile parameters",
            "Check voltage/current limits against device specifications"
        ))
        return
    
    # Display test configuration
    console.print(f"[bold cyan]Battery Test Configuration[/bold cyan]")
    
    config_table = Table(show_header=False)
    config_table.add_column("Parameter", style="cyan")
    config_table.add_column("Value", style="green")
    
    config_table.add_row("Profile", profile)
    config_table.add_row("Cycles", str(cycles))
    config_table.add_row("Charge Voltage", f"{test_profile['charge_voltage']:.1f}V")
    config_table.add_row("Charge Current", f"{test_profile['charge_current']:.1f}A")
    config_table.add_row("Discharge Current", f"{test_profile['discharge_current']:.1f}A")
    config_table.add_row("Cutoff Voltage", f"{test_profile['cutoff_voltage']:.1f}V")
    config_table.add_row("Rest Time", f"{test_profile['rest_time']}s")
    
    console.print(config_table)
    
    if dry_run:
        console.print("\n[yellow]✓ Dry run completed - configuration valid[/yellow]")
        return
    
    # Confirm before starting
    if not click.confirm("\nProceed with battery test?"):
        console.print("Test cancelled")
        return
    
    # Initialize test orchestrator
    orchestrator = BatteryTestOrchestrator(
        ctx.obj['power_client'],
        ctx.obj['load_client'],
        ctx.obj['safety_monitor'],
        console
    )
    
    # Register emergency stop callback
    def emergency_stop(safety_event=None):
        console.print("\n[red]EMERGENCY STOP ACTIVATED[/red]")
        orchestrator.emergency_stop()
    
    ctx.obj['safety_monitor'].set_emergency_stop_callback(emergency_stop)
    
    # Execute test with progress tracking
    try:
        console.print(f"\n[bold green]Starting battery test...[/bold green]")
        
        results = orchestrator.run_battery_test(test_profile, cycles)
        
        # Display results
        console.print(f"\n[bold green]✓ Test completed successfully![/bold green]")
        
        results_table = create_test_results_table(results.__dict__)
        console.print(results_table)
        
        # Export results if requested
        export_file = f"battery_test_{results.test_id}.csv"
        console.print(f"\n[dim]Results saved to: {export_file}[/dim]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
        orchestrator.emergency_stop()
    except Exception as e:
        console.print(create_error_panel(
            f"Test failed: {e}",
            "Check device connections and try again"
        ))
        orchestrator.emergency_stop()


@test.command()
@click.option('--profile', '-p', required=True, help='Profile name')
@click.option('--voltage', type=float, required=True, help='Charge voltage (V)')
@click.option('--current', type=float, required=True, help='Charge current (A)')
@click.option('--discharge', type=float, required=True, help='Discharge current (A)')
@click.option('--cutoff', type=float, required=True, help='Cutoff voltage (V)')
@click.option('--rest', type=int, default=60, help='Rest time (s)')
@click.pass_context
def create_profile(ctx, profile, voltage, current, discharge, cutoff, rest):
    """Create a new test profile."""
    config = ctx.obj['config']
    
    # Create profile dictionary
    profile_data = {
        'name': profile,
        'description': f'Custom profile: {voltage}V @ {current}A',
        'charge_voltage': voltage,
        'charge_current': current,
        'discharge_current': discharge,
        'cutoff_voltage': cutoff,
        'rest_time': rest
    }
    
    # Validate profile
    try:
        if not config.validate_test_profile(profile_data):
            console.print(create_error_panel(
                "Profile validation failed",
                "Check parameters against device specifications"
            ))
            return
        
        # Update configuration
        config.update_test_profile(profile, profile_data)
        config.save_config()
        
        console.print(f"[green]✓[/green] Test profile '{profile}' created successfully")
        
    except Exception as e:
        console.print(create_error_panel(f"Error creating profile: {e}"))


@test.command()
@click.pass_context
def list_profiles(ctx):
    """List available test profiles."""
    config = ctx.obj['config']
    profiles = config.list_test_profiles()
    
    if not profiles:
        console.print("[yellow]No test profiles available[/yellow]")
        return
    
    table = Table(title="Available Test Profiles", show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="green")
    
    for name, description in profiles.items():
        table.add_row(name, description)
    
    console.print(table)


# Real-time monitoring
@cli.command()
@click.option('--interval', '-i', default=1.0, type=float,
              help='Update interval in seconds')
@click.option('--export', type=click.Path(),
              help='Export monitoring data to CSV file')
@click.option('--duration', '-d', type=int,
              help='Monitoring duration in seconds')
@click.pass_context
def monitor(ctx, interval, export, duration):
    """Real-time monitoring with data export capability."""
    console.print("[bold blue]Starting real-time monitoring...[/bold blue]")
    console.print(f"Update interval: {interval}s")
    
    if duration:
        console.print(f"Duration: {duration}s")
    
    if export:
        console.print(f"Exporting to: {export}")
    
    # Create monitoring layout
    layout = create_monitoring_layout()
    
    # Data logging setup
    data_log = [] if export else None
    start_time = time.time()
    update_count = 0
    
    with Live(layout, refresh_per_second=1/interval, screen=True) as live:
        try:
            while True:
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Check duration limit
                if duration and elapsed >= duration:
                    break
                
                # Get device readings
                try:
                    load_data = ctx.obj['load_client'].get_readings()
                    power_data = ctx.obj['power_client'].get_status()
                    
                    # Safety monitoring
                    if isinstance(load_data, dict) and 'error' not in load_data:
                        ctx.obj['safety_monitor'].check_reading_safety('bk8520', load_data)
                    
                    if isinstance(power_data, dict):
                        ctx.obj['safety_monitor'].check_reading_safety('bk9206b', power_data)
                
                except Exception as e:
                    load_data = {"error": str(e)}
                    power_data = {"error": str(e)}
                
                # Update displays
                layout["load"].update(create_status_table("BK8520 Load Tester", load_data))
                layout["power"].update(create_status_table("BK9206b Power Supply", power_data))
                
                # Update footer with statistics
                update_count += 1
                footer_text = f"Updates: {update_count} | Elapsed: {format_time(elapsed)} | Press Ctrl+C to stop"
                layout["footer"].update(footer_text)
                
                # Log data for export
                if data_log is not None and isinstance(load_data, dict) and isinstance(power_data, dict):
                    log_entry = {
                        'timestamp': current_time,
                        'elapsed_time': elapsed,
                        'load_voltage': load_data.get('voltage', 0),
                        'load_current': load_data.get('current', 0),
                        'load_power': load_data.get('power', 0),
                        'power_voltage_actual': power_data.get('voltage_actual', 0),
                        'power_current_actual': power_data.get('current_actual', 0),
                        'power_mode': power_data.get('operating_mode', 'N/A'),
                        'power_output_enabled': power_data.get('output_enabled', False)
                    }
                    data_log.append(log_entry)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            pass
    
    # Export data if requested
    if export and data_log:
        try:
            import csv
            with open(export, 'w', newline='') as f:
                if data_log:
                    writer = csv.DictWriter(f, fieldnames=data_log[0].keys())
                    writer.writeheader()
                    writer.writerows(data_log)
            
            console.print(f"[green]✓[/green] Data exported to {export} ({len(data_log)} records)")
        except Exception as e:
            console.print(create_error_panel(f"Export failed: {e}"))
    
    console.print(f"\nMonitoring completed: {update_count} updates over {format_time(elapsed)}")


# Configuration management
@cli.group()
def config():
    """Configuration management commands."""
    pass


@config.command()
@click.pass_context
def show(ctx):
    """Show current configuration."""
    from .utils.display import create_configuration_table
    
    config_data = ctx.obj['config'].config
    table = create_configuration_table(config_data)
    console.print(table)


@config.command()
@click.pass_context  
def validate(ctx):
    """Validate current configuration."""
    config_manager = ctx.obj['config']
    
    try:
        # Re-validate configuration
        config_manager._validate_config()
        console.print("[green]✓[/green] Configuration is valid")
        
        # Validate test profiles
        profiles = config_manager.list_test_profiles()
        for profile_name in profiles:
            try:
                profile = config_manager.get_test_profile(profile_name)
                config_manager.validate_test_profile(profile)
                console.print(f"[green]✓[/green] Profile '{profile_name}' is valid")
            except Exception as e:
                console.print(f"[red]✗[/red] Profile '{profile_name}': {e}")
        
    except Exception as e:
        console.print(create_error_panel(f"Configuration validation failed: {e}"))


# API server mode
@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8080, type=int, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
@click.pass_context
def serve(ctx, host, port, reload):
    """Start REST API server for external integration."""
    console.print(f"[bold blue]Starting API server on {host}:{port}[/bold blue]")
    
    try:
        import uvicorn
        from .api.server import create_app
        
        # Create FastAPI app with dependency injection
        app = create_app(
            config=ctx.obj['config'],
            load_client=ctx.obj['load_client'],
            power_client=ctx.obj['power_client'],
            safety_monitor=ctx.obj['safety_monitor']
        )
        
        # Start server
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info" if ctx.obj['verbose'] else "warning"
        )
        
    except ImportError:
        console.print(create_error_panel(
            "API server dependencies not available",
            "Install with: pip install 'bk-integration[api]'"
        ))
    except Exception as e:
        console.print(create_error_panel(f"Server startup failed: {e}"))


# Safety monitoring commands
@cli.group()
def safety():
    """Safety monitoring and event management."""
    pass


@safety.command()
@click.pass_context
def status(ctx):
    """Show safety monitoring status."""
    safety_monitor = ctx.obj['safety_monitor']
    summary = safety_monitor.get_safety_summary()
    
    table = Table(title="Safety Monitor Status", show_header=True)
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Monitoring Active", "✓ Yes" if summary['monitoring_active'] else "✗ No")
    table.add_row("Emergency Stop Configured", "✓ Yes" if summary['emergency_stop_configured'] else "✗ No")
    table.add_row("Total Events", str(summary['total_events']))
    table.add_row("Recent Events (24h)", str(summary['recent_events_24h']))
    table.add_row("Devices Monitored", ", ".join(summary['devices_monitored']))
    
    console.print(table)
    
    # Show event counts by level
    if summary['event_counts']:
        counts_table = Table(title="Event Counts (24h)", show_header=True)
        counts_table.add_column("Level", style="cyan")
        counts_table.add_column("Count", style="green")
        
        for level, count in summary['event_counts'].items():
            counts_table.add_row(level.title(), str(count))
        
        console.print(counts_table)


@safety.command()
@click.option('--level', type=click.Choice(['info', 'warning', 'critical', 'emergency']),
              help='Filter by safety level')
@click.option('--device', type=click.Choice(['bk8520', 'bk9206b']),
              help='Filter by device')
@click.option('--hours', default=24.0, type=float,
              help='Hours to look back')
@click.pass_context
def events(ctx, level, device, hours):
    """Show recent safety events."""
    from .utils.safety import SafetyLevel
    
    safety_monitor = ctx.obj['safety_monitor']
    
    # Convert level string to enum
    level_enum = None
    if level:
        level_enum = SafetyLevel(level)
    
    events = safety_monitor.get_recent_events(level_enum, device, hours)
    
    if not events:
        console.print(f"[green]No safety events in the last {hours} hours[/green]")
        return
    
    table = Table(title=f"Safety Events (Last {hours}h)", show_header=True)
    table.add_column("Time", style="cyan")
    table.add_column("Level", style="yellow")
    table.add_column("Device", style="blue")
    table.add_column("Parameter", style="green")
    table.add_column("Value", style="white")
    table.add_column("Message", style="white")
    
    for event in events[-20:]:  # Show last 20 events
        from datetime import datetime
        
        timestamp = datetime.fromtimestamp(event.timestamp).strftime("%H:%M:%S")
        
        # Color code by level
        level_colors = {
            'info': 'green',
            'warning': 'yellow', 
            'critical': 'red',
            'emergency': 'bold red'
        }
        level_color = level_colors.get(event.level.value, 'white')
        
        table.add_row(
            timestamp,
            f"[{level_color}]{event.level.value.upper()}[/{level_color}]",
            event.device,
            event.parameter,
            str(event.value),
            event.message
        )
    
    console.print(table)
    
    if len(events) > 20:
        console.print(f"[dim]Showing 20 of {len(events)} events[/dim]")


if __name__ == '__main__':
    cli()