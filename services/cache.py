from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime

import structlog
from qdrant_client import AsyncQdrantClient, models

from config.settings import Settings
from models.domain import CacheEntry, CacheStats

logger = structlog.get_logger()


class SemanticCache:
    def __init__(self, settings: Settings) -> None:
        self._client = AsyncQdrantClient(url=settings.qdrant_url)
        self._collection = settings.qdrant_cache_collection
        self._hits = 0
        self._misses = 0

    async def ensure_collection(self, dense_dim: int) -> None:
        collections = await self._client.get_collections()
        names = [c.name for c in collections.collections]
        if self._collection not in names:
            await self._client.create_collection(
                collection_name=self._collection,
                vectors_config=models.VectorParams(
                    size=dense_dim,
                    distance=models.Distance.COSINE,
                ),
            )
            logger.info("cache_collection_created", collection=self._collection)

    async def get(
        self, query_embedding: list[float], threshold: float
    ) -> CacheEntry | None:
        results = await self._client.query_points(
            collection_name=self._collection,
            query=query_embedding,
            limit=1,
            score_threshold=threshold,
        )
        if not results.points:
            self._misses += 1
            return None
        hit = results.points[0]
        payload = hit.payload or {}
        created_at = payload.get("created_at", 0)
        ttl = payload.get("ttl", 3600)
        if time.time() - created_at > ttl:
            await self._client.delete(
                collection_name=self._collection,
                points_selector=models.PointIdsList(points=[hit.id]),
            )
            self._misses += 1
            return None
        self._hits += 1
        return CacheEntry(
            query_hash=str(hit.id),
            response=payload.get("response", ""),
            similarity=hit.score,
            created_at=datetime.fromtimestamp(created_at),
            ttl=ttl,
        )

    async def put(
        self, query_embedding: list[float], response: str, ttl: int
    ) -> None:
        point_id = hashlib.md5(
            json.dumps(query_embedding[:8]).encode()
        ).hexdigest()
        await self._client.upsert(
            collection_name=self._collection,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=query_embedding,
                    payload={
                        "response": response,
                        "created_at": time.time(),
                        "ttl": ttl,
                    },
                )
            ],
        )

    async def clear(self, older_than: datetime | None) -> int:
        if older_than is None:
            info = await self._client.get_collection(self._collection)
            count = info.points_count or 0
            dim = info.config.params.vectors
            vec_size = dim.size if hasattr(dim, "size") else 1024
            await self._client.delete_collection(self._collection)
            await self.ensure_collection(vec_size)
            return count
        cutoff = older_than.timestamp()
        result = await self._client.count(
            collection_name=self._collection,
            count_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="created_at",
                        range=models.Range(lt=cutoff),
                    )
                ]
            ),
        )
        count = result.count
        if count > 0:
            await self._client.delete(
                collection_name=self._collection,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="created_at",
                                range=models.Range(lt=cutoff),
                            )
                        ]
                    )
                ),
            )
        return count

    async def stats(self) -> CacheStats:
        info = await self._client.get_collection(self._collection)
        total = info.points_count or 0
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
        return CacheStats(
            total_entries=total,
            hit_rate=hit_rate,
            avg_similarity=0.0,
        )