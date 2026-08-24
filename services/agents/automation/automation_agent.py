from typing import List, Optional
from services.agents.base.base_agent import BaseAgent, AgentResponse
from services.models.base import ModelProvider, LLMMessage
from services.tools.n8n.n8n_tool import N8NTool


class AutomationAgent(BaseAgent):
    def __init__(self, model_provider: ModelProvider, **kwargs):
        n8n_tool = N8NTool()
        super().__init__(
            name="AutomationAgent",
            description="Especialista em automação de processos e integração via n8n.",
            model_provider=model_provider,
            tools=[n8n_tool],
            system_prompt="Você é o AutomationAgent, encarregado de disparar automações e fluxos n8n."
        )

    async def run(self, user_message: str, history: Optional[List[LLMMessage]] = None) -> AgentResponse:
        n8n_tool = self.tools.get("n8n_automation_tool")
        tool_result = await n8n_tool.execute(
            webhook_path="webhook/demo-agent",
            payload={"message": user_message, "agent": self.name}
        ) if n8n_tool else None

        messages = [LLMMessage(role="system", content=self.system_prompt)]
        if history:
            messages.extend(history)
        messages.append(LLMMessage(role="user", content=user_message))

        llm_response = await self.provider.generate(messages=messages)
        content = f"[Automation Agent]: {llm_response.content}"
        if tool_result:
            content += f"\n\n*Status Automação (n8n)*: {tool_result.data}"

        return AgentResponse(
            agent_name=self.name,
            content=content,
            metadata={"agent": self.name, "model": llm_response.model, "n8n_status": tool_result.success if tool_result else False}
        )
