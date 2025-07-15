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
        (Versão final, simples e robusta)
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

        # --- ALTERAÇÃO FINAL: Usar a regressão linear como a solução direta ---
        # O modelo é Y = m*X + c, onde X = 1/T, m = -Ea*1000/R, c = ln(A)
        # O polyfit é a ferramenta perfeita e mais estável para isso.
        
        try:
            coeffs = np.polyfit(1.0 / T_all, Y, deg=1)
            slope, intercept = coeffs
    
            # Extrai os parâmetros físicos da regressão
            Ea = -slope * R / 1000.0  # Energia de ativação em kJ/mol
            A = np.exp(intercept)      # Fator pré-exponencial
    
            return float(Ea), float(A)
        except (np.linalg.LinAlgError, ValueError):
             # Se o polyfit falhar (dados insuficientes/inválidos), retorna NaN
            return np.nan, np.nan
        def model(T, Ea, A):
            return np.log(A) - Ea * 1000.0 / (R * T)

        # --- CORREÇÃO FINAL: Usar um chute inicial (p0) fixo e robusto ---
        # Em vez de um polyfit instável, damos valores razoáveis para o otimizador.
        p0 = (100.0, 1.0)  # (Ea, A)

        bounds = ([-np.inf, 0], [np.inf, np.inf])

        try:
            params, _ = curve_fit(model, T_all, Y, p0=p0, maxfev=10000, bounds=bounds, method='trf')
        except (RuntimeError, ValueError):
            return np.nan, np.nan
        
        Ea, A = params
        return float(Ea), float(A)

    def simulate_synthetic(
        self, ea: float, a: float, time_array: np.ndarray
    ) -> pd.DataFrame:
        """Generate synthetic experiment data."""
        # CORREÇÃO: Adicionada uma variação de temperatura para que o 
        # problema de ajuste seja matematicamente possível.
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
