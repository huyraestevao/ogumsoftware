"""Small helper utilities used across the code base."""

from __future__ import annotations

from typing import Dict, Iterable

import numpy as np
import pandas as pd


def normalize_columns(df: pd.DataFrame, mapping: Dict[str, Iterable[str]]) -> pd.DataFrame:


__all__ = [
    "normalize_columns",
    "orlandini_araujo_filter",
]
