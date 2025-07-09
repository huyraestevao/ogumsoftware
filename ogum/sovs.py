import numpy as np
from scipy.integrate import solve_ivp

class SOVSSolver:
    """Solver para o modelo SOVS de sinterização baseado em ODE."""

    def __init__(self, Ea: float, A: float, *, n: float = 1.0, x0: float = 0.0, dx: float = 1e-3) -> None:
        """Initialize solver with material parameters.

        Args:
            Ea: Energia de ativação (J/mol).
            A: Fator pré-exponencial.
            n: Expoente cinético ``x``.
            x0: Valor inicial de ``x``.
            dx: Passo de integração.
        """
        self.Ea = Ea
        self.A = A
        self.n = n
        self.x0 = x0
        self.dx = dx

    def _ode(self, t, x, T):
        R = 8.314
        k = self.A * np.exp(-self.Ea / (R * T))
        return k * (1 - x) * x**self.n

    def solve(self, t: np.ndarray, T: np.ndarray) -> np.ndarray:
        start = self.x0
        if np.isclose(start, 0.0) and self.n > 0:
            start = self.dx
        sol = solve_ivp(
            fun=lambda tt, xx: self._ode(tt, xx, np.interp(tt, t, T)),
            t_span=(t[0], t[-1]),
            y0=[start],
            t_eval=t,
        )
        return sol.y[0]
