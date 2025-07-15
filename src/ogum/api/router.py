from __future__ import annotations

# ruff: noqa: D100, E402
"""FastAPI endpoints exposing core Ogum functionality."""

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel
import pandas as pd
import numpy as np

from ogum.processing import calculate_log_theta
from ogum.fem_interface import create_unit_mesh, densify_mesh

router = APIRouter()


class MasterInput(BaseModel):
    """Payload for `/calc-master` containing master curve data."""

    time_s: list[float]
    temperature_c: list[float]
    density_pct: list[float]
    energia_ativacao_kj: float


class MasterOutput(BaseModel):
    """Response model for `/calc-master`."""

    logtheta: list[Optional[float]]
    valor: list[float]
    tempo_s: list[float]


class FEMInput(BaseModel):
    """Input parameters for the `/fem-sim` endpoint."""

    mesh_size: float
    history: list[tuple[float, float]]
    Ea: float
    A: float


@router.post("/calc-master", response_model=MasterOutput)
def calc_master(input: MasterInput) -> dict:
    """Calculate the master curve for a sintering experiment."""
    df = pd.DataFrame(
        {
            "Time_s": input.time_s,
            "Temperature_C": input.temperature_c,
            "DensidadePct": input.density_pct,
        }
    )
    df_out = calculate_log_theta(df, energia_ativacao_kj=input.energia_ativacao_kj)
    logtheta_list = [None if np.isnan(v) else v for v in df_out["logtheta"]]
    return {
        "logtheta": logtheta_list,
        "valor": df_out["valor"].tolist(),
        "tempo_s": df_out["tempo_s"].tolist(),
    }


@router.post("/fem-sim")
def fem_sim(input: FEMInput) -> dict[str, list[float]]:
    """Run a simple FEM densification simulation."""
    mesh = create_unit_mesh(input.mesh_size)
    densities = densify_mesh(mesh, input.history, Ea=input.Ea, A=input.A)
    return {"densities": densities.tolist()}


@router.get("/health")
def health() -> dict[str, str]:
    """Return application status."""
    return {"status": "ok"}
