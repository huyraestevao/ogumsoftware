"""Small helper utilities used across the code base."""
from __future__ import annotations

from typing import Dict, Iterable

import numpy as np
import pandas as pd


def normalize_columns(df: pd.DataFrame, mapping: Dict[str, Iterable[str]]) -> pd.DataFrame:
    """Return a DataFrame with columns renamed based on a mapping."""
    rename_dict = {}
    for col in df.columns:
        lower_col = col.lower()
        for standard, names in mapping.items():
            if any(name.lower() in lower_col for name in names):
                rename_dict[col] = standard
                break
    return df.rename(columns=rename_dict)


def orlandini_araujo_filter(df: pd.DataFrame, bin_size: int = 10) -> pd.DataFrame:
    """Group rows by time bins and average values.

    The function searches for columns starting with ``Time_s``, ``Temperature_C``
    and ``DensidadePct`` and groups the data in ``bin_size`` second intervals,
    returning the mean of each bin.
    """
    time_col = next((c for c in df.columns if c.startswith("Time_s")), None)
    temp_col = next((c for c in df.columns if c.startswith("Temperature_C")), None)
    dens_col = next((c for c in df.columns if c.startswith("DensidadePct")), None)

    if not (time_col and temp_col and dens_col):
        raise ValueError(
            "Faltam colunas (Time_s, Temperature_C, DensidadePct) p/ Orlandini-Araujo."
        )

    dfc = df[[time_col, temp_col, dens_col]].copy()
    dfc["bin"] = np.floor(dfc[time_col] / bin_size).astype(int)
    grouped = (
        dfc.groupby("bin").agg({time_col: "mean", temp_col: "mean", dens_col: "mean"})
        .reset_index(drop=True)
    )
    return grouped
