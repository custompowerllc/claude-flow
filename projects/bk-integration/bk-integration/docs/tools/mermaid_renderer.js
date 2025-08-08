#!/usr/bin/env node
/**
 * Alternative Mermaid renderer using puppeteer directly
 */

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

async function renderMermaidToSVG(mermaidCode, outputPath) {
    let browser;
    
    try {
        // Launch browser with specific flags to handle Linux environments
        browser = await puppeteer.launch({
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--no-first-run',
                '--no-zygote',
                '--single-process'
            ]
        });
        
        const page = await browser.newPage();
        
        // Create HTML page with Mermaid
        const html = `
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <style>
                body { margin: 0; padding: 20px; background: white; }
                .mermaid { font-family: Arial, sans-serif; }
            </style>
        </head>
        <body>
            <div class="mermaid">${mermaidCode}</div>
            <script>
                mermaid.initialize({
                    startOnLoad: true,
                    theme: 'default',
                    themeVariables: {
                        primaryColor: '#e1f5fe',
                        primaryTextColor: '#333',
                        primaryBorderColor: '#2196F3',
                        lineColor: '#666'
                    }
                });
            </script>
        </body>
        </html>`;
        
        await page.setContent(html);
        await page.waitForSelector('.mermaid svg', { timeout: 10000 });
        
        // Get the SVG element
        const svg = await page.$eval('.mermaid svg', el => el.outerHTML);
        
        // Save SVG to file
        fs.writeFileSync(outputPath, svg);
        console.log(`✓ SVG saved to: ${outputPath}`);
        
        return svg;
        
    } catch (error) {
        console.error('Error rendering Mermaid:', error.message);
        return null;
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// CLI usage
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length !== 2) {
        console.log('Usage: node mermaid_renderer.js <mermaid-code> <output-file>');
        process.exit(1);
    }
    
    const mermaidCode = args[0];
    const outputFile = args[1];
    
    renderMermaidToSVG(mermaidCode, outputFile)
        .then(() => process.exit(0))
        .catch(err => {
            console.error('Failed to render:', err);
            process.exit(1);
        });
}

module.exports = { renderMermaidToSVG };