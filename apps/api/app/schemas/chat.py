from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="Message input from user", example="Olá")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID")
    user_id: Optional[str] = Field(None, description="Optional user ID")
    model: Optional[str] = Field(None, description="Optional model override")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Response message from AI agent")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata")
