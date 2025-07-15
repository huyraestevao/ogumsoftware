import pytest
from httpx import AsyncClient

# A importação do 'app' continua necessária, pois o httpx a utiliza nos bastidores
from ogum.api import app


@pytest.mark.asyncio
async def test_health_endpoint():
    # ALTERADO AQUI: removido o argumento 'app=app'
    async with AsyncClient(base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_calc_master_endpoint():
    payload = {
        "time_s": [0, 1, 2],
        "temperature_c": [100.0, 110.0, 120.0],
        "density_pct": [10.0, 20.0, 30.0],
        "energia_ativacao_kj": 50.0,
    }
    # ALTERADO AQUI: removido o argumento 'app=app'
    async with AsyncClient(base_url="http://test") as client:
        resp = await client.post("/calc-master", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert {"logtheta", "valor", "tempo_s"} <= data.keys()
    assert len(data["logtheta"]) == len(payload["time_s"])


@pytest.mark.asyncio
async def test_fem_sim_endpoint():
    payload = {
        "mesh_size": 0.5,
        "history": [(0.0, 1000.0), (1.0, 1000.0)],
    }
    # ALTERADO AQUI: removido o argumento 'app=app'
    async with AsyncClient(base_url="http://test") as client:
        resp = await client.post("/fem-sim", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "densities" in data
    assert isinstance(data["densities"], list)
