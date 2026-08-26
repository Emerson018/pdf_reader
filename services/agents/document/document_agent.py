from typing import List, Optional, Dict, Any
from services.agents.base.base_agent import BaseAgent, AgentResponse
from services.models.base import ModelProvider, LLMMessage
from services.tools.database.document_search_tool import DocumentSearchTool
from services.core.rules_loader import load_system_rules
from services.cache.redis_cache_service import redis_cache_service
from services.orchestrator.routing.query_rewriter import rewrite_query_with_history

DOCUMENT_AGENT_BASE_PROMPT = """Você é o DocumentAgent, assistente especialista em consultar e responder dúvidas sobre todos os documentos, certificados, manuais e arquivos armazenados no banco de dados vetorial RAG da aplicação.

Instruções Adicionais de Formatação:
1. Avalie os documentos recuperados no contexto RAG. Se houver certificados, diplomas, certificados de conclusão de curso, manuais ou imagens nos trechos fornecidos, detalhe exatamente o conteúdo de CADA documento (nome do arquivo, participante, instituição, datas ou termos principais).
"""


class DocumentAgent(BaseAgent):
    """Specialized AI Agent for consulting documents, certificates, and manuals with strict RAG grounding,
    Redis Semantic Caching (<5ms), and Conversational Query Rewriting.
    """

    def __init__(self, model_provider: ModelProvider, **kwargs):
        doc_tool = DocumentSearchTool()
        super().__init__(
            name="DocumentAgent",
            description="Especialista em consulta RAG ao banco de dados vetorial com Cache Semântico Redis e Reescrita Conversacional.",
            model_provider=model_provider,
            tools=[doc_tool],
            system_prompt=DOCUMENT_AGENT_BASE_PROMPT
        )

    async def run(self, user_message: str, history: Optional[List[LLMMessage]] = None, **kwargs) -> AgentResponse:
        doc_tool = self.tools.get("document_search_tool")
        
        # 1. Conversational Query Rewriting (Contextual Query Expansion)
        search_query = await rewrite_query_with_history(
            user_message=user_message,
            history=history,
            model_provider=self.provider
        )

        # 2. Generate Query Embedding for Vector Search and Cache Lookup
        query_embedding: Optional[List[float]] = None
        try:
            query_embedding = await self.provider.generate_embedding(search_query)
        except Exception:
            pass

        # 3. Redis Semantic Cache Lookup (<5ms)
        if query_embedding:
            cached_res = await redis_cache_service.get_semantic_cache(
                query_embedding=query_embedding,
                similarity_threshold=0.86
            )
            if cached_res:
                return AgentResponse(
                    agent_name=self.name,
                    content=cached_res["response"],
                    metadata={
                        "agent": self.name,
                        "cache_hit": True,
                        "cache_similarity": cached_res["similarity"],
                        "cache_latency_ms": cached_res["cache_latency_ms"],
                        "matched_query": cached_res["matched_query"],
                        "search_query": search_query,
                        "rag_source": "redis_semantic_cache"
                    }
                )

        # 4. Cache Miss: Execute hybrid vector + FTS search with candidate limit 8
        search_res = await doc_tool.execute(query=search_query, limit=8) if doc_tool else None

        passages_text = ""
        found_count = 0
        search_metadata: Dict[str, Any] = {}

        if search_res and search_res.success and search_res.data.get("passages"):
            passages = search_res.data["passages"]
            found_count = len(passages)
            search_metadata = search_res.data.get("filters_applied", {})

            passages_text = "\n\n--- Trechos e Análises Visuais do Banco de Dados Vetorial (PostgreSQL HNSW + RRF) ---\n"
            for idx, p in enumerate(passages, 1):
                page_info = f" | Página: {p['page']}" if p.get('page') else ""
                img_info = f" | Imagem: {p['image_ref']}" if p.get('image_ref') else (" | Elemento Visual Detectado" if p.get('has_image') else "")
                score_info = f" | RRF Score: {p['rrf_score']}" if p.get('rrf_score') is not None else ""

                passages_text += f"[{idx}] Documento: '{p['document']}'{page_info}{img_info}{score_info}\nConteúdo:\n{p['content']}\n\n"
        else:
            passages_text = "\n\n--- Nenhuma passagem ou informação foi encontrada no banco de dados vetorial para a consulta fornecida. ---\n"

        # Load dynamic strict rules from system_rules.txt
        strict_rules = load_system_rules()
        system_prompt_combined = f"{strict_rules}\n\n{self.system_prompt}"

        prompt_with_context = (
            f"Pergunta do Usuário: {search_query}\n"
            f"{passages_text}\n"
            "INSTRUÇÃO OBRIGATÓRIA: Siga rigorosamente as REGRAS DO SISTEMA contidas no prompt do sistema. "
            "Se trechos foram encontrados acima, responda de forma Objetiva, Direta e Sintética unicamente com base neles. "
            "Se NENHUM trecho relevante for encontrado ou se a informação não constar no banco de dados, responda estritamente que não há nenhum dado no banco de dados referente à pergunta."
        )

        messages = [LLMMessage(role="system", content=system_prompt_combined)]
        if history:
            messages.extend(history)
        messages.append(LLMMessage(role="user", content=prompt_with_context))

        llm_response = await self.provider.generate(messages=messages)
        content = llm_response.content.strip()

        metadata = {
            "agent": self.name,
            "model": llm_response.model,
            "cache_hit": False,
            "search_query": search_query,
            "document_chunks_found": found_count,
            "search_type": "hybrid_vector_rrf",
            "search_filters": search_metadata,
            "rag_source": "postgresql_document_chunks"
        }

        # 5. Persist Response in Redis Semantic Cache (TTL: 24 hours)
        if query_embedding and content:
            await redis_cache_service.set_semantic_cache(
                query_text=search_query,
                query_embedding=query_embedding,
                response_text=content,
                metadata=metadata,
                ttl_seconds=86400
            )

        return AgentResponse(
            agent_name=self.name,
            content=content,
            metadata=metadata
        )
