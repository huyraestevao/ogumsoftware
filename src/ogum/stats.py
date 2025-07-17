"""Statistical utilities for kinetic analysis."""

from __future__ import annotations

from typing import List, Tuple, Literal

import base64
import io

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import shapiro

from .material_calibrator import MaterialCalibrator


def bootstrap_ea(
    experiments: List[pd.DataFrame], n_bootstrap: int = 1000
) -> Tuple[float, float]:
    """Estimate 95% confidence interval for activation energy using bootstrapping.

    Parameters
    ----------
    experiments : list of pandas.DataFrame
        Each DataFrame must contain ``Time_s``, ``Temperature_C`` and
        ``DensidadePct`` columns.
    n_bootstrap : int, default=1000
        Number of bootstrap replicates.

    Returns:
    -------
    tuple of float
        Lower and upper bounds of the 95% confidence interval for ``Ea``
        in kJ/mol.
    """
    if not experiments:
        raise ValueError("No experiments provided")

    rng = np.random.default_rng()
    eas = np.empty(n_bootstrap, dtype=float)
    n = len(experiments)
    for i in range(n_bootstrap):
        idx = rng.integers(0, n, n)
        sample = [experiments[j] for j in idx]
        combined = pd.concat(sample, ignore_index=True)
        calib = MaterialCalibrator()
        params = calib.fit(combined)
        eas[i] = params["Ea"]

    ci_low, ci_high = np.percentile(eas, [2.5, 97.5])
    return float(ci_low), float(ci_high)


def shapiro_residuals(fit_results: pd.DataFrame) -> float:
    """Return Shapiro–Wilk p-value for residual normality.

    Parameters
    ----------
    fit_results : pandas.DataFrame
        DataFrame containing a ``residual`` column.

    Returns:
    -------
    float
        P-value of the Shapiro–Wilk test.
    """
    if "residual" not in fit_results:
        raise ValueError("DataFrame must contain 'residual' column")

    _, p_value = shapiro(fit_results["residual"].to_numpy(dtype=float))
    return float(p_value)


def generate_report(results: dict, output: Literal["md", "html"] = "md") -> str:
    """Generate a Markdown or HTML statistical report.

    Parameters
    ----------
    results : dict
        Dictionary with keys ``ea_bootstrap`` (tuple of floats), ``shapiro_p``
        (float) and ``residuals`` (array-like of bootstrap Ea values).
    output : {{'md', 'html'}}, default 'md'
        Format of the generated report.

    Returns:
    -------
    str
        Rendered report.
    """
    ci_low, ci_high = results["ea_bootstrap"]
    shapiro_p = results["shapiro_p"]
    values = np.asarray(results.get("residuals", []), dtype=float)

    fig, ax = plt.subplots()
    ax.hist(values, bins=20, color="C0", edgecolor="black")
    ax.set_title("Bootstrap Ea")
    ax.set_xlabel("Ea (kJ/mol)")
    ax.set_ylabel("Frequency")
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    b64 = base64.b64encode(buffer.getvalue()).decode()

    if output == "html":
        image = f'<img src="data:image/png;base64,{b64}" />'
        report = (
            "<h2>Relat\u00f3rio Estat\u00edstico</h2>"
            f"<p><b>Intervalo Ea 95%:</b> {ci_low:.2f} – {ci_high:.2f} kJ/mol</p>"
            f"<p><b>p-valor Shapiro:</b> {shapiro_p:.3f}</p>" + image
        )
    else:
        image = f"![bootstrap](data:image/png;base64,{b64})"
        report = (
            "## Relat\u00f3rio Estat\u00edstico\n\n"
            f"* Intervalo Ea 95%: {ci_low:.2f} – {ci_high:.2f} kJ/mol\n"
            f"* p-valor Shapiro: {shapiro_p:.3f}\n\n" + image + "\n"
        )
    return report


__all__ = ["bootstrap_ea", "shapiro_residuals", "generate_report"]
