import pytest
import pandas as pd
import pandas.testing as pdt

from ogum import utils


def test_add_suffix_once():
    assert utils.add_suffix_once("col", "_x") == "col_x"
    assert utils.add_suffix_once("col_x", "_x") == "col_x"


def test_orlandini_araujo_filter_basic():
    df = pd.DataFrame({
        "Time_s": [0, 1, 2, 3],
        "Temperature_C": [10, 20, 30, 40],
        "DensidadePct": [5, 7, 9, 11],
    })
    result = utils.orlandini_araujo_filter(df, bin_size=2)

    expected = pd.DataFrame({
        "Time_s": [0.5, 2.5],
        "Temperature_C": [15.0, 35.0],
        "DensidadePct": [6.0, 10.0],
    })
    pdt.assert_frame_equal(result, expected)


def test_orlandini_araujo_filter_missing():
    df = pd.DataFrame({"Time_s": [0, 1]})
    with pytest.raises(ValueError):
        utils.orlandini_araujo_filter(df)
