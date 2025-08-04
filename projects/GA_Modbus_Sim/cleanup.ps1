# GA BMS Monitor - Emergency Cleanup Script for Windows PowerShell
#
# This script attempts to send a cleanup signal to the running GA BMS Monitor
# application to gracefully shut it down when the GUI is frozen.
#
# Usage: .\cleanup.ps1
#
# Note: Run PowerShell as Administrator for best results

Write-Host "GA BMS Monitor - Emergency Cleanup" -ForegroundColor Blue
Write-Host "==================================" -ForegroundColor Blue
Write-Host "Platform: Windows (PowerShell)" -ForegroundColor Green
Write-Host ""

# Function to find Python processes
function Find-BMSProcess {
    $pythonProcesses = Get-Process | Where-Object {
        $_.ProcessName -match "python" -and 
        $_.CommandLine -match "(src\.app|src/app\.py|GA_Modbus_Python_App)"
    }
    
    if ($pythonProcesses) {
        return $pythonProcesses[0]
    }
    
    # Try alternative method
    $wmiProcesses = Get-WmiObject Win32_Process | Where-Object {
        $_.Name -match "python" -and
        $_.CommandLine -match "(src\.app|src/app\.py|GA_Modbus_Python_App)"
    }
    
    if ($wmiProcesses) {
        return Get-Process -Id $wmiProcesses[0].ProcessId
    }
    
    return $null
}

Write-Host "Searching for GA BMS Monitor process..." -ForegroundColor Yellow
$process = Find-BMSProcess

if (-not $process) {
    Write-Host "❌ GA BMS Monitor is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure the application is running with one of these commands:"
    Write-Host "  - python -m src.app"
    Write-Host "  - python3 -m src.app"
    Write-Host "  - .\run_app.bat"
    exit 1
}

Write-Host "✓ Found GA BMS Monitor" -ForegroundColor Green
Write-Host "  PID: $($process.Id)" -ForegroundColor Cyan
Write-Host "  Process: $($process.ProcessName)" -ForegroundColor Cyan
Write-Host ""

Write-Host "This will attempt to send a cleanup signal to the application." -ForegroundColor Yellow
Write-Host "The application will:"
Write-Host "  • Stop monitoring"
Write-Host "  • Finish writing CSV data"
Write-Host "  • Close the active session"
Write-Host "  • Disconnect from BMS"
Write-Host "  • Exit gracefully"
Write-Host ""

$response = Read-Host "Continue? [Y/n]"
if ($response -ne "" -and $response -notmatch "^[Yy]$") {
    Write-Host "Cleanup cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host "Attempting cleanup..." -ForegroundColor Yellow

# Try to send Ctrl+C signal using Windows API
try {
    Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    public class Win32 {
        [DllImport("kernel32.dll")]
        public static extern bool GenerateConsoleCtrlEvent(uint dwCtrlEvent, uint dwProcessGroupId);
        
        [DllImport("kernel32.dll")]
        public static extern bool AttachConsole(uint dwProcessId);
        
        [DllImport("kernel32.dll")]
        public static extern bool FreeConsole();
        
        public const uint CTRL_C_EVENT = 0;
        public const uint CTRL_BREAK_EVENT = 1;
    }
"@

    # Try to attach to the process console and send Ctrl+Break
    $attached = [Win32]::AttachConsole($process.Id)
    if ($attached) {
        $sent = [Win32]::GenerateConsoleCtrlEvent([Win32]::CTRL_BREAK_EVENT, 0)
        [Win32]::FreeConsole()
        
        if ($sent) {
            Write-Host "✓ Cleanup signal sent successfully" -ForegroundColor Green
            Write-Host ""
            Write-Host "The application is now performing cleanup operations."
            Write-Host "Check the application console for progress messages."
            
            # Wait and check if process is still running
            Start-Sleep -Seconds 3
            $stillRunning = Get-Process -Id $process.Id -ErrorAction SilentlyContinue
            if ($stillRunning) {
                Write-Host "Application is still running - cleanup in progress..." -ForegroundColor Yellow
            } else {
                Write-Host "✓ Application has exited successfully" -ForegroundColor Green
            }
            
            exit 0
        }
    }
} catch {
    Write-Host "Could not send signal using Windows API" -ForegroundColor Yellow
}

# Fallback: Try graceful termination
Write-Host "Attempting graceful termination..." -ForegroundColor Yellow
try {
    $process.CloseMainWindow()
    if ($process.WaitForExit(5000)) {
        Write-Host "✓ Application closed successfully" -ForegroundColor Green
    } else {
        Write-Host "Application did not respond to close request" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Options:" -ForegroundColor Yellow
        Write-Host "1. Check the application window - it may have a dialog open"
        Write-Host "2. Use Task Manager to end the process"
        Write-Host "3. Force terminate with: Stop-Process -Id $($process.Id) -Force"
    }
} catch {
    Write-Host "❌ Failed to close application gracefully" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}