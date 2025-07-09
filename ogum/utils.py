"""Small helper utilities used across the code base."""
from __future__ import annotations

from typing import Dict, Iterable

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter

from .core import (
    DataHistory,
    SinteringDataRecord,
    add_suffix_once,
    criar_titulo,
    exibir_mensagem,
    exibir_erro,
    criar_caixa_colapsavel,
    gerar_link_download,
    boltzmann_sigmoid,
    generalized_logistic_stable,
)


def normalize_columns(df: pd.DataFrame, mapping: Dict[str, Iterable[str]]) -> pd.DataFrame:
    """Return a DataFrame with columns renamed based on a mapping.

    Parameters
    ----------
    df:
        DataFrame cujos nomes de colunas serão normalizados.
    mapping:
        Dicionário onde a chave é o nome desejado e o valor é uma lista
        de nomes possíveis (case insensitive) encontrados em ``df``.
    """
    rename_dict = {}
    for col in df.columns:
        lower_col = col.lower()
        for standard, names in mapping.items():
            if any(name.lower() in lower_col for name in names):
                rename_dict[col] = standard
                break
    return df.rename(columns=rename_dict)


def calculate_derivatives_robust(
    df: pd.DataFrame, time_col: str, temp_col: str, dens_col: str
) -> tuple[interp1d, interp1d, interp1d]:
    """Return interpolators for T, dT/dt and dp/dT as functions of density."""
    df_sorted = df.sort_values(time_col).reset_index(drop=True)
    n_pts = len(df_sorted)
    if n_pts < 5:
        raise ValueError("Dados insuficientes (<5 pontos) para cálculo robusto.")

    max_win = 11
    win = min(max_win, n_pts if n_pts % 2 == 1 else n_pts - 1)
    window_length = win if win >= 5 else (5 if n_pts >= 5 else n_pts)
    if window_length >= 5:
        y_vals = savgol_filter(df_sorted[dens_col].values, window_length, 2)
        t_vals = savgol_filter(df_sorted[temp_col].values + 273.15, window_length, 2)
    else:
        y_vals = df_sorted[dens_col].values
        t_vals = df_sorted[temp_col].values + 273.15

    dTdt = np.gradient(t_vals, df_sorted[time_col].values)
    dpdT = np.gradient(y_vals, t_vals)

    interp_df = (
        pd.DataFrame({"dens": y_vals, "T": t_vals, "dTdt": dTdt, "dpdT": dpdT})
        .sort_values("dens")
        .drop_duplicates("dens")
    )
    if len(interp_df) < 2:
        raise ValueError("Dados insuficientes após filtragem para interpolação.")

    f_T = interp1d(interp_df["dens"], interp_df["T"], kind="linear", bounds_error=False, fill_value="extrapolate")
    f_dTdt = interp1d(interp_df["dens"], interp_df["dTdt"], kind="linear", bounds_error=False, fill_value="extrapolate")
    f_dpdT = interp1d(interp_df["dens"], interp_df["dpdT"], kind="linear", bounds_error=False, fill_value="extrapolate")

    return f_T, f_dTdt, f_dpdT


def orlandini_araujo_filter(df: pd.DataFrame, bin_size: int = 10) -> pd.DataFrame:
    """Apply the Orlandini-Araújo filter aggregating rows by time bins."""
    time_col = next((c for c in df.columns if c.startswith("Time_s")), None)
    temp_col = next((c for c in df.columns if c.startswith("Temperature_C")), None)
    dens_col = next((c for c in df.columns if c.startswith("DensidadePct")), None)
    if not (time_col and temp_col and dens_col):
        raise ValueError(
            "Faltam colunas (Time_s, Temperature_C, DensidadePct) para Orlandini-Araújo."
        )

    dfc = df.copy()
    dfc["bin"] = np.floor(dfc[time_col] / bin_size).astype(int)
    agg_dict = {col: "mean" for col in df.columns}
    grouped = dfc.groupby("bin").agg(agg_dict).reset_index(drop=True)
    return grouped


__all__ = [
    "normalize_columns",
    "calculate_derivatives_robust",
    "orlandini_araujo_filter",
    "SinteringDataRecord",
    "DataHistory",
    "add_suffix_once",
    "criar_titulo",
    "exibir_mensagem",
    "exibir_erro",
    "criar_caixa_colapsavel",
    "gerar_link_download",
    "boltzmann_sigmoid",
    "generalized_logistic_stable",
]
