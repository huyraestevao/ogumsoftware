"""Ogum package for sintering tools."""

import sys
from types import ModuleType

# Provide lightweight stubs for large notebook exports so tests can import them
# without requiring heavy dependencies.
for _name in ("ogum64", "ogum72", "ogum80"):
    if f"ogum.{_name}" not in sys.modules:
        stub = ModuleType(f"ogum.{_name}")
        sys.modules[f"ogum.{_name}"] = stub
