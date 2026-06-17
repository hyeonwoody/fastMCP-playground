from pathlib import Path
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "rag_prompt.txt"


class Qwen:
    def __init__(self) -> None:
        self._llm = ChatOllama(model="qwen2.5:7b-instruct")
        template = _PROMPT_PATH.read_text()
        self._chain = ChatPromptTemplate.from_template(template) | self._llm

    def generate(self, question: str, context: str, model: str = "qwen2.5:7b-instruct") -> str:
        print("its QWEN")
        if model != self._llm.model:
            template = _PROMPT_PATH.read_text()
            print(template)
            self._chain = ChatPromptTemplate.from_template(template) | self._llm
        result = self._chain.invoke({"question": question, "context": context})
        return result.content
