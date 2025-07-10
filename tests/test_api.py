from fastapi.testclient import TestClient
import numpy as np

from api.main import app

client = TestClient(app)


def test_filter_endpoint_success():
    payload = {"data_points": [1.0, 2.0, 3.0, 4.0, 5.0], "window_length": 3, "polyorder": 1}
    response = client.post("/processing/filter", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["original_data"] == payload["data_points"]
    assert isinstance(data["filtered_data"], list)
    assert len(data["filtered_data"]) == len(payload["data_points"])


def test_filter_endpoint_invalid_window():
    payload = {"data_points": [1, 2, 3, 4], "window_length": 4, "polyorder": 1}
    response = client.post("/processing/filter", json=payload)
    assert response.status_code == 400


def test_activation_energy_endpoint_success():
    temperatures = [300.0, 400.0, 500.0, 600.0]
    Q_true = 50_000.0
    rates = np.exp(-Q_true / (8.314 * np.array(temperatures)))
    payload = {"temperatures": temperatures, "rates": rates.tolist()}

    response = client.post("/processing/activation-energy", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert abs(data["Q"] - 50.0) < 0.5
    assert data["r_squared"] > 0.99


def test_activation_energy_endpoint_mismatch():
    payload = {"temperatures": [300.0, 400.0], "rates": [1.0]}
    response = client.post("/processing/activation-energy", json=payload)
    assert response.status_code == 400
