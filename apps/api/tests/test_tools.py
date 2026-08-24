import pytest
from services.tools.database.database_tool import DatabaseTool
from services.tools.n8n.n8n_tool import N8NTool
from services.tools.mcp.mcp_tool import MCPTool


@pytest.mark.asyncio
async def test_database_tool():
    tool = DatabaseTool()
    result = await tool.execute(query_description="Buscar usuários", limit=5)
    assert result.success is True
    assert result.data["count"] == 5


@pytest.mark.asyncio
async def test_n8n_tool_fallback():
    tool = N8NTool()
    result = await tool.execute(webhook_path="webhook/test", payload={"test": True})
    assert result.success is True
    assert "received_payload" in result.data


@pytest.mark.asyncio
async def test_mcp_tool():
    tool = MCPTool()
    result = await tool.execute(server_name="test_server", method="query", params={"q": "hello"})
    assert result.success is True
    assert result.data["mcp_server"] == "test_server"
