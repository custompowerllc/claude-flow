# GEHC PHTC Test Application Makefile
.PHONY: help install install-dev test lint format type-check clean docs build deploy venv

# Default target
help:
	@echo "GEHC PHTC Test Application - Development Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  venv          Create virtual environment"
	@echo "  install       Install production dependencies"
	@echo "  install-dev   Install development dependencies"
	@echo ""
	@echo "Development Commands:"
	@echo "  test          Run all tests"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-cov      Run tests with coverage"
	@echo "  lint          Run all linting checks"
	@echo "  format        Format code with black and isort"
	@echo "  type-check    Run mypy type checking"
	@echo ""
	@echo "Documentation Commands:"
	@echo "  docs          Build documentation"
	@echo "  docs-serve    Serve documentation locally"
	@echo ""
	@echo "Build Commands:"
	@echo "  build         Build package"
	@echo "  clean         Clean build artifacts"
	@echo ""
	@echo "Application Commands:"
	@echo "  run           Run the application"
	@echo "  run-demo      Run with demo configuration"

# Python and pip commands
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
ISORT := $(PYTHON) -m isort
MYPY := $(PYTHON) -m mypy
FLAKE8 := $(PYTHON) -m flake8

# Virtual environment setup
venv:
	$(PYTHON) -m venv .venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source .venv/bin/activate  # Linux/Mac"
	@echo "  .venv\Scripts\activate.bat # Windows"

# Installation targets
install:
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e .

install-dev:
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e .[dev]
	pre-commit install

# Testing targets
test:
	$(PYTEST) gehc_phtc_test/tests/ -v

test-unit:
	$(PYTEST) gehc_phtc_test/tests/ -v -m "unit"

test-integration:
	$(PYTEST) gehc_phtc_test/tests/ -v -m "integration"

test-hardware:
	$(PYTEST) gehc_phtc_test/tests/ -v -m "hardware"

test-cov:
	$(PYTEST) gehc_phtc_test/tests/ --cov=gehc_phtc_test --cov-report=html --cov-report=term

test-all:
	$(PYTEST) gehc_phtc_test/tests/ --cov=gehc_phtc_test --cov-report=html --cov-report=term -v

# Code quality targets
lint: flake8 mypy

flake8:
	$(FLAKE8) gehc_phtc_test/

mypy:
	$(MYPY) gehc_phtc_test/

format:
	$(BLACK) gehc_phtc_test/
	$(ISORT) gehc_phtc_test/

format-check:
	$(BLACK) --check gehc_phtc_test/
	$(ISORT) --check-only gehc_phtc_test/

type-check:
	$(MYPY) gehc_phtc_test/

# Documentation targets
docs:
	cd docs && make html

docs-serve:
	cd docs/_build/html && $(PYTHON) -m http.server 8000

docs-clean:
	cd docs && make clean

# Build targets
build: clean
	$(PYTHON) -m build

build-wheel:
	$(PYTHON) -m build --wheel

build-sdist:
	$(PYTHON) -m build --sdist

# Application targets
run:
	$(PYTHON) -m gehc_phtc_test

run-demo:
	$(PYTHON) -m gehc_phtc_test --config gehc_phtc_test/config/demo_config.json

run-profile:
	$(PYTHON) -m gehc_phtc_test --profile basic_test

# Cleanup targets
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

clean-all: clean
	rm -rf .venv/
	rm -rf docs/_build/

# Development convenience targets
check: format-check lint test

ci: format-check lint test-all

dev-setup: venv install-dev
	@echo "Development environment setup complete!"
	@echo "Activate virtual environment with: source .venv/bin/activate"

# Windows compatibility
install-win:
	python -m pip install --upgrade pip setuptools wheel
	python -m pip install -e .[dev]

venv-win:
	python -m venv .venv
	@echo "Virtual environment created. Activate with: .venv\Scripts\activate.bat"