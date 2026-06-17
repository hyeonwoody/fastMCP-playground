"""model configs / local models"""
import os
from fastmcp import FastMCP
from services.port import VectorStorePort
from services.port import LlmPort

mcp = FastMCP("Hello MCP")


def get_vector_store() -> VectorStorePort:
    backend = os.environ.get("VECTOR_STORE", "qdrant")
    if backend == "chroma":
        from services.store.chroma import ChromaVectorStore
        return ChromaVectorStore()
    from services.store.qdrant import QdrantVectorStore
    return QdrantVectorStore()

def get_llm() -> LlmPort:
    from services.llm.openAI import OpenAI
    return OpenAI()

vector_store: VectorStorePort = get_vector_store()
llm: LlmPort = get_llm()
