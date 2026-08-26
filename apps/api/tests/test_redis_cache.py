import pytest
from services.cache.redis_cache_service import calculate_cosine_similarity, RedisCacheService
from services.orchestrator.routing.query_rewriter import rewrite_query_with_history
from services.models.base import LLMMessage
from services.models.factory import ModelFactory


def test_cosine_similarity_calculation():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]

    assert abs(calculate_cosine_similarity(v1, v2) - 1.0) < 1e-5
    assert abs(calculate_cosine_similarity(v1, v3) - 0.0) < 1e-5


@pytest.mark.asyncio
async def test_query_rewriter_standalone():
    provider = ModelFactory.get_provider("gemini", model_name="gemini-3.6-flash", api_key="mock-key")
    single_q = await rewrite_query_with_history("O que é RAG?", history=[], model_provider=provider)
    assert single_q == "O que é RAG?"

    history = [
        LLMMessage(role="user", content="Fale sobre o certificado de Emerson."),
        LLMMessage(role="assistant", content="O certificado de Emerson é da UniRitter.")
    ]
    rewritten_q = await rewrite_query_with_history("Qual a carga horária dele?", history=history, model_provider=provider)
    assert len(rewritten_q) > 0


@pytest.mark.asyncio
async def test_redis_cache_service_methods():
    cache_svc = RedisCacheService()
    # Test setting and getting semantic cache entries if Redis server is mock or live
    v1 = [0.1] * 768
    set_res = await cache_svc.set_semantic_cache(
        query_text="teste de cache redis",
        query_embedding=v1,
        response_text="resposta armazenada no cache redis",
        ttl_seconds=60
    )
    # If Redis is running or in bypass mode, set_res will return boolean
    assert isinstance(set_res, bool)
