#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import pwv_kpno

# Sphinx extensions / features
extensions = [
    'sphinx.ext.autodoc',  # Auto-documentation
    'sphinx.ext.viewcode',  # Adds links to source code
    'sphinx.ext.napoleon',  # Adds support for google doc style
    'sphinx.ext.mathjax',  # For rendering mathematical equations
    'sphinx.ext.autosectionlabel',  # Auto generates section labels
    'sphinxcontrib.fulltoc',  # Adds full table contents to side bar
    'sphinx_copybutton'  # Adds copy button to demo code
]

# Rendering settings
templates_path = ['./templates']
autosectionlabel_prefix_document = True  # Add file name prefix to section labels
source_suffix = ['.rst']  # The suffixes of source files
master_doc = 'source/index'  # Document with master table of contents
pygments_style = 'sphinx'  # Syntax highlighting style
highlight_language = 'python3'
html_static_path = ['./static/']

# General project meta data
project = 'pwv_kpno'
copyright = '2018, MWV Research Group'
author = 'Daniel J. Perrefort'
version = pwv_kpno.__version__
release = pwv_kpno.__version__

# Specify theme specific settings
html_theme = 'bootstrap'
links = [
    ("Quick Start", "source/quick_start.html", 1),
    ("API Documentation", "source/api/pwv_kpno.html", 1),
    ("Examples", "source/examples/correcting_photometry.html", 1),
    ("Validation", "source/validation/overview.html", 1),
    ("Need Help?", "https://github.com/mwvgroup/pwv_kpno/issues/new/choose", 1),
    ("Source Code", "https://github.com/mwvgroup/pwv_kpno", 1)
]

html_theme_options = {
    'navbar_sidebarrel': False,  # Disable next / last page buttons in nav bar
    'navbar_links': links,  # Specifies custom nav bar links
    'bootswatch_theme': "flatly",
    'source_link_position': "footer"
}

html_sidebars = {
    '**': ['localtoc.html'],
    'source/index': None
}


# Add custom css code
def setup(app):
    app.add_stylesheet('css/custom_style.css')
