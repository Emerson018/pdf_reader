import pytest
from services.agents.backend.backend_architect_agent import BackendArchitectAgent
from services.agents.database.database_optimizer_agent import DatabaseOptimizerAgent
from services.agents.frontend.frontend_developer_agent import FrontendDeveloperAgent
from services.models.factory import ModelFactory


@pytest.mark.asyncio
async def test_backend_architect_agent_execution():
    provider = ModelFactory.get_provider("gemini", model_name="gemini-3.6-flash", api_key="mock-key")
    agent = BackendArchitectAgent(model_provider=provider)
    response = await agent.run(user_message="Como projetar uma arquitetura de microsserviços escalável?")
    assert response.agent_name == "BackendArchitectAgent"
    assert "Backend Architect" in response.content


@pytest.mark.asyncio
async def test_database_optimizer_agent_execution():
    provider = ModelFactory.get_provider("gemini", model_name="gemini-3.6-flash", api_key="mock-key")
    agent = DatabaseOptimizerAgent(model_provider=provider)
    response = await agent.run(user_message="Como usar EXPLAIN ANALYZE para otimizar queries lentas?")
    assert response.agent_name == "DatabaseOptimizerAgent"
    assert "Database Optimizer" in response.content


@pytest.mark.asyncio
async def test_frontend_developer_agent_execution():
    provider = ModelFactory.get_provider("gemini", model_name="gemini-3.6-flash", api_key="mock-key")
    agent = FrontendDeveloperAgent(model_provider=provider)
    response = await agent.run(user_message="Como otimizar Core Web Vitals em um aplicativo Next.js 14?")
    assert response.agent_name == "FrontendDeveloperAgent"
    assert "Frontend Developer" in response.content
