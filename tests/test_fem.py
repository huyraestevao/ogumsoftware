import pytest

from ogum.fem_interface import create_unit_mesh


def test_fem_stub():
    with pytest.raises(ModuleNotFoundError):
        create_unit_mesh(1.0)
