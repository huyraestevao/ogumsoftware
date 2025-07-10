"""Stub interface for optional FEniCSx integration."""

from typing import Any

try:  # pragma: no cover - optional dependency
    from dolfinx.mesh import create_rectangle, CellType
    from mpi4py import MPI
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    create_rectangle = None  # type: ignore
    CellType = None  # type: ignore
    MPI = None  # type: ignore
    np = None  # type: ignore


def create_unit_mesh(mesh_size: float) -> Any:
    """Create a simple unit mesh using FEniCSx.

    Args:
        mesh_size: Desired element size of the mesh.

    Returns:
        A mesh object from FEniCSx.
    """
    try:
        if None in {create_rectangle, CellType, MPI, np}:
            raise ImportError

        n = int(1 / mesh_size)
        if n < 1:
            n = 1

        return create_rectangle(
            MPI.COMM_WORLD,
            np.array([[0, 0], [1, 1]], dtype=float),
            [n, n],
            CellType.triangle,
        )
    except ImportError as exc:
        raise ModuleNotFoundError("fenicsx not installed") from exc
