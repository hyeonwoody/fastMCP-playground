from __future__ import annotations

import asyncio
from functools import lru_cache

import structlog
import torch
from FlagEmbedding import BGEM3FlagModel

from config.settings import Settings
from models.domain import EmbeddingResult

logger = structlog.get_logger()

_model = None


def _get_model(model_name: str):
    global _model
    if _model is None:
        from FlagEmbedding import BGEM3FlagModel

        logger.info("loading_embedding_model", model=model_name)
        _model = BGEM3FlagModel(model_name, use_fp16=True)
    return _model


class BGEm3Embedding:
    def __init__(self, settings: Settings) -> None:
        self._model_name = settings.embedding_model
        self._batch_size = settings.embedding_batch_size
        logger.info("loading_embedding_model", model=settings.embedding_model)
        self._model = BGEM3FlagModel(
            settings.embedding_model, use_fp16=torch.cuda.is_available()
        )

    async def embed(self, texts: list[str]) -> list[EmbeddingResult]:
        model = _get_model(self._model_name)
        output = await asyncio.to_thread(
            model.encode,
            texts,
            batch_size=self._batch_size,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
        )
        results = []
        for i in range(len(texts)):
            dense = output["dense_vecs"][i].tolist()
            sparse_raw = output["lexical_weights"][i]
            sparse = {int(k): float(v) for k, v in sparse_raw.items()}
            results.append(EmbeddingResult(dense=dense, sparse=sparse))
        return results

    async def embed_dense(self, texts: list[str]) -> list[list[float]]:
        results = await self.embed(texts)
        return [r.dense for r in results]

    async def embed_sparse(self, texts: list[str]) -> list[dict[int, float]]:
        results = await self.embed(texts)
        return [r.sparse for r in results]