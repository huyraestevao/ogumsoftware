"""Utility classes and functions shared across Ogum modules."""

from __future__ import annotations

import base64
import copy
import datetime
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from uuid import uuid4
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import ipywidgets as widgets
from IPython.display import HTML, display


def add_suffix_once(col: str, suffix: str) -> str:
    """Return ``col`` with ``suffix`` appended once.

    Args:
        col: Column name.
        suffix: Suffix to append.

    Returns:
        Column name with suffix appended if it was not already present.
    """
    return col if col.endswith(suffix) else f"{col}{suffix}"


def criar_titulo(texto: str, nivel: int = 2) -> widgets.HTML:
    """Create a HTML heading widget.

    Args:
        texto: Heading text.
        nivel: Heading level between 1 and 6.

    Returns:
        The HTML widget with the given level and text.
    """
    return widgets.HTML(f"<h{nivel}>{texto}</h{nivel}>")


def exibir_mensagem(msg: str) -> None:
    """Display an informational message in blue."""
    display(HTML(f"<p style='color:blue; font-style:italic;'>{msg}</p>"))


def exibir_erro(msg: str) -> None:
    """Display an error message in red."""
    display(HTML(f"<p style='color:red; font-weight:bold;'>ERRO: {msg}</p>"))


def criar_caixa_colapsavel(titulo: str, conteudo: widgets.Widget, aberto: bool = False) -> widgets.Accordion:
    """Create a collapsible accordion box.

    Args:
        titulo: Title for the box.
        conteudo: Widget to show when expanded.
        aberto: Whether the accordion starts opened.

    Returns:
        The configured :class:`widgets.Accordion` instance.
    """
    acc = widgets.Accordion(children=[conteudo])
    acc.set_title(0, titulo)
    if not aberto:
        acc.selected_index = None
    return acc


def gerar_link_download(df: pd.DataFrame, nome_arquivo: str = "dados.xlsx") -> widgets.HTML:
    """Create a download link for a DataFrame as an Excel file.

    The file content is encoded in base64 and embedded in the link.

    Args:
        df: DataFrame to export.
        nome_arquivo: Base name for the file.

    Returns:
        HTML widget containing the download link.
    """
    uid = uuid4().hex[:6]
    stem = Path(nome_arquivo).stem
    final_name = f"{stem}_{uid}.xlsx"

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    b64 = base64.b64encode(output.getvalue()).decode()
    return widgets.HTML(
        f"<a download='{final_name}' href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}' target='_blank'>Clique aqui para baixar: {final_name}</a>"
    )


def orlandini_araujo_filter(df: pd.DataFrame, bin_size: int = 10) -> pd.DataFrame:
    """Apply the Orlandini--Araújo smoothing filter.

    The data are grouped by ``bin_size`` seconds using the time column that
    starts with ``"Time_s"``. Numeric columns are averaged while non-numeric
    columns keep the first value.

    Args:
        df: Input data.
        bin_size: Width of each time bin in seconds.

    Returns:
        The filtered DataFrame.
    """
    time_col = next((c for c in df.columns if c.startswith("Time_s")), None)
    if time_col is None:
        raise ValueError("Coluna de tempo (Time_s*) não encontrada para o filtro Orlandini-Araújo.")

    dfc = df.copy()
    dfc["bin"] = np.floor(dfc[time_col] / bin_size).astype(int)
    agg_dict = {
        c: "mean" if pd.api.types.is_numeric_dtype(df[c]) else "first" for c in df.columns
    }
    grouped = dfc.groupby("bin").agg(agg_dict).reset_index(drop=True)
    return grouped


def boltzmann_sigmoid(x: np.ndarray, A1: float, A2: float, x0: float, dx: float) -> np.ndarray:
    """Classic 4-parameter Boltzmann sigmoid."""
    exp_term = np.exp(np.clip((x - x0) / dx, -700, 700))
    return A2 + (A1 - A2) / (1 + exp_term)


def generalized_logistic_stable(x: np.ndarray, A1: float, A2: float, x0: float, b: float, c: float) -> np.ndarray:
    """Numerically stable generalized logistic curve."""
    z = -(x - x0) / b
    log_1_plus_exp_z = np.where(z > 30, z, np.log1p(np.exp(z)))
    denominator = np.exp(c * log_1_plus_exp_z)
    return A2 + (A1 - A2) / (denominator + 1e-12)


@dataclass
class SinteringDataRecord:
    """Container for a sintering dataset and its metadata."""

    ensaio_id: int
    Ea: float
    tipo_dado_y: str
    df: pd.DataFrame
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataHistory:
    """Simple in-memory history stack for DataFrames."""

    def __init__(self) -> None:
        self.history: List[Dict[str, Any]] = []

    def push(self, data: pd.DataFrame, module_name: str) -> None:
        """Store a copy of ``data`` with provenance information."""
        record = {
            "timestamp": datetime.datetime.now(),
            "module": module_name,
            "columns": list(data.columns),
            "data": copy.deepcopy(data),
        }
        self.history.append(record)

    def pop(self) -> Optional[Dict[str, Any]]:
        """Remove and return the most recent record."""
        return self.history.pop() if self.history else None

    def peek(self) -> Optional[Dict[str, Any]]:
        """Return the most recent record without removing it."""
        return self.history[-1] if self.history else None

    def get_all(self) -> List[Dict[str, Any]]:
        """Return a shallow copy of the entire history."""
        return list(self.history)

