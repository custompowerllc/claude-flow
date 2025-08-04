#!/usr/bin/env pwsh

# PowerShell script to run standalone Modbus logger for serial number 0561 (P3E-Report structure)
# Usage: .\run_standalone_0561.ps1

$serial_number = "0561"
$rma_number = "8765"
$COM_PORT = "COM34"  # Default COM port - change as needed

# Get available COM ports
Write-Host "Available COM ports:" -ForegroundColor Yellow
try {
    $ports = [System.IO.Ports.SerialPort]::getportnames()
    foreach ($port in $ports) {
        if ($port -eq $COM_PORT) {
            Write-Host "  $port (selected)" -ForegroundColor Green
        } else {
            Write-Host "  $port" -ForegroundColor White
        }
    }
}
catch {
    Write-Host "Could not enumerate COM ports" -ForegroundColor Red
}

# Create output directory structure
$output_base = "test-artifacts\0561"
if (-not (Test-Path $output_base)) {
    New-Item -ItemType Directory -Path $output_base -Force | Out-Null
    Write-Host "Created directory: $output_base" -ForegroundColor Green
}

# Create charge and discharge subdirectories
New-Item -ItemType Directory -Path "$output_base\charge" -Force | Out-Null
New-Item -ItemType Directory -Path "$output_base\discharge" -Force | Out-Null
New-Item -ItemType Directory -Path "$output_base\screenshots" -Force | Out-Null

Write-Host "Directory structure ready for pack 0561" -ForegroundColor Green
Write-Host ""

# Prompt for test type
Write-Host "Select test type:" -ForegroundColor Cyan
Write-Host "1. Charge test (output to charge folder)"
Write-Host "2. Discharge test (output to discharge folder)"
Write-Host "3. General test (output to main folder)"
$choice = Read-Host "Enter choice (1-3, default: 3)"

switch ($choice) {
    "1" { $output_path = "$output_base\charge" }
    "2" { $output_path = "$output_base\discharge" }
    default { $output_path = $output_base }
}

Write-Host "Output will be saved to: $output_path" -ForegroundColor Yellow
Write-Host ""

# Change to parent directory and run the standalone Modbus logger
Set-Location ..

Write-Host "Starting standalone logger for pack 0561..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop logging" -ForegroundColor Yellow

python src/modbus_standalone_logger.py --port $COM_PORT --serial-number $serial_number --rma-number $rma_number --output-path $output_path

# Return to P3E-Report directory
Set-Location "P3E-Report"

Write-Host ""
Write-Host "Logging session completed for pack 0561" -ForegroundColor Green
Read-Host "Press Enter to exit"