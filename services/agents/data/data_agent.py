from typing import List, Optional
from services.agents.base.base_agent import BaseAgent, AgentResponse
from services.models.base import ModelProvider, LLMMessage
from services.tools.database.database_tool import DatabaseTool


class DataAgent(BaseAgent):
    def __init__(self, model_provider: ModelProvider, **kwargs):
        db_tool = DatabaseTool()
        super().__init__(
            name="DataAgent",
            description="Especialista em análise de dados, consultas em banco de dados SQL e métricas.",
            model_provider=model_provider,
            tools=[db_tool],
            system_prompt="Você é o DataAgent, um agente especialista em banco de dados e engenharia de dados."
        )

    async def run(self, user_message: str, history: Optional[List[LLMMessage]] = None) -> AgentResponse:
        messages = [LLMMessage(role="system", content=self.system_prompt)]
        if history:
            messages.extend(history)
        messages.append(LLMMessage(role="user", content=user_message))

        db_tool = self.tools.get("database_query_tool")
        tool_result = await db_tool.execute(query_description=user_message) if db_tool else None

        llm_response = await self.provider.generate(messages=messages)
        content = f"[Data Agent]: {llm_response.content}"
        if tool_result and tool_result.success:
            content += f"\n\n*Resultado da Ferramenta de Dados*: {tool_result.data}"

        return AgentResponse(
            agent_name=self.name,
            content=content,
            metadata={"agent": self.name, "model": llm_response.model}
        )
