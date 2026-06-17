"""Port interfaces for swappable backends"""
from typing import Protocol


class VectorStorePort(Protocol):
    def add(self, id: str, vector: list[float]) -> None: ...
    def search(self, query: list[float], top_k: int = 5) -> list[tuple[str, float]]: ...