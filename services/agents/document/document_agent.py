from typing import List, Optional
from services.agents.base.base_agent import BaseAgent, AgentResponse
from services.models.base import ModelProvider, LLMMessage
from services.tools.database.document_search_tool import DocumentSearchTool

DOCUMENT_AGENT_SYSTEM_PROMPT = """Você é o DocumentAgent, assistente especialista exclusivo na consulta do Manual do Colaborador e documentos internos da empresa.

Regras Estritas de Resposta:
1. Responda ESTRITAMENTE com base nos trechos e análises visuais de imagens/diagramas fornecidos no contexto.
2. É PROIBIDO buscar informações na web ou usar conhecimentos externos fora dos trechos recuperados do documento.
3. Analise cuidadosamente a seção "Análise de Elementos Visuais (Diagramas/Organogramas/Imagens)" dos trechos, pois muitas informações cruciais (como infográficos, 5 momentos da higienização, tabelas e fluxogramas) estão descritas nessa seção.
4. Se a informação não constar nos trechos fornecidos, informe educadamente que a informação não consta no documento disponibilizado.
"""


class DocumentAgent(BaseAgent):
    """Specialized AI Agent for consulting employee manual and internal company documents with strict grounding."""

    def __init__(self, model_provider: ModelProvider, **kwargs):
        doc_tool = DocumentSearchTool()
        super().__init__(
            name="DocumentAgent",
            description="Especialista em consulta ao Manual do Colaborador e documentos internos da empresa.",
            model_provider=model_provider,
            tools=[doc_tool],
            system_prompt=DOCUMENT_AGENT_SYSTEM_PROMPT
        )

    async def run(self, user_message: str, history: Optional[List[LLMMessage]] = None) -> AgentResponse:
        doc_tool = self.tools.get("document_search_tool")
        search_res = await doc_tool.execute(query=user_message) if doc_tool else None

        passages_text = ""
        if search_res and search_res.success and search_res.data.get("passages"):
            passages = search_res.data["passages"]
            passages_text = "\n\n--- Trechos e Análises Visuais do Manual do Colaborador ---\n"
            for idx, p in enumerate(passages, 1):
                page_info = f" (Página {p['page']})" if p.get('page') else ""
                passages_text += f"[{idx}] (Documento: {p['document']}{page_info}):\n{p['content']}\n\n"

        prompt_with_context = (
            f"Pergunta do Usuário: {user_message}\n"
            f"{passages_text}\n"
            "Responda à pergunta do usuário utilizando APENAS os trechos e análises de elementos visuais acima."
        )

        messages = [LLMMessage(role="system", content=self.system_prompt)]
        if history:
            messages.extend(history)
        messages.append(LLMMessage(role="user", content=prompt_with_context))

        llm_response = await self.provider.generate(messages=messages)
        content = f"[Document Agent - Manual do Colaborador]:\n{llm_response.content}"

        return AgentResponse(
            agent_name=self.name,
            content=content,
            metadata={
                "agent": self.name,
                "model": llm_response.model,
                "document_chunks_found": len(search_res.data.get("passages", [])) if search_res else 0
            }
        )
