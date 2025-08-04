# GA BMS CLI Runner Script for Windows PowerShell
# This script activates the virtual environment and runs the BMS CLI

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Check if virtual environment exists
$VenvActivate = Join-Path $ScriptDir "venv\Scripts\Activate.ps1"

if (Test-Path $VenvActivate) {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & $VenvActivate
    Write-Host "Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "Warning: Virtual environment not found at $VenvActivate" -ForegroundColor Yellow
    Write-Host "Please create a virtual environment first with: python -m venv venv" -ForegroundColor Yellow
    Write-Host "Continuing without virtual environment..." -ForegroundColor Yellow
}

# Run the BMS CLI
Write-Host "`nStarting GA BMS Monitor CLI..." -ForegroundColor Cyan
python -m src.cli.bms_cli

# Keep window open if script fails
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nPress any key to exit..." -ForegroundColor Red
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}