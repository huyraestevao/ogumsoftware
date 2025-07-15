"""Widgets utilities for creating interactive final reports."""

from __future__ import annotations

from typing import Callable, List, Optional

import ipywidgets as widgets
from IPython.display import clear_output

from .core import SinteringDataRecord, exibir_mensagem, exibir_erro


class FinalReportModule:
    """UI module to generate statistical HTML reports."""

    def __init__(
        self,
        sintering_records: List[SinteringDataRecord],
        *,
        on_busy: Optional[Callable[[bool, str], None]] = None,
        log_output: Optional[widgets.Output] = None,
    ) -> None:
        """Initialize the report with a list of sintering records."""
        self.sintering_records = list(sintering_records)
        self.on_busy = on_busy
        self.log_output = log_output
        self._build_ui()

    def _build_ui(self) -> None:
        """Create the widget layout used by the report module."""
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
        """Generate the report and display the resulting HTML."""
        if self.on_busy:
            self.on_busy(True, "Gerando relatório...")
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
                exibir_mensagem("Relatório gerado com sucesso", self.log_output)
            except Exception as exc:  # pragma: no cover - visual feedback only
                self.report_html.value = f"<b>Erro ao gerar relatório: {exc}</b>"
                exibir_erro(str(exc), self.log_output)
            finally:
                if self.on_busy:
                    self.on_busy(False, "")
