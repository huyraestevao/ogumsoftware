"""Processing routines for sintering experiment data."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .core import R, cumtrapz


def calculate_log_theta(
    df_ensaio: pd.DataFrame, energia_ativacao_kj: float
) -> pd.DataFrame:
    """Calculate log(theta) for a single test and activation energy.

    Parameters
    ----------
    df_ensaio : pd.DataFrame
        Data for one experiment containing ``Time_s*``, ``Temperature_C*`` and
        ``DensidadePct*`` columns.
    energia_ativacao_kj : float
        Activation energy in kJ/mol.

    Returns:
    -------
    pd.DataFrame
        DataFrame with columns ``logtheta``, ``valor`` and ``tempo_s``.
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

    if df_ensaio[time_col].size < 2:
        raise ValueError("Insufficient data for integration")

    T_k = df_ensaio[temp_col].to_numpy(dtype=float) + 273.15
    Ea_j = energia_ativacao_kj * 1000.0

    theta_inst = (1.0 / T_k) * np.exp(-Ea_j / (R * T_k))
    integrated = cumtrapz(
        theta_inst, df_ensaio[time_col].to_numpy(dtype=float), initial=0
    )

    with np.errstate(divide="ignore", invalid="ignore"):
        log_integrated = np.log10(integrated)
    log_integrated[~np.isfinite(log_integrated)] = np.nan

    return pd.DataFrame(
        {
            "logtheta": log_integrated,
            "valor": df_ensaio[dens_col].to_numpy(),
            "tempo_s": df_ensaio[time_col].to_numpy(),
        }
    )


__all__ = ["calculate_log_theta"]
