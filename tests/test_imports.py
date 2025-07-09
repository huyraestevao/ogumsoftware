import importlib
import pytest


@pytest.mark.parametrize("m", ["ogum.core", "ogum.utils"])
def test_imports(m):
    """Ensure all public modules can be imported without side effects."""
    assert importlib.import_module(m)
