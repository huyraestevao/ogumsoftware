import os
import sys

sys.path.insert(0, os.path.abspath('../../src'))

from ogum import __version__

project = 'Ogum Sintering Suite'
version = release = __version__

extensions = [
    'nbsphinx',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

nbsphinx_execute = 'never'

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'alabaster'
