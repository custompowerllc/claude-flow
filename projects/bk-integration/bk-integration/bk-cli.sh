#!/bin/bash
# Convenience wrapper script for BK-Integration CLI

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set up Python path and virtual environment
export PYTHONPATH="$SCRIPT_DIR"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"
CONFIG_FILE="$SCRIPT_DIR/config.json"

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found at $SCRIPT_DIR/venv"
    echo "Please run: python3 -m venv $SCRIPT_DIR/venv && $SCRIPT_DIR/venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "⚠️  Config file not found, using config.example.json"
    CONFIG_FILE="$SCRIPT_DIR/config.example.json"
fi

# Execute the CLI with all passed arguments
exec "$VENV_PYTHON" -m bk_integration.cli --config "$CONFIG_FILE" "$@"