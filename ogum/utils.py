"""Small helper utilities used across the code base."""

from __future__ import annotations



import numpy as np
import pandas as pd


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




    # Preserve all original columns averaging values inside each bin
    agg_dict = {col: "mean" for col in df.columns}
    grouped = dfc.groupby("bin").agg(agg_dict).reset_index(drop=True)
    return grouped


__all__ = ["normalize_columns", "orlandini_araujo_filter"]
