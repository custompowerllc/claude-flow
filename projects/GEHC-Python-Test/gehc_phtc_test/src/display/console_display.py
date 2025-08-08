"""
GEHC PHTC RS422 Test Application - Console Display with Rich UI

This module provides the ConsoleDisplay class that handles all console output
using the Rich library for enhanced terminal user interface.
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.status import Status
from rich.syntax import Syntax
from rich import box
from rich.align import Align
from rich.columns import Columns


@dataclass
class CommandResult:
    """Data class for storing command execution results."""
    command: str
    sent_at: datetime
    response: Optional[str]
    success: bool
    error_message: Optional[str]
    duration_ms: float
    retry_count: int = 0


class ConsoleDisplay:
    """Enhanced console display using Rich library for professional terminal UI."""
    
    def __init__(
        self, 
        console: Optional[Console] = None,
        verbose_level: int = 0,
        quiet_mode: bool = False
    ):
        """Initialize the console display.
        
        Args:
            console: Rich Console instance. If None, creates a new one.
            verbose_level: Verbosity level (0=normal, 1=verbose, 2=very verbose, 3=debug)
            quiet_mode: If True, suppresses non-essential output
        """
        self.console = console or Console()
        self.verbose_level = verbose_level
        self.quiet_mode = quiet_mode
        
        # Color scheme
        self.colors = {
            "success": "green",
            "warning": "yellow", 
            "error": "red",
            "info": "blue",
            "data": "cyan",
            "command": "magenta",
            "response": "bright_green"
        }
        
        # Progress tracking
        self.command_count = 0
        self.success_count = 0
        self.error_count = 0
        self.warning_count = 0
    
    def show_startup_info(self, config: Dict[str, Any], serial_port: str) -> None:
        """Display startup information and configuration.
        
        Args:
            config: Configuration dictionary
            serial_port: Serial port being used
        """
        if self.quiet_mode:
            return
        
        # Create configuration table
        config_table = Table(title="Configuration", box=box.ROUNDED)
        config_table.add_column("Parameter", style="bold blue")
        config_table.add_column("Value", style="green")
        
        # Add serial configuration
        serial_config = config.get("serial", {})
        config_table.add_row("Serial Port", serial_port)
        config_table.add_row("Baud Rate", str(serial_config.get("baudrate", "9600")))
        config_table.add_row("Data Bits", str(serial_config.get("bytesize", "8")))
        config_table.add_row("Stop Bits", str(serial_config.get("stopbits", "1")))
        config_table.add_row("Parity", str(serial_config.get("parity", "None")))
        
        # Add communication configuration
        comm_config = config.get("communication", {})
        config_table.add_row("Timeout", f"{comm_config.get('timeout', 30)} seconds")
        config_table.add_row("Retries", str(comm_config.get('retries', 3)))
        
        self.console.print(config_table)
        self.console.print()
    
    def show_message(
        self, 
        message: str, 
        level: str = "info", 
        timestamp: bool = True
    ) -> None:
        """Display a message with appropriate styling.
        
        Args:
            message: Message to display
            level: Message level (info, success, warning, error)
            timestamp: Whether to include timestamp
        """
        if self.quiet_mode and level == "info":
            return
        
        color = self.colors.get(level, "white")
        
        if timestamp:
            ts = datetime.now().strftime("%H:%M:%S")
            prefix = f"[dim]{ts}[/dim] "
        else:
            prefix = ""
        
        # Add appropriate symbols
        symbols = {
            "success": "✅",
            "warning": "⚠️ ",
            "error": "❌",
            "info": "ℹ️ "
        }
        
        symbol = symbols.get(level, "")
        styled_message = f"{prefix}{symbol} [{color}]{message}[/{color}]"
        
        self.console.print(styled_message)
    
    def show_connection_status(self, connected: bool, port: str = "") -> None:
        """Display connection status.
        
        Args:
            connected: Whether connection is established
            port: Serial port name
        """
        if connected:
            status_text = Text("🔗 CONNECTED", style="bold green")
            if port:
                status_text.append(f" to {port}", style="green")
        else:
            status_text = Text("🔌 DISCONNECTED", style="bold red")
        
        panel = Panel(
            Align.center(status_text),
            title="[bold]Connection Status[/bold]",
            border_style="green" if connected else "red",
            padding=(0, 1)
        )
        
        self.console.print(panel)
    
    def show_command_sending(self, command: str) -> None:
        """Display command being sent.
        
        Args:
            command: Command being sent
        """
        if self.verbose_level > 0 or not self.quiet_mode:
            cmd_text = Text("📤 SENDING: ", style="bold magenta")
            cmd_text.append(command, style="cyan")
            self.console.print(cmd_text)
    
    def show_command_response(
        self, 
        response: str, 
        success: bool = True,
        duration_ms: float = 0
    ) -> None:
        """Display command response.
        
        Args:
            response: Response received
            success: Whether the command was successful
            duration_ms: Command execution duration in milliseconds
        """
        if success:
            status_icon = "✅"
            color = "bright_green"
        else:
            status_icon = "❌"
            color = "red"
        
        # Format duration
        if duration_ms > 0:
            duration_str = f" ({duration_ms:.1f}ms)"
        else:
            duration_str = ""
        
        resp_text = Text(f"📥 {status_icon} RESPONSE{duration_str}: ", style=f"bold {color}")
        resp_text.append(response[:100] + "..." if len(response) > 100 else response, style=color)
        
        self.console.print(resp_text)
    
    def create_progress_bar(self, description: str, total: int) -> Progress:
        """Create a progress bar for command execution.
        
        Args:
            description: Description for the progress bar
            total: Total number of items to process
            
        Returns:
            Rich Progress instance
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        )
    
    def execute_test_sequence(
        self, 
        communication, 
        commands: List[Dict[str, Any]],
        timeout: float = 30.0,
        retries: int = 3
    ) -> List[CommandResult]:
        """Execute a sequence of test commands with progress tracking.
        
        Args:
            communication: Communication instance
            commands: List of commands to execute
            timeout: Timeout per command
            retries: Number of retry attempts
            
        Returns:
            List of CommandResult objects
        """
        results = []
        
        with self.create_progress_bar("Executing test sequence", len(commands)) as progress:
            task = progress.add_task("Processing commands...", total=len(commands))
            
            for i, cmd_config in enumerate(commands):
                command = cmd_config.get("command", "")
                expected = cmd_config.get("expected", "")
                description = cmd_config.get("description", f"Command {i+1}")
                
                progress.update(task, description=f"Executing: {description}")
                
                # Execute command with retries
                result = self._execute_single_command(
                    communication, command, expected, timeout, retries
                )
                results.append(result)
                
                # Update counters
                if result.success:
                    self.success_count += 1
                else:
                    self.error_count += 1
                
                self.command_count += 1
                progress.advance(task)
        
        return results
    
    def _execute_single_command(
        self,
        communication,
        command: str,
        expected: str = "",
        timeout: float = 30.0,
        max_retries: int = 3
    ) -> CommandResult:
        """Execute a single command with retry logic.
        
        Args:
            communication: Communication instance
            command: Command to send
            expected: Expected response pattern
            timeout: Timeout in seconds
            max_retries: Maximum retry attempts
            
        Returns:
            CommandResult object
        """
        retry_count = 0
        start_time = datetime.now()
        
        while retry_count <= max_retries:
            try:
                if self.verbose_level > 0:
                    self.show_command_sending(command)
                
                # Send command
                response = communication.send_command(command, timeout)
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                
                # Check if response matches expected (if provided)
                success = True
                error_message = None
                
                if expected and expected not in response:
                    success = False
                    error_message = f"Response does not contain expected text: '{expected}'"
                
                if self.verbose_level > 0:
                    self.show_command_response(response, success, duration_ms)
                
                return CommandResult(
                    command=command,
                    sent_at=start_time,
                    response=response,
                    success=success,
                    error_message=error_message,
                    duration_ms=duration_ms,
                    retry_count=retry_count
                )
                
            except Exception as e:
                retry_count += 1
                error_message = str(e)
                
                if retry_count <= max_retries:
                    if self.verbose_level > 0:
                        self.show_message(f"Command failed, retrying ({retry_count}/{max_retries}): {error_message}", "warning")
                    continue
                else:
                    duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                    return CommandResult(
                        command=command,
                        sent_at=start_time,
                        response=None,
                        success=False,
                        error_message=error_message,
                        duration_ms=duration_ms,
                        retry_count=retry_count - 1
                    )
    
    def show_data_table(
        self, 
        data: List[Dict[str, Any]], 
        title: str = "Data",
        max_rows: int = 50
    ) -> None:
        """Display data in a formatted table.
        
        Args:
            data: List of dictionaries containing data
            title: Table title
            max_rows: Maximum number of rows to display
        """
        if not data:
            self.show_message("No data to display", "warning")
            return
        
        # Create table
        table = Table(title=title, box=box.ROUNDED, show_header=True)
        
        # Add columns based on first row
        first_row = data[0]
        for key in first_row.keys():
            table.add_column(key.replace("_", " ").title(), style="cyan")
        
        # Add rows (limit to max_rows)
        for i, row in enumerate(data[:max_rows]):
            table.add_row(*[str(value) for value in row.values()])
        
        if len(data) > max_rows:
            table.add_row(*["..." for _ in first_row.keys()], style="dim")
            table.add_row(*[f"({len(data) - max_rows} more rows)" for _ in range(len(first_row.keys()) - 1)] + [""], style="dim")
        
        self.console.print(table)
    
    def show_final_summary(self, results: List[CommandResult]) -> None:
        """Display final test summary with statistics.
        
        Args:
            results: List of CommandResult objects
        """
        if self.quiet_mode:
            return
        
        # Calculate statistics
        total_commands = len(results)
        successful_commands = sum(1 for r in results if r.success)
        failed_commands = total_commands - successful_commands
        avg_duration = sum(r.duration_ms for r in results) / total_commands if results else 0
        total_duration = sum(r.duration_ms for r in results)
        
        # Create summary table
        summary_table = Table(title="Test Execution Summary", box=box.DOUBLE_EDGE)
        summary_table.add_column("Metric", style="bold blue")
        summary_table.add_column("Value", style="bold")
        summary_table.add_column("Status", justify="center")
        
        # Add rows with status indicators
        summary_table.add_row("Total Commands", str(total_commands), "📊")
        summary_table.add_row(
            "Successful", 
            str(successful_commands), 
            "✅" if successful_commands == total_commands else "⚠️"
        )
        summary_table.add_row(
            "Failed", 
            str(failed_commands), 
            "❌" if failed_commands > 0 else "✅"
        )
        summary_table.add_row(
            "Success Rate", 
            f"{(successful_commands/total_commands*100):.1f}%" if total_commands > 0 else "N/A",
            "✅" if successful_commands == total_commands else "❌"
        )
        summary_table.add_row("Average Duration", f"{avg_duration:.1f}ms", "⏱️")
        summary_table.add_row("Total Duration", f"{total_duration:.1f}ms", "⏱️")
        
        self.console.print()
        self.console.print(summary_table)
        
        # Show failed commands if any
        if failed_commands > 0 and self.verbose_level > 0:
            self.console.print()
            failed_table = Table(title="Failed Commands", box=box.ROUNDED)
            failed_table.add_column("Command", style="red")
            failed_table.add_column("Error", style="yellow")
            failed_table.add_column("Retries", style="dim")
            
            for result in results:
                if not result.success:
                    failed_table.add_row(
                        result.command,
                        result.error_message or "Unknown error",
                        str(result.retry_count)
                    )
            
            self.console.print(failed_table)
    
    def save_results(
        self, 
        results: List[CommandResult], 
        filename: str, 
        format_type: str = "txt"
    ) -> None:
        """Save test results to file.
        
        Args:
            results: List of CommandResult objects
            filename: Output filename
            format_type: Output format (txt, json, csv)
        """
        try:
            output_path = Path(filename)
            
            if format_type == "json":
                data = []
                for result in results:
                    data.append({
                        "command": result.command,
                        "sent_at": result.sent_at.isoformat(),
                        "response": result.response,
                        "success": result.success,
                        "error_message": result.error_message,
                        "duration_ms": result.duration_ms,
                        "retry_count": result.retry_count
                    })
                
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2)
            
            elif format_type == "csv":
                with open(output_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "Command", "Sent At", "Response", "Success", 
                        "Error Message", "Duration (ms)", "Retry Count"
                    ])
                    
                    for result in results:
                        writer.writerow([
                            result.command,
                            result.sent_at.isoformat(),
                            result.response,
                            result.success,
                            result.error_message,
                            result.duration_ms,
                            result.retry_count
                        ])
            
            else:  # txt format
                with open(output_path, 'w') as f:
                    f.write("GEHC PHTC RS422 Test Results\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for i, result in enumerate(results, 1):
                        f.write(f"Command {i}: {result.command}\n")
                        f.write(f"Status: {'SUCCESS' if result.success else 'FAILED'}\n")
                        f.write(f"Duration: {result.duration_ms:.1f}ms\n")
                        f.write(f"Response: {result.response}\n")
                        if result.error_message:
                            f.write(f"Error: {result.error_message}\n")
                        f.write("-" * 30 + "\n\n")
            
            self.show_message(f"Results saved to {output_path}", "success")
            
        except Exception as e:
            self.show_message(f"Failed to save results: {e}", "error")
    
    def show_interactive_help(self) -> None:
        """Display help for interactive mode."""
        help_table = Table(title="Interactive Mode Commands", box=box.ROUNDED)
        help_table.add_column("Command", style="bold cyan")
        help_table.add_column("Description", style="white")
        
        help_table.add_row("help", "Show this help message")
        help_table.add_row("status", "Show connection status")
        help_table.add_row("send <message>", "Send a message to the device")
        help_table.add_row("quit, exit, q", "Exit the application")
        
        self.console.print(help_table)
    
    def send_command_interactive(self, communication, message: str) -> None:
        """Send a command in interactive mode.
        
        Args:
            communication: Communication instance
            message: Message to send
        """
        try:
            with Status("Sending command...", console=self.console):
                response = communication.send_command(message)
            
            self.show_command_response(response, True)
            
        except Exception as e:
            self.show_message(f"Failed to send command: {e}", "error")