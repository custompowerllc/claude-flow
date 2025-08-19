#!/usr/bin/env pwsh

# P3E Test Manager - Consolidated script for dashboard and standalone logger
# Usage: .\p3e_test_manager.ps1

# Settings file path
$SettingsFile = "p3e_test_manager_settings.json"

# Function to load settings from JSON file
function Load-Settings {
    if (Test-Path $SettingsFile) {
        try {
            $settings = Get-Content $SettingsFile -Raw | ConvertFrom-Json
            return $settings
        } catch {
            Write-Host "Warning: Could not load settings file. Using defaults." -ForegroundColor Yellow
        }
    }
    
    # Return default settings
    return @{
        LastSerialNumber = "0520"
        LastTestType = "charge"
        LastComPort = "COM3"
        LastOperation = "1"
        LastMonitoringMode = "1"
    }
}

# Function to save settings to JSON file
function Save-Settings {
    param($settings)
    try {
        $settings | ConvertTo-Json | Set-Content $SettingsFile
        Write-Host "Settings saved successfully." -ForegroundColor Green
    } catch {
        Write-Host "Warning: Could not save settings." -ForegroundColor Yellow
    }
}

# Function to display header
function Show-Header {
    Clear-Host
    Write-Host "===============================================" -ForegroundColor Cyan
    Write-Host "         P3E Battery Test Manager              " -ForegroundColor Cyan
    Write-Host "===============================================" -ForegroundColor Cyan
    Write-Host ""
}

# Function to get serial number
function Get-SerialNumber {
    param($settings)
    
    Write-Host "Available pack serial numbers:" -ForegroundColor Yellow
    Write-Host "  0515, 0518, 0520, 0533, 0535, 0561, 0564, 0583"
    Write-Host ""
    Write-Host "Last used: $($settings.LastSerialNumber)" -ForegroundColor Green
    $serial = Read-Host "Enter pack serial number (press Enter for last used: $($settings.LastSerialNumber))"
    
    # Use last used if empty
    if ([string]::IsNullOrEmpty($serial)) {
        $serial = $settings.LastSerialNumber
        Write-Host "Using last used: $serial" -ForegroundColor Yellow
    }
    
    # Validate serial number
    if ($serial -notmatch '^\d{4}$') {
        Write-Host "Invalid serial number format. Using last used: $($settings.LastSerialNumber)" -ForegroundColor Red
        return $settings.LastSerialNumber
    }
    
    # Update settings
    $settings.LastSerialNumber = $serial
    return $serial
}

# Function to get test type
function Get-TestType {
    param($settings)
    
    Write-Host "`nSelect test type:" -ForegroundColor Yellow
    Write-Host "1. Charge test"
    Write-Host "2. Discharge test"
    Write-Host "3. General test (root folder)"
    
    # Show last used choice
    $lastChoice = switch ($settings.LastTestType) {
        "charge" { "1" }
        "discharge" { "2" }
        default { "3" }
    }
    Write-Host "Last used: $lastChoice ($($settings.LastTestType))" -ForegroundColor Green
    $choice = Read-Host "Enter choice (press Enter for last used: $lastChoice)"
    
    # Use last used if empty
    if ([string]::IsNullOrEmpty($choice)) {
        $choice = $lastChoice
        Write-Host "Using last used: $choice ($($settings.LastTestType))" -ForegroundColor Yellow
    }
    
    $testType = switch ($choice) {
        "1" { "charge" }
        "2" { "discharge" }
        default { "root" }
    }
    
    # Update settings
    $settings.LastTestType = $testType
    return $testType
}

# Function to run dashboard
function Run-Dashboard {
    param($serial, $testType, $settings)
    
    $base_path = "test-artifacts\$serial"
    $search_path = switch ($testType) {
        "charge" { "$base_path\charge" }
        "discharge" { "$base_path\discharge" }
        default { $base_path }
    }
    
    # Check if directory exists
    if (-not (Test-Path $search_path)) {
        Write-Host "Directory not found: $search_path" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        return
    }
    
    # Find CSV files
    $csv_files = Get-ChildItem -Path $search_path -Filter "*$serial*.csv" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
    
    if ($csv_files.Count -eq 0) {
        Write-Host "No CSV files found in $search_path" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        return
    }
    
    # Ask for monitoring mode
    Write-Host "`nSelect monitoring mode:" -ForegroundColor Yellow
    Write-Host "1. Historical view (analyze complete file)"
    Write-Host "2. Real-time monitoring (watch live updates)"
    Write-Host "Last used: $($settings.LastMonitoringMode)" -ForegroundColor Green
    $mode_choice = Read-Host "Enter choice (press Enter for last used: $($settings.LastMonitoringMode))"
    
    # Use last used if empty
    if ([string]::IsNullOrEmpty($mode_choice)) {
        $mode_choice = $settings.LastMonitoringMode
        Write-Host "Using last used: $mode_choice" -ForegroundColor Yellow
    }
    
    # Update settings
    $settings.LastMonitoringMode = $mode_choice
    
    $selected_csv = $null
    
    if ($mode_choice -eq "1") {
        # Historical mode - show list of files
        Write-Host "`nAvailable CSV files:" -ForegroundColor Cyan
        for ($i = 0; $i -lt $csv_files.Count; $i++) {
            $file = $csv_files[$i]
            Write-Host "$($i + 1). $($file.Name) - Modified: $($file.LastWriteTime)"
        }
        
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
        $mode_flag = "--historical"
    } else {
        # Real-time mode - use latest file
        $selected_csv = $csv_files[0]
        $mode_flag = ""
    }
    
    Write-Host "`nSelected file: $($selected_csv.Name)" -ForegroundColor Green
    Write-Host "Full path: $($selected_csv.FullName)" -ForegroundColor Gray
    
    # Change to parent directory and run dashboard
    $current_dir = Get-Location
    Write-Host "Current directory: $current_dir" -ForegroundColor Gray
    
    Set-Location ..
    $new_dir = Get-Location
    Write-Host "Changed to directory: $new_dir" -ForegroundColor Gray
    
    Write-Host "`nLaunching dashboard..." -ForegroundColor Cyan
    
    # Check if virtual environment exists and activate it
    $venv_activate = $null
    if (Test-Path "venv\Scripts\activate.ps1") {
        $venv_activate = ".\venv\Scripts\activate.ps1"
        Write-Host "Found virtual environment at: venv" -ForegroundColor Green
    } elseif (Test-Path "new_venv\Scripts\activate.ps1") {
        $venv_activate = ".\new_venv\Scripts\activate.ps1"
        Write-Host "Found virtual environment at: new_venv" -ForegroundColor Green
    }
    
    # Build command with session type
    $session_type_flag = ""
    if ($testType -ne "root") {
        $session_type_flag = "--session-type $testType"
    }
    
    if ($mode_flag) {
        $cmd = "python -m src.modbus_dashboard `"$($selected_csv.FullName)`" $mode_flag $session_type_flag"
    } else {
        $cmd = "python -m src.modbus_dashboard `"$($selected_csv.FullName)`" $session_type_flag"
    }
    
    Write-Host "Command: $cmd" -ForegroundColor Gray
    
    try {
        if ($venv_activate) {
            # Run with virtual environment
            Write-Host "Activating virtual environment..." -ForegroundColor Yellow
            & $venv_activate
        }
        
        # Run the dashboard
        Invoke-Expression $cmd
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "`nDashboard exited with error code: $LASTEXITCODE" -ForegroundColor Red
        }
    } catch {
        Write-Host "`nError launching dashboard: $_" -ForegroundColor Red
        Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    }
    
    # Return to P3E-Report directory
    Set-Location $current_dir
}

# Function to test file discovery
function Test-FileDiscovery {
    Write-Host "=== Testing File Discovery ===" -ForegroundColor Cyan
    $test_serials = @("0520", "0561")
    foreach ($serial in $test_serials) {
        Write-Host "`nTesting serial ${serial}:" -ForegroundColor Yellow
        foreach ($test_type in @("charge", "discharge")) {
            $csv_path = "release/$serial/$test_type"
            Write-Host "  Path: $csv_path" -ForegroundColor Gray
            if (Test-Path $csv_path) {
                $csv_files = Get-ChildItem -Path $csv_path -Filter "*$serial*.csv" -ErrorAction SilentlyContinue
                Write-Host "    Directory exists, found $($csv_files.Count) CSV files" -ForegroundColor Green
                if ($csv_files.Count -gt 0) {
                    Write-Host "    Files: $($csv_files.Name -join ', ')" -ForegroundColor Green
                }
            } else {
                Write-Host "    Directory does not exist" -ForegroundColor Red
            }
        }
    }
    Write-Host "`n=== End Test ===" -ForegroundColor Cyan
}

# Function to generate screenshots for all packs
function Generate-AllScreenshots {
    # Use the correct test-artifacts path in GA_Modbus_Python_App
    $test_artifacts_path = "../../GA_Modbus_Python_App/P3E-Report/test-artifacts"
    
    # Debug: Show current directory and test-artifacts path
    $current_location = Get-Location
    Write-Host "Working from directory: $current_location" -ForegroundColor Gray
    
    # Check if test-artifacts directory exists
    if (-not (Test-Path $test_artifacts_path)) {
        Write-Host "Test-artifacts directory not found: $test_artifacts_path" -ForegroundColor Red
        Write-Host "Full path would be: $(Join-Path $current_location $test_artifacts_path)" -ForegroundColor Gray
        Read-Host "Press Enter to exit"
        return
    }
    
    Write-Host "`nGenerating dashboard screenshots for all packs..." -ForegroundColor Cyan
    Write-Host "This will create screenshots for both charge and discharge sessions using the latest CSV files." -ForegroundColor Yellow
    Write-Host "Screenshots will capture cell voltages when cell delta is at its peak value.`n" -ForegroundColor Yellow
    
    # Get all serial number directories
    $serial_dirs = Get-ChildItem -Path $test_artifacts_path -Directory | Where-Object { $_.Name -match '^\d{4}$' }
    
    if ($serial_dirs.Count -eq 0) {
        Write-Host "No serial number directories found in $test_artifacts_path" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        return
    }
    
    $current_dir = Get-Location
    Set-Location ..
    
    # Check if virtual environment exists
    $venv_activate = $null
    if (Test-Path "venv\Scripts\activate.ps1") {
        $venv_activate = ".\venv\Scripts\activate.ps1"
        Write-Host "Found virtual environment at: venv" -ForegroundColor Green
    } elseif (Test-Path "new_venv\Scripts\activate.ps1") {
        $venv_activate = ".\new_venv\Scripts\activate.ps1"
        Write-Host "Found virtual environment at: new_venv" -ForegroundColor Green
    }
    
    if ($venv_activate) {
        Write-Host "Activating virtual environment..." -ForegroundColor Yellow
        & $venv_activate
    }
    
    foreach ($serial_dir in $serial_dirs) {
        $serial = $serial_dir.Name
        Write-Host "Processing pack $serial..." -ForegroundColor Cyan
        
        # Process charge and discharge
        foreach ($test_type in @("charge", "discharge")) {
            $csv_path = "$test_artifacts_path/$serial/$test_type"
            $screenshots_path = "$test_artifacts_path/$serial/screenshots"
            
            # Find latest CSV file
            if (Test-Path $csv_path) {
                $csv_files = Get-ChildItem -Path $csv_path -Filter "*$serial*.csv" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
                Write-Host "    Found $($csv_files.Count) CSV files in $csv_path" -ForegroundColor Gray
                if ($csv_files.Count -gt 0) {
                    Write-Host "    Latest file: $($csv_files[0].Name)" -ForegroundColor Gray
                    $latest_csv = $csv_files[0]
                    $screenshot_name = "$serial-$test_type.png"
                    $screenshot_path = "$screenshots_path/$screenshot_name"
                    
                    Write-Host "  Generating $test_type screenshot: $screenshot_name" -ForegroundColor Green
                    Write-Host "    CSV file: $($latest_csv.FullName)" -ForegroundColor Gray
                    Write-Host "    Screenshot path: $screenshot_path" -ForegroundColor Gray
                    
                    # Build command with session type and screenshot export (headless mode for faster processing)
                    $cmd = "python -m src.modbus_dashboard `"$($latest_csv.FullName)`" --historical --session-type $test_type --export-screenshot `"$screenshot_path`" --no-gui"
                    Write-Host "    Command: $cmd" -ForegroundColor Gray
                    
                    try {
                        # Run the dashboard with screenshot export
                        Write-Host "    Executing dashboard command..." -ForegroundColor Gray
                        Invoke-Expression $cmd
                        
                        if ($LASTEXITCODE -eq 0) {
                            Write-Host "    ✓ Screenshot saved: $screenshot_path" -ForegroundColor Green
                        } else {
                            Write-Host "    ✗ Failed to generate screenshot for $serial $test_type (exit code: $LASTEXITCODE)" -ForegroundColor Red
                        }
                    } catch {
                        Write-Host "    ✗ Error generating screenshot: $_" -ForegroundColor Red
                    }
                } else {
                    # Only show warning if directory exists but no CSV files found
                    Write-Host "  ⚠ No CSV files found in $csv_path" -ForegroundColor Yellow
                }
            }
            # Remove the "Directory not found" warning since empty directories are normal
        }
        
        Write-Host ""
    }
    
    # Return to P3E-Report directory
    Set-Location $current_dir
    
    Write-Host "Screenshot generation completed!" -ForegroundColor Green
    Write-Host "Screenshots saved in respective {serial-number}/screenshots/ folders" -ForegroundColor Cyan
    Write-Host "`nSummary of generated screenshots:" -ForegroundColor Yellow
    
    # Show summary of generated screenshots
    foreach ($serial_dir in $serial_dirs) {
        $serial = $serial_dir.Name
        $screenshots_path = "$test_artifacts_path/$serial/screenshots"
        if (Test-Path $screenshots_path) {
            $screenshots = Get-ChildItem -Path $screenshots_path -Filter "$serial-*.png" -ErrorAction SilentlyContinue
            if ($screenshots.Count -gt 0) {
                Write-Host "  $serial - $($screenshots.Count) screenshot(s): $($screenshots.Name -join ', ')" -ForegroundColor Green
            }
        }
    }
}

# Function to run standalone logger
function Run-StandaloneLogger {
    param($serial, $testType, $settings)
    
    $rma_number = "8765"  # Default RMA number
    
    # Get COM port
    Write-Host "`nAvailable COM ports:" -ForegroundColor Yellow
    try {
        $ports = [System.IO.Ports.SerialPort]::getportnames()
        foreach ($port in $ports) {
            Write-Host "  $port" -ForegroundColor White
        }
    } catch {
        Write-Host "Could not enumerate COM ports" -ForegroundColor Red
    }
    
    Write-Host "Last used: $($settings.LastComPort)" -ForegroundColor Green
    $COM_PORT = Read-Host "`nEnter COM port (press Enter for last used: $($settings.LastComPort))"
    if ([string]::IsNullOrEmpty($COM_PORT)) {
        $COM_PORT = $settings.LastComPort
        Write-Host "Using last used: $COM_PORT" -ForegroundColor Yellow
    }
    
    # Update settings
    $settings.LastComPort = $COM_PORT
    
    # Set output path based on test type
    $output_base = "P3E-Report\test-artifacts\$serial"
    $output_path = switch ($testType) {
        "charge" { "$output_base\charge" }
        "discharge" { "$output_base\discharge" }
        default { $output_base }
    }
    
    # Create directories if needed
    if (-not (Test-Path $output_base)) {
        New-Item -ItemType Directory -Path $output_base -Force | Out-Null
    }
    New-Item -ItemType Directory -Path "$output_base\charge" -Force | Out-Null
    New-Item -ItemType Directory -Path "$output_base\discharge" -Force | Out-Null
    New-Item -ItemType Directory -Path "$output_base\screenshots" -Force | Out-Null
    
    Write-Host "`nOutput will be saved to: $output_path" -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop logging" -ForegroundColor Yellow
    
    # Change to parent directory and run logger
    $current_dir = Get-Location
    Set-Location ..
    
    Write-Host "`nStarting standalone logger for pack $serial..." -ForegroundColor Cyan
    
    # Check if virtual environment exists
    $venv_activate = $null
    if (Test-Path "venv\Scripts\activate.ps1") {
        $venv_activate = ".\venv\Scripts\activate.ps1"
    } elseif (Test-Path "new_venv\Scripts\activate.ps1") {
        $venv_activate = ".\new_venv\Scripts\activate.ps1"
    }
    
    try {
        if ($venv_activate) {
            Write-Host "Activating virtual environment..." -ForegroundColor Yellow
            & $venv_activate
        }
        
        python -m src.modbus_standalone_logger --port $COM_PORT --serial-number $serial --rma-number $rma_number --output-path $output_path
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "`nLogger exited with error code: $LASTEXITCODE" -ForegroundColor Red
        }
    } catch {
        Write-Host "`nError launching logger: $_" -ForegroundColor Red
    }
    
    # Return to P3E-Report directory
    Set-Location $current_dir
    
    Write-Host "`nLogging session completed" -ForegroundColor Green
}

# Main script
Show-Header

# Load settings
$settings = Load-Settings

# Select operation mode
Write-Host "Select operation:" -ForegroundColor Yellow
Write-Host "1. Run Dashboard (view CSV data)"
Write-Host "2. Run Standalone Logger (collect new data)"
Write-Host "3. Generate All Screenshots (batch screenshot generation)"
Write-Host "4. Test File Discovery (debug)"
Write-Host "5. Exit"
Write-Host "Last used: $($settings.LastOperation)" -ForegroundColor Green
$operation = Read-Host "`nEnter choice (press Enter for last used: $($settings.LastOperation))"

# Use last used if empty
if ([string]::IsNullOrEmpty($operation)) {
    $operation = $settings.LastOperation
    Write-Host "Using last used: $operation" -ForegroundColor Yellow
}

# Update settings
$settings.LastOperation = $operation

if ($operation -eq "5") {
    Write-Host "Exiting..." -ForegroundColor Gray
    exit 0
}

# Skip serial number and test type selection for screenshot generation (option 3) and test (option 4)
if ($operation -eq "3" -or $operation -eq "4") {
    $serial_number = $null
    $test_type = $null
} else {
    # Get serial number
    $serial_number = Get-SerialNumber -settings $settings

    # Get test type
    $test_type = Get-TestType -settings $settings
}

# Execute selected operation
switch ($operation) {
    "1" { Run-Dashboard -serial $serial_number -testType $test_type -settings $settings }
    "2" { Run-StandaloneLogger -serial $serial_number -testType $test_type -settings $settings }
    "3" { Generate-AllScreenshots }
    "4" { Test-FileDiscovery }
    default { 
        Write-Host "Invalid operation selected" -ForegroundColor Red
    }
}

# Save settings before exit
Save-Settings -settings $settings

Read-Host "`nPress Enter to exit"