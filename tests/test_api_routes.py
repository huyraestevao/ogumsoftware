from fastapi.testclient import TestClient
from ogum.api import app

client = TestClient(app)


def test_health_route():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
