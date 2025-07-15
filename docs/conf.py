import os
import sys

sys.path.insert(0, os.path.abspath('../src'))

from ogum import __version__

project = "Ogum Sintering Suite"

version = __version__
release = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
]

autosummary_generate = True

html_theme = "alabaster"
