import numpy as np
from scipy.integrate import solve_ivp

class SOVSSolver:
    """Integrate the Skorohod–Olevsky (SOVS) sintering model.

    The governing equation is

    ``dx/dt = A * exp(-Ea / (R * T)) * (1 - x) * x**n``,
    where ``x`` is the relative density fraction.
    """

    def __init__(
        self,
        Ea: float,
        A: float,
        x0: float = 0.0,
        dx: float = 1e-3,
        n: float = 1.0,
        R: float = 8.314,
    ) -> None:
        """Create a solver instance.

        Args:
            Ea: Activation energy in J/mol.
            A: Pre-exponential factor.
            x0: Initial relative density fraction.
            dx: Step size used by the integrator.
            n: Reaction order exponent in ``x**n``.
            R: Universal gas constant.
        """


        self.Ea = Ea
        self.A = A
        self.n = n
        self.x0 = x0
        self.dx = dx
        self.n = n
        self.R = R

    def _ode(self, t: float, x: float, T: float) -> float:
        """Return ``dx/dt`` for the SOVS model.


            t_eval=t,
        )
        return sol.y[0]
