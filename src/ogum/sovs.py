"""Numerical solver for the Skorohod--Olevsky sintering model."""

import numpy as np
from scipy.integrate import solve_ivp


class SOVSSolver:
    """Integrate the Skorohod–Olevsky (SOVS) sintering model.

    The governing equation is:

        dx/dt = A * exp(-Ea / (R * T)) * (1 - x) * x**n

    where ``x`` is the relative density fraction.
    """

    def __init__(
        self,
        Ea: float,
        A: float,
        x0: float = 0.0,
        dx: float = 1e-3,
        n: float = 0.0,
        R: float = 8.314,
    ) -> None:
        """Create a solver instance.

        Args:
            Ea: Activation energy in J/mol.
            A: Pre‐exponential factor (1/s).
            x0: Initial relative density fraction.
            dx: Step size used by the integrator.
            n: Reaction‐order exponent in ``x**n`` (default 0 for first‐order kinetics).
            R: Universal gas constant (J/(mol·K)).
        """
        self.Ea = Ea
        self.A = A
        self.n = n
        self.x0 = x0
        self.dx = dx
        self.R = R

    def _ode(self, t: float, x: float, T: float) -> float:
        """Return ``dx/dt`` for the SOVS model at a given time point.

        Args:
            t: Current time.
            x: Current density fraction.
            T: Current temperature.

        Returns:
            Rate of change dx/dt.
        """
        k = self.A * np.exp(-self.Ea / (self.R * T))
        return k * (1 - x) * x**self.n

    def solve(self, t: np.ndarray, T: np.ndarray) -> np.ndarray:
        """Integrate the SOVS ODE over a time‐temperature profile.

        Args:
            t: 1D array of time points.
            T: 1D array of temperatures (same length as `t`).

        Returns:
            1D array of density fraction x(t), evaluated at each time in `t`.
        """
        sol = solve_ivp(
            fun=lambda tt, xx: self._ode(tt, xx, np.interp(tt, t, T)),
            t_span=(t[0], t[-1]),
            y0=[self.x0],
            t_eval=t,
        )
        return sol.y[0]
