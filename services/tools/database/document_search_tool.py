import logging
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import select, func, or_, text
from apps.api.app.db.session import AsyncSessionLocal
from apps.api.app.models.models import DocumentChunk
from services.tools.base.base_tool import BaseTool
from services.models.factory import ModelFactory

logger = logging.getLogger(__name__)

PORTUGUESE_STOPWORDS = {
    "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas", "para", "por", "com",
    "sem", "sob", "sobre", "atras", "acordo", "segundo", "conforme", "quais", "quaisquer",
    "qual", "como", "onde", "quando", "quem", "que", "estao", "estava", "estavam", "sao",
    "ser", "seria", "neste", "nesta", "nestes", "nestas", "deste", "desta", "aquilo", "esse",
    "essa", "esses", "essas", "este", "esta", "estos", "estas", "documento", "manual",
    "representadas", "representado", "representa", "mostra", "mostram", "exibe", "existe",
    "existem", "faz", "fazer", "tem", "têm", "tinha", "tinham", "os", "as", "um", "uma",
    "uns", "umas", "ao", "aos", "pelo", "pela", "entre", "ate", "após", "apos"
}


def extract_search_keywords(user_query: str) -> List[str]:
    """Extracts meaningful keywords from conversational user queries, preserving numbers and key nouns."""
    tokens = re.findall(r'\b\w+\b', user_query.lower())
    keywords = []
    for t in tokens:
        if t.isdigit():
            keywords.append(t)
        elif len(t) >= 3 and t not in PORTUGUESE_STOPWORDS:
            keywords.append(t)

    return keywords if keywords else [t for t in tokens if len(t) >= 2]


class DocumentSearchInput(BaseModel):
    query: str = Field(..., description="Query terms or question to search in ingested documents")
    limit: int = Field(4, description="Maximum number of relevant document passages to return")


class DocumentSearchTool(BaseTool):
    name: str = "document_search_tool"
    description: str = "Searches ingested company documents using Hybrid Search (pgvector HNSW Cosine Similarity + PostgreSQL Full-Text RRF Fusion)."
    args_schema = DocumentSearchInput

    async def _run(self, query: str, limit: int = 4) -> Dict[str, Any]:
        logger.info(f"DocumentSearchTool performing Hybrid Search (Vector + Full-Text RRF) for: '{query}'")

        try:
            keywords = extract_search_keywords(query)
            clean_keywords_str = " ".join(keywords)

            # Generate query embedding via GeminiProvider
            provider = ModelFactory.get_provider("gemini", model_name="gemini-3.6-flash")
            query_embedding = await provider.generate_embedding(query)

            async with AsyncSessionLocal() as session:
                chunk_ranks: Dict[str, Dict[str, Any]] = {}

                # 1. Semantic Vector Search (Cosine Similarity)
                if query_embedding:
                    stmt_vector = (
                        select(DocumentChunk)
                        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
                        .limit(limit * 2)
                    )
                    res_vector = await session.execute(stmt_vector)
                    semantic_chunks = res_vector.scalars().all()

                    for rank_idx, chunk in enumerate(semantic_chunks, 1):
                        cid = str(chunk.id)
                        chunk_ranks[cid] = {
                            "chunk": chunk,
                            "semantic_rank": rank_idx,
                            "keyword_rank": 999
                        }

                # 2. Full-Text Search (Sparse Keyword Matching)
                if clean_keywords_str.strip():
                    ts_vector = func.to_tsvector('portuguese', DocumentChunk.content)
                    ts_query = func.websearch_to_tsquery('portuguese', clean_keywords_str)
                    rank = func.ts_rank(ts_vector, ts_query)

                    stmt_kw = (
                        select(DocumentChunk)
                        .where(ts_vector.op("@@")(ts_query))
                        .order_by(rank.desc())
                        .limit(limit * 2)
                    )
                    res_kw = await session.execute(stmt_kw)
                    keyword_chunks = res_kw.scalars().all()

                    for rank_idx, chunk in enumerate(keyword_chunks, 1):
                        cid = str(chunk.id)
                        if cid in chunk_ranks:
                            chunk_ranks[cid]["keyword_rank"] = rank_idx
                        else:
                            chunk_ranks[cid] = {
                                "chunk": chunk,
                                "semantic_rank": 999,
                                "keyword_rank": rank_idx
                            }

                # 3. Reciprocal Rank Fusion (RRF) Calculation
                # Formula: RRF_score = alpha / (60 + semantic_rank) + (1 - alpha) / (60 + keyword_rank)
                alpha = 0.6
                scored_chunks = []
                for cid, item in chunk_ranks.items():
                    sem_rank = item["semantic_rank"]
                    kw_rank = item["keyword_rank"]
                    rrf_score = (alpha / (60.0 + sem_rank)) + ((1.0 - alpha) / (60.0 + kw_rank))
                    scored_chunks.append((rrf_score, item["chunk"]))

                scored_chunks.sort(key=lambda x: x[0], reverse=True)
                top_chunks = [chunk for _, chunk in scored_chunks[:limit]]

                # Fallback to standard query if top_chunks empty
                if not top_chunks:
                    stmt_top = select(DocumentChunk).limit(limit)
                    res_top = await session.execute(stmt_top)
                    top_chunks = res_top.scalars().all()

                results = [
                    {
                        "document": chunk.document_name,
                        "chunk_index": chunk.chunk_index,
                        "content": chunk.content,
                        "page": chunk.metadata_json.get("page") if chunk.metadata_json else None
                    }
                    for chunk in top_chunks
                ]

                return {
                    "query": query,
                    "count": len(results),
                    "search_type": "hybrid_vector_rrf",
                    "passages": results
                }
        except Exception as e:
            logger.error(f"Error in DocumentSearchTool Hybrid Search: {e}")
            return {
                "query": query,
                "count": 0,
                "passages": [],
                "error": str(e)
            }
