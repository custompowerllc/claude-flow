#!/usr/bin/env python3
"""
Simple Mermaid to PDF converter using alternative rendering methods.
Falls back to styled code blocks if diagram rendering fails.
"""

import os
import sys
import re
import subprocess
from pathlib import Path
import tempfile
import base64
import requests
from urllib.parse import quote

def fix_svg_text_rendering(svg_content):
    """Fix common SVG text rendering issues for PDF generation."""
    if not svg_content or '<svg' not in svg_content:
        return svg_content
    
    import re
    
    # First, ensure all text elements have proper attributes
    def fix_text_element(match):
        text_element = match.group(0)
        # Add essential attributes if missing
        if 'font-family' not in text_element:
            text_element = text_element.replace('<text', '<text font-family="Arial, sans-serif"')
        if 'font-size' not in text_element:
            text_element = text_element.replace('<text', '<text font-size="12px"')
        if 'fill=' not in text_element:
            text_element = text_element.replace('<text', '<text fill="#333333"')
        if 'text-anchor' not in text_element:
            text_element = text_element.replace('<text', '<text text-anchor="middle"')
        return text_element
    
    # Apply fixes to all text elements
    svg_content = re.sub(r'<text[^>]*>', fix_text_element, svg_content)
    
    # Add comprehensive CSS styles
    css_styles = '''
    <defs>
    <style type="text/css"><![CDATA[
        * {
            font-family: Arial, sans-serif !important;
        }
        text {
            font-family: Arial, sans-serif !important;
            font-size: 12px !important;
            fill: #333333 !important;
            text-anchor: middle !important;
            dominant-baseline: central !important;
            alignment-baseline: central !important;
        }
        .label text, .nodeLabel text {
            font-size: 11px !important;
            font-weight: bold !important;
            fill: #000000 !important;
        }
        .edgeLabel text, .edge-label text {
            font-size: 10px !important;
            fill: #666666 !important;
        }
        .cluster text, .cluster-label text {
            font-size: 13px !important;
            font-weight: bold !important;
            fill: #000000 !important;
        }
        .titleText, .title text {
            font-size: 16px !important;
            font-weight: bold !important;
            fill: #000000 !important;
        }
        .sectionTitle, .section-title text {
            font-size: 14px !important;
            font-weight: bold !important;
            fill: #000000 !important;
        }
        .actor text {
            font-size: 12px !important;
            font-weight: normal !important;
            fill: #000000 !important;
        }
        .messageText, .message-text text {
            font-size: 11px !important;
            fill: #333333 !important;
        }
        /* Ensure shapes are visible */
        rect, circle, ellipse, path {
            stroke: #333333 !important;
            stroke-width: 1.5px !important;
        }
        .node rect, .node circle, .node ellipse {
            fill: #ffffff !important;
            stroke: #333333 !important;
            stroke-width: 2px !important;
        }
        .edgePath path, .edge-path path {
            stroke: #666666 !important;
            stroke-width: 2px !important;
            fill: none !important;
        }
    ]]></style>
    </defs>
    '''
    
    # Insert CSS after opening <svg> tag
    svg_content = re.sub(r'(<svg[^>]*>)', r'\1' + css_styles, svg_content)
    
    # Also ensure text content is preserved by checking for empty text elements
    def ensure_text_content(match):
        full_match = match.group(0)
        if '></text>' in full_match:  # Empty text element
            # Try to find content in title or other attributes
            if 'title=' in full_match:
                title_match = re.search(r'title="([^"]*)"', full_match)
                if title_match:
                    content = title_match.group(1)
                    full_match = full_match.replace('></text>', f'>{content}</text>')
        return full_match
    
    svg_content = re.sub(r'<text[^>]*>.*?</text>', ensure_text_content, svg_content, flags=re.DOTALL)
    
    return svg_content

def enhance_svg_for_text_visibility(svg_content):
    """Enhanced function to make text visible in SVGs with missing text content."""
    import re
    
    print(f"    Enhancing SVG for text visibility...")
    
    # The main issue: Convert foreignObject text to native SVG text elements
    def convert_foreign_object_to_text(match):
        foreign_obj = match.group(0)
        
        # Extract the transform attribute from parent g element if present
        parent_transform = re.search(r'<g[^>]*transform="translate\(([^)]+)\)"[^>]*>', svg_content[:match.start()])
        x_offset, y_offset = 0, 0
        if parent_transform:
            coords = parent_transform.group(1).split(',')
            if len(coords) >= 2:
                x_offset = float(coords[0].strip())
                y_offset = float(coords[1].strip())
        
        # Extract text content from nested HTML
        text_content = None
        
        # Look for text in various HTML structures
        p_match = re.search(r'<p[^>]*>([^<]+)</p>', foreign_obj)
        span_match = re.search(r'<span[^>]*>([^<]+)</span>', foreign_obj)
        div_match = re.search(r'<div[^>]*>([^<]+)</div>', foreign_obj)
        
        if p_match:
            text_content = p_match.group(1).strip()
        elif span_match:
            text_content = span_match.group(1).strip()
        elif div_match:
            text_content = div_match.group(1).strip()
        
        if text_content and len(text_content) > 0:
            # Create native SVG text element
            text_element = f'''<text x="{x_offset}" y="{y_offset}" 
                font-family="Arial, sans-serif" 
                font-size="12" 
                fill="#333333" 
                text-anchor="middle" 
                dominant-baseline="central">{text_content}</text>'''
            
            print(f"    Converted foreignObject text: '{text_content}'")
            return text_element
        
        return foreign_obj
    
    # Replace all foreignObject elements
    svg_content = re.sub(
        r'<foreignObject[^>]*>.*?</foreignObject>', 
        convert_foreign_object_to_text, 
        svg_content, 
        flags=re.DOTALL
    )
    
    # Also look for g elements with labels and convert them to text
    def convert_label_group_to_text(match):
        group_element = match.group(0)
        
        # Extract transform translate values
        transform_match = re.search(r'transform="translate\(([^)]+)\)"', group_element)
        x, y = 0, 0
        if transform_match:
            coords = transform_match.group(1).split(',')
            if len(coords) >= 2:
                x = float(coords[0].strip())
                y = float(coords[1].strip())
        
        # Look for text content in nested elements
        text_matches = re.findall(r'>([^<]+)</', group_element)
        meaningful_text = [text.strip() for text in text_matches 
                          if text.strip() and len(text.strip()) > 1 
                          and not text.strip().startswith('#')
                          and 'font-family' not in text.strip()]
        
        if meaningful_text:
            text_content = meaningful_text[0]  # Take the first meaningful text
            text_element = f'''<text x="{x}" y="{y}" 
                font-family="Arial, sans-serif" 
                font-size="12" 
                fill="#333333" 
                text-anchor="middle" 
                dominant-baseline="central">{text_content}</text>'''
            
            print(f"    Converted label group text: '{text_content}'")
            return group_element + text_element
        
        return group_element
    
    # Apply to label groups
    svg_content = re.sub(
        r'<g class="label"[^>]*>.*?</g>', 
        convert_label_group_to_text, 
        svg_content, 
        flags=re.DOTALL
    )
    
    # Force all existing text elements to be visible
    def force_text_visibility(match):
        text_element = match.group(0)
        # Ensure it has proper styling
        if 'font-family' not in text_element:
            text_element = text_element.replace('<text', '<text font-family="Arial, sans-serif"')
        if 'font-size' not in text_element:
            text_element = text_element.replace('<text', '<text font-size="12px"')
        if 'fill=' not in text_element and 'style=' not in text_element:
            text_element = text_element.replace('<text', '<text fill="#333333"')
        # Remove any opacity that might hide text
        text_element = re.sub(r'opacity="[^"]*"', '', text_element)
        text_element = re.sub(r'fill-opacity="[^"]*"', '', text_element)
        return text_element
    
    svg_content = re.sub(r'<text[^>]*>', force_text_visibility, svg_content)
    
    return svg_content

def render_mermaid_with_kroki(mermaid_code):
    """Render Mermaid using Kroki service (online)."""
    try:
        # Encode the diagram for Kroki
        encoded = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('ascii')
        
        # Request SVG from Kroki service
        url = f"https://kroki.io/mermaid/svg/{encoded}"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            svg_content = response.text
            # Fix common SVG text rendering issues
            svg_content = fix_svg_text_rendering(svg_content)
            return svg_content
        else:
            print(f"Kroki service failed with status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error using Kroki service: {e}")
        return None

def render_mermaid_with_mermaid_ink(mermaid_code):
    """Render Mermaid using mermaid.ink service (online)."""
    try:
        # Encode the diagram for mermaid.ink
        encoded = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('ascii')
        
        # Request SVG from mermaid.ink with additional parameters for text rendering
        url = f"https://mermaid.ink/svg/{encoded}?theme=default&backgroundColor=white"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            svg_content = response.text
            # Fix common SVG text rendering issues
            svg_content = fix_svg_text_rendering(svg_content)
            return svg_content
        else:
            print(f"Mermaid.ink service failed with status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error using mermaid.ink service: {e}")
        return None

def render_mermaid_with_quickchart(mermaid_code):
    """Render Mermaid using QuickChart service (alternative)."""
    try:
        import json
        
        # Prepare the request for QuickChart
        chart_config = {
            "chart": {
                "type": "graphviz",
                "data": mermaid_code
            },
            "format": "svg",
            "width": 800,
            "height": 600,
            "backgroundColor": "#ffffff"
        }
        
        url = "https://quickchart.io/chart"
        response = requests.post(
            url,
            json=chart_config,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            svg_content = response.text
            if '<svg' in svg_content:
                svg_content = fix_svg_text_rendering(svg_content)
                return svg_content
        
        print(f"QuickChart service failed with status: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"Error using QuickChart service: {e}")
        return None

def create_styled_mermaid_fallback(mermaid_code, index):
    """Create a nicely styled fallback for Mermaid diagrams."""
    # Add visual indicators to make it clear this is a diagram
    styled_code = f"""
<div class="mermaid-fallback">
    <div class="mermaid-header">📊 Mermaid Diagram #{index}</div>
    <pre class="mermaid-code"><code>{mermaid_code}</code></pre>
    <div class="mermaid-note">Note: This diagram would be rendered visually in a Mermaid-compatible viewer</div>
</div>
"""
    return styled_code

def split_complex_diagram(mermaid_code):
    """Split very complex diagrams into smaller, renderable parts."""
    lines = mermaid_code.strip().split('\n')
    
    # Check if this is the large API architecture diagram
    if ('Client Applications' in mermaid_code and 
        'BK8520 REST API Server' in mermaid_code and
        len(lines) > 80):
        
        print("    Creating simplified architecture overview...")
        
        # Create a high-level overview diagram
        simplified_diagram = '''graph TB
    subgraph "Client Layer"
        CLIENTS[Web, Python, cURL, JS Clients]
    end
    
    subgraph "API Layer"
        HEALTH[Health & System APIs]
        DEVICE_MGMT[Device Management APIs]
        DEVICE_CTRL[Device Control APIs] 
        BATTERY[Battery Testing APIs]
    end
    
    subgraph "Hardware Layer"
        BK8520[BK8520 Electronic Load<br/>Serial: /dev/ttyUSB0<br/>Max: 120V, 60A, 999W]
    end
    
    CLIENTS --> HEALTH
    CLIENTS --> DEVICE_MGMT
    CLIENTS --> DEVICE_CTRL
    CLIENTS --> BATTERY
    
    HEALTH --> BK8520
    DEVICE_MGMT --> BK8520
    DEVICE_CTRL --> BK8520
    BATTERY --> BK8520
    
    classDef client fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef api fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef hardware fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    
    class CLIENTS client
    class HEALTH,DEVICE_MGMT,DEVICE_CTRL,BATTERY api
    class BK8520 hardware'''
        
        return simplified_diagram
    
    return simplify_large_mermaid_diagram(mermaid_code)

def simplify_large_mermaid_diagram(mermaid_code):
    """Simplify large mermaid diagrams by reducing complexity."""
    lines = mermaid_code.strip().split('\n')
    
    # If diagram is too large, try to simplify
    if len(lines) > 50 or len(mermaid_code) > 3000:
        print("    Large diagram detected, attempting simplification...")
        
        simplified_lines = []
        for line in lines:
            # Skip styling and class definitions to reduce complexity
            if line.strip().startswith('classDef') or line.strip().startswith('class '):
                continue
                
            # Keep essential structure but simplify labels
            if '-->' in line or '--->' in line:
                # Simplify connection labels
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) > 2:
                        # Keep first and last part, simplify middle
                        line = f"{parts[0]}|...|{parts[-1]}"
            
            # Simplify long node labels and remove emojis
            if '[' in line and ']' in line:
                # Extract node definition and simplify
                start = line.find('[')
                end = line.rfind(']')
                if end - start > 50:  # Long label
                    before = line[:start+1]
                    after = line[end:]
                    middle = line[start+1:end]
                    
                    # Remove emojis and clean up
                    import re
                    middle = re.sub(r'[📊📋ℹ️⚡⚙️🛡️🔋🛑📈📡🔌]', '', middle)
                    
                    # Truncate long labels
                    if '<br/>' in middle:
                        parts = middle.split('<br/>')
                        # Take first meaningful part
                        main_part = parts[0].strip()
                        if len(main_part) > 30:
                            main_part = main_part[:30] + '...'
                        middle = main_part
                    else:
                        middle = middle[:40] + '...' if len(middle) > 40 else middle
                    
                    line = before + middle + after
            
            simplified_lines.append(line)
        
        return '\n'.join(simplified_lines)
    
    return mermaid_code

def process_mermaid_blocks(content):
    """Find and replace Mermaid code blocks with rendered SVGs or styled fallbacks."""
    
    # Pattern to match Mermaid code blocks
    pattern = r'```mermaid\n(.*?)\n```'
    
    def replace_mermaid(match):
        mermaid_code = match.group(1).strip()
        index = replace_mermaid.counter
        replace_mermaid.counter += 1
        
        print(f"  Processing Mermaid diagram {index}...")
        
        # Try to split complex diagrams or simplify large ones
        simplified_code = split_complex_diagram(mermaid_code)
        
        # Try different rendering methods with debugging
        svg = None
        
        # Method 1: Try mermaid.ink service first (often more reliable)
        if not svg:
            print(f"    Trying mermaid.ink service...")
            svg = render_mermaid_with_mermaid_ink(simplified_code)
            if svg and len(svg) > 100:
                print(f"    Got SVG from mermaid.ink ({len(svg)} chars)")
        
        # Method 2: Try Kroki service
        if not svg:
            print(f"    Trying Kroki service...")
            svg = render_mermaid_with_kroki(simplified_code)
            if svg and len(svg) > 100:
                print(f"    Got SVG from Kroki ({len(svg)} chars)")
        
        # Method 3: Try QuickChart service  
        if not svg:
            print(f"    Trying QuickChart service...")
            svg = render_mermaid_with_quickchart(simplified_code)
            if svg and len(svg) > 100:
                print(f"    Got SVG from QuickChart ({len(svg)} chars)")
        
        if svg and svg.strip() and '<svg' in svg:
            # Verify text content exists (check for various text formats)
            import re
            simple_text = re.findall(r'<text[^>]*>([^<]+)</text>', svg)
            tspan_text = re.findall(r'<tspan[^>]*>([^<]+)</tspan>', svg)
            all_text_content = simple_text + tspan_text
            print(f"    Found {len(simple_text)} simple text + {len(tspan_text)} tspan elements")
            
            # If no text found, try to enhance the SVG
            if len(all_text_content) == 0:
                print(f"    No text content detected, applying enhanced fixes...")
                svg = enhance_svg_for_text_visibility(svg)
            
            # Clean up SVG and embed
            svg_clean = svg.strip()
            print(f"    ✅ Successfully rendered diagram {index}")
            return f'<div class="mermaid-diagram">{svg_clean}</div>'
        else:
            # Fallback to styled code block
            print(f"    ⚠️  Using styled fallback for diagram {index}")
            return create_styled_mermaid_fallback(mermaid_code, index)
    
    replace_mermaid.counter = 1
    
    # Replace all Mermaid blocks
    processed = re.sub(pattern, replace_mermaid, content, flags=re.DOTALL)
    
    return processed

def create_enhanced_html_template(content, title="BK8520 API Diagram Documentation"):
    """Create HTML template with enhanced Mermaid support."""
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
                margin: 1.5cm;
                @bottom-center {{
                    content: "Page " counter(page);
                }}
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 100%;
                margin: 0;
                padding: 15px;
                background: white;
            }}
            
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                margin: 30px 0 20px 0;
                font-size: 24px;
            }}
            
            h2 {{
                color: #34495e;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 8px;
                margin: 25px 0 15px 0;
                font-size: 20px;
                page-break-after: avoid;
            }}
            
            h3 {{
                color: #7f8c8d;
                margin: 20px 0 10px 0;
                font-size: 16px;
                page-break-after: avoid;
            }}
            
            /* Mermaid diagrams */
            .mermaid-diagram {{
                margin: 15px 0;
                text-align: center;
                page-break-inside: avoid;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }}
            
            .mermaid-diagram svg {{
                max-width: 100%;
                height: auto;
                background: white;
                border-radius: 4px;
            }}
            
            /* Mermaid fallback styling */
            .mermaid-fallback {{
                margin: 15px 0;
                page-break-inside: avoid;
                border: 2px dashed #3498db;
                border-radius: 8px;
                background: #f0f8ff;
            }}
            
            .mermaid-header {{
                background: #3498db;
                color: white;
                padding: 8px 15px;
                font-weight: bold;
                border-radius: 6px 6px 0 0;
                margin: -1px -1px 0 -1px;
            }}
            
            .mermaid-code {{
                background: #f8f9fa;
                border: none;
                margin: 10px;
                padding: 15px;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                line-height: 1.4;
                overflow-x: auto;
            }}
            
            .mermaid-note {{
                font-style: italic;
                color: #666;
                padding: 8px 15px;
                font-size: 12px;
                background: #e8f4fd;
                margin: 0 10px 10px 10px;
                border-radius: 4px;
            }}
            
            /* Regular code blocks */
            pre {{
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 12px;
                overflow-x: auto;
                page-break-inside: avoid;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                line-height: 1.4;
                margin: 15px 0;
            }}
            
            code {{
                background-color: #f8f9fa;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 13px;
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
                margin: 15px 0;
                page-break-inside: avoid;
                font-size: 13px;
            }}
            
            th, td {{
                border: 1px solid #ddd;
                padding: 8px 12px;
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
                margin: 10px 0;
                padding-left: 25px;
            }}
            
            li {{
                margin: 3px 0;
            }}
            
            /* Print-specific styles */
            @media print {{
                body {{
                    font-size: 11pt;
                    line-height: 1.4;
                }}
                
                h1 {{ font-size: 16pt; }}
                h2 {{ font-size: 14pt; }}
                h3 {{ font-size: 12pt; }}
                
                .mermaid-diagram, .mermaid-fallback {{
                    background: white;
                    border: 2px solid #ccc;
                    break-inside: avoid;
                }}
                
                pre {{ font-size: 9pt; }}
                table {{ font-size: 10pt; }}
                
                h1, h2, h3, h4, h5, h6 {{
                    page-break-after: avoid;
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

def generate_pdf_with_simple_mermaid(input_file, output_file=None):
    """Generate PDF from markdown with simple Mermaid support."""
    try:
        import markdown
        from weasyprint import HTML
    except ImportError:
        print("Installing required packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'markdown', 'weasyprint', 'requests'], check=True)
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
        'markdown.extensions.attr_list',
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
        description='Convert markdown to PDF with simple Mermaid diagram support'
    )
    parser.add_argument(
        'input',
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
        generate_pdf_with_simple_mermaid(args.input, args.output)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()