import logging
from typing import List, Optional
from services.agents.base.base_agent import BaseAgent, AgentResponse
from services.models.base import ModelProvider, LLMMessage

logger = logging.getLogger(__name__)

RAG_ENGINEER_SYSTEM_PROMPT = """You are a RAG Pipeline Engineer, a retrieval-augmented generation specialist who designs and ships production-grade RAG systems. You focus on retrieval quality, chunking strategy, embedding models, pgvector HNSW index tuning, hybrid search (BM25 + dense vectors), Reranking, and RAGAS evaluations.

Your Core Mission:
1. Retrieval Architecture — Chunking (structural vs semantic), embedding validation, HNSW index optimization (m, ef_construction), hybrid search fusion (RRF).
2. Pipeline Engineering — Async non-blocking ingestion, metadata pre-filtering, context compression, deduplication.
3. Evaluation & Metrics — Faithfulness, context precision, context recall, answer relevancy.
4. Agentic RAG — LangGraph multi-step retrieval, query decomposition, and query reformulation.

Communication Style:
- Professional, technical, data-driven, and focused on production-grade RAG standards.
- Provide code diffs, SQL schemas for pgvector, and python RAG pipeline logic when requested.
"""


class RAGPipelineEngineerAgent(BaseAgent):
    """Specialized AI Agent for RAG architecture, vector search, chunking strategies, and retrieval evaluation."""

    def __init__(self, model_provider: ModelProvider, **kwargs):
        super().__init__(
            name="RAGPipelineEngineerAgent",
            description="Especialista em arquitetura RAG, estratégias de chunking, busca híbrida, pgvector, HNSW e métricas RAGAS.",
            model_provider=model_provider,
            system_prompt=RAG_ENGINEER_SYSTEM_PROMPT
        )

    async def run(self, user_message: str, history: Optional[List[LLMMessage]] = None) -> AgentResponse:
        messages = [LLMMessage(role="system", content=self.system_prompt)]
        if history:
            messages.extend(history)
        messages.append(LLMMessage(role="user", content=user_message))

        llm_response = await self.provider.generate(messages=messages)
        content = f"[RAG Pipeline Engineer 🔍]:\n{llm_response.content}"

        return AgentResponse(
            agent_name=self.name,
            content=content,
            metadata={
                "agent": self.name,
                "model": llm_response.model,
                "type": "rag_engineering"
            }
        )
