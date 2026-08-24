import logging
from typing import List, Optional
from services.agents.base.base_agent import BaseAgent, AgentResponse
from services.models.base import ModelProvider, LLMMessage

logger = logging.getLogger(__name__)

FRONTEND_DEVELOPER_SYSTEM_PROMPT = """You are Frontend Developer, an expert frontend developer specializing in modern web technologies (Next.js, React, TypeScript, Tailwind CSS), UI component implementation, accessibility (WCAG 2.1 AA), and performance optimization (Core Web Vitals).

Your Core Mission:
1. Modern Web Applications — Build responsive, pixel-perfect, accessible UI components in React/Next.js/TypeScript.
2. UX & Performance Optimization — Core Web Vitals, code splitting, sub-150ms interaction latency, mobile-first responsive layouts.
3. State Management & API Integration — Clean component architecture, WebSocket/RPC integration, robust error handling.

Communication Style:
- Detail-oriented, UX-focused, performance-first, and technically precise with clean TypeScript code examples.
"""


class FrontendDeveloperAgent(BaseAgent):
    """Specialized AI Agent for frontend development, Next.js, React components, Tailwind CSS, and Web Vitals performance."""

    def __init__(self, model_provider: ModelProvider, **kwargs):
        super().__init__(
            name="FrontendDeveloperAgent",
            description="Especialista em desenvolvimento frontend, Next.js 14, React, TypeScript, Tailwind CSS e acessibilidade UI.",
            model_provider=model_provider,
            system_prompt=FRONTEND_DEVELOPER_SYSTEM_PROMPT
        )

    async def run(self, user_message: str, history: Optional[List[LLMMessage]] = None) -> AgentResponse:
        messages = [LLMMessage(role="system", content=self.system_prompt)]
        if history:
            messages.extend(history)
        messages.append(LLMMessage(role="user", content=user_message))

        llm_response = await self.provider.generate(messages=messages)
        content = f"[Frontend Developer 🖥️]:\n{llm_response.content}"

        return AgentResponse(
            agent_name=self.name,
            content=content,
            metadata={
                "agent": self.name,
                "model": llm_response.model,
                "type": "frontend_development"
            }
        )
