import logging
from fastapi import APIRouter, HTTPException, status
from apps.api.app.schemas.chat import ChatRequest, ChatResponse
from apps.api.app.services.chat_service import chat_service

logger = logging.getLogger(__name__)
router = APIRouter()


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
