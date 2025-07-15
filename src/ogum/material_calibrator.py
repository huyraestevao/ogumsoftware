"""Tools for calibrating material kinetics from flash sintering experiments."""
# ruff: noqa: D416

from __future__ import annotations

from typing import List, Tuple, Union

import numpy as np
import pandas as pd
# A importação do curve_fit não é mais necessária, pois usamos polyfit
# from scipy.optimize import curve_fit

from .core import R
from .processing import calculate_log_theta


class MaterialCalibrator:
    """Calibrate activation energy and pre--exponential factor."""

    def __init__(self, experiments: Union[pd.DataFrame, List[pd.DataFrame]]) -> None:
        """Store experiment data."""
        if isinstance(experiments, pd.DataFrame):
            self.experiments = [experiments]
        else:
            self.experiments = list(experiments)

    @staticmethod
    def fit(
        experiments: Union[pd.DataFrame, List[pd.DataFrame]],
    ) -> Tuple[float, float]:
        """Return ``(Ea_kj, A)`` fitted from the provided experiments.
        (Versão final, usando regressão linear direta para máxima robustez)
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

        # --- CORREÇÃO FINAL: Usar a regressão linear como a solução direta ---
        # O modelo é Y = m*X + c, onde X = 1/T, m = -Ea*1000/R, c = ln(A)
        # O polyfit é a ferramenta perfeita e mais estável para isso.
        try:
            # Fit a line (degree 1 polynomial) to the transformed data
            slope, intercept = np.polyfit(1.0 / T_all, Y, deg=1)
    
            # Calculate physical parameters from the regression
            Ea = -slope * R / 1000.0  # Activation energy in kJ/mol
            A = np.exp(intercept)      # Pre-exponential factor
    
            return float(Ea), float(A)
        except (np.linalg.LinAlgError, ValueError):
             # If polyfit fails (e.g., insufficient data), return NaN
            return np.nan, np.nan

    def simulate_synthetic(
        self, ea: float, a: float, time_array: np.ndarray
    ) -> pd.DataFrame:
        """Generate synthetic experiment data."""
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
        """Return master curve analysis for stored experiments."""
        ea, _ = self.fit(self.experiments)
        frames = [calculate_log_theta(df, ea) for df in self.experiments]
        return pd.concat(frames, ignore_index=True)


__all__ = ["MaterialCalibrator"]
