import asyncio
import logging
from typing import Dict, Any, List
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

logger = logging.getLogger(__name__)


class OrchestrationGraph:
    """LangGraph Orchestration Graph connecting Router, Agents, and Multi-Agent Parallel Workflows."""

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

    async def execute_multi_agent_orchestration(self, user_message: str) -> Dict[str, Any]:
        """Executes all 10 specialized AI agents concurrently and synthesizes a unified Multi-Agent Report."""
        logger.info(f"Orchestrating Multi-Agent Broadcast across all 10 AI agents for: '{user_message[:40]}...'")

        agents_list = [
            ("📄 DocumentAgent (RAG & Documentos Locais)", self.document_agent),
            ("🏗️ BackendArchitect (Arquitetura & APIs)", self.backend_architect_agent),
            ("🎨 FrontendDeveloper (UI/UX & Componentes)", self.frontend_developer_agent),
            ("⚡ DatabaseOptimizer (SQL & Indexação)", self.database_optimizer_agent),
            ("🧠 RAGPipelineEngineer (Estratégias RAG)", self.rag_engineer_agent),
            ("🔍 CodeReviewer (Qualidade & Segurança)", self.code_reviewer_agent),
            ("🎯 PromptEngineer (Prompts & Eng. de IA)", self.prompt_engineer_agent),
            ("📊 DataAgent (Métricas & Análise de Dados)", self.data_agent),
            ("🤖 AutomationAgent (Automação & n8n)", self.automation_agent),
            ("🔬 ResearchAgent (Pesquisa & Síntese)", self.research_agent),
        ]

        tasks = [agent.run(user_message) for _, agent in agents_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        report_sections = []
        executed_agents = []

        for (label, agent_obj), res in zip(agents_list, results):
            if isinstance(res, Exception):
                logger.error(f"Error executing agent {label}: {res}")
                report_sections.append(f"#### {label}\n⚠️ *Instabilidade temporária no processamento deste agente.*")
            else:
                executed_agents.append(res.agent_name)
                report_sections.append(f"#### {label}\n{res.content}\n")

        unified_response = (
            f"## 🤖 Painel de Orquestração Multi-Agentes (Análise Consolidada)\n\n"
            f"**Tarefa Solicitada:** *\"{user_message}\"*\n"
            f"**Total de Agentes Especialistas Consultados:** {len(executed_agents)} IAs ativas\n\n"
            + "\n---\n\n".join(report_sections)
        )

        return {
            "response": unified_response,
            "agent": "MultiAgentOrchestrator",
            "metadata": {
                "orchestration_mode": "multi_agent_broadcast",
                "agents_executed": executed_agents,
                "agents_count": len(executed_agents)
            }
        }

    async def execute(self, user_message: str) -> Dict[str, Any]:
        """Executes the orchestration workflow graph."""
        target_node = await self.router.route(user_message)
        logger.info(f"Orchestration Supervisor routed request to: {target_node}")

        if target_node == "multi_agent_orchestration":
            return await self.execute_multi_agent_orchestration(user_message)

        elif target_node == "frontend_developer_agent":
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
            return await self.execute_multi_agent_orchestration(user_message)
