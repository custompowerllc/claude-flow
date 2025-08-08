"""Sphinx configuration for GEHC PHTC Test Application documentation."""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Project information
project = "GEHC PHTC Test Application"
copyright = f"{datetime.now().year}, GEHC Development Team"
author = "GEHC Development Team"

# Version information
try:
    from gehc_phtc_test import __version__
    version = __version__
    release = __version__
except ImportError:
    version = "1.0.0"
    release = "1.0.0"

# Extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.todo",
    "myst_parser",
]

# Source file extensions
source_suffix = {
    ".rst": None,
    ".md": None,
}

# Master document
master_doc = "index"

# Language
language = "en"

# Exclude patterns
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# HTML theme
html_theme = "sphinx_rtd_theme"

# HTML theme options
html_theme_options = {
    "canonical_url": "",
    "analytics_id": "",
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "vcs_pageview_mode": "",
    "style_nav_header_background": "white",
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

# HTML static files
html_static_path = ["_static"]

# HTML context
html_context = {
    "display_github": True,
    "github_user": "gehc",
    "github_repo": "phtc-test",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

# Custom sidebar templates
html_sidebars = {
    "**": [
        "relations.html",
        "searchbox.html",
    ]
}

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pyserial": ("https://pyserial.readthedocs.io/en/latest/", None),
    "rich": ("https://rich.readthedocs.io/en/stable/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
    "click": ("https://click.palletsprojects.com/en/8.1.x/", None),
}

# Todo extension settings
todo_include_todos = True

# Coverage settings
coverage_show_missing_items = True