#!/usr/bin/env python3
"""
GEHC PHTC RS422 CLI Demo Script

This script demonstrates the CLI application features without requiring
actual hardware. It shows the Rich UI components in action.
"""

import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from rich import box
from rich.align import Align
from datetime import datetime


def demo_console_display():
    """Demonstrate the ConsoleDisplay features."""
    console = Console()
    
    # Show startup banner
    banner_text = Text()
    banner_text.append("GEHC PHTC RS422 Test Application\n", style="bold cyan")
    banner_text.append("Version 1.0.0", style="dim")
    
    panel = Panel(
        banner_text,
        title="[bold blue]Welcome[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )
    
    console.print(panel)
    console.print()
    
    # Demo configuration table
    config_table = Table(title="Configuration", box=box.ROUNDED)
    config_table.add_column("Parameter", style="bold blue")
    config_table.add_column("Value", style="green")
    
    config_table.add_row("Serial Port", "/dev/ttyUSB0 (Demo)")
    config_table.add_row("Baud Rate", "9600")
    config_table.add_row("Data Bits", "8")
    config_table.add_row("Stop Bits", "1")
    config_table.add_row("Parity", "None")
    config_table.add_row("Timeout", "30.0 seconds")
    config_table.add_row("Retries", "3")
    
    console.print(config_table)
    console.print()
    
    # Demo connection status
    status_text = Text("🔗 CONNECTED", style="bold green")
    status_text.append(" to /dev/ttyUSB0", style="green")
    
    status_panel = Panel(
        Align.center(status_text),
        title="[bold]Connection Status[/bold]",
        border_style="green",
        padding=(0, 1)
    )
    
    console.print(status_panel)
    
    # Demo messages at different levels
    ts = datetime.now().strftime("%H:%M:%S")
    console.print(f"[dim]{ts}[/dim] ✅ [green]System initialized successfully[/green]")
    console.print(f"[dim]{ts}[/dim] ℹ️  [blue]Configuration loaded from default.json[/blue]")
    console.print(f"[dim]{ts}[/dim] ℹ️  [blue]Serial port opened with RTS/CTS flow control[/blue]")
    console.print(f"[dim]{ts}[/dim] ⚠️  [yellow]Device may not respond - demo mode active[/yellow]")
    
    # Demo command sending/receiving with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Executing test sequence", total=4)
        
        commands = [
            ("STATUS", "OK", True, 45.2),
            ("VERSION", "GEHC-PHTC-V2.1.0", True, 32.8),
            ("CONFIG", "CONFIG_DATA_...", True, 89.1),
            ("INVALID", "ERROR: Unknown command", False, 128.5)
        ]
        
        for i, (cmd, resp, success, duration) in enumerate(commands):
            progress.update(task, description=f"Executing: {cmd}")
            
            # Show command being sent
            cmd_text = Text("📤 SENDING: ", style="bold magenta")
            cmd_text.append(cmd, style="cyan")
            console.print(cmd_text)
            
            time.sleep(0.3)  # Simulate command execution
            
            # Show response
            if success:
                status_icon = "✅"
                color = "bright_green"
            else:
                status_icon = "❌"
                color = "red"
            
            resp_text = Text(f"📥 {status_icon} RESPONSE ({duration:.1f}ms): ", style=f"bold {color}")
            resp_text.append(resp, style=color)
            console.print(resp_text)
            console.print()
            
            progress.advance(task)
    
    # Demo results table
    results_table = Table(title="Test Execution Results", box=box.ROUNDED)
    results_table.add_column("Command", style="cyan")
    results_table.add_column("Response", style="white")
    results_table.add_column("Duration", style="yellow")
    results_table.add_column("Status", justify="center")
    
    results_table.add_row("STATUS", "OK", "45.2ms", "✅")
    results_table.add_row("VERSION", "V2.1.0", "32.8ms", "✅")
    results_table.add_row("CONFIG", "CONFIG_DATA", "89.1ms", "✅")
    results_table.add_row("INVALID", "ERROR", "128.5ms", "❌")
    
    console.print(results_table)
    
    # Demo summary
    summary_table = Table(title="Test Execution Summary", box=box.DOUBLE_EDGE)
    summary_table.add_column("Metric", style="bold blue")
    summary_table.add_column("Value", style="bold")
    summary_table.add_column("Status", justify="center")
    
    summary_table.add_row("Total Commands", "4", "📊")
    summary_table.add_row("Successful", "3", "✅")
    summary_table.add_row("Failed", "1", "❌")
    summary_table.add_row("Success Rate", "75.0%", "⚠️")
    summary_table.add_row("Average Duration", "73.9ms", "⏱️")
    summary_table.add_row("Total Duration", "295.6ms", "⏱️")
    
    console.print()
    console.print(summary_table)
    
    # Demo interactive help
    help_table = Table(title="Interactive Mode Commands", box=box.ROUNDED)
    help_table.add_column("Command", style="bold cyan")
    help_table.add_column("Description", style="white")
    
    help_table.add_row("help", "Show this help message")
    help_table.add_row("status", "Show connection status")
    help_table.add_row("send <message>", "Send a message to the device")
    help_table.add_row("quit, exit, q", "Exit the application")
    
    console.print()
    console.print(help_table)


def demo_cli_help():
    """Show CLI help and available options."""
    console = Console()
    
    console.print("[bold green]GEHC PHTC RS422 CLI Application - Feature Demo[/bold green]\n")
    
    console.print("[bold]Available CLI Features:[/bold]")
    features = [
        "Rich-based terminal UI with colors and formatting",
        "Serial port auto-detection and configuration", 
        "Multiple test profiles (default, quick, full, custom)",
        "Interactive mode with live command execution",
        "Progress tracking with visual progress bars",
        "Comprehensive error handling and retry logic",
        "Multiple output formats (TXT, JSON, CSV)",
        "Configurable timeouts and retry attempts",
        "Real-time status updates and connection monitoring",
        "Professional data tables and summary reports"
    ]
    
    for i, feature in enumerate(features, 1):
        console.print(f"  {i:2d}. {feature}")
    
    console.print(f"\n[bold]Example Commands:[/bold]")
    examples = [
        "python -m gehc_phtc_test.src.main --help",
        "python -m gehc_phtc_test.src.main --port /dev/ttyUSB0 --test-profile quick",
        "python -m gehc_phtc_test.src.main --config config/custom.json --verbose",
        "python -m gehc_phtc_test.src.main --interactive --port COM3",
        "python -m gehc_phtc_test.src.main --output-file results.json --format json",
        "python -m gehc_phtc_test.src.main --test-profile full --timeout 60 --retries 5"
    ]
    
    for example in examples:
        console.print(f"  [cyan]{example}[/cyan]")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "display":
        demo_console_display()
    elif len(sys.argv) > 1 and sys.argv[1] == "help":
        demo_cli_help()
    else:
        console = Console()
        console.print("[bold red]GEHC PHTC RS422 CLI Demo[/bold red]")
        console.print("\nUsage:")
        console.print("  [cyan]python demo_cli.py display[/cyan] - Show Rich UI components demo")
        console.print("  [cyan]python demo_cli.py help[/cyan]    - Show CLI features and examples")
        console.print("\nTo test the actual CLI:")
        console.print("  [cyan]source venv/bin/activate[/cyan]")
        console.print("  [cyan]python -m gehc_phtc_test.src.main --help[/cyan]")