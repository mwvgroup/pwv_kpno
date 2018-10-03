#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Sphinx extensions / features
extensions = [
    'sphinx.ext.autodoc',           # Auto-documentation
    'sphinx.ext.viewcode',          # Adds links to source code
    'sphinx.ext.napoleon',          # Adds support for google doc style
    'sphinx.ext.mathjax',           # For rendering mathematical equations
    'sphinx.ext.autosectionlabel',  # Auto generates section labels
    'sphinxcontrib.fulltoc'         # Adds full table pf contents to side bar
    ]

# Rendering settings
templates_path = ['../templates', './local_templates']
autosectionlabel_prefix_document = True  # Add file name prefix to section labels
source_suffix = ['.rst']                 # The suffixes of source files
master_doc = 'index'                     # Document with master table of contents
exclude_patterns = ['.DS_Store']         # File patterns to ignore
pygments_style = 'sphinx'                # Syntax highlighting style
highlight_language = 'python3'
html_static_path = ['../custom_style.css']

# General project meta data
from pwv_kpno import __version__ as pk_version
project = 'pwv_kpno'
copyright = '2018, Daniel J. Perrefort'
author = 'Daniel J. Perrefort'
version = pk_version
release = pk_version

# Specify theme specific settings
html_theme = 'bootstrap'
links = [
    ("Documentation", "../../documentation/html/install.html", 1),
    ("Examples", "../../examples/html/correcting_spectra.html", 1),
    ("Validation", "../../validation/html/overview.html", 1),
    ("Need Help?", "https://github.com/mwvgroup/pwv_kpno/issues/new/choose", 1),
    ("Source Code", "https://github.com/mwvgroup/pwv_kpno", 1)
]

html_theme_options = {
    'navbar_sidebarrel': False,  # Disable next / last page buttons in nav bar
    'navbar_links': links,       # Specifies custom nav bar links

    'bootswatch_theme': "cosmo",
    'navbar_class': "navbar navbar-inverse",  # Invert nav bar color
    'source_link_position': "footer"
}

# Set default sidebar options
# These will be overwritten by the custom_toc extension
html_sidebars = {'**': ['localtoc.html'], 'search': []}


# Add custom css code
def setup(app):
    app.add_stylesheet("custom_style.css")
