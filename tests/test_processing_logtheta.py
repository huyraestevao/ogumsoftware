import numpy as np
import pandas as pd

from ogum.processing import calculate_log_theta


def test_logtheta_no_nan():
    t = np.array([0.1, 0.2, 0.3])
    T = np.array([1000, 1010, 1020])
    x = np.array([10, 30, 60])  # densidade %
    df = pd.DataFrame({"Time_s": t, "Temperature_C": T, "DensidadePct": x})
    out = calculate_log_theta(df, 60)
    assert out["logtheta"].notna().all()
