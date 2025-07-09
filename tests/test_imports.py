import importlib
import pytest


@pytest.mark.parametrize("m", ["ogum", "ogum.core", "ogum.utils"])
def test_imports(m):
    assert importlib.import_module(m)
