import numpy as np

from core.solver import apply_savitzky_golay_filter


def test_apply_savitzky_golay_filter():
    rng = np.random.default_rng(0)
    data = np.linspace(0, 10, 100) + rng.normal(scale=0.5, size=100)
    filtered = apply_savitzky_golay_filter(data, window_length=11, polyorder=3)

    assert filtered.shape == data.shape
    assert np.var(filtered) < np.var(data)
