from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime
from typing import Protocol

from models.domain import (

    DocumentDetail,
    DocumentMeta,
    EmbeddingResult,
    RerankResult,
    SearchHit,
    VectorPoint,
)


class EmbeddingPort(Protocol):
    async def embed(self, texts: list[str]) -> list[EmbeddingResult]: ...

    async def embed_dense(self, texts: list[str]) -> list[list[float]]: ...

    async def embed_sparse(self, texts: list[str]) -> list[dict[int, float]]: ...


class VectorStorePort(Protocol):
    async def upsert(self, collection: str, points: list[VectorPoint]) -> None: ...

    async def search(
        self,
        collection: str,
        query_dense: list[float],
        query_sparse: dict[int, float] | None,
        top_k: int,
        filters: dict | None,
    ) -> list[SearchHit]: ...

    async def delete_by_document(self, collection: str, document_id: str) -> int: ...

    async def list_documents(self, collection: str) -> list[DocumentMeta]: ...

    async def get_document(
        self, collection: str, document_id: str
    ) -> DocumentDetail | None: ...

    async def rebuild_collection(self, collection: str) -> int: ...

    async def list_collections(self) -> list[str]: ...

    async def ensure_collection(self, collection: str, dense_dim: int) -> None: ...

class RerankerPort(Protocol):
    async def rerank(
        self, query: str, documents: list[str], top_k: int
    ) -> list[RerankResult]: ...

class LLMPort(Protocol):
    async def generate(self, prompt: str, context: str, **kwargs) -> str: ...

    async def stream(
        self, prompt: str, context: str, **kwargs
    ) -> AsyncIterator[str]: ...