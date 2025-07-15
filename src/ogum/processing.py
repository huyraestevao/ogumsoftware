"""Processing routines for sintering experiment data."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .core import R, cumtrapz


# -----------------------------------------------------------------------------#
# Função pública
# -----------------------------------------------------------------------------#
def calculate_log_theta(
    df_ensaio: pd.DataFrame,
    energia_ativacao_kj: float | None = None,
    **kwargs,
) -> pd.DataFrame:
    """Calcula log‑theta para um ensaio e uma *Ea* dada.

    Aceita tanto o nome **``energia_ativacao_kj``** (padrão interno) quanto
    os aliases usados nos testes/legacy – ``Ea_kJ`` ou ``Ea_kj`` – para fins
    de compatibilidade.
    """
    # ------------------------------------------------------------------#
    # Compatibilidade de nomes de argumento
    # ------------------------------------------------------------------#
    if energia_ativacao_kj is None:
        energia_ativacao_kj = kwargs.get("Ea_kJ") or kwargs.get("Ea_kj")
        if energia_ativacao_kj is None:
            raise TypeError(
                "missing required argument 'energia_ativacao_kj' "
                "(também aceito Ea_kJ= ou Ea_kj=)"
            )

    # ------------------------------------------------------------------#
    # Localiza colunas com possíveis sufixos
    # ------------------------------------------------------------------#
    time_col = next((c for c in df_ensaio.columns if c.startswith("Time_s")), None)
    temp_col = next((c for c in df_ensaio.columns if c.startswith("Temperature_C")), None)
    dens_col = next((c for c in df_ensaio.columns if c.startswith("DensidadePct")), None)

    if not (time_col and temp_col and dens_col):
        raise ValueError("Required columns missing")

    if df_ensaio[time_col].size < 2:
        raise ValueError("Insufficient data for integration")

    # ------------------------------------------------------------------#
    # Cálculo do log‑theta
    # ------------------------------------------------------------------#
    T_k = df_ensaio[temp_col].to_numpy(float) + 273.15
    Ea_j = energia_ativacao_kj * 1000.0

    theta_inst = (1.0 / T_k) * np.exp(-Ea_j / (R * T_k))
    integrated = cumtrapz(theta_inst, df_ensaio[time_col].to_numpy(float), initial=0)

    with np.errstate(divide="ignore", invalid="ignore"):
        safe_int = np.where(integrated == 0, np.finfo(float).tiny, integrated)
        log_integrated = np.log10(safe_int)
    log_integrated[~np.isfinite(log_integrated)] = np.nan

    return pd.DataFrame(
        {
            "logtheta": log_integrated,
            "valor": df_ensaio[dens_col].to_numpy(),
            "tempo_s": df_ensaio[time_col].to_numpy(),
        }
    )


__all__ = ["calculate_log_theta"]
