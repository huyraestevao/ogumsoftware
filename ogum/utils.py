from __future__ import annotations
import copy
import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import pandas as pd

# Constante universal dos gases (J/mol.K)
R = 8.314

@dataclass
class SinteringDataRecord:
    """Estrutura de dados para registrar resultados de sinterização."""
    ensaio_id: int
    Ea: float
    tipo_dado_y: str
    df: pd.DataFrame
    metadata: dict = field(default_factory=dict)


class DataHistory:
    """Armazena snapshots de DataFrames ao longo do processamento."""

    def __init__(self) -> None:
        self.history: List[Dict[str, Any]] = []

    def push(self, data: pd.DataFrame, module_name: str) -> None:
        record = {
            "timestamp": datetime.datetime.now(),
            "module": module_name,
            "columns": list(data.columns),
            "data": copy.deepcopy(data),
        }
        self.history.append(record)

    def pop(self) -> Optional[Dict[str, Any]]:
        return self.history.pop() if self.history else None

    def peek(self) -> Optional[Dict[str, Any]]:
        return self.history[-1] if self.history else None

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self.history)

