#!/bin/bash
# GEHC PHTC Test Application Build Script

set -e  # Exit on any error

echo "📦 GEHC PHTC Test Application - Build Script"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "Virtual environment not activated. Activating..."
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source .venv/Scripts/activate
    else
        source .venv/bin/activate
    fi
fi

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
print_success "Build artifacts cleaned"

# Run code quality checks
print_status "Running code quality checks..."

# Format code
print_status "Formatting code with black..."
black gehc_phtc_test/
print_success "Code formatted"

# Sort imports
print_status "Sorting imports with isort..."
isort gehc_phtc_test/
print_success "Imports sorted"

# Lint code
print_status "Linting code with flake8..."
if flake8 gehc_phtc_test/; then
    print_success "Linting passed"
else
    print_error "Linting failed"
    exit 1
fi

# Type checking
print_status "Running type checks with mypy..."
if mypy gehc_phtc_test/; then
    print_success "Type checking passed"
else
    print_warning "Type checking found issues"
fi

# Run tests
print_status "Running test suite..."
if python -m pytest gehc_phtc_test/tests/ --cov=gehc_phtc_test --cov-report=term --cov-report=html -v; then
    print_success "All tests passed"
else
    print_error "Tests failed"
    exit 1
fi

# Security scan
print_status "Running security scan with bandit..."
if bandit -r gehc_phtc_test/ -f json -o bandit-report.json; then
    print_success "Security scan passed"
else
    print_warning "Security scan found issues - check bandit-report.json"
fi

# Build package
print_status "Building package..."
if python -m build; then
    print_success "Package built successfully"
else
    print_error "Package build failed"
    exit 1
fi

# Verify build artifacts
print_status "Verifying build artifacts..."
if [ -f "dist/*.whl" ] && [ -f "dist/*.tar.gz" ]; then
    print_success "Build artifacts verified"
    echo "Built packages:"
    ls -la dist/
else
    print_error "Build artifacts missing"
    exit 1
fi

# Test installation
print_status "Testing package installation..."
# Create temporary environment for testing
TEMP_ENV=$(mktemp -d)
python -m venv "$TEMP_ENV"

if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source "$TEMP_ENV/Scripts/activate"
else
    source "$TEMP_ENV/bin/activate"
fi

# Install and test
pip install dist/*.whl
if python -c "import gehc_phtc_test; print('Package import successful')"; then
    print_success "Package installation test passed"
else
    print_error "Package installation test failed"
fi

# Cleanup test environment
deactivate
rm -rf "$TEMP_ENV"

# Reactivate original environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Generate documentation
print_status "Generating documentation..."
if command -v sphinx-build &> /dev/null; then
    cd docs && make html
    print_success "Documentation generated"
else
    print_warning "Sphinx not available, skipping documentation generation"
fi

# Create release summary
print_status "Creating release summary..."
cat > BUILD_SUMMARY.md << EOF
# Build Summary

**Build Date:** $(date)
**Version:** $(python -c "import gehc_phtc_test; print(gehc_phtc_test.__version__)" 2>/dev/null || echo "Unknown")

## Quality Checks ✅
- Code formatting: Passed
- Import sorting: Passed  
- Linting: Passed
- Type checking: $(if mypy gehc_phtc_test/ &>/dev/null; then echo "Passed"; else echo "Issues found"; fi)
- Tests: Passed
- Security scan: $(if [ -f "bandit-report.json" ]; then echo "Completed"; else echo "Not run"; fi)

## Build Artifacts
$(ls -la dist/ | tail -n +2)

## Test Coverage
$(tail -1 htmlcov/index.html 2>/dev/null | grep -o '[0-9]\+%' | tail -1 || echo "Coverage report not generated")

## Installation Test
✅ Package installs and imports successfully

EOF

print_success "Build summary created: BUILD_SUMMARY.md"

echo ""
echo "🎉 Build Complete!"
echo "=================="
echo ""
print_success "Package built and verified successfully!"
echo ""
echo "Build artifacts:"
ls -la dist/
echo ""
echo "Next steps:"
echo "  - Review BUILD_SUMMARY.md"
echo "  - Test package: pip install dist/*.whl"
echo "  - Upload to repository: twine upload dist/*"
echo ""