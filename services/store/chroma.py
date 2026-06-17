"""FAISS / Chroma"""
import chromadb


class ChromaVectorStore:
    def __init__(self) -> None:
        client = chromadb.Client()
        self._collection = client.get_or_create_collection(name="synapster")

    def add(self, id: str, vector: list[float]) -> None:
        self._collection.add(ids=[id], embeddings=[vector])

    def search(self, query: list[float], top_k: int = 5) -> list[tuple[str, float]]:
        results = self._collection.query(query_embeddings=[query], n_results=top_k)
        return list(zip(results["ids"][0], results["distances"][0]))