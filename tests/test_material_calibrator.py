import numpy as np
import pandas as pd

from ogum.material_calibrator import MaterialCalibrator


def test_basic_instantiation():
    df = pd.DataFrame(
        {
            "Time_s": np.linspace(0, 1, 5),
            "Temperature_C": np.full(5, 1000.0),
            "DensidadePct": np.linspace(0, 50, 5),
        }
    )
    calib = MaterialCalibrator(df)
    assert len(calib.experiments) == 1


def test_fit_returns_parameters_close():
    t = np.linspace(0, 10, 50)
    ea_true = 60.0
    a_true = 2.0
    calib_tmp = MaterialCalibrator(pd.DataFrame())
    df = calib_tmp.simulate_synthetic(ea_true, a_true, t)
    est_ea, est_a = MaterialCalibrator.fit(df)
    assert np.isclose(est_ea, ea_true, rtol=0.3)
    assert np.isclose(est_a, a_true, rtol=0.3)


def test_simulate_synthetic_structure():
    t = np.linspace(0, 5, 10)
    calib_tmp = MaterialCalibrator(pd.DataFrame())
    df = calib_tmp.simulate_synthetic(40.0, 1.0, t)
    assert list(df.columns) == ["Time_s", "Temperature_C", "DensidadePct"]
    assert df["DensidadePct"].between(0, 100).all()
    assert (df["Temperature_C"] == df["Temperature_C"].iloc[0]).all()


def test_curve_master_analysis_columns():
    t = np.linspace(0, 2, 10)
    calib_tmp = MaterialCalibrator(pd.DataFrame())
    df = calib_tmp.simulate_synthetic(50.0, 1.0, t)
    calib = MaterialCalibrator(df)
    result = calib.curve_master_analysis()
    assert list(result.columns) == ["logtheta", "valor", "tempo_s"]
    assert len(result) == len(df)
