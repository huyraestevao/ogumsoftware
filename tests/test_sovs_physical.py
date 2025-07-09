import numpy as np

from ogum.sovs import SOVSSolver
from ogum.core import R


def test_physical_solution_constant_T():
    Ea = 1e5
    A = 2.0
    solver = SOVSSolver(Ea=Ea, A=A, x0=0.0, dx=1e-3)
    t = np.linspace(0, 10, 11)
    T_const = 1000.0
    T = np.full_like(t, T_const)

    x_numeric = solver.solve(t, T)

    k = A * np.exp(-Ea / (R * T_const))
    x_expected = 1 - np.exp(-k * t)

    assert np.allclose(x_numeric, x_expected, rtol=1e-5, atol=1e-7)
