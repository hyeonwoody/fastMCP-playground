from __future__ import annotations

import httpx
import structlog

from config.settings import Settings

logger = structlog.get_logger()


class ApiReadmeFetcher:
    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.api_base_url.rstrip("/")

    async def fetch_project_name(self, project_id: int) -> str:
        url = f"{self._base_url}/api/v1/projects/id/{project_id}/name"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text.strip().strip('"')

    async def fetch_readme(self, project_name: str) -> str:
        url = f"{self._base_url}/api/v1/media/serve/portfolio/readme/name/{project_name}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text
