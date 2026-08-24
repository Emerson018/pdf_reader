import os
import sys

sys.path.insert(0, os.getcwd())

import asyncio
import logging
from sqlalchemy import select
from apps.api.app.core.config import Settings
from apps.api.app.db.session import AsyncSessionLocal
from apps.api.app.models.models import DocumentChunk
from services.models.factory import ModelFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("embeddings_generator")


async def generate_embeddings_for_all_chunks():
    logger.info("=== Starting Vector Embeddings Generation for all Document Chunks ===")
    
    current_settings = Settings()
    gemini_provider = ModelFactory.get_provider(
        provider_name="gemini",
        model_name="gemini-3.6-flash",
        api_key=current_settings.GEMINI_API_KEY
    )

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(DocumentChunk))
        chunks = result.scalars().all()

        logger.info(f"Found {len(chunks)} document chunks. Generating embeddings...")

        for chunk in chunks:
            logger.info(f"Generating embedding for Chunk {chunk.chunk_index} ({chunk.document_name})...")
            embedding_vec = await gemini_provider.generate_embedding(chunk.content)
            chunk.embedding = embedding_vec
            session.add(chunk)

        await session.commit()
        logger.info(f"=== Successfully updated vector embeddings for all {len(chunks)} chunks! ===")


if __name__ == "__main__":
    asyncio.run(generate_embeddings_for_all_chunks())
