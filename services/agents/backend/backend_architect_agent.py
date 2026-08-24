import logging
from typing import List, Optional
from services.agents.base.base_agent import BaseAgent, AgentResponse
from services.models.base import ModelProvider, LLMMessage

logger = logging.getLogger(__name__)

BACKEND_ARCHITECT_SYSTEM_PROMPT = """You are Backend Architect, a senior backend architect who specializes in scalable system design, database architecture, API development, and cloud infrastructure.

Your Core Mission:
1. System Architecture — Monolith vs Microservices, REST/GraphQL/gRPC APIs, WebSocket streaming, event-driven architectures.
2. Data & Schema Engineering — High-performance persistence layers, sub-20ms query times, ETL pipelines, schema migrations.
3. System Reliability — Error handling, circuit breakers, graceful degradation, rate limiting, dead-letter queues.
4. Security & Performance — Defense in depth, least privilege, encryption at rest/in transit, caching strategies.

Communication Style:
- Strategic, security-first, performance-conscious, and scalability-minded.
"""


class BackendArchitectAgent(BaseAgent):
    """Specialized AI Agent for backend system architecture, API design, data schemas, and server-side scalability."""

    def __init__(self, model_provider: ModelProvider, **kwargs):
        super().__init__(
            name="BackendArchitectAgent",
            description="Especialista em arquitetura backend, design de APIs, microsserviços, escalabilidade e infraestrutura de servidores.",
            model_provider=model_provider,
            system_prompt=BACKEND_ARCHITECT_SYSTEM_PROMPT
        )

    async def run(self, user_message: str, history: Optional[List[LLMMessage]] = None) -> AgentResponse:
        messages = [LLMMessage(role="system", content=self.system_prompt)]
        if history:
            messages.extend(history)
        messages.append(LLMMessage(role="user", content=user_message))

        llm_response = await self.provider.generate(messages=messages)
        content = f"[Backend Architect 🏗️]:\n{llm_response.content}"

        return AgentResponse(
            agent_name=self.name,
            content=content,
            metadata={
                "agent": self.name,
                "model": llm_response.model,
                "type": "backend_architecture"
            }
        )
