# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import re
import os
import subprocess
import sphinx_rtd_theme

def get_git_version():
    """Return the short and long versions from git describe or return unknown"""
    try:
        version = subprocess.check_output(["git", "describe", "--tags", "--always"]).strip().decode("utf-8")

        # Extract only the first two version numbers (e.g., "1.2" from "v1.2.3")
        match = re.match(r"v?(\d+\.\d+)", version)
        short_version = match.group(1) if match else version  # Default to base_version if no match

        return short_version, version
    except Exception:
        return "unknown"

def get_context():
    """Return the current RTD version or git branch name"""
    try:
        git_context = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        ).strip().decode("utf-8")

        # Check for RTD version, default to git_version if not on RTD
        context = os.getenv("READTHEDOCS_VERSION", git_context)

        return context
    except Exception:
        return ""

# -- Project information -----------------------------------------------------

project = 'SeedLink'
copyright = '2024, International FDSN'
author = 'FDSN'

# Set the short (major.minor) version and full release values
version, release = get_git_version()

# -- General configuration ---------------------------------------------------

# Default in Sphinx 2, but not in older versions
master_doc = 'index'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
  'sphinx_rtd_theme',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['docs', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'sticky_navigation': False,
}

html_logo='_static/FDSN-logo.png'
html_favicon = '_static/favicon.ico'
html_title = 'SeedLink'
html_show_sphinx = False
html_search_language = 'en'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_css_files = [
  'css/fdsn_rtd_theme.css',
]

html_js_files = [
  'js/sidebar_context.js'
]

# Enable sphinxmark for draft documentation
if get_context() == "draft":
    extensions.append("sphinxmark")
    sphinxmark_enable = True
    sphinxmark_div = "document"
