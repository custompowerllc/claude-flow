#!/bin/bash

# BK-Integration Documentation PDF Generator
# Generates a PDF from the markdown documentation

echo "BK-Integration PDF Generator"
echo "============================"

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
echo "Generating PDF from bk8520-api-diagram.md with enhanced Mermaid diagrams..."
python simple_mermaid_pdf.py bk8520-api-diagram.md -o bk8520-api-diagram-final.pdf

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ PDF generated successfully: bk8520-api-diagram-final.pdf"
    echo ""
    # Try to get file size
    if command -v du &> /dev/null; then
        echo "File info:"
        du -h bk8520-api-diagram-final.pdf
    fi
else
    echo "❌ Failed to generate PDF"
    exit 1
fi

# Deactivate virtual environment
deactivate