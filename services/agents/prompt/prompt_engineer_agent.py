import logging
from typing import List, Optional
from services.agents.base.base_agent import BaseAgent, AgentResponse
from services.models.base import ModelProvider, LLMMessage

logger = logging.getLogger(__name__)

PROMPT_ENGINEER_SYSTEM_PROMPT = """You are Prompt Engineer, a specialist in crafting, testing, and systematically optimizing system prompts for LLMs — turning vague human instructions into reliable, production-grade AI behaviors.

Your Core Mission:
1. System Prompt Design — Role, Constraints, Reasoning Scaffolds (<thinking> tags), and Few-Shot Examples (<example> tags).
2. Prompt Testing & Evaluation — Define output schemas (JSON/Markdown), edge cases, and injection defenses.
3. Prompt Versioning & Changelogs — Version control prompts like code (`v1`, `v2`) with measurable quality metrics.
4. Behavior Contract — Translate ambiguous requirements into precise, explicit instructions for AI models.

Communication Style:
- Precise, methodical, structured, and focused on production-grade prompt templates and JSON schemas.
- Provide before/after prompt comparisons, few-shot blocks, and test cases.
"""


class PromptEngineerAgent(BaseAgent):
    """Specialized AI Agent for prompt engineering, system prompt creation, few-shot design, and LLM behavior optimization."""

    def __init__(self, model_provider: ModelProvider, **kwargs):
        super().__init__(
            name="PromptEngineerAgent",
            description="Especialista em Prompt Engineering, criação de system prompts, poucas amostras (few-shot) e otimização de comportamento de LLMs.",
            model_provider=model_provider,
            system_prompt=PROMPT_ENGINEER_SYSTEM_PROMPT
        )

    async def run(self, user_message: str, history: Optional[List[LLMMessage]] = None) -> AgentResponse:
        messages = [LLMMessage(role="system", content=self.system_prompt)]
        if history:
            messages.extend(history)
        messages.append(LLMMessage(role="user", content=user_message))

        llm_response = await self.provider.generate(messages=messages)
        content = f"[Prompt Engineer 🧬]:\n{llm_response.content}"

        return AgentResponse(
            agent_name=self.name,
            content=content,
            metadata={
                "agent": self.name,
                "model": llm_response.model,
                "type": "prompt_engineering"
            }
        )
