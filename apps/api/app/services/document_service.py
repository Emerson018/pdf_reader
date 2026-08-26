import os
import time
import uuid
import asyncio
import logging
try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        import pypdf as pymupdf
from typing import Dict, Any, List, Optional
from sqlalchemy import select, delete
from apps.api.app.core.config import Settings
from apps.api.app.db.session import AsyncSessionLocal, engine, Base
from apps.api.app.models.models import DocumentChunk
from services.storage.minio_service import minio_service
from services.models.factory import ModelFactory

logger = logging.getLogger("document_service")

# In-memory progress tracking for upload/embedding tasks
INGESTION_TASKS: Dict[str, Dict[str, Any]] = {}


class DocumentService:
    """Service to handle PDF file ingestion, vector embedding generation, and status tracking."""

    @staticmethod
    def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
        return INGESTION_TASKS.get(task_id)

    @staticmethod
    def list_ingested_documents(chunks: List[DocumentChunk]) -> List[Dict[str, Any]]:
        doc_map = {}
        for c in chunks:
            if c.document_name not in doc_map:
                doc_map[c.document_name] = {
                    "document_name": c.document_name,
                    "total_chunks": 0,
                    "created_at": c.created_at.isoformat() if c.created_at else None
                }
            doc_map[c.document_name]["total_chunks"] += 1
        return list(doc_map.values())

    @staticmethod
    async def start_pdf_ingestion(file_bytes: bytes, filename: str, process_images: bool = True) -> Dict[str, Any]:
        task_id = str(uuid.uuid4())
        
        # Save temp file
        temp_dir = os.path.join(os.getcwd(), "temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        temp_pdf_path = os.path.join(temp_dir, f"{task_id}_{filename}")
        
        with open(temp_pdf_path, "wb") as f:
            f.write(file_bytes)

        # Initialize tracking info
        INGESTION_TASKS[task_id] = {
            "task_id": task_id,
            "filename": filename,
            "process_images": process_images,
            "status": "processing",  # 'processing', 'completed', 'failed'
            "total_pages": 0,
            "current_page": 0,
            "progress_percent": 0.0,
            "start_time": time.time(),
            "elapsed_seconds": 0.0,
            "estimated_remaining_seconds": 0.0,
            "message": "Iniciando leitura e processamento do PDF..."
        }

        # Spawn background processing task
        asyncio.create_task(
            DocumentService._run_ingestion_pipeline(task_id, temp_pdf_path, filename, process_images=process_images)
        )

        return {
            "task_id": task_id,
            "filename": filename,
            "process_images": process_images,
            "message": "Upload iniciado e processamento em segundo plano ativado."
        }

    @staticmethod
    async def _run_ingestion_pipeline(task_id: str, temp_pdf_path: str, filename: str, process_images: bool = True):
        task_info = INGESTION_TASKS[task_id]
        start_time = time.time()

        try:
            # Ensure DB schema is ready
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            # Upload original PDF to MinIO object storage
            task_info["message"] = "Enviando arquivo PDF original para o MinIO..."
            await minio_service.upload_file_async(temp_pdf_path, object_name=filename)

            # Open PDF with PyMuPDF
            doc = pymupdf.open(temp_pdf_path)
            total_pages = len(doc)
            task_info["total_pages"] = total_pages

            if total_pages == 0:
                task_info["status"] = "failed"
                task_info["message"] = "O arquivo PDF não possui páginas legíveis."
                return

            current_settings = Settings()
            gemini_provider = ModelFactory.get_provider(
                provider_name="gemini",
                model_name="gemini-3.6-flash",
                api_key=current_settings.GEMINI_API_KEY
            )

            chunks_to_insert = []

            for page_idx in range(total_pages):
                page_num = page_idx + 1
                page = doc[page_idx]
                text = page.get_text() or ""

                image_object_name = None
                has_images = False
                visual_description = ""

                # Process images and execute Gemini Vision ONLY if process_images option is enabled
                if process_images:
                    images = page.get_images()
                    has_images = len(images) > 0

                    # Render pixmap for visual analysis
                    pix = page.get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("png")
                    image_object_name = f"images/{filename}/page_{page_num}.png"

                    # Upload page image to MinIO
                    temp_img_path = os.path.join(os.path.dirname(temp_pdf_path), f"temp_{task_id}_p{page_num}.png")
                    pix.save(temp_img_path)
                    await minio_service.upload_file_async(temp_img_path, object_name=image_object_name)
                    if os.path.exists(temp_img_path):
                        os.remove(temp_img_path)

                    # Call Gemini Vision if visual elements exist
                    if has_images or len(text.strip()) < 300 or page_idx in [0, 2, 5, 8, 24, 25]:
                        prompt = (
                            f"Analise detalhadamente a imagem da Página {page_num} do documento {filename}. "
                            "TRANSCREVA INTEGRALMENTE E DESCREVA DE FORMA EXAUSTIVA todos os textos visuais, diagramas, "
                            "fluxogramas, ícones, números, listas numeradas, passos, tabelas e organogramas contidos na imagem. "
                            "Responda em português completo."
                        )
                        try:
                            visual_description = await gemini_provider.generate_vision(
                                prompt=prompt,
                                image_bytes=img_bytes
                            )
                        except Exception as e:
                            logger.error(f"Vision analysis failed for page {page_num}: {e}")

                full_chunk_content = f"--- Página {page_num} do Documento {filename} ---\n\n"
                if text.strip():
                    full_chunk_content += f"**Conteúdo de Texto:**\n{text.strip()}\n\n"
                if visual_description.strip():
                    full_chunk_content += f"**Análise de Elementos Visuais:**\n{visual_description.strip()}\n\n"

                # Generate 768-dim vector embedding
                vector_emb = await gemini_provider.generate_embedding(full_chunk_content)

                chunks_to_insert.append(
                    DocumentChunk(
                        document_name=filename,
                        chunk_index=page_num,
                        content=full_chunk_content,
                        embedding=vector_emb,
                        metadata_json={
                            "page": page_num,
                            "has_image": has_images,
                            "process_images": process_images,
                            "image_object_name": image_object_name
                        }
                    )
                )

                # Update real-time progress & ETA
                elapsed = time.time() - start_time
                avg_time_per_page = elapsed / page_num
                remaining_pages = total_pages - page_num
                eta = remaining_pages * avg_time_per_page
                progress_pct = round((page_num / total_pages) * 100, 1)

                mode_label = "Texto + Visão AI" if process_images else "Apenas Texto (Modo Rápido)"
                task_info["current_page"] = page_num
                task_info["progress_percent"] = progress_pct
                task_info["elapsed_seconds"] = round(elapsed, 1)
                task_info["estimated_remaining_seconds"] = round(eta, 1)
                task_info["message"] = f"[{mode_label}] Gerando embeddings no PostgreSQL para Página {page_num}/{total_pages}..."

            # Persist to PostgreSQL
            task_info["message"] = "Salvando vetores e chunks no PostgreSQL..."
            async with AsyncSessionLocal() as session:
                await session.execute(delete(DocumentChunk).where(DocumentChunk.document_name == filename))
                for chunk in chunks_to_insert:
                    session.add(chunk)
                await session.commit()

            total_elapsed = round(time.time() - start_time, 1)
            task_info["status"] = "completed"
            task_info["progress_percent"] = 100.0
            task_info["current_page"] = total_pages
            task_info["elapsed_seconds"] = total_elapsed
            task_info["estimated_remaining_seconds"] = 0.0
            mode_desc = "Multimodal (Texto + Visão)" if process_images else "Apenas Texto"
            task_info["message"] = f"Processamento de {filename} ({mode_desc}) concluído com sucesso em {total_elapsed}s!"

        except Exception as e:
            logger.exception(f"Error ingesting PDF {filename}")
            task_info["status"] = "failed"
            task_info["message"] = f"Erro no embeeding do PDF: {str(e)}"
        finally:
            if os.path.exists(temp_pdf_path):
                try:
                    os.remove(temp_pdf_path)
                except Exception:
                    pass


document_service = DocumentService()
