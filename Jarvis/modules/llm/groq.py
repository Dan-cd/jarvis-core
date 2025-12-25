from Jarvis.modules.llm.base import BaseLLM
from Jarvis.core.config import Config


class GroqLLM(BaseLLM):

    def __init__(self, client, model: str | None = None):
        self.client = client
        self.model = model or Config.GROQ_MODEL

    def generate(self, prompt: str, context: list) -> str:
        messages = context + [{"role": "user", "content": prompt}]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        return response.choices[0].message.content