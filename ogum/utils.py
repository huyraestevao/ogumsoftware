"""Small helper utilities used across the code base."""

from __future__ import annotations

from typing import Dict, Iterable

import numpy as np
import pandas as pd


def normalize_columns(
    df: pd.DataFrame, mapping: Dict[str, Iterable[str]]
) -> pd.DataFrame:
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


def orlandini_araujo_filter(df: pd.DataFrame, bin_size: int = 10) -> pd.DataFrame:
    """Apply the Orlandini–Araújo smoothing filter.

    The data are averaged in ``bin_size`` second windows. Columns beginning with
    ``"Time_s"``, ``"Temperature_C"`` and ``"DensidadePct"`` are required.

    Parameters
    ----------
    df:
        Input DataFrame containing at least the required columns.
    bin_size:
        Width of each time bin in seconds.

    Returns
    -------
    pandas.DataFrame
        The filtered DataFrame.
    """
    time_col = next((c for c in df.columns if c.startswith("Time_s")), None)
    temp_col = next((c for c in df.columns if c.startswith("Temperature_C")), None)
    dens_col = next((c for c in df.columns if c.startswith("DensidadePct")), None)

    if not (time_col and temp_col and dens_col):
        raise ValueError(
            "Faltam colunas (Time_s, Temperature_C, DensidadePct) para Orlandini-Araújo."
        )

    dfc = df.copy()
    dfc["bin"] = np.floor(dfc[time_col] / bin_size).astype(int)

    # Preserve all original columns averaging values inside each bin
    agg_dict = {col: "mean" for col in df.columns}
    grouped = dfc.groupby("bin").agg(agg_dict).reset_index(drop=True)
    return grouped


__all__ = ["normalize_columns", "orlandini_araujo_filter"]
