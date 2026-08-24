import logging
from typing import AsyncGenerator, Dict, List, Optional, Any
from services.models.base import ModelProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(ModelProvider):
    """OpenAI Model Provider implementation with graceful mock fallback."""

    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name=model_name, api_key=api_key, **kwargs)
        self.client = None
        key_str = (self.api_key or "").strip()

        if key_str and not key_str.startswith("mock-") and key_str != "your-openai-api-key-here" and key_str != "mock-key-or-real-key":
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=key_str)
                masked_key = f"{key_str[:7]}...{key_str[-4:]}" if len(key_str) > 11 else "***"
                logger.info(f"OpenAI AsyncOpenAI client initialized for model '{self.model_name}' with API Key ({masked_key}).")
            except ImportError:
                logger.warning("openai package not installed. Provider will run in fallback mock mode.")
            except Exception as e:
                logger.warning(f"Failed to initialize AsyncOpenAI client: {e}")
        else:
            logger.info(f"No valid OpenAI API key detected (current key value: '{key_str[:15]}...'). Operating in mock fallback mode.")

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        if self.client:
            try:
                formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=formatted_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                content = response.choices[0].message.content or ""
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                }
                return LLMResponse(content=content, model=self.model_name, usage=usage, raw_response=response.model_dump())
            except Exception as e:
                logger.error(f"Error calling OpenAI API: {e}. Falling back to mock response.", exc_info=True)
                
        # Graceful fallback response
        last_user_msg = next((m.content for m in reversed(messages) if m.role == "user"), "Olá")
        content = f"[Resposta de Demonstração (OpenAI Provider Mock)]: Recebi a sua mensagem '{last_user_msg}'. O sistema de abstração de LLM da plataforma está operacional!"
        return LLMResponse(
            content=content,
            model=f"{self.model_name}-mock",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        )

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        if self.client:
            try:
                formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
                stream = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=formatted_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                    **kwargs
                )
                async for chunk in stream:
                    delta = chunk.choices[0].delta.content if chunk.choices else ""
                    if delta:
                        yield delta
                return
            except Exception as e:
                logger.error(f"Error streaming from OpenAI API: {e}. Falling back to mock stream.", exc_info=True)

        response = await self.generate(messages, temperature, max_tokens, **kwargs)
        for word in response.content.split(" "):
            yield word + " "
