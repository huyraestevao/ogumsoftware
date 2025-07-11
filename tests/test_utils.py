import pandas as pd
import pytest
from scipy.signal import savgol_filter as scipy_savgol

from ogum import utils


def test_normalize_columns_basic():
    df = pd.DataFrame({"Tempo_s": [1, 2], "densidadepct": [0.1, 0.2]})
    mapping = {"Time_s": ["tempo_s"], "DensidadePct": ["densidadepct"]}
    result = utils.normalize_columns(df, mapping)
    assert list(result.columns) == ["Time_s", "DensidadePct"]


def test_orlandini_araujo_filter():
    df = pd.DataFrame(
        {
            "Time_s": [0, 1, 2, 11, 12],
            "Temperature_C": [100, 102, 101, 103, 104],
            "DensidadePct": [10, 20, 30, 40, 50],
        }
    )
    filtered = utils.orlandini_araujo_filter(df, bin_size=10)
    expected = pd.DataFrame(
        {
            "Time_s": [1.0, 11.5],
            "Temperature_C": [101.0, 103.5],
            "DensidadePct": [20.0, 45.0],
        }
    )
    pd.testing.assert_frame_equal(filtered.reset_index(drop=True), expected)


def test_orlandini_missing_columns():
    df = pd.DataFrame({"Time_s": [0], "Temperature_C": [100]})
    with pytest.raises(ValueError):
        utils.orlandini_araujo_filter(df)


def test_savgol_filter_basic():
    df = pd.DataFrame({"A": [1, 2, 3, 4, 5], "B": [10, 11, 12, 13, 14]})
    result = utils.savgol_filter(df, window=5, polyorder=2)
    expected = pd.DataFrame(
        {
            "A": scipy_savgol(df["A"].to_numpy(), 5, 2),
            "B": scipy_savgol(df["B"].to_numpy(), 5, 2),
        }
    )
    pd.testing.assert_frame_equal(result, expected)
