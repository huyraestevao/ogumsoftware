# coding: utf-8
"""Simple FEM solver using FEniCSx for uniaxial compression tests.

This script generates a unit square mesh, defines a linear viscous material
model and solves for the displacement field under prescribed compression on
the top boundary. Results are written to an XDMF file.
"""

from __future__ import annotations

from pathlib import Path
import json

import numpy as np
from mpi4py import MPI
from dolfinx import fem, mesh
from dolfinx.fem import petsc
from dolfinx.io import XDMFFile
import pyvista as pv
import ufl


def run_fem_simulation(
    mesh_params: dict,
    material_params: dict,
    bc_params: dict,
    output_filename: str,
    job_id: str,
    total_time: float,
    num_steps: int,
) -> None:
    """Run a uniaxial compression simulation and save the result.

    Args:
        mesh_params: Parameters controlling mesh generation.
        material_params: Dictionary with material constants.
        bc_params: Boundary condition parameters.
        output_filename: Path for the XDMF results file.
        job_id: Identifier used for status JSON files.
        total_time: Total simulated time.
        num_steps: Number of time steps.
    """
    status_path = Path(f"fem_output/{job_id}.json")
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps({"status": "running"}))

    try:
        # ------------------------------------------------------------------
        # Mesh and function space
        # ------------------------------------------------------------------
        width = float(mesh_params.get("width", 1.0))
        height = float(mesh_params.get("height", 1.0))
        nx = int(mesh_params.get("nx", 20))
        ny = int(mesh_params.get("ny", 20))
        domain = mesh.create_rectangle(
            MPI.COMM_WORLD,
            [[0.0, 0.0], [width, height]],
            [nx, ny],
            mesh.CellType.triangle,
        )
        V = fem.VectorFunctionSpace(domain, ("Lagrange", 1))

        # ------------------------------------------------------------------
        # Material parameters
        # ------------------------------------------------------------------
        eta = float(material_params.get("eta", 1.0))
        strain_rate = float(bc_params.get("strain_rate", -0.1))

        # ------------------------------------------------------------------
        # Boundary conditions
        # ------------------------------------------------------------------
        def bottom(x):
            return np.isclose(x[1], 0.0)

        def top(x):
            return np.isclose(x[1], height)

        def bottom_left(x):
            return np.isclose(x[0], 0.0) & np.isclose(x[1], 0.0)

        u_bc_bottom = np.array([0.0], dtype=np.double)
        u_bc_bottom_left = np.array([0.0, 0.0], dtype=np.double)
        u_bc_top = fem.Constant(domain, np.array([0.0, 0.0], dtype=np.double))

        bc_bottom = fem.dirichletbc(
            u_bc_bottom, fem.locate_dofs_geometrical(V.sub(1), bottom), V.sub(1)
        )
        bc_bottom_left = fem.dirichletbc(
            u_bc_bottom_left,
            fem.locate_dofs_geometrical(V.sub(0), bottom_left),
            V.sub(0),
        )
        bc_top = fem.dirichletbc(u_bc_top, fem.locate_dofs_geometrical(V, top), V)
        bcs = [bc_bottom, bc_bottom_left, bc_top]

        # ------------------------------------------------------------------
        # Variational form
        # ------------------------------------------------------------------
        u = fem.Function(V)
        du = ufl.TrialFunction(V)
        v = ufl.TestFunction(V)

        def epsilon(u_):
            return ufl.sym(ufl.grad(u_))

        def sigma(u_):
            return 2 * eta * epsilon(u_)

        F = ufl.inner(sigma(u), epsilon(v)) * ufl.dx
        J = ufl.derivative(F, u, du)

        problem = petsc.NonlinearProblem(fem.form(F), u, bcs=bcs, J=fem.form(J))
        solver = petsc.NewtonSolver(domain.comm)

        out_path = Path(output_filename)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with XDMFFile(domain.comm, out_path, "w") as f:
            f.write_mesh(domain)
            dt = total_time / num_steps
            for step in range(1, num_steps + 1):
                t = step * dt
                u_bc_top.value[1] = strain_rate * t
                solver.solve(problem, u)
                f.write_function(u, t)

        # --------------------------------------------------------------
        # Preview image
        # --------------------------------------------------------------
        if domain.comm.rank == 0:
            try:
                grid = pv.read(out_path)
                plotter = pv.Plotter(off_screen=True)
                plotter.add_mesh(grid, scalars="u", show_edges=True)
                plotter.screenshot(str(out_path.with_suffix(".png")))
                plotter.close()
            except Exception as exc:  # pragma: no cover - best effort preview
                print(f"Failed to generate preview: {exc}")

        if domain.comm.rank == 0:
            status_path.write_text(
                json.dumps(
                    {
                        "status": "completed",
                        "image_path": str(out_path.with_suffix(".png")),
                        "data_path": str(out_path),
                    }
                )
            )
    except Exception as exc:  # pragma: no cover - propagate error
        status_path.write_text(json.dumps({"status": "failed", "error": str(exc)}))
        raise


def main() -> None:
    """Entry point for manual execution with default parameters."""
    run_fem_simulation(
        {"width": 1.0, "height": 1.0, "nx": 20, "ny": 20},
        {"eta": 1.0},
        {"strain_rate": -0.1},
        "fem_output/uniaxial_compression.xdmf",
        "example",
        total_time=1.0,
        num_steps=10,
    )


if __name__ == "__main__":
    main()
