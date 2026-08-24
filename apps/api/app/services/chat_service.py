import logging
import uuid
from typing import Dict, Any
from sqlalchemy import select
from apps.api.app.core.config import Settings
from apps.api.app.db.session import AsyncSessionLocal
from apps.api.app.models.models import Conversation, Message, AgentRun
from services.orchestrator.orchestrator_service import OrchestratorService

logger = logging.getLogger(__name__)


class ChatService:
    """Service layer connecting HTTP endpoints to Orchestrator and PostgreSQL persistence."""

    def get_orchestrator(self, model_override: str = None) -> OrchestratorService:
        current_settings = Settings()
        provider = current_settings.DEFAULT_PROVIDER
        model = model_override or current_settings.DEFAULT_MODEL

        # Get corresponding API key based on configured provider
        if provider.lower() in ["gemini", "google"]:
            api_key = current_settings.GEMINI_API_KEY
        else:
            api_key = current_settings.OPENAI_API_KEY

        return OrchestratorService(
            provider_name=provider,
            model_name=model,
            api_key=api_key
        )

    async def process_message(
        self,
        message: str,
        conversation_id: str = None,
        user_id: str = None,
        model_override: str = None
    ) -> Dict[str, Any]:
        conv_uuid = None
        if conversation_id:
            try:
                conv_uuid = uuid.UUID(conversation_id)
            except ValueError:
                conv_uuid = uuid.uuid4()
        else:
            conv_uuid = uuid.uuid4()

        conv_str = str(conv_uuid)
        logger.info(f"Processing message for conversation {conv_str}: '{message[:40]}...'")

        # 1. Execute via Orchestrator (dynamically loaded provider)
        orchestrator = self.get_orchestrator(model_override=model_override)
        orchestration_result = await orchestrator.run_chat(message)
        response_text = orchestration_result["response"]
        agent_name = orchestration_result.get("agent", "DirectLLM")
        metadata = orchestration_result.get("metadata", {})

        # 2. Persist in PostgreSQL (non-blocking exception handling)
        try:
            async with AsyncSessionLocal() as session:
                # Ensure conversation exists
                stmt = select(Conversation).where(Conversation.id == conv_uuid)
                result = await session.execute(stmt)
                conv = result.scalar_one_or_none()

                if not conv:
                    conv = Conversation(
                        id=conv_uuid,
                        title=message[:50]
                    )
                    session.add(conv)
                    await session.flush()

                # User message
                user_msg_db = Message(
                    conversation_id=conv_uuid,
                    role="user",
                    content=message
                )
                session.add(user_msg_db)

                # Assistant message
                assistant_msg_db = Message(
                    conversation_id=conv_uuid,
                    role="assistant",
                    content=response_text,
                    metadata_json=metadata
                )
                session.add(assistant_msg_db)

                # Agent run record
                run_record = AgentRun(
                    conversation_id=conv_uuid,
                    agent_name=agent_name,
                    status="completed",
                    input={"message": message},
                    output={"response": response_text},
                    metadata_json=metadata
                )
                session.add(run_record)

                await session.commit()
        except Exception as e:
            logger.warning(f"Database persistence skipped/failed: {e}")

        return {
            "response": response_text,
            "conversation_id": conv_str,
            "metadata": {
                "agent": agent_name,
                **metadata
            }
        }


chat_service = ChatService()
