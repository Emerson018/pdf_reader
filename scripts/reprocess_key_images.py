import os
import sys

sys.path.insert(0, os.getcwd())

import asyncio
import logging
import pymupdf
from sqlalchemy import select
from apps.api.app.core.config import Settings
from apps.api.app.db.session import AsyncSessionLocal
from apps.api.app.models.models import DocumentChunk
from services.storage.minio_service import minio_service
from services.models.factory import ModelFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reprocess_images")


async def reprocess_key_pages():
    pdf_path = "manual-do-colaborador.pdf"
    if not os.path.exists(pdf_path):
        await minio_service.download_file_async("manual-do-colaborador.pdf", pdf_path)

    current_settings = Settings()
    gemini_provider = ModelFactory.get_provider(
        provider_name="gemini",
        model_name="gemini-3.6-flash",
        api_key=current_settings.GEMINI_API_KEY
    )

    doc = pymupdf.open(pdf_path)

    # Key image pages to exhaustively extract
    target_pages = [1, 3, 6, 9, 25, 26, 36, 37]

    async with AsyncSessionLocal() as session:
        for page_idx in target_pages:
            page_num = page_idx - 1
            if page_num >= len(doc):
                continue

            page = doc[page_num]
            text = page.get_text() or ""
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            image_object_name = f"images/page_{page_idx}.png"

            prompt = (
                f"Analise a imagem da Página {page_idx} do documento hospitalar. "
                "TRANSCREVA E EXPLICITE DE FORMA COMPLETA E DETALHADA todos os textos, títulos, passos, ícones, números, listas e regras visuais contidas na imagem. "
                "Por exemplo: se houver '5 momentos para higienização das mãos', transcreva explicitamente cada um dos 5 momentos. "
                "Se houver '7 metas de segurança', transcreva explicitamente cada uma das 7 metas. "
                "Responda em português claro e completo."
            )

            logger.info(f"=== Reprocessing Page {page_idx} with Exhaustive Vision Prompt ===")
            vision_desc = await gemini_provider.generate_vision(prompt=prompt, image_bytes=img_bytes)
            logger.info(f"Page {page_idx} vision length: {len(vision_desc)} chars.")

            full_content = f"--- Página {page_idx} do Documento manual-do-colaborador.pdf ---\n\n"
            if text.strip():
                full_content += f"**Conteúdo de Texto:**\n{text.strip()}\n\n"
            if vision_desc.strip():
                full_content += f"**Análise de Elementos Visuais (Diagramas/Organogramas/Imagens):**\n{vision_desc.strip()}\n\n"

            logger.info(f"Generating vector embedding for Page {page_idx}...")
            emb = await gemini_provider.generate_embedding(full_content)

            # Query existing chunk or update
            stmt = select(DocumentChunk).where(
                DocumentChunk.document_name == "manual-do-colaborador.pdf",
                DocumentChunk.chunk_index == page_idx
            )
            result = await session.execute(stmt)
            chunk = result.scalar_one_or_none()

            if chunk:
                chunk.content = full_content
                chunk.embedding = emb
                chunk.metadata_json = {
                    "page": page_idx,
                    "has_image": True,
                    "image_url": f"http://localhost:9001/ai-platform-artifacts/{image_object_name}"
                }
            else:
                session.add(
                    DocumentChunk(
                        document_name="manual-do-colaborador.pdf",
                        chunk_index=page_idx,
                        content=full_content,
                        embedding=emb,
                        metadata_json={
                            "page": page_idx,
                            "has_image": True,
                            "image_url": f"http://localhost:9001/ai-platform-artifacts/{image_object_name}"
                        }
                    )
                )

            await session.commit()
            logger.info(f"Successfully saved Page {page_idx} to PostgreSQL!")
            await asyncio.sleep(2.0)

    logger.info("=== Reprocessing Key Pages Complete! ===")


if __name__ == "__main__":
    asyncio.run(reprocess_key_pages())
