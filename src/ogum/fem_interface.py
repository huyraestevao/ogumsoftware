"""Interface utilities for running finite element simulations."""

from typing import Any, Callable, List, Tuple
from threading import Thread
import numpy as np


def create_unit_mesh(mesh_size: float) -> Any:
    """Gera uma malha unitária quadrada de passo `mesh_size` usando FEniCSx."""
    try:
        from mpi4py import MPI
        from dolfinx.mesh import create_rectangle, CellType
    except (ImportError, OSError) as exc:
        raise ModuleNotFoundError("FEniCSx ou mpi4py não instalado") from exc
    domain = [[0.0, 0.0], [1.0, 1.0]]
    n = max(1, int(1.0 / mesh_size))
    mesh = create_rectangle(MPI.COMM_WORLD, domain, [n, n], CellType.triangle)
    return mesh


def densify_mesh(
    mesh,
    temperature_history: List[Tuple[float, float]],
    Ea: float,
    A: float,
    solver_options: dict | None = None,
) -> np.ndarray:
    """Resolve a densificação via ``SOVSSolver`` em cada célula da malha."""
    from ogum.sovs import SOVSSolver
    times, temps_c = zip(*temperature_history)
    temps_k = np.array(temps_c, dtype=float) + 273.15
    times_arr = np.asarray(times, dtype=float)
    solver = SOVSSolver(Ea=Ea, A=A, **(solver_options or {}))
    num_cells = mesh.topology.index_map(mesh.topology.dim).size_local
    densities = np.empty(num_cells)
    for i in range(num_cells):
        rho = solver.solve(times_arr, temps_k)
        densities[i] = rho[-1]
    return np.array(densities)


def densify_mesh_async(
    mesh: Any,
    temperature_history: List[Tuple[float, float]],
    Ea: float,
    A: float,
    solver_options: dict | None = None,
    callback: Callable | None = None,
) -> tuple[Thread, dict]:
    """Execute :func:`densify_mesh` in a separate thread."""
    result: dict = {"densities": None, "error": None}
    def _target() -> None:
        try:
            result["densities"] = densify_mesh(
                mesh, temperature_history, Ea, A, solver_options
            )
        except Exception as exc:
            result["error"] = exc
        if callback is not None:
            callback(result)
    thread = Thread(target=_target, daemon=True)
    thread.start()
    return thread, result


__all__ = ["create_unit_mesh", "densify_mesh", "densify_mesh_async"]
