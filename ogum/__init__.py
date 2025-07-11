"""Ogum Sintering modules."""

from .core import (
    R,
    SinteringDataRecord,
    DataHistory,
    add_suffix_once,
    criar_titulo,
    exibir_mensagem,
    exibir_erro,
    gerar_link_download,
    boltzmann_sigmoid,
    generalized_logistic_stable,
    SOVSSolver,
)
from .utils import normalize_columns, orlandini_araujo_filter, savgol_filter
from .plotting import plot_sintering_curves
from .processing import calculate_log_theta
from .material_calibrator import MaterialCalibrator
from .stats import bootstrap_ea, shapiro_residuals, generate_report

__all__ = [
    "R",
    "SinteringDataRecord",
    "DataHistory",
    "add_suffix_once",
    "criar_titulo",
    "exibir_mensagem",
    "exibir_erro",
    "gerar_link_download",
    "boltzmann_sigmoid",
    "generalized_logistic_stable",
    "SOVSSolver",
    "normalize_columns",
    "orlandini_araujo_filter",
    "savgol_filter",
    "calculate_log_theta",
    "MaterialCalibrator",
    "plot_sintering_curves",
    "bootstrap_ea",
    "shapiro_residuals",
    "generate_report",
]
