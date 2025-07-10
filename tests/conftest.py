"""Pytest configuration with lightweight stubs for optional GUI modules."""

import sys
from pathlib import Path
import types

# Ensure project root is on sys.path so test modules can import ``ogum``.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Provide minimal stubs for optional GUI dependencies so that modules importing
# them do not fail during tests.

if "IPython.display" not in sys.modules:
    display_mod = types.ModuleType("IPython.display")

    def display(*args, **kwargs):
        pass

    class HTML(str):
        pass

    def clear_output(*args, **kwargs):
        pass

    display_mod.display = display
    display_mod.HTML = HTML
    display_mod.clear_output = clear_output
    sys.modules["IPython.display"] = display_mod

if "ipywidgets" not in sys.modules:

    class DummyModule(types.ModuleType):
        class Dummy:
            def __init__(self, *args, **kwargs):
                pass

            def __call__(self, *args, **kwargs):
                return self

            def __getattr__(self, name):
                def method(*args, **kwargs):
                    return None

                return method

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        def __getattr__(self, name):
            return self.Dummy

    widgets_mod = DummyModule("ipywidgets")
    sys.modules["ipywidgets"] = widgets_mod
