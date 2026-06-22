from app.state import mcp, ports, settings
from models.schemas import AskQuestionInput, MetadataFilter
from pipelines.retrieval import retrieve

@mcp.tool()
async def ask_question(
    question: str,
    session_id: str | None = None,
    top_k: int = 5,
    project_name: str | None = None,
    content_type: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """RAG query: retrieve relevant context and generate an answer using the LLM."""
    inp = AskQuestionInput(
        question=question,
        session_id=session_id,
        top_k=top_k,
        filters=MetadataFilter(
            project_name=project_name,
            content_type=content_type,
            tags=tags,
        )
        if any([project_name, content_type, tags])
        else None,
    )

    query_embeddings = await ports.embedding.embed([inp.question])
    query_emb = query_embeddings[0]
    cached = await ports.cache.get(
        query_emb.dense, settings.cache_similarity_threshold
    )
    if cached:
        return {
            "answer": cached.response,
            "sources": [],
            "cached": True,
        }

    filters_dict = inp.filters.model_dump(exclude_none=True) if inp.filters else None
    results = await retrieve(
        query=inp.question,
        top_k=inp.top_k,
        strategy="hybrid",
        filters=filters_dict,
        collection=settings.qdrant_collection,
        embedding_port=ports.embedding,
        store_port=ports.store,
        reranker_port=ports.reranker,
    )

    context = "\n\n---\n\n".join(
        f"[{r.metadata.source_file} / {r.metadata.section_title or 'N/A'}]\n{r.content}"
        for r in results
    )
    
    answer = await ports.llm.generate(inp.question, context)

    await ports.cache.put(query_emb.dense, answer, settings.cache_ttl_seconds)

    return {
        "answer": answer,
        "sources": [r.model_dump() for r in results],
        "cached": False,
    }
