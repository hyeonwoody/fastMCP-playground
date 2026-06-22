from __future__ import annotations

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, HTTPException

from app.state import ports, settings
from models.schemas import ProjectCreate, SyncResult
from pipelines.sync import sync_readme

logger = structlog.get_logger()

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/{project_id}/readme/sync")
async def sync_project_readme(project_id: int) -> dict:
    
    result = await sync_readme(
        project_id=project_id,
        fetcher_port=ports.fetcher,
        embedding_port=ports.embedding,
        store_port=ports.store,
        settings=settings,
    )

    return result.model_dump()
