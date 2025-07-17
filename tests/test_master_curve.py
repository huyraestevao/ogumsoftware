import numpy as np
import pandas as pd

from ogum.master_curve import build_master_curve
from ogum.material_calibrator import MaterialCalibrator


def _synthetic() -> pd.DataFrame:
    t = np.linspace(0, 2, 20)
    df = MaterialCalibrator.simulate_synthetic(60.0, 2.0, t)
    return df.rename(
        columns={"Time_s": "time", "Temperature_C": "temperature", "DensidadePct": "density"}
    )


def test_build_master_curve_structure():
    df = _synthetic()
    result = build_master_curve(df)
    assert list(result.columns) == ["master_time", "master_density", "activation_energy"]
    assert len(result) == len(df)


def test_build_master_curve_activation_energy():
    df = _synthetic()
    result = build_master_curve(df)
    ea = result["activation_energy"].iloc[0]
    assert np.isclose(ea, 60.0, rtol=0.3)

