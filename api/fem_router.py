from __future__ import annotations

import uuid
from typing import Dict

from fastapi import APIRouter, BackgroundTasks, status
from pydantic import BaseModel
import json
from pathlib import Path

from fem.solver import run_fem_simulation

router = APIRouter(prefix="/fem")


class FemSimulationRequest(BaseModel):
    mesh_params: Dict[str, float]
    material_params: Dict[str, float]
    bc_params: Dict[str, float]


@router.post("/simulation", status_code=status.HTTP_202_ACCEPTED)
def start_fem_simulation(
    request: FemSimulationRequest, background_tasks: BackgroundTasks
) -> dict[str, str]:
    job_id = str(uuid.uuid4())
    output_name = f"fem_output/{job_id}.xdmf"
    background_tasks.add_task(
        run_fem_simulation,
        request.mesh_params,
        request.material_params,
        request.bc_params,
        output_name,
        job_id,
    )
    return {
        "message": "FEM simulation started in the background.",
        "job_id": job_id,
    }


@router.get("/simulation/status/{job_id}")
def fem_simulation_status(job_id: str) -> dict[str, str]:
    status_file = Path(f"fem_output/{job_id}.json")
    if not status_file.exists():
        return {"status": "pending"}
    with status_file.open() as f:
        return json.load(f)
