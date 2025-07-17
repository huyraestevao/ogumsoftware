"""Additional FastAPI routes exposing scientific utilities."""

from __future__ import annotations

from fastapi import APIRouter
import pandas as pd

from ogum.data_refinement import DataRefinement
from ogum.master_curve import build_master_curve
from ogum.material_calibrator import MaterialCalibrator

from .schemas import (
    RefineRequest,
    RefineResponse,
    MasterCurveRequest,
    MasterCurveResponse,
    CalibrateRequest,
    CalibrateResponse,
    SinteringRecord,
)

router = APIRouter()


@router.post("/refine", response_model=RefineResponse, tags=["Science"])
def refine(data: RefineRequest) -> RefineResponse:
    """Filter sintering data using :class:`DataRefinement`.

    Parameters
    ----------
    data : RefineRequest
        Records to be processed.

    Returns
    -------
    RefineResponse
        Filtered records.
    """
    df = pd.DataFrame([r.dict() for r in data.records])
    refined = DataRefinement(df).df_refined
    records = [
        SinteringRecord(**row)
        for row in refined.to_dict(orient="records")
    ]
    return RefineResponse(records=records)


@router.post(
    "/master-curve",
    response_model=MasterCurveResponse,
    tags=["Science"],
)
def master_curve(data: MasterCurveRequest) -> MasterCurveResponse:
    """Build the Arrhenius master curve from sintering records.

    Parameters
    ----------
    data : MasterCurveRequest
        Input sintering data.

    Returns
    -------
    MasterCurveResponse
        Master curve arrays and activation energy.
    """
    df = pd.DataFrame([r.dict() for r in data.records])
    curve = build_master_curve(df)
    return MasterCurveResponse(
        master_time=curve["master_time"].tolist(),
        master_density=curve["master_density"].tolist(),
        activation_energy=float(curve["activation_energy"].iloc[0]),
    )


@router.post("/calibrate", response_model=CalibrateResponse, tags=["Science"])
def calibrate(data: CalibrateRequest) -> CalibrateResponse:
    """Calibrate material parameters from sintering records.

    Parameters
    ----------
    data : CalibrateRequest
        Experimental data records.

    Returns
    -------
    CalibrateResponse
        Fitted activation energy and pre-exponential factor.
    """
    df = pd.DataFrame([r.dict() for r in data.records])
    df_exp = df.rename(
        columns={
            "time": "Time_s",
            "temperature": "Temperature_C",
            "density": "DensidadePct",
        }
    )
    ea, a_param = MaterialCalibrator.fit(df_exp)
    return CalibrateResponse(Ea=ea, A=a_param)


__all__ = ["router"]
