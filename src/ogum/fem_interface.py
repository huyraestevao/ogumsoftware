"""Interface utilities for running finite element simulations."""

from typing import Any, Callable, List, Tuple
from threading import Thread

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
    except (ImportError, OSError) as exc:  # pragma: no cover - optional deps
        raise ModuleNotFoundError("FEniCSx ou mpi4py não instalado") from exc

    domain = [[0.0, 0.0], [1.0, 1.0]]
    n = max(1, int(1.0 / mesh_size))
    mesh = create_rectangle(MPI.COMM_WORLD, domain, [n, n], CellType.triangle)
    return mesh


# --- ALTERAÇÃO 1: Adicionar Ea e A como argumentos da função ---
def densify_mesh(
    mesh,
    temperature_history: List[Tuple[float, float]],
    Ea: float,
    A: float,
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
    Ea : float
        Activation energy in kJ/mol.
    A : float
        Pre-exponential factor (1/s).
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

    # --- ALTERAÇÃO 2: Passar os parâmetros ao criar o solver ---
    solver = SOVSSolver(Ea=Ea, A=A, **(solver_options or {}))

    num_cells = mesh.topology.index_map(mesh.topology.dim).size_local
    densities = []
    for _ in range(num_cells):
        rho = solver.solve(times_arr, temps_k)
        densities.append(rho[-1])

    return np.array(densities)


# --- ALTERAÇÃO 3: Atualizar a função assíncrona para também passar Ea e A ---
def densify_mesh_async(
    mesh: Any,
    temperature_history: List[Tuple[float, float]],
    Ea: float,
    A: float,
    solver_options: dict | None = None,
    callback: Callable | None = None,
) -> tuple[Thread, dict]:
    """Execute :func:`densify_mesh` in a separate thread.

    Parameters
    ----------
    mesh : dolfinx.mesh.Mesh
        Mesh used for the calculation.
    temperature_history : list of (time_s, temp_C)
        Thermal history ``T(t)``.
    Ea : float
        Activation energy in kJ/mol.
    A : float
        Pre-exponential factor (1/s).
    solver_options : dict, optional
        Extra options for :class:`~ogum.sovs.SOVSSolver`.
    callback : callable, optional
        Function called when the computation finishes. It receives the result
        dictionary as a single argument.

    Returns:
    -------
    (Thread, dict)
        The started thread and a dictionary containing ``densities`` or
        ``error`` keys.
    """
    result: dict = {"densities": None, "error": None}

    def _target() -> None:
        try:
            result["densities"] = densify_mesh(
                mesh, temperature_history, Ea, A, solver_options
            )
        except Exception as exc:  # pragma: no cover - best effort
            result["error"] = exc
        if callback is not None:
            callback(result)

    thread = Thread(target=_target, daemon=True)
    thread.start()
    return thread, result


__all__ = ["create_unit_mesh", "densify_mesh", "densify_mesh_async"]
