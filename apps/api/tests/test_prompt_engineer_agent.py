import pytest
from services.agents.prompt.prompt_engineer_agent import PromptEngineerAgent
from services.models.factory import ModelFactory


@pytest.mark.asyncio
async def test_prompt_engineer_agent_execution():
    provider = ModelFactory.get_provider("gemini", model_name="gemini-3.6-flash", api_key="mock-key")
    agent = PromptEngineerAgent(model_provider=provider)
    response = await agent.run(user_message="Crie um system prompt estruturado para um agente de atendimento.")
    assert response.agent_name == "PromptEngineerAgent"
    assert "Prompt Engineer" in response.content
