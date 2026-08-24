import pytest
from fastapi.testclient import TestClient
from apps.api.app.main import app

client = TestClient(app)


def test_chat_endpoint_success():
    payload = {"message": "Olá, tudo bem?"}
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0
    assert "conversation_id" in data


def test_chat_endpoint_empty_message():
    payload = {"message": "   "}
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 400
