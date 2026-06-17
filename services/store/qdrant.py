"""Qdrant vector store adapter"""
import os
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

COLLECTION = "synapster"
DIM = 384  # all-MiniLM-L6-v2


class QdrantVectorStore:
    def __init__(self) -> None:
        url = os.environ.get("QDRANT_URL")
        print(url)
        self._client = QdrantClient(url=url) if url else QdrantClient(":memory:")
        if not self._client.collection_exists(COLLECTION):
            self._client.create_collection(
                collection_name=COLLECTION,
                vectors_config=VectorParams(
                    size=DIM,
                    distance=Distance.COSINE,
                ),
            )
        
    def add(self, id: str, vector: list[float]) -> None:
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, id))
        print("ADDDING")
        self._client.upsert(
            collection_name=COLLECTION,
            points=[PointStruct(id=point_id, vector=vector, payload={"name": id})],
        )

    def search(self, query: list[float], top_k: int = 5) -> list[tuple[str, float]]:
        results = self._client.search(
            collection_name=COLLECTION,
            query_vector=query,
            limit=top_k,
        )
        return [(r.payload["name"], r.score) for r in results]
