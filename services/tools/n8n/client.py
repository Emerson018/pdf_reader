import logging
import httpx
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class N8NClient:
    """Resilient client for interacting with n8n webhooks and API."""

    def __init__(self, base_url: str = "http://localhost:5678", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["X-N8N-API-KEY"] = api_key

    async def trigger_webhook(
        self,
        webhook_path: str,
        payload: Dict[str, Any],
        timeout_seconds: float = 30.0
    ) -> Dict[str, Any]:
        """Trigger an n8n webhook endpoint with payload."""
        url = webhook_path if webhook_path.startswith("http") else f"{self.base_url}/{webhook_path.lstrip('/')}"
        logger.info(f"Triggering n8n webhook at URL: {url}")

        try:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                try:
                    return response.json()
                except Exception:
                    return {"raw_text": response.text, "status_code": response.status_code}
        except httpx.TimeoutException:
            logger.error(f"Timeout triggering n8n webhook at {url}")
            raise RuntimeError(f"n8n webhook timeout after {timeout_seconds}s")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from n8n webhook: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"n8n webhook returned HTTP {e.response.status_code}: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to n8n webhook: {e}")
            raise RuntimeError(f"Failed to communicate with n8n: {str(e)}")
