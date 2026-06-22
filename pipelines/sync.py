from __future__ import annotations

from datetime import datetime, timezone

import structlog

from config.settings import Settings
from models.schemas import SyncResult
from pipelines.ingestion import ingest_document
from services.ports import EmbeddingPort, ReadmeFetcherPort, VectorStorePort

logger = structlog.get_logger()


async def sync_readme(
    project_id: int,
    fetcher_port: ReadmeFetcherPort,
    embedding_port: EmbeddingPort,
    store_port: VectorStorePort,
    settings: Settings,
) -> SyncResult:
    project_name = await fetcher_port.fetch_project_name(project_id)

    logger.info("sync_start", project_id=project_id, project_name=project_name)

    readme_content = await fetcher_port.fetch_readme(project_name)

    result = await ingest_document(
        content=readme_content,
        source_file="README.md",
        project_name=project_name,
        content_type="markdown",
        tags=[],
        embedding_port=embedding_port,
        store_port=store_port,
        settings=settings,
    )
    logger.info("sync_complete", chunks=result.chunk_count)

    synced_at = datetime.now(timezone.utc)

    return SyncResult(
        project_id=project_id,
        project_name=project_name,
        chunks_processed=result.chunk_count,
        synced_at=synced_at.isoformat(),
    )
