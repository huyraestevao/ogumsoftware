import numpy as np
from scipy import stats
from scipy.signal import savgol_filter


def apply_savitzky_golay_filter(
    data_array: np.ndarray, window_length: int, polyorder: int
) -> np.ndarray:
    """Apply Savitzky–Golay smoothing to a 1D array.

    Parameters
    ----------
    data_array : np.ndarray
        Array containing the data to be smoothed.
    window_length : int
        Size of the moving window; must be odd.
    polyorder : int
        Order of the polynomial used for the fit.

    Returns:
    -------
    np.ndarray
        Smoothed array with same shape as ``data_array``.
    """
    return savgol_filter(data_array, window_length=window_length, polyorder=polyorder)


def calculate_activation_energy(
    temperatures: np.ndarray, rates: np.ndarray
) -> dict[str, float]:
    """Compute activation energy from Arrhenius data.

    Parameters
    ----------
    temperatures : np.ndarray
        Absolute temperatures in Kelvin.
    rates : np.ndarray
        Rate values corresponding to ``temperatures``.

    Returns:
    -------
    dict[str, float]
        Dictionary with keys ``Q`` (kJ/mol), ``r_squared``, ``slope`` and
        ``intercept`` from the linear regression.
    """
    if temperatures.size != rates.size:
        raise ValueError("temperatures and rates must have the same length")

    inv_T = 1.0 / temperatures.astype(float)
    ln_rate = np.log(rates.astype(float))

    regression = stats.linregress(inv_T, ln_rate)
    r_squared = regression.rvalue ** 2
    Q = -regression.slope * 8.314 / 1000.0

    return {
        "Q": Q,
        "r_squared": r_squared,
        "slope": regression.slope,
        "intercept": regression.intercept,
    }
