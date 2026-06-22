"""store in vector DB"""
from __future__ import annotations

from models.domain import VectorPoint
from services.ports import VectorStorePort


async def index(
    points: list[VectorPoint],
    store_port: VectorStorePort,
    collection: str,
) -> int:
    if not points:
        return 0
    await store_port.upsert(collection, points)
    return len(points)