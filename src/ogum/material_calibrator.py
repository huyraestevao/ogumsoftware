"""Tools for calibrating material kinetics from flash sintering experiments."""
# ruff: noqa: D416

from __future__ import annotations

from typing import List, Tuple, Union

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from .core import R
from .processing import calculate_log_theta


class MaterialCalibrator:
    """Calibrate activation energy and pre--exponential factor.

    Parameters
    ----------
    experiments : Union[pd.DataFrame, List[pd.DataFrame]]
        One or more experimental datasets with columns ``Time_s``,
        ``Temperature_C`` and ``DensidadePct``.
    """

    def __init__(self, experiments: Union[pd.DataFrame, List[pd.DataFrame]]) -> None:
        """Store experiment data.

        Parameters
        ----------
        experiments
            Single DataFrame or list of DataFrames containing the experimental
            columns.
        """
        if isinstance(experiments, pd.DataFrame):
            self.experiments = [experiments]
        else:
            self.experiments = list(experiments)

    @staticmethod
    def fit(
        experiments: Union[pd.DataFrame, List[pd.DataFrame]],
    ) -> Tuple[float, float]:
        """Return ``(Ea_kj, A)`` fitted from the provided experiments.

        The regression is performed on ``ln(dens_rate / (1-x))`` versus ``1/T``,
        assuming first-order kinetics.

        Parameters
        ----------
        experiments
            List of DataFrames or a single DataFrame as accepted by
            :class:`MaterialCalibrator`.

        Returns
        -------
        Tuple[float, float]
            Estimated activation energy in kJ/mol and pre-exponential factor.
        """
        exps = (
            [experiments]
            if isinstance(experiments, pd.DataFrame)
            else list(experiments)
        )
        temps: List[np.ndarray] = []
        ys: List[np.ndarray] = []

        for df in exps:
            t = df["Time_s"].to_numpy(dtype=float)
            T = df["Temperature_C"].to_numpy(dtype=float) + 273.15
            x = df["DensidadePct"].to_numpy(dtype=float) / 100.0
            if t.size < 2:
                continue
            dxdt = np.gradient(x, t)

            with np.errstate(divide='ignore', invalid='ignore'):
                arg = dxdt / (1 - x)
            
            mask = (arg > 0) & (x >= 0) & (x < 1) & np.isfinite(arg)

            if not np.any(mask):
                continue

            temps.append(T[mask])
            ys.append(np.log(arg[mask]))

        if not temps:
            raise ValueError("No valid data for fitting")

        T_all = np.concatenate(temps)
        Y = np.concatenate(ys)

        def model(T, Ea, A):
            return np.log(A) - Ea * 1000.0 / (R * T)

        # linear regression as initial guess
        coeffs = np.polyfit(1.0 / T_all, Y, deg=1)
        slope, intercept = coeffs
        p0 = (-slope * R / 1000.0, float(np.exp(intercept)))

        bounds = ([-np.inf, 0], [np.inf, np.inf])

        try:
            params, _ = curve_fit(model, T_all, Y, p0=p0, maxfev=10000, bounds=bounds, method='trf')
        except RuntimeError:
            return np.nan, np.nan
        
        Ea, A = params
        return float(Ea), float(A)

    def simulate_synthetic(
        self, ea: float, a: float, time_array: np.ndarray
    ) -> pd.DataFrame:
        """Generate synthetic experiment data.

        Parameters
        ----------
        ea : float
            Activation energy in kJ/mol.
        a : float
            Pre-exponential factor (1/s).
        time_array : np.ndarray
            Time vector in seconds.

        Returns
        -------
        pd.DataFrame
            Columns ``Time_s``, ``Temperature_C`` and ``DensidadePct``.
        """
        # CORREÇÃO: Adicionada uma pequena variação de temperatura para
        # que o problema de ajuste seja matematicamente possível.
        T_c = np.linspace(1000.0, 1050.0, num=len(time_array))
        T_k = T_c + 273.15
        
        k = a * np.exp(-(ea * 1000.0) / (R * T_k))
        dens = 1 - np.exp(-k * time_array)
        return pd.DataFrame(
            {
                "Time_s": time_array,
                "Temperature_C": T_c,
                "DensidadePct": dens * 100.0,
            }
        )
    def curve_master_analysis(self) -> pd.DataFrame:
        """Return master curve analysis for stored experiments.

        Uses :func:`~ogum.processing.calculate_log_theta` with the fitted
        activation energy.

        Returns
        -------
        pd.DataFrame
            Concatenated ``logtheta`` results for all experiments.
        """
        ea, _ = self.fit(self.experiments)
        frames = [calculate_log_theta(df, ea) for df in self.experiments]
        return pd.concat(frames, ignore_index=True)


__all__ = ["MaterialCalibrator"]
