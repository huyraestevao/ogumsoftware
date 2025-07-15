import os
import sys

sys.path.insert(0, os.path.abspath('../src'))

project = "Ogum Sintering Suite"

from ogum import __version__ as _version
version = release = _version

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
]

autosummary_generate = True
