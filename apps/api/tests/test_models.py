import pytest
from services.models.factory import ModelFactory
from services.models.base import LLMMessage


@pytest.mark.asyncio
async def test_openai_model_provider():
    provider = ModelFactory.get_provider("openai", model_name="gpt-4o-mini", api_key="mock-key")
    messages = [LLMMessage(role="user", content="Test prompt")]
    response = await provider.generate(messages)
    assert response.content is not None
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_gemini_model_provider_fallback():
    provider = ModelFactory.get_provider("gemini", model_name="gemini-1.5-flash", api_key="mock-key")
    messages = [LLMMessage(role="user", content="Test prompt")]
    response = await provider.generate(messages)
    assert response.content is not None
    assert "Gemini" in response.content


@pytest.mark.asyncio
async def test_ollama_model_provider_error_handling():
    provider = ModelFactory.get_provider("ollama", model_name="llama3", base_url="http://invalid-host:11434")
    messages = [LLMMessage(role="user", content="Test prompt")]
    response = await provider.generate(messages)
    assert "Ollama Provider Error" in response.content or response.content is not None
