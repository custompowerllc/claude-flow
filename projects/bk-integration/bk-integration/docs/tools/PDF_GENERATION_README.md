# PDF Generation Guide for BK-Integration Documentation

This directory contains tools to generate PDF versions of the BK-Integration documentation with proper diagram rendering.

## Available Tools

### 1. Basic PDF Generator (`generate_pdf.py`)
Converts the main documentation to PDF with proper ASCII art diagram preservation.

**Features:**
- Preserves ASCII art diagrams
- Syntax highlighting for code blocks
- Professional styling and formatting
- Page breaks optimization

**Usage:**
```bash
# Install dependencies
pip install -r pdf_requirements.txt

# Generate PDF
python generate_pdf.py bk-integration.md -o bk-integration-guide.pdf
```

### 2. Mermaid Diagram PDF Generator (`generate_pdf_mermaid.py`)
Enhanced version that renders Mermaid diagrams as proper vector graphics.

**Features:**
- Converts Mermaid diagrams to SVG
- All features of basic generator
- Better visual quality for diagrams
- Interactive diagram themes

**Prerequisites:**
- Node.js and npm installed
- Mermaid CLI (auto-installed if npm available)

**Usage:**
```bash
# The script will auto-install dependencies
python generate_pdf_mermaid.py bk-integration-mermaid.md -o bk-integration-mermaid.pdf
```

### 3. Quick Generation Script (`generate_pdf.sh`)
Bash script that handles virtual environment and dependencies automatically.

**Usage:**
```bash
# Make executable (first time only)
chmod +x generate_pdf.sh

# Run the script
./generate_pdf.sh
```

## Installation

### System Requirements

#### For Basic PDF Generation:
```bash
# Ubuntu/Debian
sudo apt-get install python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0

# macOS
brew install python3 cairo pango gdk-pixbuf libffi

# Install Python packages
pip install -r pdf_requirements.txt
```

#### For Mermaid Support (Optional):
```bash
# Install Node.js first
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node

# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli
```

## Generated Files

- **bk-integration-guide.pdf** - Main documentation with ASCII diagrams
- **bk-integration-mermaid.pdf** - Documentation with rendered Mermaid diagrams
- **bk-integration.html** - Intermediate HTML (for debugging, auto-deleted)

## Customization

### Modify Styling
Edit the CSS in `generate_pdf.py` or `generate_pdf_mermaid.py`:
- Page size (default: A4)
- Margins (default: 2cm)
- Font family and sizes
- Color scheme
- Code block styling

### Mermaid Themes
Edit the `config` object in `generate_pdf_mermaid.py`:
```python
config = {
    "theme": "default",  # or "dark", "forest", "neutral"
    "themeVariables": {
        "primaryColor": "#e1f5fe",
        # Add more theme variables
    }
}
```

## Troubleshooting

### Common Issues

1. **WeasyPrint Installation Fails**
   ```bash
   # Install system dependencies first
   sudo apt-get install python3-dev python3-setuptools python3-wheel
   sudo apt-get install libcairo2-dev libpango1.0-dev
   ```

2. **Mermaid CLI Not Found**
   - Ensure Node.js is installed: `node --version`
   - Install globally: `npm install -g @mermaid-js/mermaid-cli`
   - Check installation: `mmdc --version`

3. **PDF Generation Errors**
   - Check markdown file exists
   - Verify all dependencies installed
   - Review HTML output for syntax errors
   - Use `--keep-html` flag to debug

4. **Diagrams Not Rendering**
   - For ASCII art: Ensure proper code block formatting
   - For Mermaid: Check Node.js and mmdc installation
   - Verify Mermaid syntax is correct

## Tips

1. **Large Documents**: For documents >50 pages, increase memory:
   ```bash
   export NODE_OPTIONS="--max-old-space-size=4096"
   python generate_pdf_mermaid.py large-doc.md
   ```

2. **Custom Fonts**: Place .ttf files in same directory and update CSS:
   ```css
   @font-face {
       font-family: 'CustomFont';
       src: url('custom-font.ttf');
   }
   ```

3. **Batch Processing**: Generate multiple PDFs:
   ```bash
   for file in *.md; do
       python generate_pdf.py "$file" -o "${file%.md}.pdf"
   done
   ```

## Output Quality

The generated PDFs are optimized for:
- **Print**: High-resolution, proper page breaks
- **Digital**: Searchable text, selectable code
- **Sharing**: Professional appearance, consistent formatting

## Support

For issues or improvements:
1. Check error messages carefully
2. Review this README
3. Examine the HTML output (use `--keep-html`)
4. Verify all dependencies are installed correctly