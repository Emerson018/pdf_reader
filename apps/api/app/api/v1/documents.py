import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Query
from sqlalchemy import select
from apps.api.app.db.session import AsyncSessionLocal
from apps.api.app.models.models import DocumentChunk
from apps.api.app.services.document_service import document_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/documents/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_document_endpoint(
    file: UploadFile = File(...),
    process_images: bool = Form(True)
):
    """Uploads a PDF document and starts asynchronous embedding ingestion with optional image vision analysis."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas arquivos no formato PDF são suportados."
        )

    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O arquivo PDF enviado está vazio."
            )

        result = await document_service.start_pdf_ingestion(content, file.filename, process_images=process_images)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error starting document upload ingestion")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao iniciar o upload do documento: {str(e)}"
        )


@router.get("/documents/upload/status/{task_id}")
async def get_upload_status_endpoint(task_id: str):
    """Retrieves real-time progress %, active page, elapsed time, and ETA remaining time for an ingestion task."""
    task_status = document_service.get_task_status(task_id)
    if not task_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa de upload não encontrada."
        )
    return task_status


@router.get("/documents")
async def list_documents_endpoint():
    """Lists all PDF documents currently stored and embedded in PostgreSQL."""
    try:
        async with AsyncSessionLocal() as session:
            stmt = select(DocumentChunk)
            res = await session.execute(stmt)
            chunks = res.scalars().all()
            return document_service.list_ingested_documents(chunks)
    except Exception as e:
        logger.exception("Error listing documents")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao listar documentos: {str(e)}"
        )


@router.get("/documents/chunks")
async def list_document_chunks_endpoint(
    document_name: Optional[str] = Query(None, description="Optional document name filter"),
    limit: int = Query(50, ge=1, le=200)
):
    """Retrieves chunks, text, vector dimensions, and visual metadata stored in PostgreSQL document_chunks table."""
    try:
        async with AsyncSessionLocal() as session:
            stmt = select(DocumentChunk)
            if document_name:
                stmt = stmt.where(DocumentChunk.document_name == document_name)
            stmt = stmt.order_by(DocumentChunk.chunk_index.asc()).limit(limit)
            
            res = await session.execute(stmt)
            chunks = res.scalars().all()
            
            result = []
            for c in chunks:
                emb_dim = len(c.embedding) if c.embedding is not None else 0
                result.append({
                    "id": c.id,
                    "document_name": c.document_name,
                    "chunk_index": c.chunk_index,
                    "content_preview": c.content[:300] + "..." if len(c.content) > 300 else c.content,
                    "full_content": c.content,
                    "embedding_dim": emb_dim,
                    "metadata": c.metadata_json or {},
                    "created_at": c.created_at.isoformat() if c.created_at else None
                })
            return result
    except Exception as e:
        logger.exception("Error fetching document chunks")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao consultar chunks do banco de dados: {str(e)}"
        )
