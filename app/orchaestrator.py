"""Raw + processed data"""
from services.embedding import embed
from services.retriever import retrieve
from app.state import vector_store
from app.state import llm


def embed_and_store(name: str) -> list[float]:
    vector = embed(name)
    vector_store.add(id=name, vector=vector)
    return vector


def embed_and_search(question: str) -> list[tuple[str, float]]:
    embedding = embed(question)
    return vector_store.search(embedding, 5)


def embed_and_ask(question: str) -> str:
    embedding = embed(question)
    results = retrieve(question, embedding, top_k=5)
    context = "\n".join(name for name, _ in results)
    return llm.generate(question, context)
