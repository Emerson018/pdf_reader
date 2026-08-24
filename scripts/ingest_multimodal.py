import os
import sys

sys.path.insert(0, os.getcwd())

import asyncio
import logging
import pymupdf
from sqlalchemy import delete
from apps.api.app.core.config import Settings
from apps.api.app.db.session import engine, AsyncSessionLocal, Base
from apps.api.app.models.models import DocumentChunk
from services.storage.minio_service import minio_service
from services.models.factory import ModelFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("multimodal_ingestion")


async def process_multimodal_pdf(pdf_path: str = "manual-do-colaborador.pdf"):
    if not os.path.exists(pdf_path):
        logger.info(f"Local file '{pdf_path}' not found. Downloading from MinIO object storage...")
        doc_name = os.path.basename(pdf_path)
        download_success = await minio_service.download_file_async(doc_name, pdf_path)
        if not download_success:
            logger.error(f"Failed to fetch '{pdf_path}' from MinIO.")
            return False

    doc_name = os.path.basename(pdf_path)
    logger.info(f"=== Starting Exhaustive Multimodal RAG Ingestion & Vector Embedding for '{doc_name}' ===")

    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 1. Upload original PDF to MinIO asynchronously
    logger.info("Step 1: Uploading original PDF to MinIO object storage (async)...")
    await minio_service.upload_file_async(pdf_path, object_name=doc_name)

    # 2. Initialize Gemini Provider
    current_settings = Settings()
    gemini_provider = ModelFactory.get_provider(
        provider_name="gemini",
        model_name="gemini-3.6-flash",
        api_key=current_settings.GEMINI_API_KEY
    )

    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    logger.info(f"Step 2: Processing {total_pages} pages with exhaustive visual extraction...")

    chunks_to_insert = []

    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text() or ""
        images = page.get_images()

        has_images = len(images) > 0
        logger.info(f"Page {page_num + 1}/{total_pages}: {len(text)} chars text, {len(images)} embedded images.")

        # Render page pixmap to PNG for vision analysis
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        image_object_name = f"images/page_{page_num + 1}.png"

        # Save temporary image file for MinIO async upload
        temp_img_path = f"temp_page_{page_num + 1}.png"
        pix.save(temp_img_path)
        await minio_service.upload_file_async(temp_img_path, object_name=image_object_name)
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)

        visual_description = ""
        # Perform exhaustive vision extraction for pages with visual elements or images
        if has_images or len(text.strip()) < 300 or page_num in [0, 2, 5, 8, 24, 25, 35, 36]:
            prompt = (
                f"Analise detalhadamente a imagem da Página {page_num + 1} do documento. "
                "TRANSCREVA INTEGRALMENTE E DESCREVA DE FORMA EXAUSTIVA todos os textos visuais, diagramas, "
                "fluxogramas, ícones, números, listas numeradas, passos, tabelas e organogramas contidos na imagem. "
                "Especifique com detalhes cada item ou passo ilustrado na imagem (por exemplo, quais são os 5 momentos de higienização das mãos, as metas de segurança, etc). "
                "Responda em português completo para que a busca encontre qualquer detalhe."
            )

            try:
                logger.info(f"Calling Gemini Vision for Page {page_num + 1} exhaustive extraction...")
                visual_description = await gemini_provider.generate_vision(
                    prompt=prompt,
                    image_bytes=img_bytes
                )
                logger.info(f"Exhaustive vision description generated for Page {page_num + 1} ({len(visual_description)} chars).")
            except Exception as e:
                logger.error(f"Vision analysis failed for page {page_num + 1}: {e}")

            # Sleep 2s to respect Gemini API 15 RPM limit
            await asyncio.sleep(2.0)

        # Combine text content and visual description
        full_chunk_content = f"--- Página {page_num + 1} do Documento {doc_name} ---\n\n"
        if text.strip():
            full_chunk_content += f"**Conteúdo de Texto:**\n{text.strip()}\n\n"
        if visual_description.strip():
            full_chunk_content += f"**Análise Exaustiva de Elementos Visuais (Diagramas/Organogramas/Imagens):**\n{visual_description.strip()}\n\n"

        # Generate 768-dim vector embedding
        logger.info(f"Generating vector embedding for Page {page_num + 1}...")
        vector_emb = await gemini_provider.generate_embedding(full_chunk_content)

        chunks_to_insert.append(
            DocumentChunk(
                document_name=doc_name,
                chunk_index=page_num + 1,
                content=full_chunk_content,
                embedding=vector_emb,
                metadata_json={
                    "page": page_num + 1,
                    "has_image": has_images,
                    "image_url": f"http://localhost:9001/ai-platform-artifacts/{image_object_name}"
                }
            )
        )

    # 3. Clear existing chunks for this document and store multimodal chunks
    logger.info("Step 3: Storing multimodal chunks and embeddings in PostgreSQL document_chunks table...")
    async with AsyncSessionLocal() as session:
        await session.execute(delete(DocumentChunk).where(DocumentChunk.document_name == doc_name))
        for chunk in chunks_to_insert:
            session.add(chunk)
        await session.commit()

    logger.info(f"=== Multimodal RAG Ingestion & Embedding Complete! Inserted {len(chunks_to_insert)} pages/chunks ===")
    return True


if __name__ == "__main__":
    pdf_file = "manual-do-colaborador.pdf"
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]

    asyncio.run(process_multimodal_pdf(pdf_file))
