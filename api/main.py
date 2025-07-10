from __future__ import annotations

from typing import List

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.solver import apply_savitzky_golay_filter

app = FastAPI()


class FilterRequest(BaseModel):
    """Request body for the Savitzky-Golay filter."""

    data_points: List[float]
    window_length: int
    polyorder: int


class FilterResponse(BaseModel):
    """Response containing original and filtered data."""

    original_data: List[float]
    filtered_data: List[float]


@app.post("/processing/filter", response_model=FilterResponse)
def process_filter(request: FilterRequest) -> FilterResponse:
    """Apply Savitzky-Golay filter to ``request.data_points``."""
    if request.window_length <= 0 or request.window_length % 2 == 0:
        raise HTTPException(status_code=400, detail="window_length must be a positive odd integer")

    data_array = np.array(request.data_points, dtype=float)
    filtered = apply_savitzky_golay_filter(
        data_array, window_length=request.window_length, polyorder=request.polyorder
    )
    return FilterResponse(original_data=request.data_points, filtered_data=filtered.tolist())
