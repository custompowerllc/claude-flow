#!/usr/bin/env powershell
# GA Modbus Dashboard - WebSocket Mode
# PowerShell version for Windows 10/11

Write-Host "==============================================="
Write-Host "   GA Modbus Dashboard - WebSocket Mode"
Write-Host "==============================================="
Write-Host ""

# Step 1: Activate virtual environment
Write-Host "[1/3] Activating virtual environment..."
Write-Host "Current directory before activation: $(Get-Location)"
& "venv\Scripts\Activate.ps1"
Write-Host "Current directory after activation: $(Get-Location)"
Write-Host "(check) Virtual environment activated"

# Step 2: Find the most recent CSV file
Write-Host "[2/3] Finding most recent CSV file..."
$csvFiles = Get-ChildItem -Path "logs\*.csv" -ErrorAction Stop | Sort-Object LastWriteTime -Descending
if ($csvFiles.Count -eq 0) {
    Write-Host "ERROR: No CSV files found in logs\ directory"
    exit 1
}
$latestCsv = $csvFiles[0].Name
Write-Host "(check) Found: logs\$latestCsv"

Write-Host ""

# Step 3: Start dashboard with WebSocket
Write-Host "[3/3] Starting dashboard with WebSocket integration..."
Write-Host "Dashboard URL: http://localhost (if web interface available)"
Write-Host "WebSocket Server: ws://localhost:8765"
Write-Host "CSV Data Source: logs\$latestCsv"
Write-Host ""
Write-Host "Press Ctrl+C to stop the dashboard"
Write-Host "==============================================="
Write-Host ""

python "src\modbus_dashboard.py" "logs\$latestCsv" --websocket ws://localhost:8765

Write-Host ""
Write-Host "Dashboard stopped."
