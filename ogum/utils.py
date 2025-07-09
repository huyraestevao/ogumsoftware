"""Small helper utilities used across the code base."""
from __future__ import annotations

from typing import Dict, Iterable

import numpy as np
import pandas as pd
import numpy as np


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


def orlandini_araujo_filter(df: pd.DataFrame, bin_size: int = 10) -> pd.DataFrame:

        )

    dfc = df.copy()
    dfc["bin"] = np.floor(dfc[time_col] / bin_size).astype(int)

