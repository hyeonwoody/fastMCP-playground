from __future__ import annotations

import asyncio

import structlog

from config.settings import Settings
from models.domain import RerankResult

logger = structlog.get_logger()

_reranker = None


def _get_reranker(model_name: str):
    global _reranker
    if _reranker is None:
        from FlagEmbedding import FlagReranker

        logger.info("loading_reranker_model", model=model_name)
        _reranker = FlagReranker(model_name, use_fp16=True)
    return _reranker


class BGEReranker:
    def __init__(self, settings: Settings) -> None:
        self._model_name = settings.reranker_model

    async def rerank(
        self, query: str, documents: list[str], top_k: int
    ) -> list[RerankResult]:
        if not documents:
            return []
        reranker = _get_reranker(self._model_name)
        pairs = [[query, doc] for doc in documents]
        scores = await asyncio.to_thread(reranker.compute_score, pairs)
        if isinstance(scores, float):
            scores = [scores]
        indexed = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return [
            RerankResult(index=idx, score=float(score))
            for idx, score in indexed[:top_k]
        ]