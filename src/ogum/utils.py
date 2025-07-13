"""Small helper utilities used across the code base."""

from __future__ import annotations

from typing import Dict, Iterable, Optional

import pandas as pd
from scipy.signal import savgol_filter as _savgol_filter


def normalize_columns(
    df: pd.DataFrame, mapping: Dict[str, Iterable[str]]
) -> pd.DataFrame:
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

    renames = {
        col: alias_map[col.lower()] for col in df.columns if col.lower() in alias_map
    }
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


def savgol_filter(
    df: pd.DataFrame,
    window: Optional[int] = None,
    polyorder: int = 2,
) -> pd.DataFrame:
    """Apply a Savitzky–Golay filter to numeric columns of ``df``.

    The window size is chosen adaptively when ``window`` is ``None`` using
    ``min(11, (len(df) // 2) * 2 + 1)``. Non-numeric columns are preserved.
    """
    if df.empty:
        return df.copy()

    if window is None:
        window = min(11, max(3, (len(df) // 2) * 2 + 1))
    if window % 2 == 0:
        window += 1

    df_filtered = df.copy()
    for col in df_filtered.select_dtypes(include="number").columns:
        if len(df_filtered[col]) < polyorder + 1:
            continue
        df_filtered[col] = _savgol_filter(
            df_filtered[col].to_numpy(), window, polyorder
        )

    return df_filtered


__all__ = ["normalize_columns", "orlandini_araujo_filter", "savgol_filter"]
