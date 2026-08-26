import pytest
import io
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from apps.api.app.main import app

client = TestClient(app)


def test_list_documents_endpoint():
    with patch("apps.api.app.api.v1.documents.AsyncSessionLocal") as mock_session_cls:
        mock_session = MagicMock()
        mock_session_cls.return_value.__aenter__.return_value = mock_session
        
        # Mock async execute
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        
        async def mock_execute(*args, **kwargs):
            return mock_result

        mock_session.execute = mock_execute

        response = client.get("/api/v1/documents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


def test_upload_non_pdf_file_returns_400():
    file_content = b"Not a PDF file"
    file = io.BytesIO(file_content)
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.txt", file, "text/plain")}
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_get_upload_status_not_found():
    response = client.get("/api/v1/documents/upload/status/invalid-task-id-12345")
    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"]
