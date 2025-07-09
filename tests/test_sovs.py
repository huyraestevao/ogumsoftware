import numpy as np

from ogum.sovs import SOVSSolver


def test_constant_temperature_profile():
    solver = SOVSSolver(Ea=1e5, A=1.0, x0=0.5, dx=1e-3)
    t = np.linspace(0, 10, 11)
    T = np.full_like(t, 1000.0)
    x = solver.solve(t, T)

    assert x.shape == t.shape
    assert np.all(np.diff(x) > 0)
    assert np.all(x < 1)
