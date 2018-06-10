#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Specify extensions / features
extensions = ['sphinx.ext.autodoc',      # Auto-documentation
              'sphinx.ext.viewcode',     # Adds links to source code
              'sphinx.ext.napoleon',     # Adds support for google doc style
              'sphinx.ext.mathjax',      # For rendering mathematical equations
              'sphinx.ext.autosectionlabel']  # Auto generates section labels

# adds file name as prefix to all section labels
autosectionlabel_prefix_document = True

# The suffixes of source files
source_suffix = ['.rst']

# The document containing the master table of contents
master_doc = 'index'

# General information about the project
project = 'pwv_kpno'
copyright = '2018, Daniel J. Perrefort'
author = 'Daniel J. Perrefort'
highlight_language = 'python3'

# The version info for the project
from pwv_kpno import __version__ as pk_version
version = pk_version
release = pk_version

# Patterns relative to source directory to ignore
exclude_patterns = ['.build', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# The theme to use for HTML and HTML Help pages.
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 2,  # Depth of the headers shown in the navigation bar
}

# Paths that contain custom static files
html_static_path = ['LOGO.png']
