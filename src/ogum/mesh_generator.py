"""Utilities for generating 3D meshes using gmsh."""

from __future__ import annotations

import random
import tempfile


def generate_mesh(
    radius: float,
    box_size: float,
    element_size: float,
    n_spheres: int,
) -> str:
    """Create a mesh of ``n_spheres`` packed in a box.

    Parameters
    ----------
    radius : float
        Sphere radius.
    box_size : float
        Length of the cubic domain side.
    element_size : float
        Target mesh element size.
    n_spheres : int
        Number of spheres inside the box.

    Returns:
    -------
    str
        Path to the generated ``.msh`` file.
    """
    try:
        import gmsh

        gmsh.initialize()
    except (ImportError, OSError) as exc:  # pragma: no cover - optional dep
        raise ModuleNotFoundError("gmsh não instalado ou libGLU ausente") from exc

    gmsh.model.add("pack")
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", element_size)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", element_size)
    gmsh.model.occ.addBox(0, 0, 0, box_size, box_size, box_size, 1)
    sphere_tags: list[int] = []
    for _ in range(n_spheres):
        x = random.uniform(radius, box_size - radius)
        y = random.uniform(radius, box_size - radius)
        z = random.uniform(radius, box_size - radius)
        tag = gmsh.model.occ.addSphere(x, y, z, radius)
        sphere_tags.append(tag)

    gmsh.model.occ.cut(
        [(3, 1)],
        [(3, t) for t in sphere_tags],
        removeObject=False,
        removeTool=True,
    )
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    with tempfile.NamedTemporaryFile(suffix=".msh", delete=False) as tmp:
        msh_file = tmp.name
    gmsh.write(msh_file)
    gmsh.finalize()
    return msh_file


__all__ = ["generate_mesh"]
