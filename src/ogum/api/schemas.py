"""Pydantic models for Ogum API."""

from __future__ import annotations

from pydantic import BaseModel


class SinteringRecord(BaseModel):
    """Single point in a sintering experiment."""

    time: float
    temperature: float
    density: float


class RefineRequest(BaseModel):
    """Payload for the ``/refine`` endpoint.

    Parameters
    ----------
    records : list[SinteringRecord]
        Sintering data records to be filtered.
    """

    records: list[SinteringRecord]


class RefineResponse(BaseModel):
    """Response from the ``/refine`` endpoint.

    Parameters
    ----------
    records : list[SinteringRecord]
        Filtered sintering data.
    """

    records: list[SinteringRecord]


class MasterCurveRequest(BaseModel):
    """Input for ``/master-curve``.

    Parameters
    ----------
    records : list[SinteringRecord]
        Sintering data records.
    """

    records: list[SinteringRecord]


class MasterCurveResponse(BaseModel):
    """Master curve result.

    Parameters
    ----------
    master_time : list[float]
        Time values shifted to the reference temperature.
    master_density : list[float]
        Densities associated with ``master_time``.
    activation_energy : float
        Activation energy in kJ/mol used for the shift.
    """

    master_time: list[float]
    master_density: list[float]
    activation_energy: float


class CalibrateRequest(BaseModel):
    """Input for ``/calibrate``.

    Parameters
    ----------
    records : list[SinteringRecord]
        Sintering experiment records.
    """

    records: list[SinteringRecord]


class CalibrateResponse(BaseModel):
    """Calibration parameters.

    Parameters
    ----------
    Ea : float
        Activation energy in kJ/mol.
    A : float
        Pre-exponential factor in s⁻¹.
    """

    Ea: float
    A: float


__all__ = [
    "SinteringRecord",
    "RefineRequest",
    "RefineResponse",
    "MasterCurveRequest",
    "MasterCurveResponse",
    "CalibrateRequest",
    "CalibrateResponse",
]
