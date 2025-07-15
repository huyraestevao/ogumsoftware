import pandas as pd
import pytest

from ogum.processing import calculate_log_theta


def test_calculate_log_theta_returns_dataframe():
    df = pd.DataFrame(
        {
            "Time_s": [0, 1, 2, 3],
            "Temperature_C": [100.0, 110.0, 120.0, 130.0],
            "DensidadePct": [10.0, 20.0, 30.0, 40.0],
        }
    )
    result = calculate_log_theta(df, 50.0)

    assert list(result.columns) == ["logtheta", "valor", "tempo_s"]
    assert result["logtheta"].dtype.kind in "f"
    assert result["valor"].dtype.kind in "f"
    assert result["tempo_s"].dtype.kind in "f" or result["tempo_s"].dtype.kind in "i"
    assert len(result) == len(df)


def test_calculate_log_theta_missing_columns():
    df = pd.DataFrame({"Time_s": [0, 1], "Temperature_C": [100, 110]})
    with pytest.raises(ValueError):
        calculate_log_theta(df, 50.0)


def test_calculate_log_theta_no_nan():
    df = pd.DataFrame(
        {
            "Time_s": [0, 1, 2],
            "Temperature_C": [100.0, 100.0, 100.0],
            "DensidadePct": [0.0, 10.0, 20.0],
        }
    )
    result = calculate_log_theta(df, 60)

    assert result["logtheta"].isna().sum() == 0
