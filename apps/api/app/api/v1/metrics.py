import logging
from fastapi import APIRouter, HTTPException, status
from apps.api.app.services.metrics_service import metrics_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/metrics/rag")
async def get_rag_metrics_endpoint():
    """Retrieves real-time observability metrics for Redis Semantic Cache, PostgreSQL Vector DB, and infrastructure health."""
    try:
        data = await metrics_service.get_rag_metrics()
        return data
    except Exception as e:
        logger.exception("Error retrieving RAG metrics")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao obter métricas do RAG: {str(e)}"
        )
