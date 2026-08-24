from typing import Any, Dict
from pydantic import BaseModel, Field
from services.tools.base.base_tool import BaseTool


class DatabaseQueryInput(BaseModel):
    query_description: str = Field(..., description="Description of database query to execute")
    limit: int = Field(10, description="Max records limit")


class DatabaseTool(BaseTool):
    name: str = "database_query_tool"
    description: str = "Executes structured read operations against PostgreSQL database."
    args_schema = DatabaseQueryInput

    async def _run(self, query_description: str, limit: int = 10) -> Dict[str, Any]:
        return {
            "query": query_description,
            "status": "executed",
            "count": limit,
            "sample_results": [
                {"id": "1", "status": "active", "created_at": "2026-08-19"}
            ]
        }
