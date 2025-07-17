"""Interactive helper to filter experimental data frames."""

from __future__ import annotations

from typing import Sequence

import pandas as pd
import matplotlib.pyplot as plt

try:
    from IPython.display import display, clear_output
    import ipywidgets as widgets
except Exception:  # pragma: no cover - optional dependency
    class _Dummy:
        def __getattr__(self, name):
            raise RuntimeError("ipywidgets is required for GUI functions")

    widgets = _Dummy()  # type: ignore

    def display(*args, **kwargs):  # type: ignore
        pass

    def clear_output(*args, **kwargs):  # type: ignore
        pass


class DataRefinement:
    """Provide interactive filtering of data by time and density."""

    df_original: pd.DataFrame
    df_refined: pd.DataFrame

    def __init__(self, df_mapped: pd.DataFrame) -> None:
        """Store ``df_mapped`` and create filtering widgets."""
        self.df_original = df_mapped.copy()
        self._build_widgets()
        self.df_refined = self._apply_filters()

    def _build_widgets(self) -> None:
        t_min = float(self.df_original["time"].min())
        t_max = float(self.df_original["time"].max())
        d_min = float(self.df_original["density"].min())
        d_max = float(self.df_original["density"].max())
        self.time_slider = widgets.FloatRangeSlider(
            value=(t_min, t_max),
            min=t_min,
            max=t_max,
            step=(t_max - t_min) / 100 or 1.0,
            description="tempo",
        )
        self.density_slider = widgets.FloatRangeSlider(
            value=(d_min, d_max),
            min=d_min,
            max=d_max,
            step=(d_max - d_min) / 100 or 1.0,
            description="densidade",
        )
        self.output = widgets.Output()
        self.widget = widgets.VBox(
            [self.time_slider, self.density_slider, self.output]
        )
        for w in (self.time_slider, self.density_slider):
            w.observe(self._update, names="value")

    def display(self) -> None:
        """Display the widget box."""
        display(self.widget)

    def _apply_filters(self) -> pd.DataFrame:
        t_min, t_max = self.time_slider.value
        d_min, d_max = self.density_slider.value
        mask = (
            (self.df_original["time"] >= t_min)
            & (self.df_original["time"] <= t_max)
            & (self.df_original["density"] >= d_min)
            & (self.df_original["density"] <= d_max)
        )
        return self.df_original.loc[mask].reset_index(drop=True)

    def _update(self, _=None) -> None:
        self.df_refined = self._apply_filters()
        with self.output:
            clear_output(wait=True)
            display(self.df_refined)

    def plot_before_after(self) -> tuple[plt.Figure, Sequence[plt.Axes]]:
        """Return figure with original and filtered curves side by side."""
        fig, axs = plt.subplots(1, 2, figsize=(10, 4), tight_layout=True)
        axs[0].plot(self.df_original["time"], self.df_original["density"], ".-")
        axs[0].set(xlabel="tempo", ylabel="densidade", title="Original")
        axs[1].plot(self.df_refined["time"], self.df_refined["density"], "r.-")
        axs[1].set(xlabel="tempo", ylabel="densidade", title="Refinado")
        for ax in axs:
            ax.grid(True, alpha=0.5)
        return fig, axs


__all__ = ["DataRefinement"]
