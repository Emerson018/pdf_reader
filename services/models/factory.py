from typing import Optional
from services.models.base import ModelProvider
from services.models.openai_provider import OpenAIProvider
from services.models.ollama_provider import OllamaProvider
from services.models.gemini_provider import GeminiProvider


class ModelFactory:
    """Factory to instantiate the appropriate ModelProvider."""

    @staticmethod
    def get_provider(
        provider_name: str = "openai",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ) -> ModelProvider:
        provider_name = (provider_name or "openai").lower()
        if provider_name in ["gemini", "google"]:
            model = model_name or "gemini-1.5-flash"
            return GeminiProvider(model_name=model, api_key=api_key, **kwargs)
        elif provider_name == "ollama":
            model = model_name or "llama3"
            return OllamaProvider(model_name=model, **kwargs)
        elif provider_name == "openai":
            model = model_name or "gpt-4o-mini"
            return OpenAIProvider(model_name=model, api_key=api_key, **kwargs)
        else:
            # Fallback based on model name or default to OpenAIProvider
            if "gemini" in (model_name or "").lower():
                return GeminiProvider(model_name=model_name or "gemini-1.5-flash", api_key=api_key, **kwargs)
            model = model_name or "gpt-4o-mini"
            return OpenAIProvider(model_name=model, api_key=api_key, **kwargs)
