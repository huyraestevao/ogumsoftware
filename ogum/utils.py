"""Small helper utilities used across the code base."""

from __future__ import annotations

from typing import Dict, Iterable

import pandas as pd


def normalize_columns(df: pd.DataFrame, mapping: Dict[str, Iterable[str]]) -> pd.DataFrame:
    """Return ``df`` with columns renamed according to ``mapping``.

    The ``mapping`` keys correspond to the desired column names.  Each value is
    a list of aliases (case-insensitive) that should be mapped to that key.  If
    a column already matches one of the aliases or the key (ignoring case) it
    will be renamed to the key.  Columns without a corresponding alias are left
    unchanged.
    """
    alias_map: Dict[str, str] = {}
    for new_col, aliases in mapping.items():
        for alias in [new_col, *aliases]:
            alias_map[alias.lower()] = new_col

    renames = {col: alias_map[col.lower()] for col in df.columns if col.lower() in alias_map}
    return df.rename(columns=renames)


def orlandini_araujo_filter(df: pd.DataFrame, bin_size: int = 10) -> pd.DataFrame:
    """Apply the Orlandini–Araújo smoothing filter.

    The function averages the data in ``bin_size`` second windows. It requires
    columns starting with ``"Time_s"``, ``"Temperature_C"`` and
    ``"DensidadePct"``.
    """
    time_col = next((c for c in df.columns if c.startswith("Time_s")), None)
    temp_col = next((c for c in df.columns if c.startswith("Temperature_C")), None)
    dens_col = next((c for c in df.columns if c.startswith("DensidadePct")), None)

    if not (time_col and temp_col and dens_col):
        raise ValueError("Required columns missing")

    dfc = df[[time_col, temp_col, dens_col]].copy()
    dfc["bin"] = (dfc[time_col] // bin_size).astype(int)
    grouped = dfc.groupby("bin")[[time_col, temp_col, dens_col]].mean()
    return grouped.reset_index(drop=True)


__all__ = ["normalize_columns", "orlandini_araujo_filter"]
