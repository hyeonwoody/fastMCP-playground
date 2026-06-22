from __future__ import annotations

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, HTTPException

from app.state import ports, settings
from models.schemas import ProjectCreate, SyncResult
from pipelines.sync import sync_readme

logger = structlog.get_logger()

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", status_code=201)
async def create_project(body: ProjectCreate) -> dict:
    existing = ports.project_store.get_by_name(body.name)
    if existing:
        raise HTTPException(status_code=409, detail="Project already exists")
    project = ports.project_store.create(body.name)
    return project.model_dump(mode="json")


@router.get("/")
async def list_projects() -> list[dict]:
    projects = ports.project_store.list_all()
    return [p.model_dump(mode="json") for p in projects]


@router.get("/{project_id}")
async def get_project(project_id: int) -> dict:
    project = ports.project_store.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.model_dump(mode="json")


@router.post("/{project_id}/readme/sync")
async def sync_project_readme(project_id: int) -> dict:
    
    result = await sync_readme(
        project_id=project_id,
        fetcher_port=ports.fetcher,
        embedding_port=ports.embedding,
        store_port=ports.store,
        settings=settings,
    )

    ports.project_store.update_synced_at(project_id, datetime.now(timezone.utc))

    return result.model_dump()
