"""Core utilities for Ogum notebooks."""
from dataclasses import dataclass, field
import pandas as pd

@dataclass
class SinteringDataRecord:
    """Simple structure used across notebooks."""
    ensaio_id: int
    Ea: float
    tipo_dado_y: str
    df: pd.DataFrame
    metadata: dict = field(default_factory=dict)
