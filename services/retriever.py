"""Top-K retrieval logic"""
from app.state import vector_store
from services.reranker import rerank

def retrieve(query: str, query_vector: list[float], top_k: int = 5) -> list[tuple[str, float]]:
    return vector_store.search(query_vector, top_k=top_k)

def retrieve_and_rerank(query: str, query_vector: list[float], top_k: int = 5) -> list[tuple[str, float]]:
    candidates = vector_store.search(query_vector, top_k=top_k * 3)
    return rerank(query, candidates, top_k=top_k)
