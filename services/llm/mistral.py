import os
from openai import OpenAI as OpenAIClient


class Mistral:
    def __init__(self) -> None:
        self._client = OpenAIClient(
            base_url=os.environ.get("OLLAMA_URL", "http://localhost:11434/v1"),
            api_key="ollama",
        )

    def generate(self, question: str, context: str, model: str = "mistral") -> str:
        response = self._client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"Answer based on the following context:\n\n{context}"},
                {"role": "user", "content": question},
            ],
        )
        return response.choices[0].message.content
