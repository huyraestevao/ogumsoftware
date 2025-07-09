import importlib
import sys
import types
import pytest


def _has_module(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except ModuleNotFoundError:
        return False


@pytest.fixture(autouse=True)
def _stub_dependencies(monkeypatch):
    """Provide lightweight stubs for optional dependencies."""
    if not _has_module("ipywidgets"):
        widgets = types.ModuleType("ipywidgets")
        class Dummy:  # noqa: D401 - simple placeholder
            """Placeholder class used in tests."""
            pass
        widgets.HTML = Dummy
        widgets.Accordion = Dummy
        widgets.Widget = Dummy
        monkeypatch.setitem(sys.modules, "ipywidgets", widgets)

    if not _has_module("IPython.display"):
        disp = types.ModuleType("IPython.display")
        def display(*args, **kwargs):
            return None
        class HTML(str):
            pass
        disp.display = display
        disp.HTML = HTML
        monkeypatch.setitem(sys.modules, "IPython.display", disp)


@pytest.mark.parametrize("m", ["ogum.utils"])
def test_imports(m):
    assert importlib.import_module(m)
