"""Interactive UI for generating meshes with ``generate_mesh``."""

from __future__ import annotations

import ipywidgets as widgets
from IPython.display import clear_output, display
import pyvista as pv

from .mesh_generator import generate_mesh


class MeshGeneratorUI:
    """Widget collection to generate and display a mesh."""

    def __init__(self) -> None:
        """Create widgets and set up callbacks."""
        self.radius_slider = widgets.FloatSlider(
            value=1.0,
            min=0.1,
            max=5.0,
            step=0.1,
            description="raio",
        )
        self.box_slider = widgets.FloatSlider(
            value=5.0,
            min=1.0,
            max=10.0,
            step=0.5,
            description="caixa",
        )
        self.size_slider = widgets.FloatSlider(
            value=0.5,
            min=0.1,
            max=2.0,
            step=0.1,
            description="elemento",
        )
        self.num_dropdown = widgets.Dropdown(
            options=[1, 2, 3, 5, 10],
            value=3,
            description="esferas",
        )
        self.output = widgets.Output()
        self.ui = widgets.VBox(
            [
                self.radius_slider,
                self.box_slider,
                self.size_slider,
                self.num_dropdown,
                self.output,
            ]
        )
        for w in (
            self.radius_slider,
            self.box_slider,
            self.size_slider,
            self.num_dropdown,
        ):
            w.observe(self._update, names="value")
        self.mesh_path: str | None = None
        self._update()

    def _update(self, _=None) -> None:
        with self.output:
            clear_output(wait=True)
            try:
                self.mesh_path = generate_mesh(
                    self.radius_slider.value,
                    self.box_slider.value,
                    self.size_slider.value,
                    int(self.num_dropdown.value),
                )
                mesh = pv.read(self.mesh_path)
                plotter = pv.Plotter()
                plotter.add_mesh(mesh, show_edges=True)
                plotter.show(jupyter_backend="pythreejs")
            except Exception as exc:  # pragma: no cover - visual feedback only
                display(widgets.HTML(f"<b>Erro ao gerar malha: {exc}</b>"))


__all__ = ["MeshGeneratorUI"]
