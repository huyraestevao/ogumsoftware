import numpy as np
import pytest
from httpx import AsyncClient, ASGITransport

from ogum.api import app
from ogum.material_calibrator import MaterialCalibrator


def _records() -> list[dict[str, float]]:
    t = np.linspace(0, 2, 5)
    df = MaterialCalibrator.simulate_synthetic(60.0, 2.0, t)
    df = df.rename(columns={"Time_s": "time", "Temperature_C": "temperature", "DensidadePct": "density"})
    return df.to_dict(orient="records")


@pytest.mark.asyncio
async def test_refine_valid():
    transport = ASGITransport(app=app)
    data = _records()
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/refine", json={"records": data})
    assert resp.status_code == 200
    out = resp.json()
    assert len(out["records"]) == len(data)


@pytest.mark.asyncio
async def test_refine_invalid():
    transport = ASGITransport(app=app)
    data = [{"time": 0.0, "temperature": 1000.0}]  # missing density
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/refine", json={"records": data})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_master_curve_valid():
    transport = ASGITransport(app=app)
    data = _records()
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/master-curve", json={"records": data})
    assert resp.status_code == 200
    out = resp.json()
    assert set(out) == {"master_time", "master_density", "activation_energy"}
    assert len(out["master_time"]) == len(data)


@pytest.mark.asyncio
async def test_master_curve_invalid():
    transport = ASGITransport(app=app)
    data = [{"time": 0.0, "density": 10.0, "temperature": 1000.0}, {"time": 1.0, "density": 15.0}]  # second record missing temperature
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/master-curve", json={"records": data})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_calibrate_valid():
    transport = ASGITransport(app=app)
    data = _records()
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/calibrate", json={"records": data})
    assert resp.status_code == 200
    out = resp.json()
    assert {"Ea", "A"} == set(out)
    assert out["Ea"] == pytest.approx(60.0, rel=0.3)
    assert out["A"] == pytest.approx(2.0, rel=0.3)


@pytest.mark.asyncio
async def test_calibrate_invalid():
    transport = ASGITransport(app=app)
    data = [{"time": 0.0, "temperature": 1000.0, "density": 10.0}, {"temperature": 1000.0, "density": 20.0}]  # missing time
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/calibrate", json={"records": data})
    assert resp.status_code == 422
