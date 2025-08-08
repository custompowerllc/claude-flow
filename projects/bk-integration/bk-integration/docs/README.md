# BK Integration Documentation

## Overview

This directory contains comprehensive documentation for the BK Precision device integration project, including API documentation, diagrams, and development tools.

## Directory Structure

```
docs/
├── api/                    # API Documentation
├── diagrams/              # Visual diagrams and charts  
├── tools/                 # Generation and build tools
├── archive/               # Historical versions and deprecated files
├── doc-changelog.md       # Documentation change history
└── README.md             # This navigation guide
```

## 📚 API Documentation

**Location**: `./api/`

- **`bk8520-api-documentation.md`** - BK8520 Electronic Load REST API
- **`bk9206b-api-documentation.md`** - BK9206B Power Supply REST API  
- **`bk-integration-overview.md`** - Project integration overview

## 🎨 Diagrams & Visualizations

**Location**: `./diagrams/`

- **`bk8520-api-diagram-final.html`** - Interactive BK8520 API flow chart
- **`bk8520-api-diagram-final.pdf`** - Printable BK8520 API diagram
- **`bk-integration-mermaid-enhanced.html`** - Enhanced integration flow
- **`bk-integration-mermaid-fixed.pdf`** - Integration architecture diagram
- **`bk-integration-mermaid.md`** - Mermaid source for integration diagrams

## 🛠️ Development Tools

**Location**: `./tools/`

- **`generate_pdf_mermaid.py`** - PDF generation from Mermaid diagrams
- **`mermaid_renderer.js`** - JavaScript Mermaid rendering engine
- **`pdf_requirements.txt`** - Python dependencies for PDF generation

## 📋 Quick Access

### Getting Started
1. Review **API documentation** in `./api/` folder
2. View **system diagrams** in `./diagrams/` for architecture understanding  
3. Use **generation tools** in `./tools/` for creating new documentation

### For Developers
- **BK8520 Integration**: Start with `api/bk8520-api-documentation.md`
- **BK9206B Integration**: Start with `api/bk9206b-api-documentation.md`
- **System Architecture**: View `diagrams/bk-integration-mermaid-enhanced.html`

### For Documentation Updates
- Use tools in `./tools/` directory
- Follow naming convention: `device-purpose-version.extension`
- Update this README when adding new major documentation

## 🗂️ Archive

The `./archive/` directory contains historical versions and deprecated files for reference. These files are preserved for version history but are not part of the active documentation set.

---

**Last Updated**: January 2025  
**Maintained By**: SuperClaude Documentation System