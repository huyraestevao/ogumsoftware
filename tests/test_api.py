import pytest
from httpx import AsyncClient, ASGITransport  # Importe o ASGITransport

from ogum.api import app

@pytest.mark.asyncio
async def test_fem_sim_endpoint():
    payload = {
        "mesh_size": 0.5,
        "history": [(0.0, 1000.0), (1.0, 1000.0)],
        "Ea": 60.0,  # PARÂMETRO ADICIONADO
        "A": 2.0,    # PARÂMETRO ADICIONADO
    }
    # Usamos o transport para conectar o cliente ao app em memória
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/fem-sim", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "densities" in data
    assert isinstance(data["densities"], list)


@pytest.mark.asyncio
async def test_calc_master_endpoint():
    payload = {
        "time_s": [0, 1, 2],
        "temperature_c": [100.0, 110.0, 120.0],
        "density_pct": [10.0, 20.0, 30.0],
        "energia_ativacao_kj": 50.0,
    }
    # CORREÇÃO: Usamos o transport para conectar o cliente ao app em memória
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
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
    # CORREÇÃO: Usamos o transport para conectar o cliente ao app em memória
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/fem-sim", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "densities" in data
    assert isinstance(data["densities"], list)
