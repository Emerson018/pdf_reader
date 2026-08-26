import logging
import time
from typing import Dict, Any
from sqlalchemy import select, func
from apps.api.app.db.session import AsyncSessionLocal, engine
from apps.api.app.models.models import DocumentChunk
from services.cache.redis_cache_service import redis_cache_service
from services.storage.minio_service import minio_service

logger = logging.getLogger(__name__)

START_TIME = time.time()


class MetricsService:
    """Aggregates real-time metrics for Redis Semantic Cache, PostgreSQL Vector DB, MinIO, and API Health."""

    @staticmethod
    async def get_rag_metrics() -> Dict[str, Any]:
        # 1. Fetch Redis Semantic Cache Stats
        cache_stats = await redis_cache_service.get_cache_stats()

        # 2. Fetch PostgreSQL pgvector Database Stats
        total_documents = 0
        total_chunks = 0
        total_vision_chunks = 0

        db_status = "Healthy"
        try:
            async with AsyncSessionLocal() as session:
                # Count total chunks
                stmt_total = select(func.count(DocumentChunk.id))
                res_total = await session.execute(stmt_total)
                total_chunks = res_total.scalar() or 0

                # Count distinct document names
                stmt_docs = select(func.count(func.distinct(DocumentChunk.document_name)))
                res_docs = await session.execute(stmt_docs)
                total_documents = res_docs.scalar() or 0

                # Count chunks containing vision analysis or image metadata
                stmt_vision = select(func.count(DocumentChunk.id)).where(
                    func.jsonb_extract_path_text(DocumentChunk.metadata_json, 'has_image') == 'true'
                )
                res_vision = await session.execute(stmt_vision)
                total_vision_chunks = res_vision.scalar() or 0
        except Exception as e:
            logger.error(f"Error reading PostgreSQL vector metrics: {e}")
            db_status = "Unhealthy"

        # 3. Check MinIO Object Storage Status
        minio_status = "Healthy"
        try:
            # Check bucket existence
            minio_service.client.bucket_exists(minio_service.bucket_name)
        except Exception:
            minio_status = "Degraded"

        uptime_seconds = round(time.time() - START_TIME, 1)

        return {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "uptime_seconds": uptime_seconds,
            "redis_cache": cache_stats,
            "postgresql_vector_db": {
                "status": db_status,
                "total_documents": total_documents,
                "total_chunks": total_chunks,
                "total_vision_chunks": total_vision_chunks,
                "vector_dimension": 768,
                "embedding_model": "gemini-embedding-004",
                "index_type": "HNSW Cosine Distance (m=16, ef_construction=64)",
                "search_algorithms": "Hybrid Vector + Full-Text RRF Fusion"
            },
            "minio_storage": {
                "status": minio_status,
                "bucket": minio_service.bucket_name
            },
            "infrastructure_health": {
                "api": "Healthy",
                "postgres": db_status,
                "redis": cache_stats.get("status", "Healthy"),
                "minio": minio_status
            }
        }


metrics_service = MetricsService()
