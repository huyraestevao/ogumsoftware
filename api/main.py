"""Main FastAPI application exposing processing and FEM endpoints."""

from __future__ import annotations

from typing import List

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from api.fem_router import router as fem_router

from core.solver import apply_savitzky_golay_filter, calculate_activation_energy

app = FastAPI()
app.include_router(fem_router)


class FilterRequest(BaseModel):
    """Request body for the Savitzky-Golay filter."""

    data_points: List[float]
    window_length: int
    polyorder: int


class FilterResponse(BaseModel):
    """Response containing original and filtered data."""

    original_data: List[float]
    filtered_data: List[float]


class ActivationEnergyRequest(BaseModel):
    """Input data for activation energy calculation."""

    temperatures: List[float]
    rates: List[float]


class ActivationEnergyResponse(BaseModel):
    """Results from the activation energy computation."""

    Q: float
    r_squared: float
    slope: float
    intercept: float


@app.post("/processing/filter", response_model=FilterResponse)
def process_filter(request: FilterRequest) -> FilterResponse:
    """Apply Savitzky-Golay filter to ``request.data_points``."""
    if request.window_length <= 0 or request.window_length % 2 == 0:
        raise HTTPException(
            status_code=400, detail="window_length must be a positive odd integer"
        )

    data_array = np.array(request.data_points, dtype=float)
    filtered = apply_savitzky_golay_filter(
        data_array, window_length=request.window_length, polyorder=request.polyorder
    )
    return FilterResponse(
        original_data=request.data_points, filtered_data=filtered.tolist()
    )


@app.post("/processing/activation-energy", response_model=ActivationEnergyResponse)
def compute_activation_energy(
    request: ActivationEnergyRequest,
) -> ActivationEnergyResponse:
    """Calculate activation energy ``Q`` from experimental data."""
    if len(request.temperatures) != len(request.rates):
        raise HTTPException(
            status_code=400, detail="temperatures and rates must have the same length"
        )

    temps = np.array(request.temperatures, dtype=float)
    rates = np.array(request.rates, dtype=float)
    result = calculate_activation_energy(temps, rates)
    return ActivationEnergyResponse(**result)
