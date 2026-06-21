from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

class MetadataFilter(BaseModel):
    project_name: str | None = None
    content_type: Literal["markdown", "html"] | None = None
    tags: list[str] | None = Field(default=None, max_length=20)

class ChunkMetadata(BaseModel):
    document_id: str
    project_name: str
    section_title: str | None
    source_file: str
    chunk_index: int
    content_type: str
    tags: list[str]
    created_at: str
    updated_at: str

class RetrievedChunk(BaseModel):
    chunk_id: str
    content: str
    score: float
    metadata: ChunkMetadata

class IngestDocumentInput(BaseModel):
    content: str = Field(..., max_length=500_000)
    source_file: str = Field(..., max_length=500)
    project_name: str = Field(..., max_length=100)
    content_type: Literal["markdown", "html"] = "markdown"
    tags: list[str] = Field(default_factory=list, max_length=20)

class IngestDocumentOutput(BaseModel):
    document_id: str
    chunk_count: int
    status: Literal["success", "partial", "failed"]

class IngestQAInput(BaseModel):
    content: str = Field(..., max_length=500_000)
    source_file: str = Field(..., max_length=500)
    tags: list[str] = Field(default_factory=list, max_length=20)

class IngestQAOutput(BaseModel):
    document_id: str
    entry_count: int
    status: Literal["success", "partial", "failed"]

class AskQuestionInput(BaseModel):
    question: str = Field(..., max_length=2000)
    session_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    filters: MetadataFilter | None = None

class AskQuestionOutput(BaseModel):
    answer: str
    sources: list[RetrievedChunk]
    session_id: str
    cached: bool