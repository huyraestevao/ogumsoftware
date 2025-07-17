import numpy as np
import pandas as pd

from ogum.material_calibrator import MaterialCalibrator


def _generate_data(ea: float, A: float, times: np.ndarray) -> pd.DataFrame:
    temp = np.full_like(times, 1000.0)
    dens = MaterialCalibrator._densification(times, temp, ea, A) * 100.0
    return pd.DataFrame({
        "Time_s": times,
        "Temperature_C": temp,
        "DensidadePct": dens,
    })


def test_fit_converges_close():
    t = np.linspace(0, 10, 50)
    ea_true = 60.0
    a_true = 2.0
    df = _generate_data(ea_true, a_true, t)
    calib = MaterialCalibrator()
    params = calib.fit(df)
    assert np.isclose(params["Ea"], ea_true, rtol=0.05)
    assert np.isclose(params["A"], a_true, rtol=0.05)


def test_predict_matches_observed():
    t = np.linspace(0, 8, 40)
    ea_true = 45.0
    a_true = 1.5
    df = _generate_data(ea_true, a_true, t)
    calib = MaterialCalibrator()
    calib.fit(df)
    pred = calib.predict(df)
    assert "predicted_density" in pred.columns
    assert np.allclose(pred["predicted_density"], df["DensidadePct"], rtol=1e-2)
