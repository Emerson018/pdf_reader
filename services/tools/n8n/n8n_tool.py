from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from services.tools.base.base_tool import BaseTool
from services.tools.n8n.client import N8NClient


class N8NWorkflowInput(BaseModel):
    webhook_path: str = Field("webhook/demo-agent", description="Path or slug of the n8n webhook")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Payload data for the workflow")


class N8NTool(BaseTool):
    name: str = "n8n_automation_tool"
    description: str = "Triggers automated workflows and integrations in n8n via webhooks."
    args_schema = N8NWorkflowInput

    def __init__(self, n8n_client: Optional[N8NClient] = None):
        super().__init__()
        self.client = n8n_client or N8NClient()

    async def _run(self, webhook_path: str = "webhook/demo-agent", payload: Dict[str, Any] = None) -> Dict[str, Any]:
        payload_data = payload or {}
        try:
            return await self.client.trigger_webhook(webhook_path=webhook_path, payload=payload_data)
        except Exception as e:
            # Fallback response for demonstration if n8n webhook is not active yet
            return {
                "status": "mock_executed",
                "message": f"n8n webhook call attempted on '{webhook_path}'. Details: {str(e)}",
                "received_payload": payload_data
            }
