from typing import Dict, Optional
from pydantic import BaseModel


class HealthStatus(BaseModel):
    status: str  # "ok", "degraded", "down"
    version: str = "1.0.0"
    services: Dict[str, str] = {}


class ComponentHealth(BaseModel):
    status: str
    details: Optional[str] = None
