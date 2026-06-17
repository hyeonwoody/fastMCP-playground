"""embedding model"""
from sentence_transformers import SentenceTransformer
from fastembed import SparseTextEmbedding

_model = SentenceTransformer("embaas/sentence-transformers-multilingual-e5-base")
_sparse_model = SparseTextEmbedding("Qdrant/bm25")

def embed(text: str) -> list[float]:
    return _model.encode(text).tolist()

def sparse_embed(text: str) -> tuple[list[int], list[float]]:
    result = list(_sparse_model.embed([text]))[0]
    return result.indices.tolist(), result.values.tolist()