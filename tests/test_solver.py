import numpy as np

from core.solver import apply_savitzky_golay_filter, calculate_activation_energy


def test_apply_savitzky_golay_filter():
    rng = np.random.default_rng(0)
    data = np.linspace(0, 10, 100) + rng.normal(scale=0.5, size=100)
    filtered = apply_savitzky_golay_filter(data, window_length=11, polyorder=3)

    assert filtered.shape == data.shape
    assert np.var(filtered) < np.var(data)


def test_calculate_activation_energy():
    temperatures = np.array([300.0, 400.0, 500.0, 600.0])
    Q_true = 50_000.0
    rates = np.exp(-Q_true / (8.314 * temperatures))

    result = calculate_activation_energy(temperatures, rates)

    assert np.isclose(result["Q"], 50.0, atol=0.5)
    assert result["r_squared"] > 0.99
