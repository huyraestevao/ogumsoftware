from __future__ import annotations

# ruff: noqa: D100, E402
"""Utilities for master curve calculations."""

import pandas as pd

from .processing import calculate_log_theta


def calc_cms(df: pd.DataFrame, energia_ativacao_kj: float) -> pd.DataFrame:
    """Wrapper for :func:`calculate_log_theta` returning master curve columns."""
    return calculate_log_theta(df, energia_ativacao_kj)


__all__ = ["calc_cms"]
