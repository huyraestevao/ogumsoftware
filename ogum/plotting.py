"""Plotting helpers for visualizing sintering experiments."""

import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional, Sequence, Tuple


def plot_sintering_curves(
    df_ensaio: pd.DataFrame, ax: Optional[plt.Axes] = None
) -> Tuple[plt.Figure, Sequence[plt.Axes]]:
    """Plot standard sintering curves for ``df_ensaio``.

    Parameters
    ----------
    df_ensaio : pd.DataFrame
        Data containing columns starting with ``Time_s``, ``Temperature_C``
        and ``DensidadePct``.
    ax : matplotlib.axes.Axes, optional
        Axis to draw the first subplot on. When ``None`` a new figure is
        created.

    Returns:
    -------
    (figure, axes)
        The created figure and list of axes.
    """
    time_col = next((c for c in df_ensaio.columns if c.startswith("Time_s")), None)
    temp_col = next(
        (c for c in df_ensaio.columns if c.startswith("Temperature_C")), None
    )
    dens_col = next(
        (c for c in df_ensaio.columns if c.startswith("DensidadePct")), None
    )
    if not (time_col and temp_col and dens_col):
        raise ValueError("Required columns missing")

    if ax is None:
        fig, axs = plt.subplots(1, 3, figsize=(15, 4), tight_layout=True)
    else:
        fig = ax.figure
        axs = [ax, fig.add_subplot(1, 3, 2), fig.add_subplot(1, 3, 3)]
        fig.set_size_inches(15, 4)

    fig.suptitle("Sintering Curves")

    axs[0].plot(df_ensaio[time_col], df_ensaio[dens_col], ".-")
    axs[0].set(xlabel="Tempo (s)", ylabel="Densidade (%)")

    axs[1].plot(df_ensaio[temp_col], df_ensaio[dens_col], "r.-")
    axs[1].set(xlabel="Temperatura (°C)", ylabel="Densidade (%)")

    axs[2].plot(df_ensaio[time_col], df_ensaio[temp_col], "g.-")
    axs[2].set(xlabel="Tempo (s)", ylabel="Temperatura (°C)")

    for a in axs:
        a.grid(True, alpha=0.5)

    return fig, axs


__all__ = ["plot_sintering_curves"]
