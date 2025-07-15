from __future__ import annotations

# ruff: noqa: D100, E402
"""FastAPI endpoints exposing core Ogum functionality."""
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np

from ogum.cms import calc_cms
from ogum.fem_interface import create_unit_mesh, densify_mesh
from ogum.processing import calculate_log_theta

app = FastAPI(title="Ogum Sintering API")


class MasterInput(BaseModel):
    """Input data for the master curve calculation."""
    time_s: list[float]
    temperature_c: list[float]
    density_pct: list[float]
    energia_ativacao_kj: float

# --- CORREÇÃO: Modelo de Saída para /calc-master ---
class MasterOutput(BaseModel):
    """Output data for the master curve calculation."""
    logtheta: list[Optional[float]] # Permite valores nulos (None)
    valor: list[float]
    tempo_s: list[float]

# --- CORREÇÃO: Modelo de Entrada para /fem-sim ---
class FEMInput(BaseModel):
    """Input parameters for the FEM densification solver."""
    mesh_size: float
    history: list[tuple[float, float]]
    Ea: float
    A: float


@app.post("/calc-master", response_model=MasterOutput)
def calc_master(input: MasterInput) -> dict:
    """Return master curve arrays from experimental data."""
    df = pd.DataFrame({
        "Time_s": input.time_s,
        "Temperature_C": input.temperature_c,
        "DensidadePct": input.density_pct,
    })
    df_out = calculate_log_theta(df, energia_ativacao_kj=input.energia_ativacao_kj)
    
    # Substitui NaN por None para compatibilidade com JSON
    logtheta_list = [None if np.isnan(v) else v for v in df_out["logtheta"]]

    return {
        "logtheta": logtheta_list,
        "valor": df_out["valor"].tolist(),
        "tempo_s": df_out["tempo_s"].tolist(),
    }


@app.post("/fem-sim")
def fem_sim(input: FEMInput) -> dict[str, list[float]]:
    """Simulate densification across a mesh using ``SOVSSolver``."""
    mesh = create_unit_mesh(input.mesh_size)
    densities = densify_mesh(mesh, input.history, Ea=input.Ea, A=input.A)
    return {"densities": densities.tolist()}


@app.get("/health")
def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}
