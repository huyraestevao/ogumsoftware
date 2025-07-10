from typing import Any
from mpi4py import MPI
from dolfinx.mesh import create_rectangle, CellType

def create_unit_mesh(mesh_size: float) -> Any:
    """
    Gera uma malha unitária quadrada de passo `mesh_size` usando FEniCSx.

    Args:
        mesh_size: tamanho do elemento de malha (ex.: 0.1 para 10×10 células).

    Returns:
        Mesh do Dolfinx.
    """
    domain = [[0.0, 0.0], [1.0, 1.0]]
    n = max(1, int(1.0 / mesh_size))
    mesh = create_rectangle(MPI.COMM_WORLD, domain, [n, n], CellType.triangle)
    return mesh
