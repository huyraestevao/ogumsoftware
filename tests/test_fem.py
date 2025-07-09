import pytest

from ogum.fem_interface import create_unit_mesh


def test_fem_stub():
    with pytest.raises(NotImplementedError):
        create_unit_mesh(1.0)
