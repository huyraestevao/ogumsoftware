import importlib
import os
import sys
import pytest

# Ensure the project root is on sys.path so imports of the ogum package work
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
@pytest.mark.parametrize('m', [
    'ogum.core', 'ogum.ogum64', 'ogum.ogum72', 'ogum.ogum80'
])
def test_imports(m):
    assert importlib.import_module(m)
