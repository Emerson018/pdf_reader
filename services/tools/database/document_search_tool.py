import logging
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import select, func, or_
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
    document_name: Optional[str] = Field(None, description="Optional document name filter to scope retrieval")
    page: Optional[int] = Field(None, description="Optional page number filter")
    has_image: Optional[bool] = Field(None, description="Optional filter for passages containing visual elements or images")


class DocumentSearchTool(BaseTool):
    name: str = "document_search_tool"
    description: str = "Searches ingested company documents using Hybrid Search (pgvector HNSW Cosine Similarity + PostgreSQL Full-Text RRF Fusion) with metadata filtering."
    args_schema = DocumentSearchInput

    async def _run(
        self,
        query: str,
        limit: int = 4,
        document_name: Optional[str] = None,
        page: Optional[int] = None,
        has_image: Optional[bool] = None
    ) -> Dict[str, Any]:
        logger.info(
            f"DocumentSearchTool performing Hybrid Search (Vector + Full-Text RRF) for: '{query}' "
            f"[limit={limit}, doc={document_name}, page={page}, has_image={has_image}]"
        )

        try:
            keywords = extract_search_keywords(query)
            clean_keywords_str = " ".join(keywords)

            # Generate query embedding via GeminiProvider
            provider = ModelFactory.get_provider("gemini", model_name="gemini-3.6-flash")
            query_embedding = None
            try:
                query_embedding = await provider.generate_embedding(query)
            except Exception as emb_err:
                logger.warning(f"Failed to generate query embedding: {emb_err}")

            async with AsyncSessionLocal() as session:
                # Build metadata scope SQL filters
                filters = []
                if document_name:
                    filters.append(DocumentChunk.document_name.ilike(f"%{document_name}%"))
                if page is not None:
                    filters.append(func.jsonb_extract_path_text(DocumentChunk.metadata_json, 'page') == str(page))
                if has_image is not None:
                    filters.append(func.jsonb_extract_path_text(DocumentChunk.metadata_json, 'has_image') == str(has_image).lower())

                chunk_ranks: Dict[str, Dict[str, Any]] = {}
                candidate_limit = max(50, limit * 5)

                # 1. Semantic Vector Search (Cosine Similarity) with candidate pool
                if query_embedding:
                    stmt_vector = select(DocumentChunk)
                    if filters:
                        stmt_vector = stmt_vector.where(*filters)
                    stmt_vector = (
                        stmt_vector
                        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
                        .limit(candidate_limit)
                    )
                    res_vector = await session.execute(stmt_vector)
                    semantic_chunks = res_vector.scalars().all()

                    for rank_idx, chunk in enumerate(semantic_chunks, 1):
                        cid = str(chunk.id)
                        chunk_ranks[cid] = {
                            "chunk": chunk,
                            "semantic_rank": rank_idx,
                            "keyword_rank": candidate_limit
                        }

                # 2. Full-Text Search (Sparse Keyword & Title Matching using safe plainto_tsquery)
                if keywords:
                    ts_vector = func.to_tsvector('portuguese', DocumentChunk.content)
                    ts_query = func.plainto_tsquery('portuguese', clean_keywords_str)
                    rank = func.ts_rank(ts_vector, ts_query)

                    kw_clauses = [ts_vector.op("@@")(ts_query)]
                    for k in keywords:
                        kw_clauses.append(DocumentChunk.document_name.ilike(f"%{k}%"))
                        if len(k) >= 3:
                            kw_clauses.append(DocumentChunk.content.ilike(f"%{k}%"))

                    stmt_kw = select(DocumentChunk).where(or_(*kw_clauses))
                    if filters:
                        stmt_kw = stmt_kw.where(*filters)

                    stmt_kw = stmt_kw.order_by(rank.desc()).limit(candidate_limit)
                    res_kw = await session.execute(stmt_kw)
                    keyword_chunks = res_kw.scalars().all()

                    for rank_idx, chunk in enumerate(keyword_chunks, 1):
                        cid = str(chunk.id)
                        if cid in chunk_ranks:
                            chunk_ranks[cid]["keyword_rank"] = rank_idx
                        else:
                            chunk_ranks[cid] = {
                                "chunk": chunk,
                                "semantic_rank": candidate_limit,
                                "keyword_rank": rank_idx
                            }

                # 3. Reciprocal Rank Fusion (RRF) Calculation with Document Title Boost
                alpha = 0.5
                scored_chunks = []
                for cid, item in chunk_ranks.items():
                    sem_rank = item["semantic_rank"]
                    kw_rank = item["keyword_rank"]
                    chunk = item["chunk"]
                    doc_name = chunk.document_name

                    rrf_score = (alpha / (60.0 + sem_rank)) + ((1.0 - alpha) / (60.0 + kw_rank))

                    # Title match boost
                    if keywords and any(k.lower() in doc_name.lower() for k in keywords):
                        rrf_score += 0.05

                    scored_chunks.append((rrf_score, chunk))

                scored_chunks.sort(key=lambda x: x[0], reverse=True)

                # 4. Multi-Document Diversity: Balanced candidate selection strictly respecting limit
                top_chunks: List[tuple[float, DocumentChunk]] = []
                seen_docs = set()

                # Round 1: Priority round — 1 top passage per distinct document up to requested limit
                for score, chunk in scored_chunks:
                    if len(top_chunks) >= limit:
                        break
                    if chunk.document_name not in seen_docs:
                        top_chunks.append((score, chunk))
                        seen_docs.add(chunk.document_name)

                # Round 2: Cap-controlled fill round — fill remaining slots with highest scoring passages
                doc_counts = {doc: 1 for doc in seen_docs}
                for score, chunk in scored_chunks:
                    if len(top_chunks) >= limit:
                        break
                    if any(c[1].id == chunk.id for c in top_chunks):
                        continue

                    count = doc_counts.get(chunk.document_name, 0)
                    if count < 3 or len(seen_docs) == 1:
                        top_chunks.append((score, chunk))
                        doc_counts[chunk.document_name] = count + 1

                # Round 3: Fallback fill round if still under limit
                if len(top_chunks) < limit:
                    for score, chunk in scored_chunks:
                        if len(top_chunks) >= limit:
                            break
                        if not any(c[1].id == chunk.id for c in top_chunks):
                            top_chunks.append((score, chunk))

                # Fallback to standard query if top_chunks is empty
                if not top_chunks:
                    stmt_top = select(DocumentChunk)
                    if filters:
                        stmt_top = stmt_top.where(*filters)
                    stmt_top = stmt_top.limit(limit)
                    res_top = await session.execute(stmt_top)
                    fallback_chunks = res_top.scalars().all()
                    top_chunks = [(0.0, c) for c in fallback_chunks]

                results = []
                for score, chunk in top_chunks:
                    meta = chunk.metadata_json or {}
                    image_ref = (
                        meta.get("image_url") or
                        meta.get("image_object_name") or
                        meta.get("image_path")
                    )
                    results.append({
                        "document": chunk.document_name,
                        "chunk_index": chunk.chunk_index,
                        "content": chunk.content,
                        "page": meta.get("page"),
                        "has_image": meta.get("has_image", False),
                        "image_ref": image_ref,
                        "rrf_score": round(score, 4)
                    })

                return {
                    "query": query,
                    "count": len(results),
                    "search_type": "hybrid_vector_rrf",
                    "filters_applied": {
                        "document_name": document_name,
                        "page": page,
                        "has_image": has_image
                    },
                    "passages": results
                }
        except Exception as e:
            logger.error(f"Error in DocumentSearchTool Hybrid Search: {e}")
            return {
                "query": query,
                "count": 0,
                "search_type": "hybrid_vector_rrf",
                "filters_applied": {
                    "document_name": document_name,
                    "page": page,
                    "has_image": has_image
                },
                "passages": [],
                "error": str(e)
            }

