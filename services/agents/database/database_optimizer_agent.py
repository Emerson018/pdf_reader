import logging
from typing import List, Optional
from services.agents.base.base_agent import BaseAgent, AgentResponse
from services.models.base import ModelProvider, LLMMessage

logger = logging.getLogger(__name__)

DATABASE_OPTIMIZER_SYSTEM_PROMPT = """You are Database Optimizer, an expert database specialist focusing on schema design, query optimization, indexing strategies (B-tree, GiST, GIN, partial indexes), EXPLAIN ANALYZE interpretation, and performance tuning for PostgreSQL, MySQL, and modern databases like Supabase.

Your Core Mission:
1. Optimized Schema Design — Indexed foreign keys, constraints, normalization vs denormalization.
2. Query Plan Analysis — EXPLAIN ANALYZE, eliminating N+1 queries, sub-20ms query optimization.
3. Connection Pooling & Migrations — PgBouncer, zero-downtime migration strategies, pgvector optimization.

Communication Style:
- Technical, performance-driven, precise, and obsessed with query plans and index coverage.
"""


class DatabaseOptimizerAgent(BaseAgent):
    """Specialized AI Agent for database performance tuning, indexing strategies, query plan analysis, and PostgreSQL optimization."""

    def __init__(self, model_provider: ModelProvider, **kwargs):
        super().__init__(
            name="DatabaseOptimizerAgent",
            description="Especialista em otimização de banco de dados, índices PostgreSQL, planos de execução EXPLAIN ANALYZE e tuning de SQL.",
            model_provider=model_provider,
            system_prompt=DATABASE_OPTIMIZER_SYSTEM_PROMPT
        )

    async def run(self, user_message: str, history: Optional[List[LLMMessage]] = None) -> AgentResponse:
        messages = [LLMMessage(role="system", content=self.system_prompt)]
        if history:
            messages.extend(history)
        messages.append(LLMMessage(role="user", content=user_message))

        llm_response = await self.provider.generate(messages=messages)
        content = f"[Database Optimizer 🗄️]:\n{llm_response.content}"

        return AgentResponse(
            agent_name=self.name,
            content=content,
            metadata={
                "agent": self.name,
                "model": llm_response.model,
                "type": "database_optimization"
            }
        )
