from __future__ import annotations

from datetime import datetime

import structlog
from qdrant_client import AsyncQdrantClient, models

from config.settings import Settings
from models.domain import (
    ChunkSummary,
    DocumentDetail,
    DocumentMeta,
    SearchHit,
    VectorPoint,
)

logger = structlog.get_logger()


class QdrantVectorStore:
    def __init__(self, settings: Settings) -> None:
        self._client = AsyncQdrantClient(url=settings.qdrant_url)

    async def ensure_collection(self, collection: str, dense_dim: int) -> None:
        collections = await self._client.get_collections()
        names = [c.name for c in collections.collections]
        if collection in names:
            info = await self._client.get_collection(collection_name=collection)
            vectors_cfg = info.config.params.vectors
            has_named = isinstance(vectors_cfg, dict) and "dense" in vectors_cfg
            if not has_named:
                logger.warning("collection_schema_mismatch", collection=collection)
                await self._client.delete_collection(collection_name=collection)
            else:
                return
        await self._client.create_collection(
            collection_name=collection,
            vectors_config={
                "dense": models.VectorParams(
                    size=dense_dim,
                    distance=models.Distance.COSINE,
                ),
            },
            sparse_vectors_config={
                "sparse": models.SparseVectorParams(
                    modifier=models.Modifier.IDF,
                ),
            },
        )
        logger.info("collection_created", collection=collection)

    async def upsert(self, collection: str, points: list[VectorPoint]) -> None:
        qdrant_points = [
            models.PointStruct(
                id=p.id,
                vector={
                    "dense": p.dense_vector,
                    "sparse": models.SparseVector(
                        indices=list(p.sparse_vector.keys()),
                        values=list(p.sparse_vector.values()),
                    ),
                },
                payload=p.payload,
            )
            for p in points
        ]
        await self._client.upsert(
            collection_name=collection,
            points=qdrant_points,
        )

    async def search(
        self,
        collection: str,
        query_dense: list[float],
        query_sparse: dict[int, float] | None,
        top_k: int,
        filters: dict | None,
    ) -> list[SearchHit]:
        qdrant_filter = self._build_filter(filters) if filters else None

        if query_sparse:
            results = await self._client.query_points(
                collection_name=collection,
                prefetch=[
                    models.Prefetch(
                        query=query_dense,
                        using="dense",
                        limit=top_k * 3,
                        filter=qdrant_filter,
                    ),
                    models.Prefetch(
                        query=models.SparseVector(
                            indices=list(query_sparse.keys()),
                            values=list(query_sparse.values()),
                        ),
                        using="sparse",
                        limit=top_k * 3,
                        filter=qdrant_filter,
                    ),
                ],
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                limit=top_k,
            )
        else:
            results = await self._client.query_points(
                collection_name=collection,
                query=query_dense,
                using="dense",
                limit=top_k,
                query_filter=qdrant_filter,
            )

        return [
            SearchHit(
                chunk_id=str(hit.id),
                score=hit.score,
                payload=hit.payload or {},
            )
            for hit in results.points
        ]

    async def delete_by_document(self, collection: str, document_id: str) -> int:
        result = await self._client.count(
            collection_name=collection,
            count_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document_id),
                    )
                ]
            ),
        )
        count = result.count
        if count > 0:
            await self._client.delete(
                collection_name=collection,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="document_id",
                                match=models.MatchValue(value=document_id),
                            )
                        ]
                    )
                ),
            )
        return count

    async def delete_by_project(self, collection: str, project_id: int) -> int:
        result = await self._client.count(
            collection_name=collection,
            count_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="project_id",
                        match=models.MatchValue(value=project_id),
                    )
                ]
            ),
        )
        count = result.count
        if count > 0:
            await self._client.delete(
                collection_name=collection,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="project_id",
                                match=models.MatchValue(value=project_id),
                            )
                        ]
                    )
                ),
            )
        return count

    async def list_documents(self, collection: str) -> list[DocumentMeta]:
        all_points, _ = await self._client.scroll(
            collection_name=collection,
            limit=10000,
            with_payload=True,
            with_vectors=False,
        )
        docs: dict[str, DocumentMeta] = {}
        for point in all_points:
            payload = point.payload or {}
            doc_id = payload.get("document_id", "")
            if doc_id not in docs:
                docs[doc_id] = DocumentMeta(
                    document_id=doc_id,
                    project_name=payload.get("project_name", ""),
                    source_file=payload.get("source_file", ""),
                    content_type=payload.get("content_type", ""),
                    chunk_count=0,
                    created_at=payload.get("created_at", datetime.now()),
                    updated_at=payload.get("updated_at", datetime.now()),
                )
            docs[doc_id].chunk_count += 1
        return list(docs.values())

    async def get_document(
        self, collection: str, document_id: str
    ) -> DocumentDetail | None:
        points, _ = await self._client.scroll(
            collection_name=collection,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document_id),
                    )
                ]
            ),
            limit=10000,
            with_payload=True,
            with_vectors=False,
        )
        if not points:
            return None
        first = points[0].payload or {}
        chunks = [
            ChunkSummary(
                chunk_id=str(p.id),
                chunk_index=p.payload.get("chunk_index", 0) if p.payload else 0,
                section_title=p.payload.get("section_title") if p.payload else None,
                content_preview=(p.payload.get("content", "")[:200] if p.payload else ""),
            )
            for p in points
        ]
        chunks.sort(key=lambda c: c.chunk_index)
        return DocumentDetail(
            document_id=document_id,
            project_name=first.get("project_name", ""),
            source_file=first.get("source_file", ""),
            content_type=first.get("content_type", ""),
            tags=first.get("tags", []),
            chunk_count=len(chunks),
            chunks=chunks,
            created_at=first.get("created_at", datetime.now()),
            updated_at=first.get("updated_at", datetime.now()),
        )

    async def rebuild_collection(self, collection: str) -> int:
        info = await self._client.get_collection(collection_name=collection)
        count = info.points_count or 0
        dense_config = info.config.params.vectors
        if isinstance(dense_config, dict) and "dense" in dense_config:
            dim = dense_config["dense"].size
        else:
            dim = 1024
        await self._client.delete_collection(collection_name=collection)
        await self.ensure_collection(collection, dim)
        return count

    async def list_collections(self) -> list[str]:
        collections = await self._client.get_collections()
        return [c.name for c in collections.collections]

    def _build_filter(self, filters: dict) -> models.Filter:
        conditions = []
        if "project_id" in filters and filters["project_id"]:
            conditions.append(
                models.FieldCondition(
                    key="project_id",
                    match=models.MatchValue(value=filters["project_id"]),
                )
            )
        if "project_name" in filters and filters["project_name"]:
            conditions.append(
                models.FieldCondition(
                    key="project_name",
                    match=models.MatchValue(value=filters["project_name"]),
                )
            )
        if "content_type" in filters and filters["content_type"]:
            conditions.append(
                models.FieldCondition(
                    key="content_type",
                    match=models.MatchValue(value=filters["content_type"]),
                )
            )
        if "tags" in filters and filters["tags"]:
            for tag in filters["tags"]:
                conditions.append(
                    models.FieldCondition(
                        key="tags",
                        match=models.MatchValue(value=tag),
                    )
                )
        return models.Filter(must=conditions) if conditions else models.Filter()