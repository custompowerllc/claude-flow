#!/usr/bin/env pwsh

# PowerShell script to run Modbus dashboard for serial number 0520 (P3E-Report structure)
# Usage: .\run_dashboard_0520.ps1

$serial_number = "0520"
$rma_number = "8765"

# Prompt for folder selection
Write-Host "Select test type:" -ForegroundColor Cyan
Write-Host "1. Charge tests (test-artifacts/0520/charge/)"
Write-Host "2. Discharge tests (test-artifacts/0520/discharge/)"
Write-Host "3. Main folder (test-artifacts/0520/)"
$folder_choice = Read-Host "Enter your choice (1-3)"

switch ($folder_choice) {
    "1" { $search_path = "test-artifacts\0520\charge" }
    "2" { $search_path = "test-artifacts\0520\discharge" }
    "3" { $search_path = "test-artifacts\0520" }
    default { 
        Write-Host "Invalid choice. Using main folder." -ForegroundColor Yellow
        $search_path = "test-artifacts\0520" 
    }
}

# Find CSV files in selected folder
$csv_files = Get-ChildItem -Path $search_path -Filter "*0520*.csv" | Sort-Object LastWriteTime -Descending

if ($csv_files.Count -eq 0) {
    Write-Host "No CSV files found for serial number 0520 in $search_path" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Show available files
Write-Host "`nAvailable CSV files:" -ForegroundColor Cyan
for ($i = 0; $i -lt $csv_files.Count; $i++) {
    Write-Host "$($i + 1). $($csv_files[$i].Name) - $($csv_files[$i].LastWriteTime)"
}

# Prompt for file selection
$file_choice = Read-Host "`nSelect file number (or press Enter for latest)"
if ([string]::IsNullOrEmpty($file_choice)) {
    $selected_csv = $csv_files[0]
} else {
    $file_index = [int]$file_choice - 1
    if ($file_index -ge 0 -and $file_index -lt $csv_files.Count) {
        $selected_csv = $csv_files[$file_index]
    } else {
        Write-Host "Invalid selection. Using latest file." -ForegroundColor Yellow
        $selected_csv = $csv_files[0]
    }
}

# Prompt for monitoring mode
Write-Host "`nSelect monitoring mode:" -ForegroundColor Cyan
Write-Host "1. Historical view (complete file analysis)"
Write-Host "2. Live monitoring (real-time updates)"
$mode_choice = Read-Host "Enter your choice (1-2)"

$mode_flag = if ($mode_choice -eq "2") { "" } else { "--historical" }
$mode_name = if ($mode_choice -eq "2") { "live monitoring" } else { "historical view" }

Write-Host "`nUsing CSV file: $($selected_csv.Name)" -ForegroundColor Green
Write-Host "Mode: $mode_name" -ForegroundColor Green
Write-Host "Full path: $($selected_csv.FullName)" -ForegroundColor Yellow

# Change to parent directory and run the Modbus dashboard
Set-Location ..

Write-Host "`nLaunching dashboard for serial 0520..." -ForegroundColor Cyan
if ($mode_flag) {
    python src/modbus_dashboard.py "$($selected_csv.FullName)" $mode_flag
} else {
    python src/modbus_dashboard.py "$($selected_csv.FullName)"
}

# Return to P3E-Report directory
Set-Location "P3E-Report"

Read-Host "`nPress Enter to exit"