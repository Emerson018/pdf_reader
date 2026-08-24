import os
import sys

sys.path.insert(0, os.getcwd())

import asyncio
import logging
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession
from apps.api.app.db.session import engine, AsyncSessionLocal, Base
from apps.api.app.models.models import DocumentChunk
from services.storage.minio_service import minio_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("document_ingestion")


def extract_pdf_chunks(pdf_path: str, chunk_size: int = 600, overlap: int = 100):
    """Extracts text from PDF and splits into overlapping text chunks."""
    reader = PdfReader(pdf_path)
    full_text = ""
    for idx, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        full_text += f"\n--- Página {idx+1} ---\n" + page_text

    chunks = []
    start = 0
    while start < len(full_text):
        end = start + chunk_size
        chunk_text = full_text[start:end].strip()
        if chunk_text:
            chunks.append(chunk_text)
        start += (chunk_size - overlap)

    return chunks


async def ingest_document(file_path: str):
    if not os.path.exists(file_path):
        logger.error(f"Document file not found at path: {file_path}")
        return False

    doc_name = os.path.basename(file_path)
    logger.info(f"Starting ingestion process for document: '{doc_name}'")

    # 0. Ensure tables exist in Postgres
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 1. Upload to MinIO Object Storage
    logger.info(f"1. Uploading '{doc_name}' to MinIO object storage...")
    upload_success = minio_service.upload_file(file_path=file_path, object_name=doc_name)
    if upload_success:
        logger.info("MinIO upload completed successfully.")
    else:
        logger.warning("MinIO upload returned false. Proceeding with database vector chunking.")

    # 2. Extract PDF Chunks
    logger.info(f"2. Extracting text chunks from '{doc_name}' using pypdf...")
    chunks = extract_pdf_chunks(file_path)
    logger.info(f"Extracted {len(chunks)} text chunks.")

    # 3. Store in PostgreSQL document_chunks table
    logger.info("3. Storing chunks in PostgreSQL document_chunks table...")
    async with AsyncSessionLocal() as session:
        for idx, chunk_content in enumerate(chunks):
            db_chunk = DocumentChunk(
                document_name=doc_name,
                chunk_index=idx + 1,
                content=chunk_content,
                metadata_json={"source": doc_name, "page_chunk": idx + 1}
            )
            session.add(db_chunk)
        await session.commit()

    logger.info(f"Successfully ingested {len(chunks)} document chunks into PostgreSQL!")
    return True


if __name__ == "__main__":
    doc_path = os.path.join(os.getcwd(), "manual-do-colaborador.pdf")
    if not os.path.exists(doc_path):
        doc_path = sys.argv[1] if len(sys.argv) > 1 else "manual-do-colaborador.pdf"

    asyncio.run(ingest_document(doc_path))
