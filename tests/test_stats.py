import numpy as np
import pandas as pd

from ogum.stats import bootstrap_ea, shapiro_residuals, generate_report
from ogum.material_calibrator import MaterialCalibrator


def test_bootstrap_ea_contains_true():
    rng = np.random.default_rng(0)
    t = np.linspace(0, 5, 20)
    ea_true = 60.0
    a_true = 2.0
    calib = MaterialCalibrator(pd.DataFrame())
    experiments = []
    for _ in range(3):
        df = calib.simulate_synthetic(ea_true, a_true, t)
        df["DensidadePct"] += rng.normal(scale=0.5, size=len(t))
        experiments.append(df)

    ci_low, ci_high = bootstrap_ea(experiments, n_bootstrap=200)
    assert ci_low <= ea_true <= ci_high


def test_shapiro_residuals_normal():
    rng = np.random.default_rng(1)
    df = pd.DataFrame({"residual": rng.normal(size=50)})
    p_val = shapiro_residuals(df)
    assert p_val >= 0.05


def test_generate_report_contents():
    vals = np.linspace(50, 70, 10)
    res = {
        "ea_bootstrap": (50.0, 70.0),
        "shapiro_p": 0.12,
        "residuals": vals,
    }
    text = generate_report(res, output="md")
    assert "Intervalo Ea" in text
    assert "p-valor Shapiro" in text
    assert "data:image/png;base64" in text
