#!/bin/bash
# BK-Integration Virtual Environment Activation Script

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at: $VENV_DIR"
    echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -e ."
    exit 1
fi

echo "🚀 Activating BK-Integration environment..."
source "$VENV_DIR/bin/activate"

echo "✅ BK-Integration v$(python -c 'from bk_integration import __version__; print(__version__)')"
echo "📋 Available commands:"
echo "   bk-integration --help"
echo "   bk-integration device status"
echo "   bk-integration test list-profiles"
echo "   bk-integration serve --host 0.0.0.0 --port 8080"
echo ""
echo "🔧 Configuration file: config.json (copy from config.example.json)"
echo "📝 Run 'deactivate' to exit the environment"

exec "$SHELL"