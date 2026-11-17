
from fastapi.testclient import TestClient

from app.web_app import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_summary():
    response = client.get("/api/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_records"] == 5765
    assert data["district_count"] == 38


def test_districts():
    response = client.get("/api/districts")

    assert response.status_code == 200

    districts = response.json()["districts"]

    assert len(districts) == 38


def test_records():
    response = client.get("/api/records?limit=10")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] <= 10
    assert len(data["records"]) == data["count"]


def test_district_summary():
    response = client.get("/api/district-summary")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 38
