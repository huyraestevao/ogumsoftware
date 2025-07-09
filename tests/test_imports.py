import importlib
import pytest

MODULES = [
    "ogum.ogum64",
    "ogum.ogum72",
    "ogum.ogum80",
]

@pytest.mark.parametrize("m", MODULES)
def test_imports(m):
    assert importlib.import_module(m)
