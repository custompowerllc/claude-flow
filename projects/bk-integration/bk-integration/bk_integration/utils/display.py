"""Display utilities using Rich formatting for BK-Integration CLI."""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from rich.table import Table
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn


def format_time(seconds: float) -> str:
    """Format time duration in human-readable format.
    
    Args:
        seconds: Time duration in seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.2f}h"


def format_value(value: Any, unit: str = "", precision: int = 3) -> str:
    """Format numeric value with unit and precision.
    
    Args:
        value: Numeric value to format
        unit: Unit string (V, A, W, etc.)
        precision: Number of decimal places
        
    Returns:
        Formatted value string
    """
    if isinstance(value, (int, float)):
        return f"{value:.{precision}f}{unit}"
    else:
        return f"{value}{unit}"


def create_device_status_table(title: str, status_data: Dict[str, Any]) -> Table:
    """Create a Rich table for device status display.
    
    Args:
        title: Table title
        status_data: Status data dictionary
        
    Returns:
        Rich Table object
    """
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Parameter", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    # Handle different status data formats
    if 'data' in status_data and isinstance(status_data['data'], dict):
        data = status_data['data']
    else:
        data = status_data
    
    # Common display mappings
    display_mappings = {
        'voltage': ('Voltage', 'V', 3),
        'voltage_actual': ('Voltage (Actual)', 'V', 3),
        'voltage_set': ('Voltage (Set)', 'V', 1),
        'current': ('Current', 'A', 3),
        'current_actual': ('Current (Actual)', 'A', 3),
        'current_set': ('Current (Set)', 'A', 2),
        'power': ('Power', 'W', 2),
        'power_actual': ('Power (Actual)', 'W', 3),
        'operating_mode': ('Mode', '', 0),
        'output_enabled': ('Output', '', 0),
        'input_active': ('Input Active', '', 0),
        'connected': ('Connected', '', 0),
        'device_id': ('Device ID', '', 0),
        'timestamp': ('Timestamp', '', 0)
    }
    
    # Add rows based on available data
    for key, value in data.items():
        if key in display_mappings:
            label, unit, precision = display_mappings[key]
            
            if isinstance(value, bool):
                formatted_value = "✓ Yes" if value else "✗ No"
                style = "green" if value else "red"
            elif key == 'timestamp':
                # Format timestamp
                try:
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    formatted_value = dt.strftime("%H:%M:%S")
                except:
                    formatted_value = str(value)
                style = "dim"
            elif key == 'operating_mode':
                formatted_value = str(value)
                style = "yellow" if value in ['CV', 'CC', 'TAPER'] else "white"
            else:
                formatted_value = format_value(value, unit, precision)
                style = "green"
            
            table.add_row(label, formatted_value, style=style)
    
    return table


def create_device_table(load_status: Dict[str, Any], power_status: Dict[str, Any]) -> Table:
    """Create unified device status table for both devices.
    
    Args:
        load_status: BK8520 status data
        power_status: BK9206b status data
        
    Returns:
        Rich Table object
    """
    table = Table(title="Device Status", show_header=True)
    table.add_column("Device", style="cyan", no_wrap=True)
    table.add_column("Connection", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Details", style="white")
    
    # BK8520 Load Tester row
    load_connected = load_status.get('success', False) and load_status.get('data', {}).get('connected', False)
    load_active = load_status.get('data', {}).get('status', {}).get('input_active', False)
    
    load_details = ""
    if load_status.get('data'):
        voltage = load_status['data'].get('voltage', 0)
        current = load_status['data'].get('current', 0)
        load_details = f"V: {voltage:.2f}V, I: {current:.2f}A"
    
    table.add_row(
        "BK8520 Load",
        "✓ Connected" if load_connected else "✗ Disconnected",
        "Active" if load_active else "Idle",
        load_details
    )
    
    # BK9206b Power Supply row
    power_connected = power_status.get('success', True)  # API doesn't have explicit connected field
    power_enabled = power_status.get('output_enabled', False)
    
    power_details = ""
    if isinstance(power_status, dict) and 'voltage_actual' in power_status:
        voltage = power_status.get('voltage_actual', 0)
        current = power_status.get('current_actual', 0)
        mode = power_status.get('operating_mode', 'N/A')
        power_details = f"V: {voltage:.2f}V, I: {current:.3f}A ({mode})"
    
    table.add_row(
        "BK9206b Power",
        "✓ Connected" if power_connected else "✗ Disconnected",
        "Output ON" if power_enabled else "Output OFF",
        power_details
    )
    
    return table


def create_status_table(title: str, data: Dict[str, Any]) -> Table:
    """Create a generic status table for real-time monitoring.
    
    Args:
        title: Table title
        data: Status data dictionary
        
    Returns:
        Rich Table object
    """
    return create_device_status_table(title, data)


def create_test_progress_display(test_status: Dict[str, Any]) -> Panel:
    """Create test progress display panel.
    
    Args:
        test_status: Test status data
        
    Returns:
        Rich Panel object
    """
    if not test_status.get('test_active'):
        return Panel("No active test", title="Test Status", border_style="dim")
    
    phase = test_status.get('phase', 'unknown')
    cycles_completed = test_status.get('cycles_completed', 0)
    total_cycles = test_status.get('total_cycles', 1)
    elapsed = test_status.get('elapsed_time', 0)
    
    # Create progress content
    content = []
    content.append(f"Phase: [yellow]{phase.title()}[/yellow]")
    content.append(f"Cycle: [cyan]{cycles_completed}/{total_cycles}[/cyan]")
    content.append(f"Elapsed: [green]{format_time(elapsed)}[/green]")
    
    if 'current_capacity_ah' in test_status:
        capacity = test_status['current_capacity_ah']
        content.append(f"Capacity: [blue]{capacity:.3f} Ah[/blue]")
    
    if 'current_energy_wh' in test_status:
        energy = test_status['current_energy_wh']
        content.append(f"Energy: [magenta]{energy:.3f} Wh[/magenta]")
    
    panel_content = "\n".join(content)
    
    # Color panel border based on phase
    border_colors = {
        'charging': 'green',
        'discharging': 'red',
        'rest': 'yellow',
        'complete': 'blue',
        'error': 'red',
        'stopped': 'dim'
    }
    border_style = border_colors.get(phase.lower(), 'white')
    
    return Panel(panel_content, title="Battery Test Progress", border_style=border_style)


def create_monitoring_layout() -> Layout:
    """Create layout for real-time monitoring display.
    
    Returns:
        Rich Layout object
    """
    layout = Layout()
    
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    
    layout["header"].update("[bold]BK-Integration Real-Time Monitor[/bold]")
    layout["main"].split_row(
        Layout(name="load"),
        Layout(name="power")
    )
    layout["footer"].update("[dim]Press Ctrl+C to stop monitoring[/dim]")
    
    return layout


def create_test_results_table(results: Dict[str, Any]) -> Table:
    """Create table displaying battery test results.
    
    Args:
        results: Test results data
        
    Returns:
        Rich Table object
    """
    table = Table(title="Battery Test Results", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Unit", style="dim")
    
    # Test summary
    table.add_row("Test ID", results.get('test_id', 'N/A'), "")
    table.add_row("Profile", results.get('profile', {}).get('name', 'N/A'), "")
    table.add_row("Cycles Completed", str(results.get('cycles_completed', 0)), "")
    
    # Timing
    if 'start_time' in results and 'end_time' in results:
        start = results['start_time']
        end = results['end_time']
        if isinstance(start, str) and isinstance(end, str):
            try:
                start_dt = datetime.fromisoformat(start)
                end_dt = datetime.fromisoformat(end)
                duration = (end_dt - start_dt).total_seconds()
                table.add_row("Duration", format_time(duration), "")
            except:
                pass
    
    # Performance metrics
    table.add_row("Capacity", f"{results.get('capacity_ah', 0):.3f}", "Ah")
    table.add_row("Energy", f"{results.get('energy_wh', 0):.3f}", "Wh")
    table.add_row("Efficiency", f"{results.get('efficiency_percent', 0):.1f}", "%")
    
    return table


def create_progress_bar(description: str) -> Progress:
    """Create a Rich progress bar for long operations.
    
    Args:
        description: Progress description
        
    Returns:
        Rich Progress object
    """
    return Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
        console=Console()
    )


def format_device_summary(device_name: str, status: Dict[str, Any]) -> Text:
    """Format device status as a single line summary.
    
    Args:
        device_name: Name of the device
        status: Status data
        
    Returns:
        Rich Text object
    """
    text = Text()
    text.append(f"{device_name}: ", style="bold cyan")
    
    if isinstance(status, dict):
        if 'voltage_actual' in status:  # BK9206b format
            voltage = status.get('voltage_actual', 0)
            current = status.get('current_actual', 0)
            mode = status.get('operating_mode', 'N/A')
            enabled = status.get('output_enabled', False)
            
            text.append(f"{voltage:.2f}V @ {current:.3f}A", style="green")
            text.append(f" ({mode})", style="yellow")
            text.append(" ON" if enabled else " OFF", style="green" if enabled else "red")
            
        elif 'voltage' in status:  # BK8520 format
            voltage = status.get('voltage', 0)
            current = status.get('current', 0)
            power = status.get('power', 0)
            
            text.append(f"{voltage:.2f}V @ {current:.3f}A", style="green")
            text.append(f" ({power:.1f}W)", style="blue")
            
        else:
            text.append("Status unavailable", style="red")
    else:
        text.append("Disconnected", style="red")
    
    return text


def create_configuration_table(config: Dict[str, Any]) -> Table:
    """Create table showing current configuration.
    
    Args:
        config: Configuration data
        
    Returns:
        Rich Table object
    """
    table = Table(title="Configuration", show_header=True)
    table.add_column("Section", style="cyan")
    table.add_column("Parameter", style="blue")
    table.add_column("Value", style="green")
    
    # Device configurations
    if 'devices' in config:
        devices = config['devices']
        for device_name, device_config in devices.items():
            table.add_row(device_name.title(), "URL", device_config.get('device_url', 'N/A'))
            table.add_row("", "Port", str(device_config.get('port', 'N/A')))
            
            if 'serial_port' in device_config:
                table.add_row("", "Serial Port", device_config['serial_port'])
    
    # API configuration
    if 'api' in config:
        api_config = config['api']
        table.add_row("API", "Timeout", f"{api_config.get('timeout', 30)}s")
        table.add_row("", "Retry Count", str(api_config.get('retry_count', 3)))
    
    # Logging configuration
    if 'logging' in config:
        log_config = config['logging']
        table.add_row("Logging", "Level", log_config.get('level', 'INFO'))
        table.add_row("", "File", log_config.get('file', 'bk_integration.log'))
    
    return table


def create_error_panel(error_message: str, suggestion: str = None) -> Panel:
    """Create error display panel.
    
    Args:
        error_message: Error message to display
        suggestion: Optional suggestion for resolution
        
    Returns:
        Rich Panel object
    """
    content = f"[red]{error_message}[/red]"
    
    if suggestion:
        content += f"\n\n[yellow]Suggestion:[/yellow] {suggestion}"
    
    return Panel(content, title="Error", border_style="red")