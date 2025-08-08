#!/usr/bin/env python3
"""
Generate PDF from BK-Integration documentation with proper diagram rendering.
Converts markdown to PDF while preserving ASCII art diagrams and code blocks.
"""

import os
import sys
from pathlib import Path
import markdown
from weasyprint import HTML, CSS
from markdown.extensions import codehilite, fenced_code, tables, toc
import argparse

def read_markdown_file(filepath):
    """Read markdown file content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def markdown_to_html(md_content):
    """Convert markdown to HTML with extensions."""
    # Configure markdown extensions
    extensions = [
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        'markdown.extensions.def_list',
        'markdown.extensions.abbr',
        'markdown.extensions.attr_list'
    ]
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=extensions)
    html_content = md.convert(md_content)
    
    return html_content

def create_html_template(content, title="BK-Integration Implementation Guide"):
    """Create complete HTML document with styling."""
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
            
            h4 {{
                color: #95a5a6;
                margin-top: 20px;
                page-break-after: avoid;
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
                white-space: pre;
            }}
            
            /* Inline code */
            code {{
                background-color: #f8f9fa;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 0.9em;
                color: #e83e8c;
            }}
            
            /* Code in pre blocks shouldn't have additional styling */
            pre code {{
                background-color: transparent;
                padding: 0;
                color: inherit;
            }}
            
            /* ASCII diagrams - special handling */
            pre:has(> code:only-child) {{
                background-color: #f0f4f8;
                border: 2px solid #4a90e2;
                font-size: 0.85em;
                line-height: 1.2;
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
            
            /* Lists */
            ul, ol {{
                margin: 15px 0;
                padding-left: 30px;
            }}
            
            li {{
                margin: 5px 0;
            }}
            
            /* Blockquotes */
            blockquote {{
                border-left: 4px solid #3498db;
                padding-left: 15px;
                margin: 20px 0;
                color: #555;
                font-style: italic;
            }}
            
            /* Links */
            a {{
                color: #3498db;
                text-decoration: none;
            }}
            
            a:hover {{
                text-decoration: underline;
            }}
            
            /* Strong and emphasis */
            strong {{
                font-weight: bold;
                color: #2c3e50;
            }}
            
            em {{
                font-style: italic;
            }}
            
            /* Page breaks */
            .page-break {{
                page-break-after: always;
            }}
            
            /* Special styling for API endpoints */
            p > code:first-child {{
                font-weight: bold;
            }}
            
            /* JSON code blocks */
            .language-json {{
                background-color: #f5f7fa !important;
            }}
            
            /* Python code blocks */
            .language-python {{
                background-color: #f9f9f9 !important;
            }}
            
            /* Bash code blocks */
            .language-bash {{
                background-color: #f4f4f4 !important;
            }}
            
            /* Architecture diagram special styling */
            pre:contains("┌─") {{
                background-color: #e8f4fd;
                border: 2px solid #2196F3;
                padding: 15px;
                font-weight: bold;
            }}
            
            /* Print-specific styles */
            @media print {{
                body {{
                    font-size: 10pt;
                }}
                
                h1 {{
                    font-size: 18pt;
                }}
                
                h2 {{
                    font-size: 14pt;
                }}
                
                h3 {{
                    font-size: 12pt;
                }}
                
                pre {{
                    font-size: 8pt;
                }}
                
                /* Avoid breaking inside these elements */
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

def generate_pdf(input_file, output_file=None):
    """Generate PDF from markdown file."""
    # Set default output file if not provided
    if output_file is None:
        output_file = Path(input_file).with_suffix('.pdf')
    
    # Read markdown content
    print(f"Reading markdown file: {input_file}")
    md_content = read_markdown_file(input_file)
    
    # Convert to HTML
    print("Converting markdown to HTML...")
    html_content = markdown_to_html(md_content)
    
    # Create full HTML document
    full_html = create_html_template(html_content)
    
    # Save HTML for debugging (optional)
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
    """Main function with CLI interface."""
    parser = argparse.ArgumentParser(
        description='Convert BK-Integration markdown documentation to PDF'
    )
    parser.add_argument(
        'input',
        nargs='?',
        default='bk-integration.md',
        help='Input markdown file (default: bk-integration.md)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output PDF file (default: same name as input with .pdf extension)'
    )
    parser.add_argument(
        '--keep-html',
        action='store_true',
        help='Keep intermediate HTML file for debugging'
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.input).exists():
        print(f"❌ Error: Input file '{args.input}' not found!")
        sys.exit(1)
    
    try:
        # Generate PDF
        pdf_file = generate_pdf(args.input, args.output)
        
        # Clean up HTML file if not needed
        if not args.keep_html:
            html_file = Path(pdf_file).with_suffix('.html')
            if html_file.exists():
                html_file.unlink()
                print(f"Cleaned up temporary HTML file")
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()