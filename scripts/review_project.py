import os
import sys

sys.path.insert(0, os.getcwd())

import time
import asyncio
import logging
from services.models.factory import ModelFactory
from services.agents.coding.code_reviewer_agent import CodeReviewerAgent
from apps.api.app.core.config import Settings

logging.basicConfig(level=logging.INFO)


def gather_codebase_summary():
    """Gathers key files from the project for review."""
    target_files = [
        "apps/api/app/main.py",
        "apps/api/app/services/chat_service.py",
        "services/models/gemini_provider.py",
        "services/orchestrator/routing/supervisor.py",
        "services/orchestrator/graphs/agent_graph.py",
        "services/agents/coding/code_reviewer_agent.py",
        "services/tools/database/document_search_tool.py",
        "services/storage/minio_service.py",
    ]

    codebase_text = "### KEY ARCHITECTURAL CODEBASE FOR REVIEW:\n\n"
    for rel_path in target_files:
        full_path = os.path.join(os.getcwd(), rel_path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                codebase_text += f"--- FILE: {rel_path} ---\n"
                codebase_text += f.read()[:1500] + "\n\n"
    return codebase_text


async def run_project_review():
    settings = Settings()
    provider = ModelFactory.get_provider(
        provider_name=settings.DEFAULT_PROVIDER,
        model_name="gemini-3.6-flash",
        api_key=settings.GEMINI_API_KEY
    )

    reviewer_agent = CodeReviewerAgent(model_provider=provider)
    codebase = gather_codebase_summary()

    prompt = (
        "Como Code Reviewer Agent especialista, analise o código e a arquitetura do nosso projeto 'AI Agent Platform'. "
        "Estruture sua revisão rigorosa nas categorias: 🔴 Blockers (impeditivos/segurança), 🟡 Suggestions (melhorias de código/async) e 💭 Nits (boas práticas/legibilidade).\n\n"
        f"{codebase}"
    )

    print("=== Aguardando 10s para reset da quota da API Gemini ===")
    await asyncio.sleep(10)
    print("=== Executando CodeReviewerAgent no projeto... ===")

    response = await reviewer_agent.run(prompt)

    report_path = os.path.join(os.getcwd(), "docs", "code_review_report.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(response.content)

    print(f"\nReport de Code Review salvo com sucesso em: {report_path}")


if __name__ == "__main__":
    asyncio.run(run_project_review())
