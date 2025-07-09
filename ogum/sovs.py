"""Sintering solver based on the Skorohod-Olevsky viscous sintering model."""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from .core import R


class SOVSSolver:
    """Simple numerical solver for the SOVS densification model.

    Parameters
    ----------
    Ea:
        Activation energy in J/mol.
    A:
        Pre-exponential factor with units 1/s.
    m:
        Exponent of the densification term. Defaults to 1.
    rho0:
        Initial relative density in the range 0--1.
    R_const:
        Gas constant used in the Arrhenius term. Defaults to
        :data:`ogum.core.R`.
    """

    def __init__(self, Ea: float, A: float, m: float = 1.0, rho0: float = 0.6, R_const: float = R) -> None:
        self.Ea = Ea
        self.A = A
        self.m = m
        self.rho0 = rho0
        self.R_const = R_const
        self._t_profile: np.ndarray | None = None
        self._T_profile: np.ndarray | None = None

    # ------------------------------------------------------------------
    def _interp_T(self, t: float) -> float:
        assert self._t_profile is not None
        assert self._T_profile is not None
        return float(np.interp(t, self._t_profile, self._T_profile))

    def _ode(self, t: float, y: np.ndarray) -> np.ndarray:
        rho = y[0]
        T = self._interp_T(t)
        rate = self.A * np.exp(-self.Ea / (self.R_const * T)) * (1.0 - rho) ** self.m
        return np.array([rate])

    # ------------------------------------------------------------------
    def solve(self, t: np.ndarray, T: np.ndarray) -> np.ndarray:
        """Solve the densification ODE for a time--temperature profile.

        Parameters
        ----------
        t:
            1D array with the time points in seconds.
        T:
            1D array with the temperature values in Kelvin at each time in
            ``t``.

        Returns
        -------
        numpy.ndarray
            Array of relative densities evaluated at ``t``.
        """

        t = np.asarray(t, dtype=float)
        T = np.asarray(T, dtype=float)
        if t.shape != T.shape:
            raise ValueError("t and T must have the same shape")
        if t.ndim != 1:
            raise ValueError("t and T must be one-dimensional")

        self._t_profile = t
        self._T_profile = T

        sol = solve_ivp(self._ode, (float(t[0]), float(t[-1])), np.array([self.rho0]), t_eval=t, vectorized=False)
        return sol.y[0]


__all__ = ["SOVSSolver"]
