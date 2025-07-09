import importlib
import pytest


@pytest.mark.parametrize("module", ["ogum", "ogum.core", "ogum.utils"])
def test_imports(module):
    assert importlib.import_module(module)

