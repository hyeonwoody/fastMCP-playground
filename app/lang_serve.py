"""LangServe REST API for LangChain chains"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from langserve import add_routes
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel
from app.state import llm
from services.embedding import embed
from services.retriever import retrieve

app = FastAPI(title="Synapster LangServe")

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "rag_prompt.txt"
_prompt = ChatPromptTemplate.from_template(_PROMPT_PATH.read_text())


class AskInput(BaseModel):
    question: str


def _retrieve_context(data: dict) -> dict:
    question = data["question"]
    embedding = embed(question)
    results = retrieve(question, embedding, top_k=5)
    context = "\n".join(name for name, _ in results)
    return {"question": question, "context": context}


rag_chain = RunnableLambda(_retrieve_context) | _prompt | llm._llm

add_routes(app, rag_chain, path="/ask", input_type=AskInput)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
