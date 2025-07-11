# -*- coding: utf-8 -*-
"""Utilities shared across Ogum modules."""

from __future__ import annotations

import base64
import datetime
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import normalize_columns
from .sovs import SOVSSolver

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid as cumtrapz

try:
    from IPython.display import HTML, display
    import ipywidgets as widgets
except Exception:  # pragma: no cover - optional dependency

    class _Dummy:
        def __getattr__(self, name):
            raise RuntimeError("ipywidgets is required for GUI functions")

    widgets = _Dummy()

    def display(*args, **kwargs):  # type: ignore
        pass

    def HTML(text):  # type: ignore
        return text


R = 8.314  # Constante universal dos gases (J/mol.K)


@dataclass
class SinteringDataRecord:
    """Estrutura simples para armazenar dados de sinterização."""

    ensaio_id: int
    Ea: float
    tipo_dado_y: str
    df: pd.DataFrame
    metadata: dict = field(default_factory=dict)


class DataHistory:
    """Armazena versões de DataFrames para permitir desfazer operações."""

    def __init__(self) -> None:
        """Initialize an empty history list."""
        self.history: List[Dict[str, Any]] = []

    def push(self, data: pd.DataFrame, module_name: str) -> None:
        """Store a snapshot of ``data`` with metadata.

        Args:
            data (pd.DataFrame): DataFrame to be stored.
            module_name (str): Name of the module originating the data.
        """
        record = {
            "timestamp": datetime.datetime.now(),
            "module": module_name,
            "columns": list(data.columns),
            "data": data.copy(deep=True),
        }
        self.history.append(record)

    def pop(self) -> Optional[Dict[str, Any]]:
        """Remove and return the most recent entry.

        Returns:
            Optional[Dict[str, Any]]: The latest snapshot or ``None`` if
            history is empty.
        """
        return self.history.pop() if self.history else None

    def peek(self) -> Optional[Dict[str, Any]]:
        """Return the most recent entry without removing it.

        Returns:
            Optional[Dict[str, Any]]: The latest snapshot or ``None`` if
            history is empty.
        """
        return self.history[-1] if self.history else None

    def get_all(self) -> List[Dict[str, Any]]:
        """Return a copy of the entire history.

        Returns:
            List[Dict[str, Any]]: All stored snapshots.
        """
        return list(self.history)


# ---------------------------------------------------------------------------
# Interface helper functions
# ---------------------------------------------------------------------------


def add_suffix_once(col: str, suffix: str) -> str:
    """Return ``col`` with ``suffix`` appended only once."""
    return col if col.endswith(suffix) else f"{col}{suffix}"


def criar_titulo(texto: str, nivel: int = 2) -> widgets.HTML:
    """Return an HTML widget used as a section title."""
    return widgets.HTML(f"<h{nivel}>{texto}</h{nivel}>")


def exibir_mensagem(msg: str) -> None:
    """Display a blue informational message in the notebook output.

    Args:
        msg (str): Message to be shown.
    """
    display(HTML(f"<p style='color:blue; font-style:italic;'>{msg}</p>"))


def exibir_erro(msg: str) -> None:
    """Display an error message in bold red text.

    Args:
        msg (str): Message describing the error.
    """
    display(HTML(f"<p style='color:red; font-weight:bold;'>ERRO: {msg}</p>"))



def gerar_link_download(df: pd.DataFrame, nome_arquivo: str = "dados.xlsx") -> HTML:
    """Gera link HTML para baixar ``df`` como arquivo Excel."""
    uid = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    stem = Path(nome_arquivo).stem
    final_name = f"{stem}_{uid}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    b64 = base64.b64encode(output.getvalue()).decode()
    return HTML(
        f'<a download="{final_name}" '
        f'href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" '
        f'target="_blank">Clique aqui para baixar: {final_name}</a>'
    )


# ---------------------------------------------------------------------------
# Mathematical models
# ---------------------------------------------------------------------------


def boltzmann_sigmoid(x, A1, A2, x0, dx):
    """Compute a Boltzmann sigmoidal curve.

    Args:
        x: Independent variable.
        A1: Lower asymptote.
        A2: Upper asymptote.
        x0: Center of the transition.
        dx: Slope factor.

    Returns:
        np.ndarray: Evaluated sigmoid values.
    """
    exp_term = np.exp(np.clip((x - x0) / dx, -700, 700))
    return A2 + (A1 - A2) / (1 + exp_term)


def generalized_logistic_stable(x, A1, A2, x0, b, c):
    """Stable generalized logistic function used to fit sigmoidal data.

    Args:
        x: Independent variable.
        A1: Lower asymptote.
        A2: Upper asymptote.
        x0: Location parameter.
        b: Scale parameter.
        c: Asymmetry parameter.

    Returns:
        np.ndarray: Evaluated logistic values.
    """
    z = -(x - x0) / b
    log_1_plus_exp_z = np.where(z > 30, z, np.log1p(np.exp(z)))
    denominator = np.exp(c * log_1_plus_exp_z)
    return A2 + (A1 - A2) / (denominator + 1e-12)


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
    "cumtrapz",
]
