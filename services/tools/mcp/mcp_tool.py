from typing import Any, Dict
from pydantic import BaseModel, Field
from services.tools.base.base_tool import BaseTool


class MCPInput(BaseModel):
    server_name: str = Field(..., description="Target MCP Server name")
    method: str = Field(..., description="MCP tool or protocol method to invoke")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the MCP server call")


class MCPTool(BaseTool):
    name: str = "mcp_protocol_tool"
    description: str = "Interacts with external Model Context Protocol (MCP) servers."
    args_schema = MCPInput

    async def _run(self, server_name: str, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        return {
            "mcp_server": server_name,
            "method": method,
            "status": "ready",
            "result": f"MCP adapter initialized for server '{server_name}' and method '{method}'"
        }
