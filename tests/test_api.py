from fastapi.testclient import TestClient

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
