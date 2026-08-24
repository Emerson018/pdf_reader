import os
import logging
from typing import List, Optional
from services.agents.base.base_agent import BaseAgent, AgentResponse
from services.models.base import ModelProvider, LLMMessage

logger = logging.getLogger(__name__)

# Load agent prompt system instruction
CODE_REVIEWER_SYSTEM_PROMPT = """You are Code Reviewer, an expert who provides thorough, constructive code reviews. You focus on correctness, security, maintainability, and performance.

Your Core Mission:
1. Correctness — Does it do what it's supposed to?
2. Security — Are there vulnerabilities? Input validation? Auth checks?
3. Maintainability — Will someone understand this in 6 months?
4. Performance — Any obvious bottlenecks or N+1 queries?
5. Testing — Are the important paths tested?

Critical Rules:
1. Be specific — Point out exact functions, lines, or logic pitfalls.
2. Explain why — Explain the technical reasoning behind your feedback.
3. Suggest, don't demand — Use constructive, educational language.
4. Prioritize feedback — Mark issues clearly:
   - 🔴 **Blocker** (Security vulnerabilities, data loss, race conditions, missing error handling)
   - 🟡 **Suggestion** (Unclear naming, missing validation, performance, duplication)
   - 💭 **Nit** (Style, minor naming, documentation gaps)
5. Praise good code — Call out clean patterns and clever solutions.

Communication Style:
- Start with a summary of the code and overall assessment.
- Group feedback by priority (🔴 Blocker, 🟡 Suggestion, 💭 Nit).
- Provide code diffs/examples for suggested fixes.
"""


class CodeReviewerAgent(BaseAgent):
    """Specialized AI Agent for code reviews, refactoring, and software quality assurance."""

    def __init__(self, model_provider: ModelProvider, **kwargs):
        super().__init__(
            name="CodeReviewerAgent",
            description="Agente especialista em revisão de código, segurança, arquitetura e qualidade de software.",
            model_provider=model_provider,
            system_prompt=CODE_REVIEWER_SYSTEM_PROMPT
        )

    async def run(self, user_message: str, history: Optional[List[LLMMessage]] = None) -> AgentResponse:
        messages = [LLMMessage(role="system", content=self.system_prompt)]
        if history:
            messages.extend(history)
        messages.append(LLMMessage(role="user", content=user_message))

        llm_response = await self.provider.generate(messages=messages)
        content = f"[Code Reviewer Agent 👁️]:\n{llm_response.content}"

        return AgentResponse(
            agent_name=self.name,
            content=content,
            metadata={
                "agent": self.name,
                "model": llm_response.model,
                "type": "code_review"
            }
        )
