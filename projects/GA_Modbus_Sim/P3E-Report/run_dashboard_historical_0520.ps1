# PowerShell script to open specific CSV file with Modbus Dashboard in historical mode
# File: P3E-Report\test-artifacts\0520\20250721_181803-0520-8765.csv

# Set error action preference
$ErrorActionPreference = "Stop"

# Get script directory and navigate to project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "GA Modbus Dashboard - Historical CSV Viewer" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Define the CSV file path
$CsvFile = "P3E-Report\test-artifacts\0520\20250721_181803-0520-8765.csv"

# Check if CSV file exists
if (-not (Test-Path $CsvFile)) {
    Write-Host "Error: CSV file not found: $CsvFile" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "CSV File: $CsvFile" -ForegroundColor Green
Write-Host "Mode: Historical View (no real-time updates)" -ForegroundColor Yellow
Write-Host ""

# Check for virtual environment
$VenvPaths = @("venv\Scripts\activate.ps1", "new_venv\Scripts\activate.ps1")
$VenvFound = $false

foreach ($VenvPath in $VenvPaths) {
    if (Test-Path $VenvPath) {
        Write-Host "Activating virtual environment: $VenvPath" -ForegroundColor Green
        & $VenvPath
        $VenvFound = $true
        break
    }
}

if (-not $VenvFound) {
    Write-Host "Warning: No virtual environment found. Trying system Python..." -ForegroundColor Yellow
    Write-Host "Checking for venv at: $($VenvPaths -join ', ')" -ForegroundColor Yellow
}

# Check if Python is available
try {
    $PythonVersion = python --version 2>&1
    Write-Host "Using Python: $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the dashboard with historical mode
Write-Host "Starting Modbus Dashboard in historical mode..." -ForegroundColor Cyan
Write-Host "Close the dashboard window to return to this script." -ForegroundColor Yellow
Write-Host ""

try {
    # Run the dashboard with the specific CSV file in historical mode
    python -m src.modbus_dashboard "$CsvFile" --historical --port "COM3"
    
    Write-Host ""
    Write-Host "Dashboard closed successfully." -ForegroundColor Green
    
} catch {
    Write-Host ""
    Write-Host "Error running dashboard: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure the following dependencies are installed:" -ForegroundColor Yellow
    Write-Host "  pip install matplotlib numpy pandas" -ForegroundColor White
}

Write-Host ""
Read-Host "Press Enter to exit"