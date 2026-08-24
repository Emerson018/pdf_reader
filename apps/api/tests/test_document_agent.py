import pytest
from services.agents.document.document_agent import DocumentAgent
from services.models.factory import ModelFactory


@pytest.mark.asyncio
async def test_document_agent_execution():
    provider = ModelFactory.get_provider("gemini", model_name="gemini-3.6-flash", api_key="mock-key")
    agent = DocumentAgent(model_provider=provider)
    response = await agent.run(user_message="Quais as regras do manual do colaborador?")
    assert response.agent_name == "DocumentAgent"
    assert "Document Agent" in response.content
