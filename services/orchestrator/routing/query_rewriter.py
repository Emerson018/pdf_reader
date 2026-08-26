import logging
from typing import List, Optional
from services.models.base import ModelProvider, LLMMessage

logger = logging.getLogger(__name__)

REWRITE_PROMPT = """Você é um especialista em reformulação de perguntas para sistemas RAG.
Sua única tarefa é analisar o histórico recente da conversa e a última pergunta do usuário, e gerar uma frase REFORMULADA, AUTÔNOMA e COMPLETA para ser pesquisada no banco de dados.

Instruções:
1. Substitua pronomes ambíguos ou referências relativas (como "ele", "dele", "dela", "isso", "aquele documento", "o certificado", "a regra") pelos nomes reais das entidades e documentos mencionados no histórico da conversa.
2. Se a pergunta já for autônoma, clara e completa por si só, retorne-a EXATAMENTE sem alterações.
3. Responda APENAS com a frase da pergunta reformulada. Não adicione introduções, explicações, aspas ou saudações.
"""


async def rewrite_query_with_history(
    user_message: str,
    history: Optional[List[LLMMessage]],
    model_provider: ModelProvider
) -> str:
    """Uses LLM to reformulate a follow-up query into a standalone, self-contained search query using chat history."""
    if not history or len(history) < 2:
        return user_message.strip()

    try:
        # Build clean string representation of recent history (max 6 messages)
        recent_history = history[-6:]
        history_str = ""
        for msg in recent_history:
            role_label = "Usuário" if msg.role == "user" else "Assistente"
            history_str += f"[{role_label}]: {msg.content[:200]}\n"

        prompt_input = (
            f"Histórico Recente da Conversa:\n{history_str}\n"
            f"Última Pergunta do Usuário: {user_message}\n\n"
            "Pergunta Reformulada para Busca RAG:"
        )

        messages = [
            LLMMessage(role="system", content=REWRITE_PROMPT),
            LLMMessage(role="user", content=prompt_input)
        ]

        llm_res = await model_provider.generate(messages=messages)
        rewritten = llm_res.content.strip().strip('"').strip("'")

        if rewritten and len(rewritten) > 3:
            logger.info(f"Query Rewriter: '{user_message}' -> '{rewritten}'")
            return rewritten
    except Exception as e:
        logger.warning(f"Failed to rewrite query with history: {e}")

    return user_message.strip()
