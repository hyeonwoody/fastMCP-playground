from __future__ import annotations

from dataclasses import dataclass

from fastmcp import FastMCP

from config.settings import Settings
from services.embedding import BGEm3Embedding
from services.llm.ollama import OllamaLLM
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
    llm: OllamaLLM

ports = Ports(
    embedding=BGEm3Embedding(settings),
    store=QdrantVectorStore(settings),
    llm=OllamaLLM(settings),
)
