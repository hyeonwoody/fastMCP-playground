import os
from openai import OpenAI as OpenAIClient


class OpenAI:
    def __init__(self) -> None:
        self._client = OpenAIClient(api_key=os.environ.get("OPENAI_API_KEY"))

    def generate(self, question: str, context: str, model: str = "gpt-4o-mini") -> str:
        response = self._client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"Answer based on the following context:\n\n{context}"},
                {"role": "user", "content": question},
            ],
        )
        return response.choices[0].message.content
