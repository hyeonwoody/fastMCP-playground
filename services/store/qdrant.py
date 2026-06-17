"""Qdrant vector store adapter"""
import os
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

COLLECTION = "synapster"
DIM = 768  # embaas/sentence-transformers-multilingual-e5-base

class QdrantVectorStore:
    def __init__(self) -> None:
        url = os.environ.get("QDRANT_URL")
        print(url)
        self._client = QdrantClient(url=url) if url else QdrantClient(":memory:")
        self._client.recreate_collection(
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
        response = self._client.query_points(
        collection_name=COLLECTION,
        query=query,
        limit=top_k,
        )

        return [
            (point.payload["name"], point.score)
            for point in response.points
        ]

    # hybrid search with RRF fusion
    def hybrid_search(self, dense_vector, sparse_indices, sparse_values, top_k):
        return self._client.query_points(
            collection_name=COLLECTION,
            prefetch=[
                Prefetch(query=dense_vector, using="dense", limit=top_k * 3),
                Prefetch(query=SparseVector(indices=sparse_indices, values=sparse_values),
                        using="sparse", limit=top_k * 3),
            ],
            query=FusionQuery(fusion=Fusion.RRF),
            limit=top_k,
        )