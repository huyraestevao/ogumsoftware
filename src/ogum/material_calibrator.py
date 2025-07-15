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
    # ... (código de preparação de dados) ...
    for df in exps:
        # ...
        dxdt = np.gradient(x, t)

        # --- CORREÇÃO 1: Preparação de dados mais robusta ---
        # Suprime avisos de divisão por zero e usa uma máscara para filtrar
        # apenas valores válidos (positivos e finitos).
        with np.errstate(divide='ignore', invalid='ignore'):
            arg = dxdt / (1 - x)
        
        mask = (arg > 0) & (x >= 0) & (x < 1) & np.isfinite(arg)

        if not np.any(mask):
            continue

        temps.append(T[mask])
        ys.append(np.log(arg[mask]))

    # ... (código de concatenação) ...

    def model(T, Ea, A):
        # A função do modelo em si permanece a mesma.
        return np.log(A) - Ea * 1000.0 / (R * T)

    # ... (código para chute inicial) ...

    # --- CORREÇÃO 2: Adicionar limites (bounds) para os parâmetros ---
    # Força o parâmetro 'A' a ser sempre >= 0.
    # Esta é a mudança mais importante para estabilizar o otimizador.
    bounds = ([-np.inf, 0], [np.inf, np.inf])

    try:
        # A chamada ao otimizador agora inclui os 'bounds'.
        params, _ = curve_fit(model, T_all, Y, p0=p0, maxfev=10000, bounds=bounds)
    except RuntimeError:
        # --- CORREÇÃO 3: Tratamento de erro defensivo ---
        # Se, mesmo com os bounds, a otimização falhar, retornamos um
        # resultado inválido (NaN) para não travar o programa.
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
        T_c = 1000.0
        k = a * np.exp(-(ea * 1000.0) / (R * (T_c + 273.15)))
        dens = 1 - np.exp(-k * time_array)
        return pd.DataFrame(
            {
                "Time_s": time_array,
                "Temperature_C": np.full_like(time_array, T_c),
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
