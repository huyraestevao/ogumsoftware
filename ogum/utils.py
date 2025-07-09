import numpy as np
import pandas as pd


def add_suffix_once(col: str, suffix: str) -> str:
    """Append suffix to column name only if not already present."""
    return col if col.endswith(suffix) else f"{col}{suffix}"


def orlandini_araujo_filter(df: pd.DataFrame, bin_size: int = 10) -> pd.DataFrame:
    """Aggregate sintering data by time bins.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe with 'Time_s', 'Temperature_C' and 'DensidadePct' columns.
    bin_size : int, optional
        Size of each time bin in seconds, by default 10.
    Returns
    -------
    pandas.DataFrame
        Aggregated dataframe containing the mean of each column per bin.
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
    grouped = (
        dfc.groupby("bin").agg({time_col: "mean", temp_col: "mean", dens_col: "mean"})
        .reset_index(drop=True)
    )
    return grouped
