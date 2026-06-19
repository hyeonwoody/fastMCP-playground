"""model configs / local models"""
import os
from pathlib import Path

from fastmcp import FastMCP
from fastapi import FastAPI
from services.port import VectorStorePort
from services.port import LlmPort

mcp = FastMCP("Hello MCP")
api = FastAPI(title="Synapster LangServe")

from langchain_core.prompts import ChatPromptTemplate
_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "rag_prompt.txt"
_prompt = ChatPromptTemplate.from_template(_PROMPT_PATH.read_text())


def get_vector_store() -> VectorStorePort:
    backend = os.environ.get("VECTOR_STORE", "qdrant")
    if backend == "chroma":
        from services.store.chroma import ChromaVectorStore
        return ChromaVectorStore()
    from services.store.qdrant import QdrantVectorStore
    return QdrantVectorStore()


def get_llm() -> LlmPort:
    llm = os.environ.get("LLM", "mistral")
    if llm == "openai":
        from services.llm.openAI import OpenAI
        return OpenAI()
    if llm == "mistral":
        from services.llm.mistral import Mistral
        return Mistral()
    if llm == "qwen":
        from services.llm.qwen import Qwen
        return Qwen()
    from services.llm.eeve import Eeve
    return Eeve()


vector_store: VectorStorePort = get_vector_store()
llm: LlmPort = get_llm()
