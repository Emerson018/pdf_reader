from typing import List, Optional
from services.agents.base.base_agent import BaseAgent, AgentResponse
from services.models.base import ModelProvider, LLMMessage


class ResearchAgent(BaseAgent):
    def __init__(self, model_provider: ModelProvider, **kwargs):
        super().__init__(
            name="ResearchAgent",
            description="Especialista em pesquisas, síntese de informações e busca de dados.",
            model_provider=model_provider,
            system_prompt="Você é o ResearchAgent, um agente especialista em pesquisa e análise sintética."
        )

    async def run(self, user_message: str, history: Optional[List[LLMMessage]] = None) -> AgentResponse:
        messages = [LLMMessage(role="system", content=self.system_prompt)]
        if history:
            messages.extend(history)
        messages.append(LLMMessage(role="user", content=user_message))

        llm_response = await self.provider.generate(messages=messages)
        return AgentResponse(
            agent_name=self.name,
            content=f"[Research Agent]: {llm_response.content}",
            metadata={"agent": self.name, "model": llm_response.model}
        )
