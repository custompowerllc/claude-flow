#!/usr/bin/env python3
"""
Generate PDF with Mermaid diagram support.
Converts Mermaid diagrams to SVG before PDF generation.
"""

import os
import sys
import re
import base64
import subprocess
from pathlib import Path
import tempfile
import json

def install_mermaid_cli():
    """Check and install mermaid-cli if needed."""
    try:
        # Check if mmdc is installed
        result = subprocess.run(['mmdc', '--version'], capture_output=True, text=True)
        print(f"✓ Mermaid CLI found: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("Mermaid CLI not found. Installing...")
        try:
            # Install mermaid-cli globally via npm
            subprocess.run(['npm', 'install', '-g', '@mermaid-js/mermaid-cli'], check=True)
            print("✓ Mermaid CLI installed successfully")
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("⚠ Warning: Could not install Mermaid CLI. Diagrams will be rendered as code blocks.")
            print("  To enable diagram rendering, install Node.js and run: npm install -g @mermaid-js/mermaid-cli")
            return False

def render_mermaid_diagram(mermaid_code, index):
    """Render Mermaid code to SVG."""
    try:
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as mmd_file:
            mmd_file.write(mermaid_code)
            mmd_path = mmd_file.name
        
        svg_path = mmd_path.replace('.mmd', '.svg')
        
        # Configure mermaid with custom theme
        config = {
            "theme": "default",
            "themeVariables": {
                "primaryColor": "#e1f5fe",
                "primaryTextColor": "#333",
                "primaryBorderColor": "#2196F3",
                "lineColor": "#666",
                "secondaryColor": "#fff3e0",
                "tertiaryColor": "#c8e6c9"
            }
        }
        
        config_path = mmd_path.replace('.mmd', '_config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f)
        
        # Render with mermaid-cli
        result = subprocess.run([
            'mmdc',
            '-i', mmd_path,
            '-o', svg_path,
            '-c', config_path,
            '--width', '800',
            '--height', '600'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Read SVG content
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            # Clean up temp files
            os.unlink(mmd_path)
            os.unlink(svg_path)
            os.unlink(config_path)
            
            return svg_content
        else:
            print(f"Failed to render diagram {index}: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Error rendering Mermaid diagram {index}: {e}")
        return None

def process_mermaid_blocks(content):
    """Find and replace Mermaid code blocks with rendered SVGs."""
    has_mermaid = install_mermaid_cli()
    
    if not has_mermaid:
        # Just return content as-is if Mermaid CLI is not available
        return content
    
    # Pattern to match Mermaid code blocks
    pattern = r'```mermaid\n(.*?)\n```'
    
    def replace_mermaid(match):
        mermaid_code = match.group(1)
        index = replace_mermaid.counter
        replace_mermaid.counter += 1
        
        print(f"  Rendering Mermaid diagram {index}...")
        svg = render_mermaid_diagram(mermaid_code, index)
        
        if svg:
            # Embed SVG directly in HTML
            return f'<div class="mermaid-diagram">{svg}</div>'
        else:
            # Fallback to code block
            return f'<pre><code class="language-mermaid">{mermaid_code}</code></pre>'
    
    replace_mermaid.counter = 1
    
    # Replace all Mermaid blocks
    processed = re.sub(pattern, replace_mermaid, content, flags=re.DOTALL)
    
    return processed

def create_enhanced_html_template(content, title="BK-Integration Implementation Guide"):
    """Create HTML template with Mermaid diagram support."""
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            @page {{
                size: A4;
                margin: 2cm;
                @bottom-center {{
                    content: counter(page);
                }}
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 210mm;
                margin: 0 auto;
                padding: 20px;
                background: white;
            }}
            
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                margin-top: 40px;
                page-break-before: auto;
            }}
            
            h2 {{
                color: #34495e;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 8px;
                margin-top: 30px;
                page-break-after: avoid;
            }}
            
            h3 {{
                color: #7f8c8d;
                margin-top: 25px;
                page-break-after: avoid;
            }}
            
            /* Mermaid diagrams */
            .mermaid-diagram {{
                margin: 20px 0;
                text-align: center;
                page-break-inside: avoid;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }}
            
            .mermaid-diagram svg {{
                max-width: 100%;
                height: auto;
            }}
            
            /* Code blocks */
            pre {{
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 12px;
                overflow-x: auto;
                page-break-inside: avoid;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 0.9em;
                line-height: 1.4;
            }}
            
            code {{
                background-color: #f8f9fa;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 0.9em;
                color: #e83e8c;
            }}
            
            pre code {{
                background-color: transparent;
                padding: 0;
                color: inherit;
            }}
            
            /* Tables */
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
                page-break-inside: avoid;
            }}
            
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            
            th {{
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }}
            
            tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}
            
            /* Print-specific styles */
            @media print {{
                body {{
                    font-size: 10pt;
                }}
                
                .mermaid-diagram {{
                    background: white;
                    border: 2px solid #e0e0e0;
                }}
                
                h1, h2, h3, h4, h5, h6 {{
                    page-break-after: avoid;
                }}
                
                p, blockquote, ul, ol {{
                    orphans: 3;
                    widows: 3;
                }}
            }}
        </style>
    </head>
    <body>
        {content}
    </body>
    </html>
    """
    
    return html_template

def generate_pdf_with_mermaid(input_file, output_file=None):
    """Generate PDF from markdown with Mermaid diagram support."""
    import markdown
    from weasyprint import HTML
    
    # Set default output file if not provided
    if output_file is None:
        output_file = Path(input_file).with_suffix('.pdf')
    
    # Read markdown content
    print(f"Reading markdown file: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Process Mermaid blocks
    print("Processing Mermaid diagrams...")
    processed_content = process_mermaid_blocks(md_content)
    
    # Convert to HTML
    print("Converting markdown to HTML...")
    extensions = [
        'markdown.extensions.fenced_code',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'markdown.extensions.nl2br',
    ]
    
    md = markdown.Markdown(extensions=extensions)
    html_content = md.convert(processed_content)
    
    # Create full HTML document
    full_html = create_enhanced_html_template(html_content)
    
    # Save HTML for debugging
    html_file = Path(output_file).with_suffix('.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"HTML saved to: {html_file}")
    
    # Generate PDF
    print(f"Generating PDF: {output_file}")
    HTML(string=full_html).write_pdf(output_file)
    
    print(f"✅ PDF successfully generated: {output_file}")
    return output_file

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert markdown to PDF with Mermaid diagram support'
    )
    parser.add_argument(
        'input',
        nargs='?',
        default='bk-integration-mermaid.md',
        help='Input markdown file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output PDF file'
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.input).exists():
        print(f"❌ Error: Input file '{args.input}' not found!")
        sys.exit(1)
    
    try:
        # Install dependencies
        try:
            import markdown
            import weasyprint
        except ImportError:
            print("Installing required Python packages...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'markdown', 'weasyprint'], check=True)
            import markdown
            from weasyprint import HTML
        
        # Generate PDF
        generate_pdf_with_mermaid(args.input, args.output)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()