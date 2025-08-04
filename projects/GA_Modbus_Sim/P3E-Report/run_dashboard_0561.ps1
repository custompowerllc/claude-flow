#!/usr/bin/env pwsh

# PowerShell script to run Modbus dashboard for serial number 0561 (P3E-Report structure)
# Usage: .\run_dashboard_0561.ps1

$serial_number = "0561"
$rma_number = "8765"

# Find the most recent CSV file for 0561 in P3E-Report/test-artifacts
$csv_files = Get-ChildItem -Path "test-artifacts\0561" -Filter "*0561*.csv" -Recurse | Sort-Object LastWriteTime -Descending

if ($csv_files.Count -eq 0) {
    Write-Host "No CSV files found for serial number 0561 in P3E-Report/test-artifacts/0561" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

$latest_csv = $csv_files[0].FullName
Write-Host "Using latest CSV file: $($csv_files[0].Name)" -ForegroundColor Green
Write-Host "Full path: $latest_csv" -ForegroundColor Yellow

# Change to parent directory and run the Modbus dashboard
Set-Location ..

Write-Host "Launching dashboard for serial 0561..." -ForegroundColor Cyan
python src/modbus_dashboard.py "$latest_csv" --historical

# Return to P3E-Report directory
Set-Location "P3E-Report"

Read-Host "Press Enter to exit"