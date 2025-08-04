#!/usr/bin/env pwsh

# PowerShell script to run Modbus dashboard for serial number 0520
# Usage: .\run_dashboard_0520.ps1

$serial_number = "0520"
$rma_number = "8765"
$data_dir = "Y:\home\ahu\development\GA_Modbus_Python_App\P3E-Report\test-artifacts\0520"

# Run the Modbus dashboard
python3 src/modbus_dashboard.py --dir $data_dir --sn $serial_number --rma $rma_number