# GA Standalone Modbus Logger Runner Script for Windows PowerShell
# This script runs the standalone Modbus logger with dependency checking

# Function to check if a Python package is installed
function Test-PythonPackage {
    param([string]$PackageName)
    
    try {
        $result = python -c "import $PackageName" 2>$null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

# Function to install package with pip
function Install-PythonPackage {
    param([string]$PackageName)
    
    Write-Host "📦 Installing $PackageName..." -ForegroundColor Yellow
    python -m pip install $PackageName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Successfully installed $PackageName" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Failed to install $PackageName" -ForegroundColor Red
        return $false
    }
}

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "🔋 GA Standalone Modbus Logger" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python is available: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install Python 3.7+ from https://python.org" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.7+ from https://python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if pip is available
try {
    python -m pip --version > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ pip is available" -ForegroundColor Green
    } else {
        Write-Host "❌ pip is not available" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "❌ pip is not available" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`n🔍 Checking dependencies..." -ForegroundColor Blue

# Define required and optional packages
$RequiredPackages = @("pymodbus", "pyserial")
$OptionalPackages = @("rich", "tomli", "tomli_w")

# Check required packages
$MissingRequired = @()
foreach ($package in $RequiredPackages) {
    if (Test-PythonPackage $package) {
        Write-Host "✅ $package is available" -ForegroundColor Green
    } else {
        Write-Host "⚠️  $package is missing" -ForegroundColor Yellow
        $MissingRequired += $package
    }
}

# Check optional packages
$MissingOptional = @()
foreach ($package in $OptionalPackages) {
    if (Test-PythonPackage $package) {
        Write-Host "✅ $package is available" -ForegroundColor Green
    } else {
        Write-Host "⚠️  $package is missing (optional)" -ForegroundColor Yellow
        $MissingOptional += $package
    }
}

# Install missing required packages
if ($MissingRequired.Count -gt 0) {
    Write-Host "`nInstalling required packages..." -ForegroundColor Yellow
    
    foreach ($package in $MissingRequired) {
        if (-not (Install-PythonPackage $package)) {
            Write-Host "❌ Failed to install required package: $package" -ForegroundColor Red
            Write-Host "Please install manually: python -m pip install $package" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
}

# Offer to install optional packages
if ($MissingOptional.Count -gt 0) {
    Write-Host "`nOptional packages available for enhanced experience:" -ForegroundColor Cyan
    foreach ($package in $MissingOptional) {
        Write-Host "  - $package" -ForegroundColor Yellow
    }
    
    $installOptional = Read-Host "Install optional packages? [y/N]"
    if ($installOptional -match "^[Yy]") {
        foreach ($package in $MissingOptional) {
            Install-PythonPackage $package | Out-Null
        }
    } else {
        Write-Host "ℹ️  Continuing without optional packages. Some features may be limited." -ForegroundColor Blue
    }
}

# Try to activate virtual environment if it exists
$VenvActivate = Join-Path $ScriptDir "venv\Scripts\Activate.ps1"
$NewVenvActivate = Join-Path $ScriptDir "new_venv\Scripts\Activate.ps1"

if (Test-Path $VenvActivate) {
    Write-Host "🔧 Activating virtual environment..." -ForegroundColor Blue
    try {
        & $VenvActivate
        Write-Host "✅ Virtual environment activated" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Failed to activate virtual environment. Using system Python." -ForegroundColor Yellow
    }
} elseif (Test-Path $NewVenvActivate) {
    Write-Host "🔧 Activating virtual environment..." -ForegroundColor Blue
    try {
        & $NewVenvActivate
        Write-Host "✅ Virtual environment activated" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Failed to activate virtual environment. Using system Python." -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  No virtual environment found. Using system Python." -ForegroundColor Yellow
}

Write-Host "`n🚀 Starting Standalone Modbus Logger..." -ForegroundColor Green

# Change to script directory
Set-Location $ScriptDir

# Run the logger with provided arguments
$arguments = $args -join ' '
if ($arguments) {
    python src/modbus_standalone_logger.py $args
} else {
    python src/modbus_standalone_logger.py
}

# Check exit code and handle errors
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Logger exited with error code: $LASTEXITCODE" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Red
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit $LASTEXITCODE
} else {
    Write-Host "`n✅ Logger completed successfully" -ForegroundColor Green
}