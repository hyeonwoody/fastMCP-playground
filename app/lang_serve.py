"""LangServe REST API for LangChain chains"""
from langserve import add_routes
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel
from app.state import llm, api, _prompt
from services.embedding import embed
from services.retriever import retrieve


class AskInput(BaseModel):
    question: str


def _retrieve_context(data: dict) -> dict:
    question = data["question"]
    embedding = embed(question)
    results = retrieve(question, embedding, top_k=5)
    context = "\n".join(name for name, _ in results)
    return {"question": question, "context": context}


rag_chain = RunnableLambda(_retrieve_context) | _prompt | llm._llm

add_routes(api, rag_chain, path="/ask", input_type=AskInput)
