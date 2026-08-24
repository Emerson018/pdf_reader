from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from services.models.base import ModelProvider, LLMMessage
from services.tools.base.base_tool import BaseTool


class AgentResponse(BaseModel):
    agent_name: str
    content: str
    tool_calls: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}


class BaseAgent(ABC):
    """Abstract base class for all specialized AI Agents."""

    def __init__(
        self,
        name: str,
        description: str,
        model_provider: ModelProvider,
        tools: Optional[List[BaseTool]] = None,
        system_prompt: Optional[str] = None
    ):
        self.name = name
        self.description = description
        self.provider = model_provider
        self.tools = {tool.name: tool for tool in (tools or [])}
        self.system_prompt = system_prompt or f"Você é o {name}. {description}"

    @abstractmethod
    async def run(self, user_message: str, history: Optional[List[LLMMessage]] = None) -> AgentResponse:
        """Run the agent logic given a user message and history."""
        pass
