import logging
from services.models.base import ModelProvider

logger = logging.getLogger(__name__)


class SupervisorRouter:
    """Routes user queries directly to DocumentAgent for strict RAG database search, 
    or to multi_agent_orchestration when explicitly requested.
    """

    def __init__(self, model_provider: ModelProvider):
        self.provider = model_provider

    async def route(self, user_message: str) -> str:
        text = user_message.lower()

        # Explicit Multi-Agent Orchestration Broadcast Trigger
        multi_agent_keywords = [
            "cada agente", "todos os agentes", "todos agentes", "orquestração",
            "orquestrar", "multi-agente", "multi-agent", "vários agentes",
            "análise completa com todos", "enviar a tarefa para cada agente",
            "todas as ias", "todas ias", "equipe de ias", "painel de ias", "todos os especialistas"
        ]
        if any(w in text for w in multi_agent_keywords):
            return "multi_agent_orchestration"

        # By default, ALL user queries MUST execute RAG document search on PostgreSQL database
        return "document_agent"
