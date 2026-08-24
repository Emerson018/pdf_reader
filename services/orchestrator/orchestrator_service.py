import logging
from typing import Dict, Any, Optional
from apps.api.app.core.config import Settings
from services.models.factory import ModelFactory
from services.orchestrator.graphs.agent_graph import OrchestrationGraph

logger = logging.getLogger(__name__)


class OrchestratorService:
    """High-level Orchestrator Service decoupled from HTTP layer."""

    def __init__(self, provider_name: Optional[str] = None, model_name: Optional[str] = None, api_key: Optional[str] = None):
        current_settings = Settings()
        p_name = provider_name or current_settings.DEFAULT_PROVIDER
        m_name = model_name or current_settings.DEFAULT_MODEL

        # Determine API key based on provider
        if not api_key:
            if p_name.lower() in ["gemini", "google"]:
                api_key = current_settings.GEMINI_API_KEY
            else:
                api_key = current_settings.OPENAI_API_KEY

        self.provider = ModelFactory.get_provider(
            provider_name=p_name,
            model_name=m_name,
            api_key=api_key
        )
        self.graph = OrchestrationGraph(self.provider)

    async def run_chat(self, user_message: str) -> Dict[str, Any]:
        """Runs user message through the orchestrator graph."""
        logger.info(f"Orchestrator processing chat input: '{user_message[:40]}...'")
        return await self.graph.execute(user_message)
