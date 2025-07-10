import numpy as np
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

    Returns
    -------
    np.ndarray
        Smoothed array with same shape as ``data_array``.
    """
    return savgol_filter(data_array, window_length=window_length, polyorder=polyorder)
