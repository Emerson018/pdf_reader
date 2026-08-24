from typing import List, Dict, Any, Optional, TypedDict
from services.models.base import LLMMessage


class AgentStateDict(TypedDict):
    messages: List[LLMMessage]
    next_node: str
    current_agent: str
    final_response: str
    metadata: Dict[str, Any]
