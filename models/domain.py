from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

class Chunk(BaseModel):
    content: str
    section_title: str | None = None
    chunk_index: int = 0
    metadata: dict = {}

class ChunkSummary(BaseModel):
    chunk_id: str
    chunk_index: int
    section_title: str | None
    content_preview: str

class DocumentDetail(BaseModel):
    document_id: str
    project_name: str
    source_file: str
    content_type: str
    tags: list[str]
    chunk_count: int
    chunks: list[ChunkSummary]
    created_at: datetime
    updated_at: datetime

class CacheEntry(BaseModel):
    query_hash: str
    response: str
    similarity: float
    created_at: datetime
    ttl: int

class CacheStats(BaseModel):
    total_entries: int
    hit_rate: float
    avg_similarity: float

class RerankResult(BaseModel):
    index: int
    score: float

class DocumentMeta(BaseModel):
    document_id: str
    project_name: str
    source_file: str
    content_type: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime

class EmbeddingResult(BaseModel):
    dense: list[float]
    sparse: dict[int, float]

class VectorPoint(BaseModel):
    id: str
    dense_vector: list[float]
    sparse_vector: dict[int, float]
    payload: dict

class SearchHit(BaseModel):
    chunk_id: str
    score: float
    payload: dict


class Project(BaseModel):
    id: int
    name: str
    last_synced_at: datetime | None = None