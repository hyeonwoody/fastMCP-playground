"""Optional rank"""

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import CrossEncoder
        _model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _model


def rerank(query: str, candidates: list[tuple[str, float]], top_k: int = 5) -> list[tuple[str, float]]:
    if not candidates:
        return []
    names = [name for name, _ in candidates]
    pairs = [[query, name] for name in names]
    scores = _get_model().predict(pairs).tolist()
    ranked = sorted(zip(names, scores), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]
