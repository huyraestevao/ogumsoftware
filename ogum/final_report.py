"""Widgets utilities for creating interactive final reports."""

from __future__ import annotations

from typing import List

import ipywidgets as widgets
from IPython.display import clear_output

from .core import SinteringDataRecord


class FinalReportModule:
    """UI module to generate statistical HTML reports."""

    def __init__(self, sintering_records: List[SinteringDataRecord]):
        """Initialize the report with a list of sintering records."""
        self.sintering_records = list(sintering_records)
        self._build_ui()

    def _build_ui(self) -> None:
        self.btn_generate = widgets.Button(
            description="Gerar Relatório Estatístico", button_style="info"
        )
        self.btn_generate.on_click(self._on_generate_report)
        self.out = widgets.Output()
        self.report_html = widgets.HTML()
        self.main_ui = widgets.VBox(
            [
                self.btn_generate,
                self.out,
                self.report_html,
            ]
        )

    def _on_generate_report(self, _=None) -> None:
        with self.out:
            clear_output()
            try:
                from .stats import bootstrap_ea, shapiro_residuals, generate_report

                experiments = [
                    rec.df
                    for rec in self.sintering_records
                    if {"Time_s", "Temperature_C", "DensidadePct"}.issubset(
                        rec.df.columns
                    )
                ]
                if not experiments:
                    raise ValueError(
                        "Nenhum dataset válido encontrado (Time_s, Temperature_C, DensidadePct)."
                    )

                ci_low, ci_high = bootstrap_ea(experiments)

                resid_df = None
                for rec in self.sintering_records:
                    if "residual" in rec.df.columns:
                        resid_df = rec.df[["residual"]]
                        break

                p_val = shapiro_residuals(resid_df) if resid_df is not None else 0.0
                results = {
                    "ea_bootstrap": (ci_low, ci_high),
                    "shapiro_p": p_val,
                    "residuals": resid_df["residual"] if resid_df is not None else [],
                }
                html = generate_report(results, output="html")
                self.report_html.value = html
            except Exception as exc:  # pragma: no cover - visual feedback only
                self.report_html.value = f"<b>Erro ao gerar relat\u00f3rio: {exc}</b>"
