from typing import Any


def create_unit_mesh(mesh_size: float) -> Any:
    """Create a simple unit mesh using FEniCSx.

    Args:
        mesh_size: Desired element size of the mesh.

    Returns:
        A mesh object from FEniCSx.
    """
    # TODO: implement proper mesh generation
    raise NotImplementedError("FEM integration pending")


__all__ = ["create_unit_mesh"]
