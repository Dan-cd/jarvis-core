from Jarvis.modules.llm.base import BaseLLM
import ollama


class OllamaLLM(BaseLLM):

    def __init__(self, model="phi"):
        self.model = model

    def generate(self, prompt: str, context: list) -> str:
        messages = context + [{"role": "user", "content": prompt}]

        response = ollama.chat(
            model=self.model,
            messages=messages
        )

        return response["message"]["content"]