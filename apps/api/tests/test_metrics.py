import pytest
from fastapi.testclient import TestClient
from apps.api.app.main import app

client = TestClient(app)


def test_rag_metrics_endpoint():
    response = client.get("/api/v1/metrics/rag")
    assert response.status_code == 200
    data = response.json()
    assert "redis_cache" in data
    assert "postgresql_vector_db" in data
    assert "infrastructure_health" in data
    assert data["postgresql_vector_db"]["vector_dimension"] == 768
