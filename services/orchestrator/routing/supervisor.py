import logging
from services.models.base import ModelProvider, LLMMessage

logger = logging.getLogger(__name__)


class SupervisorRouter:
    """Classifies user intent and routes execution to specialized agents."""

    def __init__(self, model_provider: ModelProvider):
        self.provider = model_provider

    async def route(self, user_message: str) -> str:
        text = user_message.lower()
        if any(w in text for w in ["frontend", "react", "next.js", "tailwind", "css", "componente", "interface", "ui", "ux"]):
            return "frontend_developer_agent"
        elif any(w in text for w in ["backend", "arquitetura", "api", "rest", "graphql", "microsserviços", "servidor"]):
            return "backend_architect_agent"
        elif any(w in text for w in ["índice", "index", "explain analyze", "tuning sql", "otimização de banco", "pgbouncer"]):
            return "database_optimizer_agent"
        elif any(w in text for w in ["prompt", "system prompt", "few-shot", "chain-of-thought", "prompt engineering"]):
            return "prompt_engineer_agent"
        elif any(w in text for w in ["rag", "embedding", "chunking", "hnsw", "busca híbrida", "rerank", "ragas", "vetor"]):
            return "rag_engineer_agent"
        elif any(w in text for w in ["código", "code", "revisar", "review", "refatorar", "refactor", "bug", "vulnerabilidade"]):
            return "code_reviewer_agent"
        elif any(w in text for w in ["manual", "colaborador", "política", "diretriz", "férias", "benefício", "regulamento", "documento"]):
            return "document_agent"
        elif any(w in text for w in ["dados", "banco", "sql", "tabela", "relatório", "métrica"]):
            return "data_agent"
        elif any(w in text for w in ["automação", "n8n", "workflow", "disparar", "webhook", "processo"]):
            return "automation_agent"
        elif any(w in text for w in ["pesquisa", "buscar", "pesquisar", "artigo", "resumo", "explicar"]):
            return "research_agent"
        else:
            return "llm_direct"
