import importlib
import pytest

MODULES = [
    "ogum",
    "ogum.core",
    "ogum.utils",
    "ogum.sovs",
    "ogum.fem_interface",
    "ogum.processing",
]


@pytest.mark.parametrize("module_name", MODULES)
def test_import_module(module_name):
    """Modules should import without raising exceptions."""
    importlib.import_module(module_name)
