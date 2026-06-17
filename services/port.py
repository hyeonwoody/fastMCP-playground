"""Port interfaces for swappable backends"""
from typing import Protocol


class VectorStorePort(Protocol):
    def add(self, id: str, vector: list[float]) -> None: ...
    def search(self, query: list[float], top_k: int = 5) -> list[tuple[str, float]]: ...


class LlmPort(Protocol):
    def generate(self, question: str, context: str, model: str = "gpt-4o-mini") -> str: ...
