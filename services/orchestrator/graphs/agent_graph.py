import logging
from typing import Dict, Any
from services.models.base import ModelProvider, LLMMessage
from services.agents.research.research_agent import ResearchAgent
from services.agents.data.data_agent import DataAgent
from services.agents.automation.automation_agent import AutomationAgent
from services.agents.document.document_agent import DocumentAgent
from services.agents.coding.code_reviewer_agent import CodeReviewerAgent
from services.agents.rag.rag_engineer_agent import RAGPipelineEngineerAgent
from services.agents.prompt.prompt_engineer_agent import PromptEngineerAgent
from services.agents.backend.backend_architect_agent import BackendArchitectAgent
from services.agents.database.database_optimizer_agent import DatabaseOptimizerAgent
from services.agents.frontend.frontend_developer_agent import FrontendDeveloperAgent
from services.orchestrator.routing.supervisor import SupervisorRouter
from services.orchestrator.state.agent_state import AgentStateDict

logger = logging.getLogger(__name__)


class OrchestrationGraph:
    """LangGraph Orchestration Graph connecting Router, Agents, and LLMs."""

    def __init__(self, provider: ModelProvider):
        self.provider = provider
        self.router = SupervisorRouter(provider)
        self.research_agent = ResearchAgent(provider)
        self.data_agent = DataAgent(provider)
        self.automation_agent = AutomationAgent(provider)
        self.document_agent = DocumentAgent(provider)
        self.code_reviewer_agent = CodeReviewerAgent(provider)
        self.rag_engineer_agent = RAGPipelineEngineerAgent(provider)
        self.prompt_engineer_agent = PromptEngineerAgent(provider)
        self.backend_architect_agent = BackendArchitectAgent(provider)
        self.database_optimizer_agent = DatabaseOptimizerAgent(provider)
        self.frontend_developer_agent = FrontendDeveloperAgent(provider)

    async def execute(self, user_message: str) -> Dict[str, Any]:
        """Executes the orchestration workflow graph."""
        # 1. Routing / Supervisor node
        target_node = await self.router.route(user_message)
        logger.info(f"Orchestration Supervisor routed request to: {target_node}")

        # 2. Agent / LLM node execution
        if target_node == "frontend_developer_agent":
            res = await self.frontend_developer_agent.run(user_message)
            return {"response": res.content, "agent": res.agent_name, "metadata": res.metadata}

        elif target_node == "backend_architect_agent":
            res = await self.backend_architect_agent.run(user_message)
            return {"response": res.content, "agent": res.agent_name, "metadata": res.metadata}

        elif target_node == "database_optimizer_agent":
            res = await self.database_optimizer_agent.run(user_message)
            return {"response": res.content, "agent": res.agent_name, "metadata": res.metadata}

        elif target_node == "prompt_engineer_agent":
            res = await self.prompt_engineer_agent.run(user_message)
            return {"response": res.content, "agent": res.agent_name, "metadata": res.metadata}

        elif target_node == "rag_engineer_agent":
            res = await self.rag_engineer_agent.run(user_message)
            return {"response": res.content, "agent": res.agent_name, "metadata": res.metadata}

        elif target_node == "code_reviewer_agent":
            res = await self.code_reviewer_agent.run(user_message)
            return {"response": res.content, "agent": res.agent_name, "metadata": res.metadata}

        elif target_node == "document_agent":
            res = await self.document_agent.run(user_message)
            return {"response": res.content, "agent": res.agent_name, "metadata": res.metadata}

        elif target_node == "data_agent":
            res = await self.data_agent.run(user_message)
            return {"response": res.content, "agent": res.agent_name, "metadata": res.metadata}

        elif target_node == "automation_agent":
            res = await self.automation_agent.run(user_message)
            return {"response": res.content, "agent": res.agent_name, "metadata": res.metadata}

        elif target_node == "research_agent":
            res = await self.research_agent.run(user_message)
            return {"response": res.content, "agent": res.agent_name, "metadata": res.metadata}

        else:
            messages = [
                LLMMessage(role="system", content="Você é o assistente inteligente da AI Agent Platform."),
                LLMMessage(role="user", content=user_message)
            ]
            llm_res = await self.provider.generate(messages)
            return {
                "response": llm_res.content,
                "agent": "DirectLLM",
                "metadata": {"model": llm_res.model, "usage": llm_res.usage or {}}
            }
