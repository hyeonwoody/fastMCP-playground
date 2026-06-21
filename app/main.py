from __future__ import annotations

from contextlib import asynccontextmanager
import structlog
import uvicorn
from fastapi import FastAPI

from app.state import mcp, ports, settings

import tools.greet
import tools.ask

logger = structlog.get_logger()

mcp_app = mcp.http_app(path="/")



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp_app.lifespan(app):
        logger.info("starting_synapster", port=settings.port)
        await ports.store.ensure_collection(settings.qdrant_collection, 1024)
        yield
        logger.info("shutting_down_synapster")


api = FastAPI(
    title="Synapster",
    description="RAG-powered document search and retrieval MCP server",
    lifespan=lifespan,
)

api.mount("/mcp", mcp_app)

@api.get("/health")
async def health():
    return {"status": "ok"}


def main():
    uvicorn.run(
        "app.main:api",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
