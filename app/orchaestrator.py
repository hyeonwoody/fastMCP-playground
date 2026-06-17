"""Raw + processed data"""
from services.embedding import embed
from services.retriever import retrieve
from app.state import vector_store


def embed_and_store(name: str) -> list[float]:
    vector = embed(name)
    vector_store.add(id=name, vector=vector)
    return vector


def embed_and_search(question: str) -> list[tuple[str, float]]:
    embedding = embed(question)
    return vector_store.search(query_vector, 5)
