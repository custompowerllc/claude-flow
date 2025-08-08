#!/bin/bash
# GEHC PHTC Test Application Setup Script

set -e  # Exit on any error

echo "🏗️  GEHC PHTC Test Application - Development Setup"
echo "=================================================="

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

# Check Python version
print_status "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        print_success "Python $PYTHON_VERSION found"
        PYTHON_CMD=python3
    else
        print_error "Python 3.8+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python3 not found. Please install Python 3.8+ first."
    exit 1
fi

# Create virtual environment
print_status "Creating virtual environment..."
if [ ! -d ".venv" ]; then
    $PYTHON_CMD -m venv .venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Detect OS and set activation script
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    ACTIVATE_SCRIPT=".venv/Scripts/activate"
    PIP_CMD=".venv/Scripts/pip"
    PYTHON_VENV=".venv/Scripts/python"
else
    ACTIVATE_SCRIPT=".venv/bin/activate"
    PIP_CMD=".venv/bin/pip"
    PYTHON_VENV=".venv/bin/python"
fi

# Activate virtual environment and upgrade pip
print_status "Activating virtual environment and upgrading pip..."
source "$ACTIVATE_SCRIPT"
$PIP_CMD install --upgrade pip setuptools wheel
print_success "Pip upgraded"

# Install dependencies
print_status "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    $PIP_CMD install -r requirements.txt
    print_success "Requirements installed"
else
    print_warning "requirements.txt not found, installing from pyproject.toml"
fi

# Install package in development mode
print_status "Installing package in development mode..."
$PIP_CMD install -e .[dev]
print_success "Package installed in development mode"

# Install pre-commit hooks
print_status "Installing pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    print_success "Pre-commit hooks installed"
else
    print_warning "Pre-commit not available, skipping hook installation"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p test_results
mkdir -p docs/_build
print_success "Directories created"

# Set up environment file
print_status "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_success "Environment file created from template"
    print_warning "Please edit .env file to configure your serial port settings"
else
    print_warning ".env file already exists"
fi

# Run initial tests
print_status "Running initial tests..."
if $PYTHON_VENV -m pytest gehc_phtc_test/tests/ --tb=short -q; then
    print_success "Initial tests passed"
else
    print_warning "Some tests failed - this is normal for initial setup"
fi

# Run code quality checks
print_status "Running code quality checks..."
if command -v black &> /dev/null; then
    black --check gehc_phtc_test/ || print_warning "Code formatting needs attention"
fi

if command -v flake8 &> /dev/null; then
    flake8 gehc_phtc_test/ || print_warning "Linting issues found"
fi

# Display summary
echo ""
echo "🎉 Setup Complete!"
echo "==================="
echo ""
print_success "Development environment ready!"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source $ACTIVATE_SCRIPT"
echo ""
echo "  2. Configure your serial port in .env file"
echo ""
echo "  3. Run the application:"
echo "     python -m gehc_phtc_test"
echo ""
echo "  4. Run in demo mode:"
echo "     python -m gehc_phtc_test --config gehc_phtc_test/config/demo_config.json"
echo ""
echo "  5. Run tests:"
echo "     make test"
echo ""
echo "  6. View all available commands:"
echo "     make help"
echo ""
echo "For more information, see README.md"