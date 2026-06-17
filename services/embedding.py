"""embedding model"""

_model = None
_sparse_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("embaas/sentence-transformers-multilingual-e5-base")
    return _model


def _get_sparse_model():
    global _sparse_model
    if _sparse_model is None:
        from fastembed import SparseTextEmbedding
        _sparse_model = SparseTextEmbedding("Qdrant/bm25")
    return _sparse_model


def embed(text: str) -> list[float]:
    return _get_model().encode(text).tolist()


def sparse_embed(text: str) -> tuple[list[int], list[float]]:
    result = list(_get_sparse_model().embed([text]))[0]
    return result.indices.tolist(), result.values.tolist()
