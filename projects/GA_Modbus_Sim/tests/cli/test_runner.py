"""
Test runner for CLI tests
"""
import pytest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def run_cli_tests():
    """Run all CLI tests"""
    test_dir = Path(__file__).parent
    
    # Run pytest with CLI test directory
    pytest_args = [
        str(test_dir),
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    return pytest.main(pytest_args)

def run_specific_test(test_name):
    """Run a specific test"""
    test_dir = Path(__file__).parent
    
    pytest_args = [
        str(test_dir),
        "-v",
        "-k", test_name,
        "--tb=short",
        "--color=yes"
    ]
    
    return pytest.main(pytest_args)

def run_test_coverage():
    """Run tests with coverage report"""
    test_dir = Path(__file__).parent
    
    pytest_args = [
        str(test_dir),
        "--cov=src.cli",
        "--cov=cli_demo",
        "--cov=temp_cli_launcher",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v"
    ]
    
    return pytest.main(pytest_args)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "coverage":
            run_test_coverage()
        else:
            run_specific_test(sys.argv[1])
    else:
        run_cli_tests()