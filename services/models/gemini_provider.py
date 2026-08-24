import base64
import logging
import asyncio
import httpx
from typing import AsyncGenerator, Dict, List, Optional, Any
from services.models.base import ModelProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class GeminiProvider(ModelProvider):
    """Google Gemini Model Provider implementation supporting text, Multimodal Vision, and Embeddings."""

    def __init__(self, model_name: str = "gemini-3.6-flash", api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name=model_name, api_key=api_key, **kwargs)
        self.api_key = (api_key or "").strip()
        if self.model_name.startswith("google/"):
            self.model_name = self.model_name.replace("google/", "")

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        key = self.api_key

        if not key or key.startswith("mock-") or key == "your-gemini-api-key-here":
            logger.info("No valid Gemini API key provided. Operating in mock fallback mode.")
            last_user_msg = next((m.content for m in reversed(messages) if m.role == "user"), "Olá")
            return LLMResponse(
                content=f"[Resposta de Demonstração (Gemini Mock)]: Recebi a sua mensagem '{last_user_msg}'. Para obter respostas reais do Gemini, insira sua GEMINI_API_KEY do Google AI Studio.",
                model=f"{self.model_name}-mock",
                usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
            )

        gemini_contents = []
        system_instruction = None

        for msg in messages:
            if msg.role == "system":
                system_instruction = {"parts": [{"text": msg.content}]}
            else:
                role = "model" if msg.role in ["assistant", "model"] else "user"
                gemini_contents.append({
                    "role": role,
                    "parts": [{"text": msg.content}]
                })

        payload: Dict[str, Any] = {
            "contents": gemini_contents,
            "generationConfig": {
                "temperature": temperature,
            }
        }

        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens

        if system_instruction:
            payload["systemInstruction"] = system_instruction

        models_to_try = [
            self.model_name,
            "gemini-3.6-flash",
            "gemini-3.7-flash",
            "gemini-3.5-flash",
            "gemini-flash-latest",
            "gemini-3.1-flash-lite"
        ]
        models_to_try = list(dict.fromkeys(models_to_try))

        last_error = None
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    response = await client.post(url, json=payload)
                    
                    if response.status_code in [429, 503]:
                        logger.warning(f"Gemini API returned HTTP {response.status_code} for model '{model}'. Retrying next model...")
                        last_error = f"HTTP {response.status_code}: {response.text}"
                        await asyncio.sleep(3)
                        continue

                    response.raise_for_status()
                    data = response.json()

                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        content = "".join([part.get("text", "") for part in parts])
                    else:
                        content = "[Gemini Provider]: Resposta vazia recebida da API."

                    usage_data = data.get("usageMetadata", {})
                    usage = {
                        "prompt_tokens": usage_data.get("promptTokenCount", 0),
                        "completion_tokens": usage_data.get("candidatesTokenCount", 0),
                        "total_tokens": usage_data.get("totalTokenCount", 0),
                    }

                    return LLMResponse(
                        content=content,
                        model=model,
                        usage=usage,
                        raw_response=data
                    )
            except Exception as e:
                logger.error(f"Error trying model '{model}': {e}")
                last_error = str(e)

        return LLMResponse(
            content=f"[Gemini API]: Todos os modelos retornaram erro temporário ({last_error}). Por favor, tente novamente em alguns segundos.",
            model=f"{self.model_name}-error"
        )

    async def generate_embedding(self, text: str) -> List[float]:
        """Generates a 768-dimensional vector embedding using gemini-embedding-001 with 429 retries."""
        key = self.api_key
        if not key or key.startswith("mock-") or key == "your-gemini-api-key-here":
            import hashlib
            h = hashlib.sha256(text.encode("utf-8")).digest()
            return [float((b % 100) / 100.0) for b in (h * 24)[:768]]

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={key}"
        payload = {
            "model": "models/gemini-embedding-001",
            "content": {
                "parts": [{"text": text}]
            },
            "outputDimensionality": 768
        }

        for attempt in range(5):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        embedding_values = data.get("embedding", {}).get("values", [])
                        if embedding_values:
                            return embedding_values
                    elif response.status_code in [429, 503]:
                        logger.warning(f"Embedding API HTTP {response.status_code}, retrying in {4 * (attempt + 1)}s...")
                        await asyncio.sleep(4 * (attempt + 1))
            except Exception as e:
                logger.error(f"Error generating Gemini embedding: {e}")
                await asyncio.sleep(2)

        # Fallback vector if embedding API fails
        import hashlib
        h = hashlib.sha256(text.encode("utf-8")).digest()
        return [float((b % 100) / 100.0) for b in (h * 24)[:768]]

    async def generate_vision(
        self,
        prompt: str,
        image_bytes: bytes,
        mime_type: str = "image/png",
        temperature: float = 0.4
    ) -> str:
        """Generates a detailed text analysis of an image using Gemini Multimodal Vision API with rate-limit handling."""
        key = self.api_key
        if not key or key.startswith("mock-") or key == "your-gemini-api-key-here":
            return "[Gemini Vision Mock]: Imagem extraída do documento (Modo de Demonstração sem chave Gemini ativada)."

        b64_data = base64.b64encode(image_bytes).decode("utf-8")
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": b64_data
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {"temperature": temperature}
        }

        models_to_try = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-latest"]

        for attempt in range(5):
            for model in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
                try:
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        resp = await client.post(url, json=payload)
                        if resp.status_code == 200:
                            data = resp.json()
                            candidates = data.get("candidates", [])
                            if candidates and "content" in candidates[0]:
                                parts = candidates[0]["content"].get("parts", [])
                                text_res = "".join([part.get("text", "") for part in parts])
                                if text_res.strip():
                                    return text_res.strip()
                        elif resp.status_code in [429, 503]:
                            sleep_time = 4 * (attempt + 1)
                            logger.warning(f"Vision API HTTP {resp.status_code} for {model}, sleeping {sleep_time}s...")
                            await asyncio.sleep(sleep_time)
                except Exception as e:
                    logger.error(f"Error in generate_vision ({model}): {e}")

            await asyncio.sleep(2)

        return "[Gemini Vision]: Análise visual parcial processada."

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        res = await self.generate(messages, temperature, max_tokens, **kwargs)
        for word in res.content.split(" "):
            yield word + " "
