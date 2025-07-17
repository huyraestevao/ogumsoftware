"""Performance benchmarks for FEM mesh generation and solving."""

from __future__ import annotations

import math
import time
from pathlib import Path

import pandas as pd
import pytest

try:
    from mpi4py import MPI
    from dolfinx import mesh, fem
    from dolfinx.fem import petsc
    import ufl
    import numpy as np
except Exception as exc:  # pragma: no cover - optional dependencies
    pytest.skip("FEniCSx not available", allow_module_level=True)


# Number of target elements for the benchmarks
CASES = [1000, 5000, 10000]

# Collect results for CSV/Markdown export
RESULTS: list[dict[str, float]] = []


def create_mesh(n_elements: int):
    """Create approximately ``n_elements`` triangular elements."""
    n = max(1, int(math.sqrt(n_elements / 2)))
    return mesh.create_rectangle(
        MPI.COMM_WORLD,
        [[0.0, 0.0], [1.0, 1.0]],
        [n, n],
        mesh.CellType.triangle,
    )


def solve_problem(domain) -> None:
    """Run a very small FEM solve on ``domain``."""
    V = fem.VectorFunctionSpace(domain, ("Lagrange", 1))
    u = fem.Function(V)
    du = ufl.TrialFunction(V)
    v = ufl.TestFunction(V)

    def epsilon(u_):
        return ufl.sym(ufl.grad(u_))

    def sigma(u_):
        return 2 * epsilon(u_)

    F = ufl.inner(sigma(u), epsilon(v)) * ufl.dx
    J = ufl.derivative(F, u, du)

    problem = petsc.NonlinearProblem(fem.form(F), u, J=fem.form(J))
    solver = petsc.NewtonSolver(domain.comm)
    solver.solve(problem, u)


@pytest.mark.parametrize("n_elements", CASES)
def test_fem_benchmark(benchmark, n_elements):
    """Benchmark mesh generation and solver execution."""
    times: dict[str, float] = {}

    def gen_mesh():
        start = time.perf_counter()
        dm = create_mesh(n_elements)
        times["mesh_time"] = time.perf_counter() - start
        return dm

    domain = benchmark(gen_mesh)

    def run_solver():
        start = time.perf_counter()
        solve_problem(domain)
        times["solve_time"] = time.perf_counter() - start

    benchmark(run_solver)

    RESULTS.append(
        {
            "n_elements": n_elements,
            "mesh_time": times.get("mesh_time", 0.0),
            "solve_time": times.get("solve_time", 0.0),
        }
    )


def pytest_sessionfinish(session, exitstatus):
    """Export benchmark results after the test session."""
    if not RESULTS:
        return
    out_dir = Path("benchmarks")
    out_dir.mkdir(exist_ok=True)
    df = pd.DataFrame(RESULTS)
    df.to_csv(out_dir / "results.csv", index=False)
    df.to_markdown(out_dir / "results.md", index=False)

