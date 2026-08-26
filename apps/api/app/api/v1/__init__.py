from fastapi import APIRouter
from apps.api.app.api.v1.health import router as health_router
from apps.api.app.api.v1.chat import router as chat_router
from apps.api.app.api.v1.documents import router as documents_router
from apps.api.app.api.v1.metrics import router as metrics_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(chat_router, tags=["chat"])
api_v1_router.include_router(documents_router, tags=["documents"])
api_v1_router.include_router(metrics_router, tags=["metrics"])

__all__ = ["api_v1_router", "health_router"]
