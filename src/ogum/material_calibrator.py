"""Tools for calibrating material kinetics from flash‑sintering experiments.

This module provides the ``MaterialCalibrator`` class, which extracts the
activation energy *Ea* and pre‑exponential factor *A* from densification
curves (density vs. time & temperature). The fitting routine implements a
straight‑line Arrhenius regression on

    ln k  =  ln A  −  Ea / (R T)

where the kinetic coefficient *k* is obtained point‑wise as:

    k_i = (dx/dt)_i / (1 − x_i)

using **backward finite differences** so that *x*, *T*, and the derivative
are evaluated at the same instant.  This avoids the positive bias observed
with centred differences when temperature increases during the run.
"""

from __future__ import annotations

from typing import List, Tuple, Union

import numpy as np
import pandas as pd

from .core import R  # universal gas constant (J mol⁻¹ K⁻¹)
from .processing import calculate_log_theta

# ------------------------------------------------------------------------------------------------------------------

class MaterialCalibrator:
    """Calibrate activation energy (Ea, kJ mol⁻¹) and pre‑exponential factor (A, s⁻¹)."""

    # --------------------------------------------------------------------------------------------------------------
    # Construction & helpers
    # --------------------------------------------------------------------------------------------------------------

    def __init__(self, experiments: Union[pd.DataFrame, List[pd.DataFrame]]) -> None:
        """Store one or more experimental DataFrames.

        Each DataFrame must contain the columns:
            * ``Time_s``        – time in seconds
            * ``Temperature_C`` – temperature in °C
            * ``DensidadePct``  – relative density in *percent*
        """
        self.experiments: List[pd.DataFrame]
        if isinstance(experiments, pd.DataFrame):
            self.experiments = [experiments]
        else:
            self.experiments = list(experiments)

    # --------------------------------------------------------------------------------------------------------------
    # Core calibration routine
    # --------------------------------------------------------------------------------------------------------------

    @staticmethod
    def fit(experiments: Union[pd.DataFrame, List[pd.DataFrame]]) -> Tuple[float, float]:
        """Return ``(Ea_kJ, A)`` fitted from the provided experiments.

        The method stacks all valid ``(T, ln k)`` pairs from the input runs and
        performs a simple least‑squares *linear* regression of ``ln k`` against
        ``1/T`` using :pyfunc:`numpy.polyfit` (degree 1).  No nonlinear solver
        is required and the approach is numerically robust even with moderate
        noise.
        """
        # Normalise input to a list of DataFrames
        exps = [experiments] if isinstance(experiments, pd.DataFrame) else list(experiments)

        T_pool: List[np.ndarray] = []      # Kelvin
        ln_k_pool: List[np.ndarray] = []   # ln(s⁻¹)

        for df in exps:
            # ---- Extract data ------------------------------------------------------------------------------------
            t = df["Time_s"].to_numpy(float)
            T = df["Temperature_C"].to_numpy(float) + 273.15  # convert °C → K
            x = df["DensidadePct"].to_numpy(float) / 100.0    # percent → fraction (0‑1)

            if t.size < 2:
                # Need at least two points for a derivative
                continue

            # ---- Backward finite difference ---------------------------------------------------------------------
            dx = np.diff(x)          # x_i − x_{i-1}
            dt = np.diff(t)          # Δt (s)
            k_i = dx / dt / (1.0 - x[:-1])   # k evaluated at t_{i-1}
            T_i = T[:-1]                       # matching temperature

            mask = (k_i > 0) & np.isfinite(k_i)
            if mask.any():
                T_pool.append(T_i[mask])
                ln_k_pool.append(np.log(k_i[mask]))

        if not T_pool:
            raise ValueError("No valid data for fitting – check input DataFrames")

        X = 1.0 / np.concatenate(T_pool)    # 1/T  (K⁻¹)
        Y = np.concatenate(ln_k_pool)       # ln(k)

        # ---- Linear regression (Y = m X + c) ---------------------------------------------------------------------
        slope, intercept = np.polyfit(X, Y, deg=1)

        # Convert slope/intercept to physical parameters
        Ea_kJ = (-slope * R) / 1000.0       # J → kJ
        A = float(np.exp(intercept))

        return float(Ea_kJ), A

    # --------------------------------------------------------------------------------------------------------------
    # Synthetic data generator (useful for tests) ------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------

    @staticmethod
    def simulate_synthetic(ea_kJ: float, A: float, time_array: np.ndarray) -> pd.DataFrame:
        """Generate a synthetic flash‑sintering run for unit testing.

        Parameters
        ----------
        ea_kJ
            Activation energy in *kJ mol⁻¹*.
        A
            Pre‑exponential factor in *s⁻¹*.
        time_array
            1‑D array of time points (s).
        """
        # Linear temperature ramp – purely illustrative
        T_c = np.linspace(1000.0, 1050.0, num=len(time_array))
        T_k = T_c + 273.15

        k = A * np.exp(-(ea_kJ * 1000.0) / (R * T_k))  # back to J in numerator
        dens = 1.0 - np.exp(-k * time_array)

        return pd.DataFrame({
            "Time_s": time_array,
            "Temperature_C": T_c,
            "DensidadePct": dens * 100.0,
        })

    # --------------------------------------------------------------------------------------------------------------
    # Utility: master curve transformation -----------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------

    def curve_master_analysis(self) -> pd.DataFrame:
        """Return *log‑theta* master curve for the stored experiments."""
        ea_kJ, _ = self.fit(self.experiments)
        frames = [calculate_log_theta(df, ea_kJ) for df in self.experiments]
        return pd.concat(frames, ignore_index=True)


__all__ = ["MaterialCalibrator"]
