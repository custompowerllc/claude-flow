#!/usr/bin/env python3
"""
Test runner for Modbus BMS Simulator

This script provides convenient commands to run different test suites
with appropriate configuration and reporting.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def get_test_dir():
    """Get the test directory path"""
    return Path(__file__).parent


def run_command(cmd, cwd=None):
    """Run a shell command and return the result"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or get_test_dir(),
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests"""
    cmd = ["python", "-m", "pytest", "unit/"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=../src", "--cov-report=html", "--cov-report=term-missing"])
    
    cmd.extend(["-m", "not slow"])  # Skip slow tests by default
    
    return run_command(cmd)


def run_integration_tests(verbose=False):
    """Run integration tests"""
    cmd = ["python", "-m", "pytest", "integration/"]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd)


def run_all_tests(verbose=False, coverage=False):
    """Run all tests"""
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=../src", "--cov-report=html", "--cov-report=term-missing"])
    
    cmd.extend(["-m", "not slow"])  # Skip slow tests by default
    
    return run_command(cmd)


def run_performance_tests(verbose=False):
    """Run performance and stress tests"""
    cmd = ["python", "-m", "pytest", "-m", "slow or performance"]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd)


def run_serial_tests(verbose=False):
    """Run tests that require serial hardware"""
    cmd = ["python", "-m", "pytest", "-m", "serial"]
    
    if verbose:
        cmd.append("-v")
    
    print("Warning: Serial tests require actual hardware or virtual COM ports")
    return run_command(cmd)


def check_dependencies():
    """Check if required test dependencies are installed"""
    required_packages = [
        "pytest",
        "pytest-mock", 
        "pymodbus",
        "pyserial"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True


def install_dependencies():
    """Install test dependencies"""
    requirements_file = get_test_dir() / "requirements.txt"
    cmd = ["pip", "install", "-r", str(requirements_file)]
    return run_command(cmd)


def lint_code():
    """Run code linting"""
    test_dir = get_test_dir()
    cmd = ["python", "-m", "flake8", ".", "--max-line-length=100", "--exclude=__pycache__"]
    return run_command(cmd, cwd=test_dir)


def format_code():
    """Format code with black"""
    test_dir = get_test_dir()
    cmd = ["python", "-m", "black", ".", "--line-length=100"]
    return run_command(cmd, cwd=test_dir)


def generate_test_report():
    """Generate comprehensive test report"""
    cmd = [
        "python", "-m", "pytest",
        "--html=test_report.html",
        "--self-contained-html",
        "--cov=../src",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v"
    ]
    
    return run_command(cmd)


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Modbus BMS Simulator Test Runner")
    
    parser.add_argument(
        "command",
        choices=[
            "unit", "integration", "all", "performance", "serial",
            "install", "check", "lint", "format", "report"
        ],
        help="Test command to run"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    args = parser.parse_args()
    
    # Change to test directory
    os.chdir(get_test_dir())
    
    if args.command == "install":
        success = install_dependencies()
    elif args.command == "check":
        success = check_dependencies()
    elif args.command == "lint":
        success = lint_code()
    elif args.command == "format":
        success = format_code()
    elif args.command == "report":
        success = generate_test_report()
    else:
        # Check dependencies before running tests
        if not check_dependencies():
            print("Dependencies check failed. Run 'python run_tests.py install' first.")
            sys.exit(1)
        
        if args.command == "unit":
            success = run_unit_tests(args.verbose, args.coverage)
        elif args.command == "integration":
            success = run_integration_tests(args.verbose)
        elif args.command == "all":
            success = run_all_tests(args.verbose, args.coverage)
        elif args.command == "performance":
            success = run_performance_tests(args.verbose)
        elif args.command == "serial":
            success = run_serial_tests(args.verbose)
        else:
            print(f"Unknown command: {args.command}")
            success = False
    
    if success:
        print(f"\n✅ {args.command.title()} completed successfully!")
    else:
        print(f"\n❌ {args.command.title()} failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()