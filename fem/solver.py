# coding: utf-8
"""Simple FEM solver using FEniCSx for uniaxial compression tests.

This script generates a unit square mesh, defines a linear viscous material
model and solves for the displacement field under prescribed compression on
the top boundary. Results are written to an XDMF file.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from mpi4py import MPI
from dolfinx import fem, mesh
from dolfinx.fem import petsc
import ufl


def main() -> None:
    """Run a minimal uniaxial compression simulation."""
    # ---------------------------------------------------------------------
    # Mesh and function space
    # ---------------------------------------------------------------------
    domain = mesh.create_rectangle(
        MPI.COMM_WORLD,
        [[0.0, 0.0], [1.0, 1.0]],
        [20, 20],
        mesh.CellType.triangle,
    )
    V = fem.VectorFunctionSpace(domain, ("Lagrange", 1))

    # ------------------------------------------------------------------
    # Material parameters
    # ------------------------------------------------------------------
    eta = 1.0
    strain_rate = -0.1

    # ------------------------------------------------------------------
    # Boundary conditions
    # ------------------------------------------------------------------
    def bottom(x):
        return np.isclose(x[1], 0.0)

    def top(x):
        return np.isclose(x[1], 1.0)

    def bottom_left(x):
        return np.isclose(x[0], 0.0) & np.isclose(x[1], 0.0)

    u_bc_bottom = np.array([0.0, 0.0], dtype=np.double)
    u_bc_bottom_left = np.array([0.0, 0.0], dtype=np.double)
    u_bc_top = np.array([0.0, strain_rate], dtype=np.double)

    bc_bottom = fem.dirichletbc(u_bc_bottom, fem.locate_dofs_geometrical(V, bottom), V)
    bc_bottom_left = fem.dirichletbc(
        u_bc_bottom_left, fem.locate_dofs_geometrical(V.sub(0), bottom_left), V.sub(0)
    )
    bc_top = fem.dirichletbc(u_bc_top, fem.locate_dofs_geometrical(V, top), V)
    bcs = [bc_bottom, bc_bottom_left, bc_top]

    # ------------------------------------------------------------------
    # Variational form
    # ------------------------------------------------------------------
    u = ufl.TrialFunction(V)
    v = ufl.TestFunction(V)

    def epsilon(u_):
        return ufl.sym(ufl.grad(u_))

    def sigma(u_):
        return 2 * eta * epsilon(u_)

    F = ufl.inner(sigma(u), epsilon(v)) * ufl.dx

    problem = petsc.LinearProblem(F, bcs=bcs)
    uh = problem.solve()

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    out_dir = Path("fem_output")
    out_dir.mkdir(exist_ok=True)
    with fem.XDMFFile(domain.comm, out_dir / "uniaxial_compression.xdmf", "w") as f:
        f.write_mesh(domain)
        f.write_function(uh)


if __name__ == "__main__":
    main()
