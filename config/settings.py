from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SYNAPSTER_",
    )

    host: str = "0.0.0.0"
    port: int = 8000

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "synapster"
    qdrant_cache_collection: str = "synapster_cache"

    embedding_model: str = "BAAI/bge-m3"
    embedding_batch_size: int = 32

    reranker_model: str = "BAAI/bge-reranker-v2-m3"

    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "EEVE-Korean-Instruct-10.8B-v1.0:latest"

    cache_similarity_threshold: float = 0.92
    cache_ttl_seconds: int = 3600

    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"

    max_session_history: int = 20
    max_concurrent_sessions: int = 100

    chunk_size: int = 512
    chunk_overlap: int = 50