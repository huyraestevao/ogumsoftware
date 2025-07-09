import pandas as pd
from ogum.utils import normalize_columns
from ogum.core import DataHistory, add_suffix_once


def test_normalize_columns():
    df = pd.DataFrame(columns=["Tempo", "Tensao", "Corrente"])
    mapping = {
        "time": ["tempo"],
        "voltage": ["tensao"],
        "current": ["corrente"],
    }
    out = normalize_columns(df, mapping)
    assert list(out.columns) == ["time", "voltage", "current"]


def test_data_history_and_suffix():
    dh = DataHistory()
    df = pd.DataFrame({"a": [1, 2]})
    dh.push(df, "m1")
    assert dh.peek()["module"] == "m1"
    renamed = add_suffix_once("col", "_x")
    assert renamed == "col_x"
    assert add_suffix_once(renamed, "_x") == "col_x"
