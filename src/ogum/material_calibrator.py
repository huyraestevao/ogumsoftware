"""Utilities for calibrating Arrhenius parameters from sintering data."""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from .core import R


class MaterialCalibrator:
    """Fit and predict densification using an Arrhenius model."""

    def __init__(self, Ea: float | None = None, A: float | None = None) -> None:
        """Create a calibrator instance.

        Parameters
        ----------
        Ea : float, optional
            Activation energy in kJ/mol.
        A : float, optional
            Pre-exponential factor in s⁻¹.
        """
        self.Ea = Ea
        self.A = A

    @staticmethod
    def _arrhenius_rate(T_k: np.ndarray, Ea: float, A: float) -> np.ndarray:
        Ea_j = Ea * 1000.0
        return A * np.exp(-Ea_j / (R * T_k))

    @staticmethod
    def _densification(t: np.ndarray, T_c: np.ndarray, Ea: float, A: float) -> np.ndarray:
        T_k = T_c + 273.15
        rates = MaterialCalibrator._arrhenius_rate(T_k, Ea, A)
        x = np.zeros_like(t, dtype=float)
        for i in range(1, len(t)):
            dt = t[i] - t[i - 1]
            x[i] = x[i - 1] + dt * (1.0 - x[i - 1]) * rates[i - 1]
        return x

    def fit(self, df: pd.DataFrame) -> Dict[str, float]:
        """Estimate ``Ea`` and ``A`` from experimental data.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame with ``Time_s``, ``Temperature_C`` and ``DensidadePct``.

        Returns:
        -------
        dict
            Dictionary with keys ``'Ea'`` and ``'A'``.
        """
        t = df["Time_s"].to_numpy(dtype=float)
        T = df["Temperature_C"].to_numpy(dtype=float)
        y = df["DensidadePct"].to_numpy(dtype=float) / 100.0

        def model(arr: tuple[np.ndarray, np.ndarray], Ea: float, A: float) -> np.ndarray:
            times, temps = arr
            return MaterialCalibrator._densification(times, temps, Ea, A)

        p0 = [self.Ea if self.Ea is not None else 50.0, self.A if self.A is not None else 1.0]
        popt, _ = curve_fit(model, (t, T), y, p0=p0, bounds=(0.0, np.inf))
        self.Ea, self.A = float(popt[0]), float(popt[1])
        return {"Ea": self.Ea, "A": self.A}

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict densification curves using fitted parameters.

        Parameters
        ----------
        df : pandas.DataFrame
            Must contain ``Time_s`` and ``Temperature_C`` columns.

        Returns:
        -------
        pandas.DataFrame
            Copy of ``df`` with ``predicted_density`` column in percent.
        """
        if self.Ea is None or self.A is None:
            raise ValueError("Model parameters not fitted")
        t = df["Time_s"].to_numpy(dtype=float)
        T = df["Temperature_C"].to_numpy(dtype=float)
        dens = MaterialCalibrator._densification(t, T, self.Ea, self.A) * 100.0
        result = df.copy()
        result["predicted_density"] = dens
        return result

    @staticmethod
    def simulate_synthetic(ea_kJ: float, A: float, time_array: np.ndarray) -> pd.DataFrame:
        """Generate synthetic densification data for testing."""
        T_c = np.full_like(time_array, 1000.0)
        dens = MaterialCalibrator._densification(time_array, T_c, ea_kJ, A)
        return pd.DataFrame({
            "Time_s": time_array,
            "Temperature_C": T_c,
            "DensidadePct": dens * 100.0,
        })


__all__ = ["MaterialCalibrator"]
