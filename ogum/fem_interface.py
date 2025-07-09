from typing import Any


def create_unit_mesh(mesh_size: float) -> Any:
    """Create a simple unit mesh using FEniCSx.

    Args:
        mesh_size: Desired element size of the mesh.

    Returns:
        A mesh object from FEniCSx.
    """
    from fenicsx.mesh import create_unit_square  # type: ignore
    # TODO: implement proper mesh generation
    pass
