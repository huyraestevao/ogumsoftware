import pytest
from ogum.fem_interface import create_unit_mesh


def test_unit_mesh_creation():
    """Ensure the unit mesh has at least two coordinate points when available."""
    try:
        mesh = create_unit_mesh(0.5)
    except ModuleNotFoundError:
        pytest.skip("FEniCSx not installed")
    else:
        assert mesh.geometry.x.shape[0] > 1
