from __future__ import annotations

from collections.abc import AsyncIterator

import ollama
import structlog

from config.settings import Settings

logger = structlog.get_logger()


class OllamaLLM:
    def __init__(self, settings: Settings) -> None:
        self._client = ollama.AsyncClient(host=settings.ollama_url)
        self._model = settings.ollama_model

    async def generate(self, prompt: str, context: str, **kwargs) -> str:
        messages = self._build_messages(prompt, context)
        response = await self._client.chat(
            model=self._model,
            messages=messages,
            stream=False,
        )
        return response["message"]["content"]

    async def stream(
        self, prompt: str, context: str, **kwargs
    ) -> AsyncIterator[str]:
        messages = self._build_messages(prompt, context)
        response = await self._client.chat(
            model=self._model,
            messages=messages,
            stream=True,
        )
        async for chunk in response:
            token = chunk["message"]["content"]
            if token:
                yield token

    def _build_messages(self, prompt: str, context: str) -> list[dict]:
        system_msg = (
            "You are answering questions based ONLY on the provided context. "
            "If the context does not contain relevant information, say so. "
            "Be specific — cite project names, technologies, and metrics."
        )
        user_msg = f"## Context\n{context}\n\n## Question\n{prompt}"
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]
