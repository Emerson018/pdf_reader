import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ToolResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseTool(ABC):
    """Abstract base class for all tools in the platform."""

    name: str
    description: str
    args_schema: Optional[Type[BaseModel]] = None

    @abstractmethod
    async def _run(self, **kwargs) -> Any:
        """Internal execution logic to be overridden by tools."""
        pass

    async def execute(self, **kwargs) -> ToolResult:
        """Executes the tool with error handling and structured output."""
        try:
            logger.info(f"Executing tool '{self.name}' with args: {kwargs}")
            if self.args_schema:
                validated_args = self.args_schema(**kwargs)
                result_data = await self._run(**validated_args.model_dump())
            else:
                result_data = await self._run(**kwargs)

            return ToolResult(
                success=True,
                data=result_data,
                metadata={"tool_name": self.name}
            )
        except Exception as e:
            logger.exception(f"Error executing tool '{self.name}': {e}")
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"tool_name": self.name}
            )
