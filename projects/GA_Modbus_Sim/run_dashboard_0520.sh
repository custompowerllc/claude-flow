#!/bin/bash

# Shell script to run Modbus dashboard for serial number 0520
# Usage: ./run_dashboard_0520.sh

set -e  # Exit on any error

# Configuration
SERIAL_NUMBER="0520"
RMA_NUMBER="8765"
DATA_DIR="./data/sessions/0520"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to find Python
find_python() {
    if command_exists python3; then
        echo "python3"
    elif command_exists python; then
        # Check if it's Python 3
        if python -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" 2>/dev/null; then
            echo "python"
        else
            return 1
        fi
    else
        return 1
    fi
}

# Function to check and activate virtual environment
check_venv() {
    if [[ -n "$VIRTUAL_ENV" ]]; then
        print_success "Virtual environment already active: $VIRTUAL_ENV"
        return 0
    fi
    
    # Check for common virtual environment directories
    local venv_dirs=("venv" "new_venv" ".venv" "env")
    
    for venv_dir in "${venv_dirs[@]}"; do
        if [[ -d "$venv_dir" && -f "$venv_dir/bin/activate" ]]; then
            print_status "Found virtual environment: $venv_dir"
            print_status "Activating virtual environment..."
            source "$venv_dir/bin/activate"
            print_success "Virtual environment activated"
            return 0
        fi
    done
    
    print_warning "No virtual environment found. Running with system Python."
    return 1
}

# Function to check dependencies
check_dependencies() {
    local python_cmd="$1"
    
    print_status "Checking dependencies..."
    
    # Check required dependencies
    local required_deps=("matplotlib" "numpy")
    local missing_deps=()
    
    for dep in "${required_deps[@]}"; do
        if ! $python_cmd -c "import $dep" >/dev/null 2>&1; then
            missing_deps+=("$dep")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        print_status "Install with: pip install ${missing_deps[*]}"
        return 1
    fi
    
    # Check optional dependencies
    local optional_deps=("pandas")
    local missing_optional=()
    
    for dep in "${optional_deps[@]}"; do
        if ! $python_cmd -c "import $dep" >/dev/null 2>&1; then
            missing_optional+=("$dep")
        fi
    done
    
    if [[ ${#missing_optional[@]} -gt 0 ]]; then
        print_warning "Missing optional dependencies: ${missing_optional[*]}"
        print_status "Install for enhanced features: pip install ${missing_optional[*]}"
    fi
    
    print_success "Dependencies check completed"
    return 0
}

# Function to check data directory
check_data_dir() {
    if [[ ! -d "$DATA_DIR" ]]; then
        print_warning "Data directory not found: $DATA_DIR"
        print_status "Creating directory..."
        mkdir -p "$DATA_DIR"
        print_success "Directory created: $DATA_DIR"
    else
        print_success "Data directory found: $DATA_DIR"
    fi
    
    # Check for CSV files
    local csv_count=$(find "$DATA_DIR" -name "*.csv" 2>/dev/null | wc -l)
    if [[ $csv_count -eq 0 ]]; then
        print_warning "No CSV files found in $DATA_DIR"
        print_status "Dashboard will monitor for new files..."
    else
        print_success "Found $csv_count CSV file(s) in data directory"
    fi
}

# Main execution
main() {
    echo "==============================================="
    echo "  Modbus Dashboard Launcher for Serial $SERIAL_NUMBER"
    echo "==============================================="
    echo
    
    # Check if we're in the right directory
    if [[ ! -f "src/modbus_dashboard.py" ]]; then
        print_error "src/modbus_dashboard.py not found!"
        print_error "Please run this script from the GA_Modbus_Python_App root directory"
        exit 1
    fi
    
    # Check and activate virtual environment
    check_venv
    
    # Find Python interpreter
    print_status "Finding Python interpreter..."
    if PYTHON_CMD=$(find_python); then
        print_success "Found Python: $PYTHON_CMD"
        $PYTHON_CMD --version
    else
        print_error "Python 3 not found!"
        print_error "Please install Python 3 or ensure it's in your PATH"
        exit 1
    fi
    
    # Check dependencies
    if ! check_dependencies "$PYTHON_CMD"; then
        print_error "Dependency check failed!"
        print_status "Please install missing dependencies and try again"
        exit 1
    fi
    
    # Check data directory
    check_data_dir
    
    # Run the dashboard
    echo
    print_status "Starting Modbus Dashboard..."
    print_status "Serial Number: $SERIAL_NUMBER"
    print_status "RMA Number: $RMA_NUMBER"
    print_status "Data Directory: $DATA_DIR"
    echo
    print_status "Press Ctrl+C to stop the dashboard"
    echo
    
    # Execute the dashboard command
    exec $PYTHON_CMD src/modbus_dashboard.py --dir "$DATA_DIR" --sn "$SERIAL_NUMBER" --rma "$RMA_NUMBER"
}

# Handle script interruption
trap 'print_status "Dashboard stopped by user"; exit 0' INT TERM

# Run main function
main "$@"