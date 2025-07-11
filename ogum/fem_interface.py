"""Interface utilities for running finite element simulations."""

from typing import Any, List, Tuple

import numpy as np


def create_unit_mesh(mesh_size: float) -> Any:
    """Gera uma malha unitária quadrada de passo `mesh_size` usando FEniCSx.

    Args:
        mesh_size: tamanho do elemento de malha (ex.: 0.1 para 10×10 células).

    Returns:
        Mesh do Dolfinx.
    """
    try:
        from mpi4py import MPI
        from dolfinx.mesh import create_rectangle, CellType
    except ImportError as exc:
        raise ModuleNotFoundError("FEniCSx ou mpi4py não instalado") from exc

    domain = [[0.0, 0.0], [1.0, 1.0]]
    n = max(1, int(1.0 / mesh_size))
    mesh = create_rectangle(MPI.COMM_WORLD, domain, [n, n], CellType.triangle)
    return mesh


def densify_mesh(
    mesh,
    temperature_history: List[Tuple[float, float]],
    solver_options: dict | None = None,
) -> np.ndarray:
    """Resolve a densificação via ``SOVSSolver`` em cada célula da malha.

    Parameters
    ----------
    mesh : dolfinx.mesh.Mesh
        A malha triangular unitária ou gerada pelo ``create_unit_mesh``.
    temperature_history : list of (time_s, temp_C)
        Sequência de pares ``(tempo em s, temperatura em \N{DEGREE CELSIUS})``
        que definem ``T(t)``.
    solver_options : dict, optional
        Parâmetros adicionais para ``SOVSSolver``.

    Returns:
    -------
    np.ndarray
        Array de densidade final para cada célula da malha.
    """
    from ogum.sovs import SOVSSolver
    import numpy as np

    times, temps_c = zip(*temperature_history)
    temps_k = np.array(temps_c, dtype=float) + 273.15
    times_arr = np.asarray(times, dtype=float)

    solver = SOVSSolver(**(solver_options or {}))

    num_cells = mesh.topology.index_map(mesh.topology.dim).size_local
    densities = []
    for _ in range(num_cells):
        rho = solver.solve(times_arr, temps_k)
        densities.append(rho[-1])

    return np.array(densities)
