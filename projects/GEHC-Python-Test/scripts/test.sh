#!/bin/bash
# GEHC PHTC Test Application Test Runner Script

set -e  # Exit on any error

echo "🧪 GEHC PHTC Test Application - Test Runner"
echo "==========================================="

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

# Parse command line arguments
TEST_TYPE="all"
VERBOSE=false
COVERAGE=true
MARKERS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        -m|--markers)
            MARKERS="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -t, --type TYPE      Test type: all, unit, integration, hardware (default: all)"
            echo "  -v, --verbose        Verbose output"
            echo "  --no-coverage        Skip coverage reporting"
            echo "  -m, --markers MARKS  Run tests with specific markers"
            echo "  -h, --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                          # Run all tests with coverage"
            echo "  $0 -t unit                  # Run only unit tests"
            echo "  $0 -t integration -v        # Run integration tests with verbose output"
            echo "  $0 -m \"not hardware\"        # Run tests except hardware tests"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "Virtual environment not activated. Activating..."
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source .venv/Scripts/activate
    else
        source .venv/bin/activate
    fi
fi

# Create test results directory
mkdir -p test_results

# Build pytest command
PYTEST_CMD="python -m pytest gehc_phtc_test/tests/"

# Add verbosity
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
else
    PYTEST_CMD="$PYTEST_CMD -q"
fi

# Add coverage
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=gehc_phtc_test --cov-report=term --cov-report=html --cov-report=xml"
fi

# Add test type markers
case $TEST_TYPE in
    unit)
        PYTEST_CMD="$PYTEST_CMD -m unit"
        print_status "Running unit tests..."
        ;;
    integration)
        PYTEST_CMD="$PYTEST_CMD -m integration"
        print_status "Running integration tests..."
        ;;
    hardware)
        PYTEST_CMD="$PYTEST_CMD -m hardware"
        print_status "Running hardware tests..."
        print_warning "Make sure hardware is connected and configured!"
        ;;
    all)
        print_status "Running all tests..."
        ;;
    *)
        print_error "Unknown test type: $TEST_TYPE"
        exit 1
        ;;
esac

# Add custom markers
if [ -n "$MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD -m \"$MARKERS\""
    print_status "Running tests with markers: $MARKERS"
fi

# Add output options
PYTEST_CMD="$PYTEST_CMD --junit-xml=test_results/junit.xml --tb=short"

# Run pre-test checks
print_status "Running pre-test checks..."

# Check code formatting
if ! black --check gehc_phtc_test/ &>/dev/null; then
    print_warning "Code formatting issues found. Run 'black gehc_phtc_test/' to fix."
fi

# Check import sorting
if ! isort --check-only gehc_phtc_test/ &>/dev/null; then
    print_warning "Import sorting issues found. Run 'isort gehc_phtc_test/' to fix."
fi

# Run linting
if ! flake8 gehc_phtc_test/ &>/dev/null; then
    print_warning "Linting issues found. Run 'flake8 gehc_phtc_test/' for details."
fi

print_success "Pre-test checks completed"

# Run the tests
print_status "Executing test command:"
echo "  $PYTEST_CMD"
echo ""

START_TIME=$(date +%s)

if eval $PYTEST_CMD; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    print_success "Tests completed successfully in ${DURATION}s"
    TEST_SUCCESS=true
else
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    print_error "Tests failed after ${DURATION}s"
    TEST_SUCCESS=false
fi

# Generate test report
print_status "Generating test report..."

cat > test_results/test_summary.md << EOF
# Test Summary Report

**Date:** $(date)
**Test Type:** $TEST_TYPE
**Duration:** ${DURATION}s
**Status:** $(if [ "$TEST_SUCCESS" = true ]; then echo "✅ PASSED"; else echo "❌ FAILED"; fi)

## Configuration
- Verbose: $VERBOSE
- Coverage: $COVERAGE
- Markers: ${MARKERS:-"None"}

## Files Generated
$(ls -la test_results/ | tail -n +2)

EOF

if [ "$COVERAGE" = true ] && [ -f "htmlcov/index.html" ]; then
    COVERAGE_PERCENT=$(grep -o '<span class="pc_cov">[0-9]\+%</span>' htmlcov/index.html | head -1 | grep -o '[0-9]\+%' || echo "Unknown")
    echo "**Coverage:** $COVERAGE_PERCENT" >> test_results/test_summary.md
    echo "" >> test_results/test_summary.md
    echo "Coverage report available at: htmlcov/index.html" >> test_results/test_summary.md
fi

# Post-test analysis
if [ "$TEST_SUCCESS" = true ]; then
    echo ""
    print_success "All tests passed! 🎉"
    
    if [ "$COVERAGE" = true ] && [ -f "htmlcov/index.html" ]; then
        echo ""
        print_status "Coverage report generated:"
        echo "  Open htmlcov/index.html in your browser"
        COVERAGE_PERCENT=$(grep -o '<span class="pc_cov">[0-9]\+%</span>' htmlcov/index.html | head -1 | grep -o '[0-9]\+%' || echo "Unknown")
        echo "  Overall coverage: $COVERAGE_PERCENT"
    fi
    
    echo ""
    echo "Test artifacts:"
    ls -la test_results/
    
else
    echo ""
    print_error "Some tests failed! 😞"
    echo ""
    echo "Troubleshooting tips:"
    echo "  1. Check test output above for specific failures"
    echo "  2. Run with -v flag for more verbose output"
    echo "  3. Run specific test types to isolate issues"
    echo "  4. Check test_results/junit.xml for detailed results"
    echo ""
    
    # Show recent failures
    if [ -f "test_results/junit.xml" ]; then
        print_status "Recent test failures:"
        grep -o 'message="[^"]*"' test_results/junit.xml | head -5 | sed 's/message="/  - /' | sed 's/"$//'
    fi
fi

# Cleanup
print_status "Cleaning up temporary files..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "📊 Test Summary:"
cat test_results/test_summary.md

exit $(if [ "$TEST_SUCCESS" = true ]; then echo 0; else echo 1; fi)