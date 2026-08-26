import pytest
from fastapi.testclient import TestClient
from apps.api.app.main import app

client = TestClient(app)


def test_export_report_markdown():
    payload = {
        "content": "Este é o conteúdo de teste da resposta RAG.",
        "metadata": {
            "agent": "DocumentAgent",
            "search_query": "Processo de Importação de Relatórios",
            "rag_source": "postgresql_document_chunks",
            "cache_hit": False
        },
        "format": "markdown"
    }
    response = client.post("/api/v1/chat/export", json=payload)
    assert response.status_code == 200
    assert "text/markdown" in response.headers["content-type"]
    assert "attachment; filename=" in response.headers["content-disposition"]
    assert "Relatório de Consulta RAG" in response.text


def test_export_report_pdf():
    payload = {
        "content": "Este é o conteúdo de teste da resposta RAG em PDF.",
        "metadata": {
            "agent": "DocumentAgent",
            "search_query": "Certificado UniRitter",
            "rag_source": "postgresql_document_chunks",
            "cache_hit": True
        },
        "format": "pdf"
    }
    response = client.post("/api/v1/chat/export", json=payload)
    assert response.status_code == 200
    assert "application/pdf" in response.headers["content-type"]
    assert "attachment; filename=" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")
