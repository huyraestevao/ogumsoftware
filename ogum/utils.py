"""Small helper utilities used across the code base."""
from __future__ import annotations

from typing import Dict, Iterable

import numpy as np
import pandas as pd


def normalize_columns(df: pd.DataFrame, mapping: Dict[str, Iterable[str]]) -> pd.DataFrame:

    if not (time_col and temp_col and dens_col):
        raise ValueError(
            "Faltam colunas (Time_s, Temperature_C, DensidadePct) para Orlandini-Araújo."
        )

    dfc = df.copy()
    dfc["bin"] = np.floor(dfc[time_col] / bin_size).astype(int)
    agg_dict = {col: "mean" for col in df.columns}
    grouped = dfc.groupby("bin").agg(agg_dict).reset_index(drop=True)
    return grouped

