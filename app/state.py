from __future__ import annotations

from dataclasses import dataclass

from fastmcp import FastMCP

from config.settings import Settings
from services.embedding import BGEm3Embedding  # must precede qdrant imports (C extension load order)
from services.reranker import BGEReranker
from services.cache import SemanticCache
from services.llm.ollama import OllamaLLM
from services.project_store import ProjectStore
from services.readme_fetcher import ApiReadmeFetcher
from services.store.qdrant import QdrantVectorStore

settings = Settings()

mcp = FastMCP(
    "synapster",
    instructions="RAG-powered document search and retrieval over markdown and HTML",
)


@dataclass
class Ports:
    embedding: BGEm3Embedding
    store: QdrantVectorStore
    reranker: BGEReranker
    llm: OllamaLLM
    cache: SemanticCache
    fetcher: ApiReadmeFetcher
    project_store: ProjectStore


ports = Ports(
    embedding=BGEm3Embedding(settings),
    store=QdrantVectorStore(settings),
    reranker=BGEReranker(settings),
    llm=OllamaLLM(settings),
    cache=SemanticCache(settings),
    fetcher=ApiReadmeFetcher(settings),
    project_store=ProjectStore(),
)
