from __future__ import annotations

import structlog

from models.schemas import ChunkMetadata, RetrievedChunk
from services.ports import EmbeddingPort, RerankerPort, VectorStorePort

logger = structlog.get_logger()


async def retrieve(
    query: str,
    top_k: int,
    strategy: str,
    filters: dict | None,
    collection: str,
    embedding_port: EmbeddingPort,
    store_port: VectorStorePort,
    reranker_port: RerankerPort
) -> list[RetrievedChunk]:
    embeddings = await embedding_port.embed([query])
    query_emb = embeddings[0]

    if strategy == "dense":
        query_sparse = None
    elif strategy == "sparse":
        query_sparse = query_emb.sparse
        query_emb.dense = [0.0] * len(query_emb.dense)
    else:
        query_sparse = query_emb.sparse

    hits = await store_port.search(
        collection=collection,
        query_dense=query_emb.dense,
        query_sparse=query_sparse,
        top_k=top_k,
        filters=filters,
    )

    if not hits:
        return []
    documents = [h.payload.get("content", "") for h in hits]
    reranked = await reranker_port.rerank(query, documents, top_k)

    results: list[RetrievedChunk] = []
    for rr in reranked:
        hit = hits[rr.index]
        payload = hit.payload
        results.append(
            RetrievedChunk(
                chunk_id=hit.chunk_id,
                content=payload.get("content", ""),
                score=rr.score,
                metadata=ChunkMetadata(
                    document_id=payload.get("document_id", ""),
                    project_name=payload.get("project_name", ""),
                    section_title=payload.get("section_title"),
                    source_file=payload.get("source_file", ""),
                    chunk_index=payload.get("chunk_index", 0),
                    content_type=payload.get("content_type", ""),
                    tags=payload.get("tags", []),
                    created_at=payload.get("created_at", ""),
                    updated_at=payload.get("updated_at", ""),
                ),
            )
        )
    return results
