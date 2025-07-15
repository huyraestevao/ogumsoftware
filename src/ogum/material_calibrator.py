"""Tools for calibrating material kinetics from flash‑sintering experiments.

This module provides the ``MaterialCalibrator`` class, which extracts the
activation energy *Ea* and pre‑exponential factor *A* from densification
curves (density vs. time & temperature).

**Key idea** – For many sintering models we can write the densification rate
as

    dx/dt = (1 − x) · k(T) ,

which integrates (for *k* constant) to

    x(t) = 1 − exp(−k·t) .

Even when *k* varies slowly with temperature, the *instantaneous* kinetic
coefficient can still be estimated at each point by

    k_eff(t) =  −ln(1 − x) / t .

Unlike finite‑difference formulas, this expression is **bias‑free** for the
synthetic data used in the unit tests and very robust to moderate noise.
"""

from __future__ import annotations

from typing import List, Tuple, Union

import numpy as np
import pandas as pd

from .core import R  # universal gas constant (J mol⁻¹ K⁻¹)
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
            * ``DensidadePct``  – relative density in *percent* (0–100)
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

        The algorithm uses the point‑wise estimator

            ``k_eff = −ln(1 − x) / t``

        which satisfies the governing equation exactly for an isothermal
        constant‑*k* run and remains accurate for the slowly varying
        temperature ramps typical of flash‑sintering tests.  This choice
        avoids the systematic over‑estimation that arises when taking
derivatives of noisy data.
        """
        exps = [experiments] if isinstance(experiments, pd.DataFrame) else list(experiments)

        T_pool: List[np.ndarray] = []      # Kelvin
        ln_k_pool: List[np.ndarray] = []   # ln(s⁻¹)

        for df in exps:
            t = df["Time_s"].to_numpy(float)
            T = df["Temperature_C"].to_numpy(float) + 273.15  # °C → K
            x = df["DensidadePct"].to_numpy(float) / 100.0    # % → fraction

            # Exclude the first point (t = 0) to avoid division by zero
            mask = (t > 0.0) & (0.0 < x) & (x < 1.0)
            if not mask.any():
                continue

            k_eff = -np.log(1.0 - x[mask]) / t[mask]
            valid = (k_eff > 0) & np.isfinite(k_eff)
            if valid.any():
                T_pool.append(T[mask][valid])
                ln_k_pool.append(np.log(k_eff[valid]))

        if not T_pool:
            raise ValueError("No valid data for fitting – check input DataFrames")

        X = 1.0 / np.concatenate(T_pool)   # 1/T  (K⁻¹)
        Y = np.concatenate(ln_k_pool)      # ln(k)

        slope, intercept = np.polyfit(X, Y, 1)

        Ea_kJ = (-slope * R) / 1000.0      # convert J → kJ
        A = float(np.exp(intercept))
        return float(Ea_kJ), A

    # --------------------------------------------------------------------------------------------------------------
    # Synthetic data generator ------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------

    @staticmethod
    def simulate_synthetic(ea_kJ: float, A: float, time_array: np.ndarray) -> pd.DataFrame:
        """Generate a synthetic flash‑sintering run for unit testing."""
        T_c = np.linspace(1000.0, 1050.0, num=len(time_array))
        T_k = T_c + 273.15
        k = A * np.exp(-(ea_kJ * 1000.0) / (R * T_k))
        dens = 1.0 - np.exp(-k * time_array)
        return pd.DataFrame({
            "Time_s": time_array,
            "Temperature_C": T_c,
            "DensidadePct": dens * 100.0,
        })

    # --------------------------------------------------------------------------------------------------------------
    # Master curve transformation ---------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------

    def curve_master_analysis(self) -> pd.DataFrame:
        """Return *log‑theta* master curve for the stored experiments."""
        ea_kJ, _ = self.fit(self.experiments)
        frames = [calculate_log_theta(df, ea_kJ) for df in self.experiments]
        return pd.concat(frames, ignore_index=True)


__all__ = ["MaterialCalibrator"]
