import numpy as np

from ogum.sovs import SOVSSolver


def test_constant_temperature_profile():
    solver = SOVSSolver(Ea=1e5, A=1.0, rho0=0.5)
    t = np.linspace(0.0, 10.0, 11)
    T = np.full_like(t, 1000.0)
    rho = solver.solve(t, T)

    assert isinstance(rho, np.ndarray)
    assert rho.shape == t.shape
    # density should increase monotonically
    assert np.all(np.diff(rho) > 0)
