"""Small helper utilities used across the code base."""
from __future__ import annotations

from typing import Dict, Iterable

import numpy as np
import pandas as pd


def normalize_columns(df: pd.DataFrame, mapping: Dict[str, Iterable[str]]) -> pd.DataFrame:
    """Rename DataFrame columns based on a mapping of possible names.

    Args:
        df (pd.DataFrame): DataFrame whose columns will be normalized.
        mapping (Dict[str, Iterable[str]]): Dictionary where keys are desired
            names and values are lists of possible (case-insensitive) column
            names found in ``df``.

    Returns:
        pd.DataFrame: DataFrame with standardized column names.
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
    """Apply the Orlandini-Araújo filter aggregating rows by time bins.

    Args:
        df (pd.DataFrame): Input DataFrame with ``Time_s``, ``Temperature_C``
            and ``DensidadePct`` columns.
        bin_size (int, optional): Bin width in seconds. Defaults to ``10``.

    Returns:
        pd.DataFrame: Filtered DataFrame.
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
    agg_dict = {col: "mean" for col in df.columns}
    grouped = dfc.groupby("bin").agg(agg_dict).reset_index(drop=True)
    return grouped

__all__ = ["normalize_columns", "orlandini_araujo_filter"]
