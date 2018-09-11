#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Specify extensions / features
extensions = ['sphinx.ext.autodoc',   # Auto-documentation
              'sphinx.ext.viewcode',  # Adds links to source code
              'sphinx.ext.napoleon',  # Adds support for google doc style
              'sphinx.ext.mathjax',   # For rendering mathematical equations
              'sphinx.ext.autosectionlabel']  # Auto generates section labels


autosectionlabel_prefix_document = True  # Add file name prefix to section labels
source_suffix = ['.rst']  # The suffixes of source files
master_doc = 'index'      # The document with the master table of contents

# General project information
from pwv_kpno import __version__ as pk_version
project = 'pwv_kpno'
copyright = '2018, Daniel J. Perrefort'
author = 'Daniel J. Perrefort'
highlight_language = 'python3'
version = pk_version
release = pk_version

# Relative file patterns to ignore
exclude_patterns = ['.build', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# Paths that contain custom static files
html_static_path = ['LOGO.png', 'custom_style.css']


html_theme = 'bootstrap'
if html_theme == 'sphinx_rtd_theme':
    html_theme_options = {
        'navigation_depth': 2,  # Depth of headers shown in the navigation bar
    }

elif html_theme == 'bootstrap':
    extensions.append('sphinxcontrib.fulltoc')
    links = [
        ("Documentation", "./install.html", 1),
        ("Examples", "./install.html", 1),
        ("Need Help?", "https://github.com/mwvgroup/pwv_kpno/issues/new")
    ]

    html_theme_options = {
        'navigation_depth': 0, # Depth of the headers shown in the navigation bar
        'navbar_pagenav': False,
        'navbar_sidebarrel': False,
        'navbar_links': links,

        'bootswatch_theme': "Cosmo",
        'navbar_class': "navbar navbar-inverse",  # Invert navbar color
        'source_link_position': "footer"
    }

    side_bar_contents = ['localtoc.html']
    pages_with_sidebar = ['install', 'accessing_data', 'atmospheric_modeling',
                          'blackbody_modeling', 'correcting_observations',
                          'modeling_custom_locations']

    html_sidebars = {page: side_bar_contents for page in pages_with_sidebar}


def setup(app):
    app.add_stylesheet("custom_style.css")
