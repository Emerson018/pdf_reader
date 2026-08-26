import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field
from apps.api.app.schemas.chat import ChatRequest, ChatResponse
from apps.api.app.services.chat_service import chat_service
from apps.api.app.services.export_service import export_service

logger = logging.getLogger(__name__)
router = APIRouter()


class ExportReportRequest(BaseModel):
    content: str = Field(..., description="The assistant response text content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata dictionary associated with the RAG query")
    format: str = Field("markdown", description="Report format: 'markdown' or 'pdf'")


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(request: ChatRequest):
    """Initial chat endpoint POST /api/v1/chat."""
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty."
        )

    try:
        result = await chat_service.process_message(
            message=request.message,
            conversation_id=request.conversation_id,
            user_id=request.user_id,
            model_override=request.model
        )
        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            metadata=result.get("metadata", {})
        )
    except Exception as e:
        logger.exception("Error processing chat request")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}"
        )


@router.post("/chat/export", status_code=status.HTTP_200_OK)
async def export_chat_report_endpoint(request: ExportReportRequest):
    """Endpoint POST /api/v1/chat/export to generate downloadable Markdown or PDF RAG reports."""
    if not request.content or not request.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report content cannot be empty."
        )

    try:
        file_bytes, filename, media_type = export_service.generate_report(
            content=request.content,
            metadata=request.metadata,
            format_type=request.format
        )
        return Response(
            content=file_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\""
            }
        )
    except Exception as e:
        logger.exception("Error exporting chat report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao exportar relatório: {str(e)}"
        )
