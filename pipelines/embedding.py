"""convert to vector"""
from __future__ import annotations

import uuid

from models.domain import Chunk, VectorPoint
from services.ports import EmbeddingPort


async def embed_chunks(
    chunks: list[Chunk],
    document_id: str,
    embedding_port: EmbeddingPort,
    batch_size: int,
) -> list[VectorPoint]:
    points: list[VectorPoint] = []
    texts = [c.content for c in chunks]

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        batch_chunks = chunks[i : i + batch_size]
        results = await embedding_port.embed(batch_texts)

        for j, (chunk, emb) in enumerate(zip(batch_chunks, results)):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{document_id}_{i + j}"))
            points.append(
                VectorPoint(
                    id=point_id,
                    dense_vector=emb.dense,
                    sparse_vector=emb.sparse,
                    payload={
                        "content": chunk.content,
                        "document_id": document_id,
                        "section_title": chunk.section_title,
                        "chunk_index": chunk.chunk_index,
                        **chunk.metadata,
                    },
                )
            )
    return points