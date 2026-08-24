import logging
import httpx
from typing import AsyncGenerator, List, Optional
from services.models.base import ModelProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class OllamaProvider(ModelProvider):
    """Ollama local model provider implementation."""

    def __init__(
        self,
        model_name: str = "llama3",
        base_url: str = "http://localhost:11434",
        **kwargs
    ):
        super().__init__(model_name=model_name, **kwargs)
        self.base_url = base_url.rstrip("/")

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "stream": False,
            "options": {"temperature": temperature}
        }
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                content = data.get("message", {}).get("content", "")
                return LLMResponse(
                    content=content,
                    model=self.model_name,
                    raw_response=data
                )
        except Exception as e:
            logger.error(f"Ollama provider error: {e}")
            return LLMResponse(
                content=f"[Ollama Provider Error]: Não foi possível conectar ao Ollama em {self.base_url} ({e})",
                model=f"{self.model_name}-error"
            )

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        res = await self.generate(messages, temperature, max_tokens, **kwargs)
        yield res.content
