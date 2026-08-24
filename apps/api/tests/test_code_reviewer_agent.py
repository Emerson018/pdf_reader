import pytest
from services.agents.coding.code_reviewer_agent import CodeReviewerAgent
from services.models.factory import ModelFactory


@pytest.mark.asyncio
async def test_code_reviewer_agent_execution():
    provider = ModelFactory.get_provider("gemini", model_name="gemini-3.6-flash", api_key="mock-key")
    agent = CodeReviewerAgent(model_provider=provider)
    response = await agent.run(user_message="Revise esta função python: def add(a,b): return a+b")
    assert response.agent_name == "CodeReviewerAgent"
    assert "Code Reviewer" in response.content
