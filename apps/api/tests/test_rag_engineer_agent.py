import pytest
from services.agents.rag.rag_engineer_agent import RAGPipelineEngineerAgent
from services.models.factory import ModelFactory


@pytest.mark.asyncio
async def test_rag_engineer_agent_execution():
    provider = ModelFactory.get_provider("gemini", model_name="gemini-3.6-flash", api_key="mock-key")
    agent = RAGPipelineEngineerAgent(model_provider=provider)
    response = await agent.run(user_message="Como configurar um índice HNSW no pgvector para melhorar o recall de busca vetorial?")
    assert response.agent_name == "RAGPipelineEngineerAgent"
    assert "RAG Pipeline Engineer" in response.content
