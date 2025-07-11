from __future__ import annotations

# ruff: noqa: D100, E402
"""FastAPI endpoints exposing core Ogum functionality."""
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

from ogum.cms import calc_cms
from ogum.fem_interface import create_unit_mesh, densify_mesh

app = FastAPI(title="Ogum Sintering API")


class MasterInput(BaseModel):
    """Input data for the master curve calculation."""

    time_s: list[float]
    temperature_c: list[float]
    density_pct: list[float]
    energia_ativacao_kj: float


class FEMInput(BaseModel):
    """Input parameters for the FEM densification solver."""

    mesh_size: float
    history: list[tuple[float, float]]


@app.post("/calc-master")
def calc_master(input: MasterInput) -> dict[str, list[float]]:
    """Return master curve arrays from experimental data."""
    df = pd.DataFrame(
        {
            "Time_s": input.time_s,
            "Temperature_C": input.temperature_c,
            "DensidadePct": input.density_pct,
        }
    )
    df_out = calc_cms(df, energia_ativacao_kj=input.energia_ativacao_kj)
    return {
        "logtheta": df_out["logtheta"].tolist(),
        "valor": df_out["valor"].tolist(),
        "tempo_s": df_out["tempo_s"].tolist(),
    }


@app.post("/fem-sim")
def fem_sim(input: FEMInput) -> dict[str, list[float]]:
    """Simulate densification across a mesh using ``SOVSSolver``."""
    mesh = create_unit_mesh(input.mesh_size)
    densities = densify_mesh(mesh, input.history)
    return {"densities": densities.tolist()}


@app.get("/health")
def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}
