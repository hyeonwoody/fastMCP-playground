"""load PDFs / images"""
from __future__ import annotations

import hashlib
from datetime import datetime

import structlog

from config.settings import Settings
from models.schemas import IngestDocumentOutput, IngestQAOutput
from pipelines.chunking import chunk
from pipelines.cleaning import clean
from pipelines.embedding import embed_chunks
from pipelines.indexing import index
from services.ports import EmbeddingPort, VectorStorePort

logger = structlog.get_logger()


async def ingest_document(
    content: str,
    source_file: str,
    project_name: str,
    content_type: str,
    tags: list[str],
    embedding_port: EmbeddingPort,
    store_port: VectorStorePort,
    settings: Settings,
) -> IngestDocumentOutput:
    document_id = hashlib.sha256(
        f"{project_name}:{source_file}".encode()
    ).hexdigest()[:16]

    try:
        cleaned = await clean(content, content_type)
        chunks = await chunk(
            cleaned, content_type, settings.chunk_size, settings.chunk_overlap
        )

        now = datetime.now().isoformat()
        for c in chunks:
            c.metadata = {
                "project_name": project_name,
                "source_file": source_file,
                "content_type": content_type,
                "tags": tags,
                "created_at": now,
                "updated_at": now,
            }

        await store_port.delete_by_document(settings.qdrant_collection, document_id)
        points = await embed_chunks(
            chunks, document_id, embedding_port, settings.embedding_batch_size
        )
        await index(points, store_port, settings.qdrant_collection)

        logger.info(
            "document_ingested",
            document_id=document_id,
            chunks=len(chunks),
        )
        return IngestDocumentOutput(
            document_id=document_id,
            chunk_count=len(chunks),
            status="success",
        )
    except Exception:
        logger.exception("ingestion_failed", document_id=document_id)
        return IngestDocumentOutput(
            document_id=document_id,
            chunk_count=0,
            status="failed",
        )


async def ingest_qa(
    content: str,
    source_file: str,
    tags: list[str],
    embedding_port: EmbeddingPort,
    store_port: VectorStorePort,
    settings: Settings,
) -> IngestQAOutput:
    document_id = hashlib.sha256(
        f"qa:{source_file}".encode()
    ).hexdigest()[:16]

    try:
        cleaned = await clean(content, "markdown")
        entries = _parse_qa_entries(cleaned)

        now = datetime.now().isoformat()
        from models.domain import Chunk

        chunks = []
        for i, (question, answer) in enumerate(entries):
            qa_text = f"Q: {question}\nA: {answer}"
            c = Chunk(
                content=qa_text,
                section_title=question,
                chunk_index=i,
                metadata={
                    "project_name": "interview",
                    "source_file": source_file,
                    "content_type": "qa",
                    "tags": tags,
                    "created_at": now,
                    "updated_at": now,
                },
            )
            chunks.append(c)

        await store_port.delete_by_document(settings.qdrant_collection, document_id)
        points = await embed_chunks(
            chunks, document_id, embedding_port, settings.embedding_batch_size
        )
        await index(points, store_port, settings.qdrant_collection)

        logger.info(
            "qa_ingested",
            document_id=document_id,
            entries=len(entries),
        )
        return IngestQAOutput(
            document_id=document_id,
            entry_count=len(entries),
            status="success",
        )
    except Exception:
        logger.exception("qa_ingestion_failed", document_id=document_id)
        return IngestQAOutput(
            document_id=document_id,
            entry_count=0,
            status="failed",
        )


def _parse_qa_entries(text: str) -> list[tuple[str, str]]:
    import re

    entries: list[tuple[str, str]] = []
    pattern = re.compile(
        r"^#{1,3}\s+(.+?)$\s*(.*?)(?=^#{1,3}\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for match in pattern.finditer(text):
        question = match.group(1).strip()
        answer = match.group(2).strip()
        if question and answer:
            entries.append((question, answer))
    return entries