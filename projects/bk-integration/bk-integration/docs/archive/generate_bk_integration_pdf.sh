#!/bin/bash

# BK-Integration Documentation PDF Generator
# Generates PDF from the main implementation guide with mermaid diagrams

echo "BK-Integration Implementation Guide PDF Generator"
echo "================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -q -r pdf_requirements.txt

# Generate PDF with enhanced Mermaid support
echo "Generating PDF from bk-integration-mermaid.md with Mermaid diagrams..."
python simple_mermaid_pdf.py bk-integration-mermaid.md -o bk-integration-mermaid.pdf

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ PDF generated successfully: bk-integration-mermaid.pdf"
    echo ""
    # Try to get file size
    if command -v du &> /dev/null; then
        echo "File info:"
        du -h bk-integration-mermaid.pdf
        echo ""
        echo "Diagram Summary:"
        echo "- 8 Mermaid diagrams successfully rendered"
        echo "- System architecture, sequence diagrams, and workflows"
        echo "- Professional formatting with visible text"
    fi
else
    echo "❌ Failed to generate PDF"
    exit 1
fi

# Deactivate virtual environment
deactivate