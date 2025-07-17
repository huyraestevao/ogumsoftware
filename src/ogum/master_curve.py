"""Master curve construction utilities."""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd

from .core import R


def _estimate_activation_energy(time: np.ndarray, temp_c: np.ndarray, dens: np.ndarray) -> float:
    """Return activation energy in kJ/mol estimated from densification data."""
    x = dens.copy().astype(float)
    if x.max() > 1.0:
        x /= 100.0
    mask = (time > 0) & (0 < x) & (x < 1)
    if mask.sum() < 2:
        raise ValueError("Insufficient data for activation energy fit")
    k_eff = -np.log(1.0 - x[mask]) / time[mask]
    inv_T = 1.0 / (temp_c[mask].astype(float) + 273.15)
    slope, _ = np.polyfit(inv_T, np.log(k_eff), 1)
    Ea_j = -slope * R
    return float(Ea_j / 1000.0)


def build_master_curve(df: pd.DataFrame, method: Literal["arrhenius"] = "arrhenius") -> pd.DataFrame:
    """Return Arrhenius master curve for densification data.

    Parameters
    ----------
    df : pandas.DataFrame
        Input data with ``time``, ``temperature`` and ``density`` columns.
    method : {{'arrhenius'}}, default 'arrhenius'
        Superposition method to apply.

    Returns
    -------
    pandas.DataFrame
        Columns ``master_time``, ``master_density`` and ``activation_energy``.
    """
    if method != "arrhenius":
        raise ValueError("Only 'arrhenius' method is supported")
    required = {"time", "temperature", "density"}
    if not required <= set(df.columns):
        raise ValueError("Input DataFrame must contain 'time', 'temperature' and 'density'")

    t = df["time"].to_numpy(float)
    T_c = df["temperature"].to_numpy(float)
    dens = df["density"].to_numpy(float)

    Ea_kJ = _estimate_activation_energy(t, T_c, dens)
    T_ref = np.mean(T_c) + 273.15
    T_k = T_c + 273.15
    a_T = np.exp((Ea_kJ * 1000.0 / R) * (1.0 / T_k - 1.0 / T_ref))
    master_time = t * a_T

    result = pd.DataFrame(
        {
            "master_time": master_time,
            "master_density": dens,
            "activation_energy": np.full_like(master_time, Ea_kJ, dtype=float),
        }
    )
    return result


__all__ = ["build_master_curve"]
